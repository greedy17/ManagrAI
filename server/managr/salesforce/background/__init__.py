import logging
import json
import pytz
from datetime import datetime
from background_task import background

from django.utils import timezone

from managr.api.decorators import log_all_exceptions, sf_api_exceptions

from managr.core.models import User
from managr.organization.models import Account, Stage
from managr.organization.serializers import AccountSerializer, StageSerializer
from managr.opportunity.models import Opportunity
from managr.opportunity.serializers import OpportunitySerializer
from managr.slack import constants as slack_consts
from managr.slack.models import OrgCustomSlackForm
from managr.slack.helpers import requests as slack_requests
from managr.slack.helpers import block_builders
from managr.slack.helpers.block_sets import get_block_set

from ..routes import routes
from ..models import (
    SFSyncOperation,
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
from ..adapter.models import AccountAdapter, OpportunityAdapter, ActivityAdapter, ContactAdapter
from ..adapter.exceptions import TokenExpired, FieldValidationError, RequiredFieldError

from .. import constants as sf_consts

logger = logging.getLogger("managr")


def emit_sf_sync(user_id, sync_id, resource, offset):
    user_id = str(user_id)
    sync_id = str(sync_id)
    return _process_resource_sync(user_id, sync_id, resource, offset)


def emit_gen_next_sync(user_id, ops_list, schedule_time=timezone.now()):
    schedule = datetime.strptime(schedule_time, "%Y-%m-%dT%H:%M%Z")
    return _process_gen_next_sync(user_id, ops_list, schedule=schedule)


def emit_gen_next_object_field_sync(user_id, ops_list, schedule_time=timezone.now()):
    schedule = datetime.strptime(schedule_time, "%Y-%m-%dT%H:%M%Z")
    return _process_gen_next_object_field_sync(user_id, ops_list, schedule=schedule)


def emit_sync_sobject_fields(user_id, sync_id, resource):
    return _process_sobject_fields_sync(user_id, sync_id, resource)


def emit_sync_sobject_validations(user_id, sync_id, resource):
    return _process_sobject_validations_sync(user_id, sync_id, resource)


def emit_sync_sobject_picklist(user_id, sync_id, resource):
    return _process_picklist_values_sync(user_id, sync_id, resource)


def emit_save_meeting_review_data(user_id, data):
    return _process_add_call_to_sf(user_id, data)


def emit_add_call_to_sf(workflow_id, *args):
    return _process_add_call_to_sf(workflow_id, *args)


def emit_update_contacts(workflow_id, *args):
    return _process_update_contacts(workflow_id, *args)


def emit_create_new_contacts(workflow_id, *args):
    return _process_create_new_contacts(workflow_id, *args)


def emit_sf_update_resource_from_meeting(workflow_id, *args):
    return _process_update_resource_from_meeting(workflow_id, *args)


def emit_generate_form_template(user_id):
    return _generate_form_template(user_id)


# SF Resource Sync Tasks


@background(schedule=0)
@log_all_exceptions
def _process_gen_next_sync(user_id, operations_list):
    user = User.objects.filter(id=user_id).first()
    if not user:
        return logger.exception(f"User not found sync operation not created {user_id}")

    return SFSyncOperation.objects.create(user=user, operations_list=operations_list).begin_tasks()


@background(schedule=0)
@log_all_exceptions
def _process_gen_next_object_field_sync(user_id, operations_list):
    user = User.objects.filter(id=user_id).first()
    if not user:
        return logger.exception(f"User not found sync operation not created {user_id}")

    return SFObjectFieldsOperation.objects.create(
        user=user, operations_list=operations_list
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

        if form_type == slack_consts.FORM_TYPE_MEETING_REVIEW:
            fields = SObjectField.objects.filter(is_public=True)
            for i, field in enumerate(fields):
                f.fields.add(field, through_defaults={"order": i})
            f.save()


@background(schedule=0, queue=sf_consts.SALESFORCE_RESOURCE_SYNC_QUEUE)
@log_all_exceptions
def _process_resource_sync(user_id, sync_id, resource, offset, attempts=1):
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
            res = sf.list_resource_data(resource, offset)
            break
        except TokenExpired:
            if attempts >= 5:
                return logger.exception(
                    f"Failed to sync {resource} data for user {user_id} after {attempts} tries"
                )
            else:
                sf.regenerate_token()
                attempts += 1

    for item in res:
        existing = model_class.objects.filter(integration_id=item.integration_id).first()
        if existing:
            serializer = serializer_class(data=item.as_dict, instance=existing)
        else:
            serializer = serializer_class(data=item.as_dict)
        # check if already exists and update

        serializer.is_valid(raise_exception=True)
        serializer.save()

    return


# SFFieldOperation Tasks


@background(schedule=0, queue=sf_consts.SALESFORCE_RESOURCE_SYNC_QUEUE)
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
            break
        except TokenExpired:
            if attempts >= 5:
                return logger.exception(
                    f"Failed to sync {resource} data for user {sf.user.id}-{sf.user.email} after {attempts} tries"
                )
            else:
                sf.regenerate_token()
                attempts += 1

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
    return


@background(schedule=0, queue=sf_consts.SALESFORCE_RESOURCE_SYNC_QUEUE)
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
            break
        except TokenExpired:
            if attempts >= 5:
                return logger.exception(
                    f"Failed to sync {resource} data for user {sf.user.id}-{sf.user.email} after {attempts} tries"
                )
            else:
                sf.regenerate_token()
                attempts += 1

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


@background(schedule=0, queue=sf_consts.SALESFORCE_RESOURCE_SYNC_QUEUE)
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
            break
        except TokenExpired:
            if attempts >= 5:
                return logger.exception(
                    f"Failed to sync {resource} data for user {sf.user.id}-{sf.user.email} after {attempts} tries"
                )
            else:
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


@background(schedule=0, queue=sf_consts.SALESFORCE_MEETING_REVIEW_WORKFLOW_QUEUE)
@sf_api_exceptions("update_object_from_review")
def _process_update_resource_from_meeting(workflow_id, *args):
    # get workflow
    workflow = MeetingWorkflow.objects.get(id=workflow_id)
    user = workflow.user
    meeting = workflow.meeting
    sf = user.salesforce_account
    # collect forms for resource meeting_review and if stages any stages related forms
    update_forms = workflow.forms.filter(
        template__form_type__in=[
            slack_consts.FORM_TYPE_MEETING_REVIEW,
            slack_consts.FORM_TYPE_STAGE_GATING,
        ]
    )
    # aggregate the data
    data = dict()
    for form in update_forms:
        data = {**data, **form.saved_data}

    attempts = 1

    try:
        return workflow.resource.update_in_salesforce(data)
    except TokenExpired:
        if attempts >= 5:
            return logger.exception(
                f"Failed to sync STAGE data for user {str(user.id)} after {attempts} tries"
            )
        else:
            sf.regenerate_token()
            attempts += 1

    # push to sf
    return


@background(schedule=0, queue=sf_consts.SALESFORCE_MEETING_REVIEW_WORKFLOW_QUEUE)
@sf_api_exceptions("add_call_log")
def _process_add_call_to_sf(workflow_id, *args):
    workflow = MeetingWorkflow.objects.get(id=workflow_id)
    user = workflow.user
    if not user:
        return logger.exception(f"User not found unable to log call {str(user.id)}")
    if not hasattr(user, "salesforce_account"):
        return logger.exception("User does not have a salesforce account cannot push to sf")

    sf = user.salesforce_account

    attempts = 1
    review_form = workflow.forms.filter(
        template__form_type=slack_consts.FORM_TYPE_MEETING_REVIEW
    ).first()

    user_timezone = user.zoom_account.timezone
    start_time = workflow.meeting.start_time
    end_time = workflow.meeting.end_time
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
        Subject=f"Meeting - {review_form.saved_data.get('meeting_type')}",
        Description=f"{review_form.saved_data.get('meeting_comments')}, this meeting started on {formatted_start} and ended on {formatted_end} ",
        WhatId=workflow.resource.integration_id,
        ActivityDate=workflow.meeting.start_time.strftime("%Y-%m-%d"),
        Status="Completed",
        TaskSubType="Call",
    )
    try:
        return ActivityAdapter.save_zoom_meeting_to_salesforce(
            data, sf.access_token, sf.instance_url
        )
    except TokenExpired:
        if attempts >= 5:
            return logger.exception(
                f"Failed to refresh user token for Salesforce operation add contact as contact role to opportunity"
            )
        else:
            sf.regenerate_token()
            attempts += 1


@background(schedule=0, queue=sf_consts.SALESFORCE_MEETING_REVIEW_WORKFLOW_QUEUE)
@sf_api_exceptions("create_new_contacts")
def _process_create_new_contacts(workflow_id, *args):
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
        if not data:
            # try and collect whatever data we have
            contact = dict(
                *filter(
                    lambda contact: contact.get("_form") == str(form.id),
                    workflow.meeting.participants,
                )
            )
            if contact:
                form.save_form(contact.get("secondary_data", {}), from_slack_object=False)
        if workflow.resource_type == slack_consts.FORM_RESOURCE_ACCOUNT:
            data["AccountId"] = workflow.resource.integration_id
        while True:
            sf = user.salesforce_account
            sf_adapter = sf.adapter_class
            logger.info(f"Data from form {data}")
            try:
                res = ContactAdapter.create_new_contact(
                    data,
                    sf.access_token,
                    sf.instance_url,
                    sf_adapter.object_fields.get("Contact", {}),
                )

                if workflow.resource_type == slack_consts.FORM_RESOURCE_OPPORTUNITY:
                    workflow.resource.add_contact_role(
                        sf.access_token, sf.instance_url, res.get("id")
                    )
                break
            except TokenExpired:
                if attempts >= 5:
                    return logger.exception(
                        f"Failed to refresh user token for Salesforce operation add contact to sf failed {str(meeting.id)}"
                    )

                else:
                    sf.regenerate_token()
                    attempts += 1
    return


@background(schedule=0, queue=sf_consts.SALESFORCE_MEETING_REVIEW_WORKFLOW_QUEUE)
@sf_api_exceptions("update_contacts_or_link_contacts")
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
                    break
                except TokenExpired:
                    if attempts >= 5:
                        logger.exception(
                            f"Failed to refresh user token for Salesforce operation add contact to sf failed {str(meeting.id)}"
                        )
                        break
                    else:
                        sf.regenerate_token()
                        attempts += 1
        # if no data was saved the resource was not updated but we still add the contact role

        if workflow.resource_type == slack_consts.FORM_RESOURCE_OPPORTUNITY:
            attempts = 1
            while True:
                sf = user.salesforce_account
                sf_adapter = sf.adapter_class
                try:
                    workflow.resource.add_contact_role(
                        sf.access_token, sf.instance_url, form.resource_object.integration_id
                    )
                    break
                except TokenExpired:
                    if attempts >= 5:
                        logger.exception(
                            f"Failed to refresh user token for Salesforce operation add contact to sf failed {str(meeting.id)}"
                        )
                        break
                    else:
                        sf.regenerate_token()
                        attempts += 1

    return


### This is currently run as async so dont catch the errors in the same way
@background(schedule=0)
def _process_create_new_resource(workflow_id, resource, *args):
    workflow = MeetingWorkflow.objects.get(id=workflow_id)
    user = workflow.user
    # get the create form
    meeting = workflow.meeting
    create_forms = workflow.forms.filter(
        template__form_type__in=[
            slack_consts.FORM_TYPE_CREATE,
            slack_consts.FORM_TYPE_STAGE_GATING,
        ]
    ).exclude(template__resource=slack_consts.FORM_RESOURCE_CONTACT)
    sf = user.salesforce_account
    data = dict()
    for form in create_forms:
        data = {**data, **form.saved_data}

    attempts = 1
    while True:
        try:

            from managr.salesforce.adapter.routes import routes as adapter_routes
            from managr.salesforce.routes import routes as model_routes

            adapter = adapter_routes.get(resource)
            res = adapter.create(
                data,
                sf.access_token,
                sf.instance_url,
                sf.adapter_class.object_fields.get(resource),
                str(workflow.user.id),
            )
            serializer = model_routes.get(resource)["serializer"](data=res.as_dict)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return serializer.instance
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

