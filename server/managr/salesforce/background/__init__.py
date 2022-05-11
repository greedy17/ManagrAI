import logging
import json
import pytz
import time
import random
from datetime import datetime

from background_task import background
from background_task.models import CompletedTask, Task


from django.utils import timezone
from django.conf import settings
from django.template.loader import render_to_string
from django.db.models import Q

from rest_framework.exceptions import ValidationError, PermissionDenied

from managr.api.decorators import log_all_exceptions, sf_api_exceptions_wf
from managr.api.emails import send_html_email

from managr.core.models import User
from managr.organization.models import (
    Account,
    Stage,
    Contact,
    Organization,
    PricebookEntry,
    OpportunityLineItem,
)
from managr.organization.serializers import AccountSerializer, StageSerializer
from managr.opportunity.models import Opportunity, Lead
from managr.opportunity.serializers import OpportunitySerializer
from managr.slack import constants as slack_consts
from managr.slack.models import OrgCustomSlackForm, OrgCustomSlackFormInstance
from managr.slack.helpers import requests as slack_requests
from managr.slack.helpers import block_builders
from managr.slack.helpers.utils import action_with_params
from managr.slack.helpers.block_sets import get_block_set
from managr.slack.helpers.exceptions import CannotSendToChannel
from managr.slack.models import UserSlackIntegration

from ..routes import routes
from ..models import (
    SFResourceSync,
    SFObjectFieldsOperation,
    SObjectField,
    SObjectValidation,
    SObjectPicklist,
    MeetingWorkflow,
)
from ..serializers import (
    SObjectFieldSerializer,
    SObjectValidationSerializer,
    SObjectPicklistSerializer,
)
from ..adapter.models import (
    AccountAdapter,
    OpportunityAdapter,
    ActivityAdapter,
    ContactAdapter,
    OpportunityLineItemAdapter,
)
from ..adapter.exceptions import (
    TokenExpired,
    FieldValidationError,
    RequiredFieldError,
    SFQueryOffsetError,
    SFNotFoundError,
    UnableToUnlockRow,
    CannotRetreiveObjectType,
)
from managr.api.decorators import slack_api_exceptions
from .. import constants as sf_consts

logger = logging.getLogger("managr")


def emit_sf_sync(user_id, sync_id, resource, limit, offset):
    user_id = str(user_id)
    sync_id = str(sync_id)
    return _process_resource_sync(user_id, sync_id, resource, limit, offset)


def emit_gen_next_sync(user_id, ops_list, schedule_time=timezone.now()):
    schedule = datetime.strptime(schedule_time, "%Y-%m-%dT%H:%M%Z")
    return _process_gen_next_sync(user_id, ops_list, schedule=schedule)


def emit_gen_next_object_field_sync(user_id, ops_list, schedule_time=timezone.now()):
    schedule = datetime.strptime(schedule_time, "%Y-%m-%dT%H:%M%Z")
    return _process_gen_next_object_field_sync(user_id, ops_list, schedule=schedule)


def emit_sync_sobject_fields(user_id, sync_id, resource, scheduled_for=timezone.now()):
    return _process_sobject_fields_sync(user_id, sync_id, resource, schedule=scheduled_for)


def emit_sync_sobject_validations(user_id, sync_id, resource, scheduled_for=timezone.now()):
    return _process_sobject_validations_sync(user_id, sync_id, resource, schedule=scheduled_for)


def emit_sync_sobject_picklist(user_id, sync_id, resource, scheduled_for=timezone.now()):

    return _process_picklist_values_sync(user_id, sync_id, resource, schedule=scheduled_for)


def emit_add_call_to_sf(workflow_id, *args):
    return _process_add_call_to_sf(workflow_id, *args)


def emit_add_update_to_sf(form_id, *args):
    return _process_add_update_to_sf(form_id, *args)


def emit_update_contacts(workflow_id, *args):
    return _process_update_contacts(workflow_id, *args)


def emit_create_new_contacts(workflow_id, *args):
    return _process_create_new_contacts(workflow_id, *args)


def emit_sf_update_resource_from_meeting(workflow_id, *args):
    return _process_update_resource_from_meeting(workflow_id, *args)


def emit_add_products_to_sf(workflow_id, *args):
    return _process_add_products_to_sf(workflow_id, *args)


def emit_generate_form_template(user_id):
    return _generate_form_template(user_id)


def emit_update_current_db_values(user_id, resource_type, integration_id, verbose_name):
    return _update_current_db_values(
        user_id, resource_type, integration_id, verbose_name=verbose_name
    )


def emit_meeting_workflow_tracker(workflow_id):
    """Checks the workflow after 5 mins to ensure completion"""
    schedule = timezone.now() + timezone.timedelta(minutes=5)
    return _process_workflow_tracker(workflow_id, schedule=schedule)


# SF Resource Sync Tasks


@background(schedule=0)
@log_all_exceptions
def _process_gen_next_sync(user_id, operations_list):
    user = User.objects.filter(id=user_id).first()
    if not user:
        return logger.exception(f"User not found sync operation not created {user_id}")
    SFResourceSync.objects.create(
        user=user,
        operations_list=operations_list,
        operation_type=sf_consts.SALESFORCE_RESOURCE_SYNC,
    ).begin_tasks()
    return


@background(schedule=0)
@log_all_exceptions
def _process_pipeline_sync(sync_id):
    sync = SFResourceSync.objects.get(id=sync_id)
    sync.begin_tasks()
    return sync.id


@background(schedule=0)
@log_all_exceptions
def _process_gen_next_object_field_sync(user_id, operations_list):
    user = User.objects.filter(id=user_id).first()
    if not user:
        return logger.exception(f"User not found sync operation not created {user_id}")

    return SFObjectFieldsOperation.objects.create(
        user=user, operations_list=operations_list, operation_type=sf_consts.SALESFORCE_FIELD_SYNC
    ).begin_tasks()


@background()
@log_all_exceptions
def _generate_form_template(user_id):
    user = User.objects.get(id=user_id)
    org = user.organization
    # delete all existing forms

    org.custom_slack_forms.all().delete()
    for form in slack_consts.INITIAL_FORMS:
        resource, form_type = form.split(".")

        f = OrgCustomSlackForm.objects.create(
            form_type=form_type, resource=resource, organization=org
        )

        public_fields = SObjectField.objects.filter(
            is_public=True,
            id__in=slack_consts.DEFAULT_PUBLIC_FORM_FIELDS.get(resource, {}).get(form_type, []),
        )
        for i, field in enumerate(public_fields):
            f.fields.add(field, through_defaults={"order": i})
        f.save()


@background(schedule=0, queue=sf_consts.SALESFORCE_RESOURCE_SYNC_QUEUE)
@log_all_exceptions
def _process_resource_sync(user_id, sync_id, resource, limit, offset, attempts=1):
    user = User.objects.filter(id=user_id).select_related("salesforce_account").first()
    if not hasattr(user, "salesforce_account"):
        return

    # if route doesnt exist catch all will catch the value error here
    route = routes[resource]
    model_class = route["model"]
    serializer_class = route["serializer"]

    while True:
        sf = user.salesforce_account
        try:
            res = sf.list_resource_data(resource, offset, limit=limit)
            logger.info(f"Pulled total {len(res)} from request for {resource}")
            attempts = 1
            break
        except TokenExpired:
            if attempts >= 5:
                return logger.exception(
                    f"Failed to sync {resource} data for user {user_id} after {attempts} tries"
                )
            else:
                sleep = 1 * 2 ** attempts + random.uniform(0, 1)
                time.sleep(sleep)
                sf.regenerate_token()
                attempts += 1
        except SFQueryOffsetError:
            return logger.warning(
                f"Failed to sync some data for resource {resource} for user {user_id} because of SF LIMIT"
            )
    for item in res:
        existing = model_class.objects.filter(integration_id=item.integration_id).first()
        if existing:
            serializer = serializer_class(data=item.as_dict, instance=existing)
        else:
            serializer = serializer_class(data=item.as_dict)
        # check if already exists and update
        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError as e:
            error_str = f"Failed to save data for {resource} {item.name if item.name else 'N/A'} with salesforce id {item.integration_id} due to the following error {e.detail}"

            # context = dict(email=user.email, error=error_str)
            # subject = render_to_string("salesforce/error_saving_resource_data.txt")
            # recipient = [settings.STAFF_EMAIL]
            # send_html_email(
            #     subject,
            #     "salesforce/error_saving_resource_data.html",
            #     settings.SERVER_EMAIL,
            #     recipient,
            #     context={**context},
            # )
            logger.exception(error_str)
            continue
        serializer.save()

    return


# SFFieldOperation Tasks


@background(schedule=0, queue=sf_consts.SALESFORCE_FIELD_SYNC_QUEUE)
@log_all_exceptions
def _process_sobject_fields_sync(user_id, sync_id, resource):
    user = User.objects.filter(id=user_id).select_related("salesforce_account").first()
    if not hasattr(user, "salesforce_account"):
        return
    attempts = 1
    while True:
        sf = user.salesforce_account
        try:
            fields = sf.get_fields(resource)
            attempts = 1
            break
        except TokenExpired:
            if attempts >= 5:
                return logger.exception(
                    f"Failed to sync {resource} data for user {sf.user.id}-{sf.user.email} after {attempts} tries"
                )
            else:
                sleep = 1 * 2 ** attempts + random.uniform(0, 1)
                time.sleep(sleep)
                sf.regenerate_token()
                attempts += 1
        except CannotRetreiveObjectType:
            sf.sobjects[resource] = False

    # make fields into model and save them
    # need to update existing ones in case they are already on a form rather than override
    for field in fields:
        existing = SObjectField.objects.filter(
            api_name=field.api_name,
            salesforce_account_id=field.salesforce_account,
            salesforce_object=resource,
        ).first()
        if existing:
            serializer = SObjectFieldSerializer(data=field.as_dict, instance=existing)
        else:
            serializer = SObjectFieldSerializer(data=field.as_dict)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        # additionally retrieve picklist values
        if field.data_type == "Picklist" or field.data_type == "MultiPicklist":
            object_picklist = None
            while True:
                sf = user.salesforce_account
                try:
                    object_picklist = sf.get_individual_picklist_values(
                        resource, field=field.api_name
                    )
                    attempts = 1

                    break
                except TokenExpired:
                    if attempts >= 5:
                        return logger.exception(
                            f"Failed to sync {resource} data for user {sf.user.id}-{sf.user.email} after {attempts} tries"
                        )
                    else:
                        sleep = 1 * 2 ** attempts + random.uniform(0, 1)
                        time.sleep(sleep)
                        sf.regenerate_token()
                        attempts += 1
            if object_picklist:
                existing_picklist = SObjectPicklist.objects.filter(
                    picklist_for=object_picklist.picklist_for,
                    salesforce_account_id=object_picklist.salesforce_account,
                    salesforce_object=resource,
                ).first()
                if existing_picklist:
                    picklist_serializer = SObjectPicklistSerializer(
                        data=object_picklist.as_dict, instance=existing_picklist
                    )
                else:
                    picklist_serializer = SObjectPicklistSerializer(data=object_picklist.as_dict)
                picklist_serializer.is_valid(raise_exception=True)
                picklist_serializer.save()
    return


@background(schedule=0, queue=sf_consts.SALESFORCE_FIELD_SYNC_QUEUE)
@log_all_exceptions
def _process_picklist_values_sync(user_id, sync_id, resource):
    user = User.objects.filter(id=user_id).select_related("salesforce_account").first()
    if not hasattr(user, "salesforce_account"):
        return

    attempts = 1
    while True:
        sf = user.salesforce_account
        try:
            values = sf.get_picklist_values(resource)
            attempts = 1
            break
        except TokenExpired:
            if attempts >= 5:
                return logger.exception(
                    f"Failed to sync picklist values for {resource} for user {sf.user.id}-{sf.user.email} after {attempts} tries"
                )
            else:
                sleep = 1 * 2 ** attempts + random.uniform(0, 1)
                time.sleep(sleep)
                sf.regenerate_token()
                attempts += 1
        except SFNotFoundError:
            logger.exception(
                f"Failed to sync picklist values for {resource} for user {sf.user.id}-{sf.user.email}"
            )
    # make fields into model and save them
    # need to update existing ones in case they are already on a form rather than override
    for value in values:
        existing = SObjectPicklist.objects.filter(
            picklist_for=value.picklist_for,
            salesforce_account_id=value.salesforce_account,
            salesforce_object=resource,
        ).first()
        if existing:
            serializer = SObjectPicklistSerializer(data=value.as_dict, instance=existing)
        else:
            serializer = SObjectPicklistSerializer(data=value.as_dict)
        serializer.is_valid(raise_exception=True)
        serializer.save()
    return


@background(schedule=0, queue=sf_consts.SALESFORCE_FIELD_SYNC_QUEUE)
@log_all_exceptions
def _process_sobject_validations_sync(user_id, sync_id, resource):
    user = User.objects.filter(id=user_id).select_related("salesforce_account").first()
    if not hasattr(user, "salesforce_account"):
        return
    attempts = 1
    while True:
        sf = user.salesforce_account
        try:
            validations = sf.get_validations(resource)
            attempts = 1
            break
        except TokenExpired:
            if attempts >= 5:
                return logger.exception(
                    f"Failed to sync {resource} data for user {sf.user.id}-{sf.user.email} after {attempts} tries"
                )
            else:
                sleep = 1 * 2 ** attempts + random.uniform(0, 1)
                time.sleep(sleep)
                sf.regenerate_token()
                attempts += 1

    # make fields into model and save them
    for validation in validations:
        existing = SObjectValidation.objects.filter(
            integration_id=validation.integration_id
        ).first()
        if existing:
            serializer = SObjectValidationSerializer(data=validation.as_dict, instance=existing)
        else:
            serializer = SObjectValidationSerializer(data=validation.as_dict)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        serializer.instance
    return


## Meeting Review Workflow tasks


@background(
    schedule=0, queue=sf_consts.SALESFORCE_MEETING_REVIEW_WORKFLOW_QUEUE,
)
@sf_api_exceptions_wf("update_object_from_review")
def _process_update_resource_from_meeting(workflow_id, *args):
    # get workflow
    workflow = MeetingWorkflow.objects.get(id=workflow_id)
    user = workflow.user
    # collect forms for resource meeting_review and if stages any stages related forms
    update_forms = workflow.forms.filter(
        template__form_type__in=[
            slack_consts.FORM_TYPE_UPDATE,
            slack_consts.FORM_TYPE_STAGE_GATING,
        ]
    )
    update_form_ids = []
    # aggregate the data
    data = dict()
    for form in update_forms:
        update_form_ids.append(str(form.id))
        data = {**data, **form.saved_data}

    attempts = 1
    while True:
        sf = user.salesforce_account
        try:
            res = workflow.resource.update_in_salesforce(data)
            attempts = 1
            update_forms.update(
                is_submitted=True, submission_date=timezone.now(), update_source="meeting"
            )
            break
        except TokenExpired as e:
            if attempts >= 5:
                return logger.exception(
                    f"Failed to update resource from meeting for user {str(user.id)} for workflow {str(workflow.id)} with email {user.email} after {attempts} tries, {e}"
                )
            else:
                sleep = 1 * 2 ** attempts + random.uniform(0, 1)
                time.sleep(sleep)
                sf.regenerate_token()
                attempts += 1
        except UnableToUnlockRow as e:
            if attempts >= 5:
                logger.exception(
                    f"Failed to update resource from meeting for user {str(user.id)} for workflow {str(workflow.id)} with email {user.email} after {attempts} tries, {e}"
                )
                raise e
            else:
                sleep = 1 * 2 ** attempts + random.uniform(0, 1)
                time.sleep(sleep)
                attempts += 1
        except Exception as e:
            if len(user.slack_integration.recap_receivers):
                _send_recap(update_form_ids, None, True)
            raise e

    if len(user.slack_integration.recap_receivers):
        _send_recap(update_form_ids, None, True)
    # push to sf
    return res


@background(
    schedule=0, queue=sf_consts.SALESFORCE_MEETING_REVIEW_WORKFLOW_QUEUE,
)
@sf_api_exceptions_wf("add_call_log")
def _process_add_products_to_sf(workflow_id, non_meeting=False, *args):
    if non_meeting:
        product_form = OrgCustomSlackFormInstance.objects.get(id=workflow_id)
        opp = Opportunity.objects.get(id=product_form.resource_id)
        user = product_form.user
    # get workflow
    else:
        workflow = MeetingWorkflow.objects.get(id=workflow_id)
        update_forms = workflow.forms.filter(
            template__form_type__in=[
                slack_consts.FORM_TYPE_UPDATE,
                slack_consts.FORM_TYPE_STAGE_GATING,
            ]
        ).first()
        opp = Opportunity.objects.get(id=update_forms.resource_id)
        user = workflow.user
        product_form = workflow.forms.filter(template__resource="OpportunityLineItem").first()
    entry = PricebookEntry.objects.get(integration_id=product_form.saved_data["PricebookEntryId"])
    update_form_ids = []
    # aggregate the data
    data = dict(OpportunityId=opp.integration_id, UnitPrice=entry.unit_price)
    update_form_ids.append(str(product_form.id))
    data = {**data, **product_form.saved_data}
    sf = user.salesforce_account
    adapter = sf.adapter_class

    attempts = 1
    while True:
        sf = user.salesforce_account
        try:
            res = OpportunityLineItemAdapter.create(
                data,
                sf.access_token,
                sf.instance_url,
                adapter.object_fields.get("OpportunityLineItem", {}),
                user.id,
            )
            attempts = 1
            product_form.is_submitted = True
            product_form.submission_date = timezone.now()
            if non_meeting:
                product_form.save()
            else:
                workflow.save()
            break
        except TokenExpired as e:
            if attempts >= 5:
                return logger.exception(
                    f"Failed to update resource from meeting for user {str(user.id)} for workflow {str(workflow.id)} with email {user.email} after {attempts} tries, {e}"
                )
            else:
                sleep = 1 * 2 ** attempts + random.uniform(0, 1)
                time.sleep(sleep)
                sf.regenerate_token()
                attempts += 1
        except UnableToUnlockRow as e:
            if attempts >= 5:
                logger.exception(
                    f"Failed to update resource from meeting for user {str(user.id)} for workflow {str(workflow.id)} with email {user.email} after {attempts} tries, {e}"
                )
                raise e
            else:
                sleep = 1 * 2 ** attempts + random.uniform(0, 1)
                time.sleep(sleep)
                attempts += 1
        except Exception as e:
            raise e
    return res


@background(schedule=0, queue=sf_consts.SALESFORCE_MEETING_REVIEW_WORKFLOW_QUEUE)
@sf_api_exceptions_wf("add_call_log")
def _process_add_call_to_sf(workflow_id, *args):
    workflow = MeetingWorkflow.objects.get(id=workflow_id)
    user = workflow.user
    if not user:
        return logger.exception(f"User not found unable to log call {str(user.id)}")
    if not hasattr(user, "salesforce_account"):
        return logger.exception("User does not have a salesforce account cannot push to sf")
    review_form = workflow.forms.filter(template__form_type=slack_consts.FORM_TYPE_UPDATE).first()
    subject = review_form.saved_data.get("meeting_type")
    description = review_form.saved_data.get("meeting_comments")
    if workflow.meeting:
        title = workflow.meeting.topic if subject is None else subject
        user_timezone = user.zoom_account.timezone
        start_time = workflow.meeting.start_time
        end_time = workflow.meeting.end_time

    else:
        title = workflow.non_zoom_meeting.event_data["title"] if subject is None else subject
        user_timezone = user.timezone
        start_time = datetime.utcfromtimestamp(
            int(workflow.non_zoom_meeting.event_data["times"]["start_time"])
        )
        end_time = datetime.utcfromtimestamp(
            int(workflow.non_zoom_meeting.event_data["times"]["end_time"])
        )
    formatted_start = (
        datetime.strftime(
            start_time.astimezone(pytz.timezone(user_timezone)), "%a, %B, %Y %I:%M %p"
        )
        if start_time
        else start_time
    )
    formatted_end = (
        datetime.strftime(end_time.astimezone(pytz.timezone(user_timezone)), "%a, %B, %Y %I:%M %p")
        if end_time
        else end_time
    )
    data = dict(
        Subject=f"Zoom Meeting - {title}",
        Description=f"{'No comments' if description is None else description}, this meeting started on {formatted_start} and ended on {formatted_end} ",
        WhatId=workflow.resource.integration_id,
        ActivityDate=start_time.strftime("%Y-%m-%d"),
        Status="Completed",
        TaskSubType="Call",
    )
    attempts = 1
    while True:
        sf = user.salesforce_account
        try:
            ActivityAdapter.save_zoom_meeting_to_salesforce(data, sf.access_token, sf.instance_url)
            attempts = 1
            break
        except TokenExpired as e:
            if attempts >= 5:
                return logger.exception(
                    f"Failed to refresh user token for Salesforce operation add contact as contact role to opportunity"
                )
            else:
                sleep = 1 * 2 ** attempts + random.uniform(0, 1)
                time.sleep(sleep)
                sf.regenerate_token()
                attempts += 1
        except UnableToUnlockRow as e:
            if attempts >= 5:
                logger.exception(
                    f"Failed to create call log from meeting for user {str(user.id)} for workflow {str(workflow.id)} with email {user.email} after {attempts} tries, {e}"
                )
                raise e
            else:
                sleep = 1 * 2 ** attempts + random.uniform(0, 1)
                time.sleep(sleep)
                attempts += 1
    return


@background(schedule=0, queue=sf_consts.SALESFORCE_MEETING_REVIEW_WORKFLOW_QUEUE)
@sf_api_exceptions_wf("add_call_log")
def _process_add_update_to_sf(form_id, *args):
    form = OrgCustomSlackFormInstance.objects.filter(id=form_id).first()
    resource = None
    if form.resource_type == "Opportunity":
        resource = Opportunity.objects.get(id=form.resource_id)
    elif form.resource_type == "Account":
        resource = Account.objects.get(id=form.resource_id)
    elif form.resource_type == "Lead":
        resource = Lead.objects.get(id=form.resource_id)
    else:
        resource = Contact.objects.get(id=form.resource_id)
    user = form.user
    if not user:
        return logger.exception(f"User not found unable to log call {str(user.id)}")
    if not hasattr(user, "salesforce_account"):
        return logger.exception("User does not have a salesforce account cannot push to sf")
    start_time = form.submission_date
    subject = (
        "No subject"
        if form.saved_data.get("meeting_type") is None
        else form.saved_data.get("meeting_type")
    )
    data = dict(
        Subject=f"{subject}",
        Description=f"{form.saved_data.get('meeting_comments')}",
        ActivityDate=start_time.strftime("%Y-%m-%d"),
        Status="Completed",
        TaskSubType="Task",
    )
    if form.resource_type in ["Account", "Opportunity"]:
        data["WhatId"] = resource.integration_id
    else:
        data["WhoId"] = resource.integration_id
    attempts = 1
    while True:
        sf = user.salesforce_account
        try:
            ActivityAdapter.save_zoom_meeting_to_salesforce(data, sf.access_token, sf.instance_url)
            attempts = 1
            break
        except TokenExpired as e:
            if attempts >= 5:
                return logger.exception(
                    f"Failed to refresh user token for Salesforce operation add contact as contact role to opportunity"
                )
            else:
                sleep = 1 * 2 ** attempts + random.uniform(0, 1)
                time.sleep(sleep)
                sf.regenerate_token()
                attempts += 1
        except UnableToUnlockRow as e:
            if attempts >= 5:
                logger.exception(
                    f"Failed to create call log from meeting for user {str(user.id)} for workflow {str(workflow.id)} with email {user.email} after {attempts} tries, {e}"
                )
                raise e
            else:
                sleep = 1 * 2 ** attempts + random.uniform(0, 1)
                time.sleep(sleep)
                attempts += 1
        except Exception as e:
            if attempts >= 5:
                logger.info(f"Add update to SF exception: {e}")
                raise e
            else:
                sleep = 1 * 2 ** attempts + random.uniform(0, 1)
                time.sleep(sleep)
                attempts += 1
    return


# @background(schedule=0, queue=sf_consts.SALESFORCE_MEETING_REVIEW_WORKFLOW_QUEUE)
# @sf_api_exceptions_wf("add_call_log")
# def _process_add_event_to_sf(form_id, *args):
#     form = OrgCustomSlackFormInstance.objects.filter(id=form_id).first()
#     resource = None
#     if form.resource_type == "Opportunity":
#         resource = Opportunity.objects.get(id=form.resource_id)
#     elif form.resource_type == "Account":
#         resource = Account.objects.get(id=form.resource_id)
#     elif form.resource_type == "Lead":
#         resource = Lead.objects.get(id=form.resource_id)
#     else:
#         resource = Contact.objects.get(id=form.resource_id)
#     user = form.user
#     if not user:
#         return logger.exception(f"User not found unable to log call {str(user.id)}")
#     if not hasattr(user, "salesforce_account"):
#         return logger.exception("User does not have a salesforce account cannot push to sf")
#     start_time = form.submission_date
#     data = dict(
#         Subject=f"{form.saved_data.get('meeting_type')}",
#         Description=f"{form.saved_data.get('meeting_comments')}",
#         ActivityDate=start_time.strftime("%Y-%m-%d"),
#         DurationInMinutes=30,
#         ActivityDateTime=start_time.strftime("%Y-%m-%dT%H:%M:%S"),
#     )
#     if form.resource_type in ["Account", "Opportunity"]:
#         data["WhatId"] = resource.integration_id
#     else:
#         data["WhoId"] = resource.integration_id
#     attempts = 1
#     while True:
#         sf = user.salesforce_account
#         try:
#             ActivityAdapter.save_zoom_meeting_to_salesforce(data, sf.access_token, sf.instance_url)
#             attempts = 1
#             break
#         except TokenExpired as e:
#             if attempts >= 5:
#                 return logger.exception(
#                     f"Failed to refresh user token for Salesforce operation add contact as contact role to opportunity"
#                 )
#             else:
#                 sleep = 1 * 2 ** attempts + random.uniform(0, 1)
#                 time.sleep(sleep)
#                 sf.regenerate_token()
#                 attempts += 1
#         except UnableToUnlockRow as e:
#             if attempts >= 5:
#                 logger.exception(
#                     f"Failed to create call log from meeting for user {str(user.id)} for workflow {str(workflow.id)} with email {user.email} after {attempts} tries, {e}"
#                 )
#                 raise e
#             else:
#                 sleep = 1 * 2 ** attempts + random.uniform(0, 1)
#                 time.sleep(sleep)
#                 attempts += 1
#         except Exception as e:
#             if attempts >= 5:
#                 logger.info(f"Add update to SF exception: {e}")
#                 raise e
#             else:
#                 sleep = 1 * 2 ** attempts + random.uniform(0, 1)
#                 time.sleep(sleep)
#                 attempts += 1
#     return


@background(schedule=0, queue=sf_consts.SALESFORCE_MEETING_REVIEW_WORKFLOW_QUEUE)
@sf_api_exceptions_wf("create_new_contacts")
def _process_create_new_contacts(workflow_id, *args):
    workflow = MeetingWorkflow.objects.get(id=workflow_id)
    user = workflow.user
    if not user:
        return logger.exception(f"User not found unable to log call {str(user.id)}")
    if not hasattr(user, "salesforce_account"):
        return logger.exception("User does not have a salesforce account cannot push to sf")
    meeting = workflow.meeting if workflow.meeting else workflow.non_zoom_meeting
    attempts = 1
    if not len(args):
        return
    contact_forms = workflow.forms.filter(id__in=args[0])

    for form in contact_forms:
        # if the resource is an account we set it to that account
        # if it is an opp we create a contact role as well
        logger.info(f"FORM {form}")
        data = form.saved_data
        if not data:
            # try and collect whatever data we have
            contact = dict(
                *filter(lambda contact: contact.get("_form") == str(form.id), meeting.participants,)
            )
            if contact:
                form.save_form(contact.get("secondary_data", {}), from_slack_object=False)
                data = form.saved_data
        if workflow.resource_type == slack_consts.FORM_RESOURCE_ACCOUNT:
            data["AccountId"] = workflow.resource.integration_id
        while True:
            sf = user.salesforce_account
            sf_adapter = sf.adapter_class
            logger.info(f"Data from form {data}")
            try:
                res = ContactAdapter.create(
                    data,
                    sf.access_token,
                    sf.instance_url,
                    sf_adapter.object_fields.get("Contact", {}),
                    str(user.id),
                )
                attempts = 1
                form.is_submitted = True
                form.update_source = "meeting"
                form.submission_date = timezone.now()
                form.save()
                break
            except TokenExpired as e:
                if attempts >= 5:
                    return logger.exception(
                        f"Failed to refresh user token for Salesforce operation add contact to sf failed {str(workflow.id)}"
                    )

                else:
                    sleep = 1 * 2 ** attempts + random.uniform(0, 1)
                    time.sleep(sleep)
                    sf.regenerate_token()
                    attempts += 1
            except UnableToUnlockRow as e:
                if attempts >= 5:
                    logger.exception(
                        f"Failed to create contact for resource log from meeting for user {str(user.id)} for workflow {str(workflow.id)} with email {user.email} after {attempts} tries, {e}"
                    )
                    raise e
                else:
                    sleep = 1 * 2 ** attempts + random.uniform(0, 1)
                    time.sleep(sleep)
                    attempts += 1

        if (
            workflow.resource_type == slack_consts.FORM_RESOURCE_OPPORTUNITY
            and res
            and res.integration_id
        ):
            while True:
                sf = user.salesforce_account
                sf_adapter = sf.adapter_class
                logger.info(f"Adding Contact Role")
                try:

                    workflow.resource.add_contact_role(
                        sf.access_token, sf.instance_url, res.integration_id
                    )
                    attempts = 1
                    break
                except TokenExpired as e:
                    if attempts >= 5:
                        return logger.exception(
                            f"Failed to refresh user token for Salesforce operation add contact to sf failed"
                        )

                    else:
                        sleep = 1 * 2 ** attempts + random.uniform(0, 1)
                        time.sleep(sleep)
                        sf.regenerate_token()
                        attempts += 1
                except UnableToUnlockRow as e:
                    if attempts >= 5:
                        logger.exception(
                            f"Failed to add contact role to resource from meeting for user {str(user.id)} for workflow {str(workflow.id)} with email {user.email} after {attempts} tries, {e}"
                        )
                        raise e
                    else:
                        sleep = 1 * 2 ** attempts + random.uniform(0, 1)
                        time.sleep(sleep)
                        attempts += 1
    return


@background(schedule=0, queue=sf_consts.SALESFORCE_MEETING_REVIEW_WORKFLOW_QUEUE)
@sf_api_exceptions_wf("update_contacts_or_link_contacts")
def _process_update_contacts(workflow_id, *args):
    workflow = MeetingWorkflow.objects.get(id=workflow_id)
    user = workflow.user
    if not user:
        return logger.exception(f"User not found unable to log call {str(user.id)}")
    if not hasattr(user, "salesforce_account"):
        return logger.exception("User does not have a salesforce account cannot push to sf")

    attempts = 1
    contact_forms = workflow.forms.filter(id__in=args[0])
    for form in contact_forms:
        # if the resource is an account we set it to that account
        # if it is an opp we create a contact role as well
        data = form.saved_data
        if workflow.resource_type == slack_consts.FORM_RESOURCE_ACCOUNT:
            data["AccountId"] = workflow.resource.integration_id
        if data:
            while True:
                sf = user.salesforce_account
                sf_adapter = sf.adapter_class
                try:
                    ContactAdapter.update_contact(
                        data,
                        sf.access_token,
                        sf.instance_url,
                        form.resource_object.integration_id,
                        sf_adapter.object_fields.get("Contact", {}),
                    )
                    attempts = 1
                    form.is_submitted = True
                    form.update_source = "meeting"
                    form.submission_date = timezone.now()
                    form.save()
                    break
                except TokenExpired as e:
                    if attempts >= 5:
                        logger.exception(
                            f"Failed to refresh user token for Salesforce operation add contact to sf failed {str(workflow.id)}"
                        )

                    else:
                        sleep = 1 * 2 ** attempts + random.uniform(0, 1)
                        time.sleep(sleep)
                        sf.regenerate_token()
                        attempts += 1
                except UnableToUnlockRow as e:
                    if attempts >= 5:
                        logger.exception(
                            f"Failed to update contact from meeting for user {str(user.id)} for workflow {str(workflow.id)} with email {user.email} after {attempts} tries, {e}"
                        )
                        raise e
                    else:
                        sleep = 1 * 2 ** attempts + random.uniform(0, 1)
                        time.sleep(sleep)
                        attempts += 1

        # if no data was saved the resource was not updated but we still add the contact role

        if workflow.resource_type == slack_consts.FORM_RESOURCE_OPPORTUNITY:
            attempts = 1
            while True:
                sf = user.salesforce_account
                sf_adapter = sf.adapter_class
                try:
                    # check to see if it already has a contact role by checking linked_contacts
                    is_linked = workflow.resource.contacts.filter(
                        integration_id=form.resource_object.integration_id
                    ).first()
                    if not is_linked:
                        workflow.resource.add_contact_role(
                            sf.access_token, sf.instance_url, form.resource_object.integration_id
                        )
                        attempts = 1
                    break

                except TokenExpired as e:
                    if attempts >= 5:
                        return logger.exception(
                            f"Failed to refresh user token for Salesforce operation add contact to sf failed {str(meeting.id)}"
                        )

                    else:
                        sleep = 1 * 2 ** attempts + random.uniform(0, 1)
                        time.sleep(sleep)
                        sf.regenerate_token()
                        attempts += 1

                except UnableToUnlockRow as e:
                    if attempts >= 5:
                        logger.exception(
                            f"Failed to add contact role from meeting for user {str(user.id)} for workflow {str(workflow.id)} with email {user.email} after {attempts} tries, {e}"
                        )
                        raise e
                    else:
                        sleep = 1 * 2 ** attempts + random.uniform(0, 1)
                        time.sleep(sleep)
                        attempts += 1
    return


### This is currently run as async so dont catch the errors in the same way
@background(schedule=0)
def _process_create_new_resource(form_ids, *args):

    create_forms = OrgCustomSlackFormInstance.objects.filter(id__in=form_ids)
    if not create_forms.count():
        return logger.exception(f"An error occured no form was found")
    user = create_forms.first().user
    resource = create_forms.first().resource_type
    # get the create form
    data = dict()
    for form in create_forms:
        data = {**data, **form.saved_data}

    attempts = 1
    while True:
        sf = user.salesforce_account
        try:

            from managr.salesforce.adapter.routes import routes as adapter_routes
            from managr.salesforce.routes import routes as model_routes

            adapter = adapter_routes.get(resource)
            res = adapter.create(
                data,
                sf.access_token,
                sf.instance_url,
                sf.adapter_class.object_fields.get(resource),
                str(user.id),
            )
            serializer = model_routes.get(resource)["serializer"](data=res.as_dict)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return serializer.instance
        except TokenExpired as e:
            if attempts >= 5:
                return logger.exception(
                    f"Failed to create new resource for user {str(user.id)} after {attempts} tries because their token is expired"
                )
            else:
                sf.regenerate_token()
                attempts += 1
        except FieldValidationError as e:
            logger.exception(
                f"Failed to create new resource for user {str(user.id)} becuase they have a field validation error"
            )
            raise FieldValidationError(e)
        except RequiredFieldError as e:
            logger.exception(
                f"Failed to create new resource for user {str(user.id)} becuase they have a field validation error"
            )
            raise RequiredFieldError(e)

    return


@background(schedule=0)
def _process_create_task(user_id, data, *args):

    user = User.objects.get(id=user_id)
    # get the create form

    attempts = 1
    while True:
        sf = user.salesforce_account
        from managr.salesforce.adapter.models import TaskAdapter

        try:
            TaskAdapter.save_task_to_salesforce(data, sf.access_token, sf.instance_url)
            break
        except TokenExpired:
            if attempts >= 5:
                return logger.exception(
                    f"Failed to create new resource for user {str(user.id)} after {attempts} tries because their token is expired"
                )
            else:
                sf.regenerate_token()
                attempts += 1
        except FieldValidationError as e:
            logger.exception(
                f"Failed to create new resource for user {str(user.id)} becuase they have a field validation error"
            )
            raise FieldValidationError(e)
        except RequiredFieldError as e:
            logger.exception(
                f"Failed to create new resource for user {str(user.id)} becuase they have a field validation error"
            )
            raise RequiredFieldError(e)

    return


@background(schedule=0)
def _process_create_event(user_id, data, *args):

    user = User.objects.get(id=user_id)
    # get the create form

    attempts = 1
    while True:
        sf = user.salesforce_account
        from managr.salesforce.adapter.models import EventAdapter

        try:
            EventAdapter.save_event_to_salesforce(data, sf.access_token, sf.instance_url)
            break
        except TokenExpired:
            if attempts >= 5:
                return logger.exception(
                    f"Failed to create new resource for user {str(user.id)} after {attempts} tries because their token is expired"
                )
            else:
                sf.regenerate_token()
                attempts += 1
        except FieldValidationError as e:
            logger.exception(
                f"Failed to create new resource for user {str(user.id)} becuase they have a field validation error"
            )
            raise FieldValidationError(e)
        except RequiredFieldError as e:
            logger.exception(
                f"Failed to create new resource for user {str(user.id)} becuase they have a field validation error"
            )
            raise RequiredFieldError(e)

    return


@background(schedule=0)
def _process_list_tasks(user_id, data, *args):

    user = User.objects.get(id=user_id)
    # get the create form

    attempts = 1
    while True:
        sf = user.salesforce_account
        from managr.salesforce.adapter.models import TaskAdapter

        try:
            TaskAdapter.save_task_to_salesforce(data, sf.access_token, sf.instance_url)
            break
        except TokenExpired:
            if attempts >= 5:
                return logger.exception(
                    f"Failed to create new resource for user {str(user.id)} after {attempts} tries because their token is expired"
                )
            else:
                sf.regenerate_token()
                attempts += 1
        except FieldValidationError as e:
            logger.exception(
                f"Failed to create new resource for user {str(user.id)} becuase they have a field validation error"
            )
            raise FieldValidationError(e)
        except RequiredFieldError as e:
            logger.exception(
                f"Failed to create new resource for user {str(user.id)} becuase they have a field validation error"
            )
            raise RequiredFieldError(e)

    return


@background(schedule=0)
@log_all_exceptions
def _process_workflow_tracker(workflow_id):
    """gets workflow and check's if all tasks are completed and manually completes if not already completed"""
    workflow = MeetingWorkflow.objects.filter(id=workflow_id).first()
    workflow.user.activity.add_meeting_activity(workflow_id)
    if workflow and workflow.in_progress:
        completed_tasks = set(workflow.completed_operations)
        all_tasks = set(workflow.operations)
        tasks_diff = list(all_tasks - completed_tasks)
        for task_hash in tasks_diff:
            # check to see if there was a problem completing the flow but all tasks are ready
            task = CompletedTask.objects.filter(task_hash=task_hash).count()
            if task:
                workflow.completed_operations.append(task_hash)
                workflow.save()


@background(schedule=0)
@log_all_exceptions
def _process_stale_data_for_delete(batch):
    for record in batch:
        # running this as for loop instead of bulk delete to keep track of records deleted
        try:
            u = User.objects.filter(id=record["user_id"]).first()
            if u:
                for resource, values in record["resource"].items():
                    qs = getattr(u, f"imported_{resource}").filter(id__in=values)
                    logger.info(
                        f"deleting {qs.count()} {resource} for user {u.email} with id {str(u.id)}"
                    )
                    qs.delete()

        except Exception as e:
            logger.exception(e)
            pass
    return


def check_for_display_value(field, value):
    from managr.salesforce.routes import routes as model_routes

    if not value:
        return value
    is_list = field.allow_multiple
    model_class = model_routes.get(field.relationship_name, {}).get("model", None)
    if not model_class:
        return value

    if field.is_public == True:
        display_keys = (
            field.display_value_keys.get("name_fields", None) if field.display_value_keys else []
        )
        if not len(display_keys):
            return value
        if is_list:
            value = value.split(";")
            results = list(model_class.objects.filter(id__in=value).values_list(*display_keys))
        else:
            results = list(model_class.objects.filter(id__in=value).values_list(*display_keys))
        if results and len(results):
            return ",".join(list(map(lambda display_vals: " ".join(display_vals), results)))
        else:
            return value


@background(schedule=0)
@slack_api_exceptions(rethrow=True)
def _send_recap(form_ids, send_to_data=None, manager_recap=False, bulk=False):
    submitted_forms = OrgCustomSlackFormInstance.objects.filter(id__in=form_ids).exclude(
        template__resource="OpportunityLineItem"
    )
    main_form = submitted_forms.filter(template__form_type__in=["CREATE", "UPDATE"]).first()
    user = main_form.user
    send_summ_to_leadership = send_to_data.get("leadership", None) if send_to_data else None
    send_summ_to_reps = send_to_data.get("reps", None) if send_to_data else None
    send_summ_to_channels = send_to_data.get("channels", None) if send_to_data else None
    resource_name = main_form.resource_object.name if main_form.resource_object.name else ""
    slack_access_token = user.organization.slack_integration.access_token
    title = (
        ":zap: *Instant Update:* Meeting Logged"
        if manager_recap
        else f":zap: *{main_form.template.resource} Recap*"
    )
    if bulk:
        title = ":zap: *Bulk Update* "
        text = ""
        for index, form in enumerate(submitted_forms):
            text += f"{form.resource_object.name}"
            if index != len(submitted_forms):
                text += ", "
    else:
        text = f"_{main_form.template.resource}_ *{resource_name}*"
    blocks = [
        block_builders.simple_section(title, "mrkdwn"),
        block_builders.section_with_button_block(
            "View Recap",
            "recap",
            text,
            action_id=action_with_params(
                slack_consts.VIEW_RECAP,
                params=[f"u={str(user.id)}", f"form_ids={','.join(form_ids)}"],
            ),
        ),
        block_builders.context_block(f"{main_form.template.resource} owned by {user.full_name}"),
    ]
    if manager_recap:
        user_channel_list = UserSlackIntegration.objects.filter(
            slack_id__in=user.slack_integration.recap_receivers
        )
        for u in user_channel_list:
            try:
                slack_requests.send_channel_message(
                    u.recap_channel,
                    slack_access_token,
                    text=f"Recap {main_form.template.resource}",
                    block_set=blocks,
                )
            except CannotSendToChannel:
                try:
                    slack_requests.send_channel_message(
                        user.slack_integration.channel,
                        slack_access_token,
                        text=f"Failed to send recap to channel",
                        block_set=[
                            block_builders.simple_section(
                                f"Unable to send recap to one of the channels you selected, please add <@{user.organization.slack_integration.bot_user_id}> to the channel _*<#{channel}>*_",
                                "mrkdwn",
                            )
                        ],
                    )
                    continue
                except Exception as e:
                    logger.exception(
                        f"Failed to send error message to user informing them of channel issue to {user.email} due to {e}"
                    )
                    continue
            except Exception as e:
                logger.exception(
                    f"Failed to send recap to channel for user {user.email} due to {e}"
                )
                continue
    else:
        query = None
        user_list = []
        if send_summ_to_leadership is not None:
            query = Q(user_level="MANAGER", id__in=send_summ_to_leadership)
            user_list.extend(
                user.organization.users.filter(query)
                .filter(is_active=True)
                .distinct()
                .select_related("slack_integration")
            )
        if send_summ_to_reps is not None:
            query = Q(id__in=send_summ_to_reps)
            user_list.extend(
                user.organization.users.filter(query)
                .filter(is_active=True)
                .distinct()
                .select_related("slack_integration")
            )
        logger.info(f"USERS LIST RECAP: {user_list}")
        for u in user_list:
            if hasattr(u, "slack_integration"):
                try:
                    r = slack_requests.send_channel_message(
                        u.slack_integration.channel,
                        slack_access_token,
                        text=f"Recap {main_form.template.resource}",
                        block_set=blocks,
                    )
                    logger.info(f"SEND RECAP RESPONSE: {r}")
                except Exception as e:
                    logger.exception(f"Failed to send recap to {u.email} due to {e}")
                    continue
        if send_summ_to_channels is not None:
            for channel in send_summ_to_channels:
                try:
                    r = slack_requests.send_channel_message(
                        channel,
                        slack_access_token,
                        text=f"Recap {main_form.template.resource}",
                        block_set=blocks,
                    )
                    logger.info(f"SEND RECAP CHANNEL RESPONSE: {r}")
                except CannotSendToChannel:
                    try:
                        slack_requests.send_channel_message(
                            user.slack_integration.channel,
                            slack_access_token,
                            text="Failed to send recap to channel",
                            block_set=[
                                block_builders.simple_section(
                                    f"Unable to send recap to one of the channels you selected, please add <@{user.organization.slack_integration.bot_user_id}> to the channel _*<#{channel}>*_",
                                    "mrkdwn",
                                )
                            ],
                        )
                        continue
                    except Exception as e:
                        logger.exception(
                            f"Failed to send error message to user informing them of channel issue to {user.email} due to {e}"
                        )
                        continue
                except Exception as e:
                    logger.exception(
                        f"Failed to send recap to channel for user {user.email} due to {e}"
                    )
                    continue


def create_alert_string(operator, data_type, config_value, saved_value, old_value, title):
    alert_string = f"{title}"
    if data_type == "date":
        saved_value = datetime.strptime(saved_value, "%Y-%m-%d")
        old_value = datetime.strptime(old_value, "%Y-%m-%d")
    if operator == "==":
        if data_type == "string" and saved_value == config_value and saved_value != old_value:
            return alert_string
    elif operator == "<=":
        if saved_value <= config_value:
            return alert_string
    elif operator == ">=":
        if saved_value >= config_value:
            return alert_string
    elif operator == "!=":
        if data_type == "string" and saved_value != config_value:
            return alert_string
        elif data_type == "date" and old_value is not None and saved_value.month != old_value.month:
            return alert_string
    return None


@background(schedule=0)
@slack_api_exceptions(rethrow=True)
def _send_instant_alert(form_ids):
    submitted_forms = OrgCustomSlackFormInstance.objects.filter(id__in=form_ids).exclude(
        template__resource="OpportunityLineItem"
    )
    main_form = submitted_forms.filter(template__form_type__in=["CREATE", "UPDATE"]).first()
    user = main_form.user
    configs = user.slack_integration.realtime_alert_configs
    sobject_fields = list(
        SObjectField.objects.filter(id__in=configs.keys()).values("id", "api_name")
    )
    resource_name = main_form.resource_object.name if main_form.resource_object.name else ""

    old_data = dict()

    if main_form.template.form_type == "UPDATE":
        for additional_stage_form in submitted_forms:
            old_data = {**old_data, **additional_stage_form.previous_data}
    new_data = dict()
    for form in submitted_forms:
        new_data = {**new_data, **form.saved_data}
    users_list = {}
    for field in sobject_fields:
        api_name = field["api_name"]
        if api_name in new_data.keys():
            for object in configs[str(field["id"])].values():
                if api_name in list(object.values()):
                    old_value = old_data[api_name] if len(old_data) else None
                    value_check = create_alert_string(
                        object["operator"],
                        object["data_type"],
                        object["value"],
                        new_data[api_name],
                        old_value,
                        object["title"],
                    )
                    if value_check:
                        recipients = object["recipients"]
                        for key in recipients.keys():
                            channel = recipients[key]
                            if recipients[key] in users_list.keys():
                                users_list[channel]["text"] += f", _{value_check}_"
                            else:
                                users_list[channel] = {
                                    "text": f":zap: *Instant Update:* _{value_check}_",
                                    "id": key,
                                }
                else:
                    continue
    if len(users_list):
        add_blocks = [
            block_builders.section_with_button_block(
                "View Recap",
                "recap",
                f"_{main_form.template.resource}_ *{resource_name}*",
                action_id=action_with_params(
                    slack_consts.VIEW_RECAP,
                    params=[f"u={str(user.id)}", f"form_ids={','.join(form_ids)}"],
                ),
            ),
            block_builders.context_block(
                f"{main_form.template.resource} owned by {user.full_name}"
            ),
        ]
        for key in users_list:
            blocks = [
                block_builders.simple_section(users_list[key]["text"], "mrkdwn"),
                *add_blocks,
            ]
            user = User.objects.get(id=users_list[key]["id"])
            try:
                slack_requests.send_channel_message(
                    key,
                    user.organization.slack_integration.access_token,
                    text=f"Recap {main_form.template.resource}",
                    block_set=blocks,
                )
            except CannotSendToChannel:
                try:
                    slack_requests.send_channel_message(
                        key,
                        user.organization.slack_integration.access_token,
                        text="Failed to send recap to channel",
                        block_set=[
                            block_builders.simple_section(
                                f"Unable to send recap to one of the channels you selected, please add <@{user.organization.slack_integration.bot_user_id}> to the channel _*<#{channel}>*_",
                                "mrkdwn",
                            )
                        ],
                    )
                    continue
                except Exception as e:
                    logger.exception(
                        f"Failed to send error message to user informing them of channel issue to {user.email} due to {e}"
                    )
                    continue
            except Exception as e:
                logger.exception(
                    f"Failed to send recap to channel for user {user.email} due to {e}"
                )
                continue
        return


def remove_field(org_id, form_field):
    org = Organization.objects.get(id=org_id)
    forms = OrgCustomSlackForm.objects.filter(organization=org)
    for form in forms:
        for index, field in enumerate(form.fields.all().order_by("forms__order")):
            if str(field.id) != form_field:
                field.forms.first().order = index
                field.forms.first().save()
            else:
                form.fields.remove(field.id)
    return


@background(schedule=0)
@slack_api_exceptions(rethrow=True)
def _send_convert_recap(form_id, account_id, contact_id, opportunity_id=None, send_to_data=None):
    lead_form = OrgCustomSlackFormInstance.objects.get(id=form_id)
    user = lead_form.user
    send_summ_to_leadership = send_to_data.get("leadership", None) if send_to_data else None
    send_summ_to_reps = send_to_data.get("reps", None) if send_to_data else None
    send_summ_to_channels = send_to_data.get("channels", None) if send_to_data else None
    slack_access_token = user.organization.slack_integration.access_token
    account = Account.objects.get(integration_id=account_id)
    contact = Contact.objects.get(integration_id=contact_id)
    opportunity = Opportunity.objects.get(integration_id=opportunity_id)
    text = f":zap: *Lead Convert Recap: {lead_form.resource_object.name}*\n*Account*: {account.name}\n*Opportunity*: {opportunity.name}\n*Contact*: {contact.secondary_data['Name']}"
    blocks = [
        block_builders.simple_section(text, "mrkdwn"),
        block_builders.context_block(f"Lead owned by {user.full_name}"),
    ]
    query = None
    user_list = []
    if send_summ_to_leadership is not None:
        query = Q(user_level="MANAGER", id__in=send_summ_to_leadership)
        user_list.extend(
            user.organization.users.filter(query)
            .filter(is_active=True)
            .distinct()
            .select_related("slack_integration")
        )
    if send_summ_to_reps is not None:
        query = Q(id__in=send_summ_to_reps)
        user_list.extend(
            user.organization.users.filter(query)
            .filter(is_active=True)
            .distinct()
            .select_related("slack_integration")
        )
    logger.info(f"USERS LIST RECAP: {user_list}")
    for u in user_list:
        if hasattr(u, "slack_integration"):
            try:
                r = slack_requests.send_channel_message(
                    u.slack_integration.channel,
                    slack_access_token,
                    text=f"Recap Lead",
                    block_set=blocks,
                )
                logger.info(f"SEND RECAP RESPONSE: {r}")
            except Exception as e:
                logger.exception(f"Failed to send recap to {u.email} due to {e}")
                continue
    if send_summ_to_channels is not None:
        for channel in send_summ_to_channels:
            try:
                r = slack_requests.send_channel_message(
                    channel, slack_access_token, text=f"Recap Lead", block_set=blocks,
                )
                logger.info(f"SEND RECAP CHANNEL RESPONSE: {r}")
            except CannotSendToChannel:
                try:
                    slack_requests.send_channel_message(
                        user.slack_integration.channel,
                        slack_access_token,
                        text="Failed to send recap to channel",
                        block_set=[
                            block_builders.simple_section(
                                f"Unable to send recap to one of the channels you selected, please add <@{user.organization.slack_integration.bot_user_id}> to the channel _*<#{channel}>*_",
                                "mrkdwn",
                            )
                        ],
                    )
                    continue
                except Exception as e:
                    logger.exception(
                        f"Failed to send error message to user informing them of channel issue to {user.email} due to {e}"
                    )
                    continue
            except Exception as e:
                logger.exception(
                    f"Failed to send recap to channel for user {user.email} due to {e}"
                )
                continue


@background(schedule=0)
@slack_api_exceptions(rethrow=True)
def _update_current_db_values(user_id, resource_type, integration_id):
    from managr.salesforce.routes import routes as model_routes

    user = User.objects.get(id=user_id)
    route = model_routes[resource_type]
    model_class = route["model"]
    resource = model_class.objects.filter(integration_id=integration_id).first()
    if resource:
        current_values = resource.get_current_values()
        serializer = routes[resource_type]["serializer"](
            data=current_values.as_dict, instance=resource
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        logger.info(f"Successfully {resource} in the Database for user {user.email}")
    return
