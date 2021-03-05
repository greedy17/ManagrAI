import logging
import json
from datetime import datetime
from background_task import background

from django.utils import timezone

from managr.api.decorators import log_all_exceptions

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
from ..adapter.models import AccountAdapter, OpportunityAdapter, ActivityAdapter
from ..adapter.exceptions import TokenExpired

from .. import constants as sf_consts

logger = logging.getLogger("managr")


## for testing


def emit_fake_event_end(workflow_id):
    schedule = timezone.now() - timezone.timedelta(seconds=30)
    return _process_fake_event_end(workflow_id, schedule=schedule)


@background(schedule=0)
def _process_fake_event_end(workflow_id):
    w = MeetingWorkflow.objects.filter(id=workflow_id).first()
    user = w.user
    access_token = user.organization.slack_integration.access_token
    ts, channel = w.meeting.slack_interaction.split("|")
    res = slack_requests.update_channel_message(
        channel,
        ts,
        access_token,
        block_set=get_block_set("final_meeting_interaction", context={"m": str(w.meeting.id)}),
    ).json()

    w.meeting.slack_interaction = f"{res['ts']}|{res['channel']}"
    w.meeting.save()

    return


def emit_sf_sync(user_id, sync_id, resource, offset):
    user_id = str(user_id)
    sync_id = str(sync_id)
    return _process_resource_sync(user_id, sync_id, resource, offset)


def emit_gen_next_sync(user_id, ops_list, schedule_time=timezone.now()):
    schedule = datetime.strptime(schedule_time, "%Y-%m-%dT%H:%M%Z")
    return _process_gen_next_sync(user_id, ops_list, schedule=schedule)


def emit_gen_next_object_field_opp_sync(user_id, ops_list, schedule_time=timezone.now()):
    schedule = datetime.strptime(schedule_time, "%Y-%m-%dT%H:%M%Z")
    return _process_gen_next_object_field_opp_sync(user_id, ops_list, schedule=schedule)


def emit_sync_sobject_fields(user_id, sync_id, resource):
    return _process_sobject_fields_sync(user_id, sync_id, resource)


def emit_sync_sobject_validations(user_id, sync_id, resource):
    return _process_sobject_validations_sync(user_id, sync_id, resource)


def emit_sync_sobject_picklist(user_id, sync_id, resource):
    return _process_picklist_values_sync(user_id, sync_id, resource)


def emit_sf_add_call_to_sf(user_id, data):
    return _process_add_call_to_sf(user_id, data)


def emit_sf_update_opportunity(user_id, meeting_review_id):
    return _process_update_opportunity(user_id, meeting_review_id)


def emit_add_c_role_to_opp(user_id, opp_id, sf_contact_id):
    return _process_add_c_role_to_opp(user_id, opp_id, sf_contact_id)


def emit_generate_form_template(user_id):
    return _generate_form_template(user_id)


@background(schedule=0)
@log_all_exceptions
def _process_add_call_to_sf(user_id, data, attempts=1):
    user = User.objects.filter(id=user_id).first()
    if not user:
        return logger.exception(f"User not found unable to log call {user_id}")
    if not hasattr(user, "salesforce_account"):
        return logger.exception("User does not have a salesforce account cannot push to sf")

    sf = user.salesforce_account
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
            return _process_add_call_to_sf(user_id, data, attempts=attempts)


@background(schedule=0)
@log_all_exceptions
def _process_add_c_role_to_opp(user_id, opp_id, sf_contact_id, attempts=1):
    user = User.objects.filter(id=user_id).first()
    if not user:
        return logger.exception(
            f"User not found add contact role not initiated {user_id}, {str(opp_id)}, {sf_contact_id}"
        )
    opp = user.owned_opportunities.filter(id=opp_id).first()
    if not opp:
        return logger.exception(
            f"Opportunity not found add contact role not initiated {user_id}, {str(opp_id)}, {sf_contact_id}"
        )
    sf = user.salesforce_account
    try:
        opp.add_contact_role(sf.access_token, sf.instance_url, sf_contact_id)
    except TokenExpired:
        if attempts >= 5:
            return logger.exception(
                f"Failed to refresh user token for Salesforce operation add contact as contact role to opportunity"
            )
        else:
            sf.regenerate_token()
            attempts += 1
            return _process_add_c_role_to_opp(user_id, opp_id, sf_contact_id, attempts=attempts)


@background(schedule=0)
@log_all_exceptions
def _process_gen_next_sync(user_id, operations_list):
    user = User.objects.filter(id=user_id).first()
    if not user:
        return logger.exception(f"User not found sync operation not created {user_id}")

    return SFSyncOperation.objects.create(user=user, operations_list=operations_list).begin_tasks()


@background(schedule=0)
@log_all_exceptions
def _process_gen_next_object_field_opp_sync(user_id, operations_list):
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
    for form in slack_consts.INITIAL_FORMS:
        resource, form_type = form.split(".")

        f = OrgCustomSlackForm.objects.create(
            form_type=form_type, resource=resource, organization=org
        )
        if form_type == slack_consts.FORM_TYPE_MEETING_REVIEW:
            f.fields.set(SObjectField.objects.filter(is_public=True))
            f.save()


@background(schedule=0, queue=sf_consts.SALESFORCE_RESOURCE_SYNC_QUEUE)
@log_all_exceptions
def _process_resource_sync(user_id, sync_id, resource, offset, attempts=1):
    user = User.objects.filter(id=user_id).select_related("salesforce_account").first()
    if not hasattr(user, "salesforce_account"):
        return
    sf = user.salesforce_account

    # if route doesnt exist catch all will catch the value error here
    route = routes[resource]
    model_class = route["model"]
    serializer_class = route["serializer"]

    while True:
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


@background(schedule=0, queue=sf_consts.SALESFORCE_RESOURCE_SYNC_QUEUE)
@log_all_exceptions
def _process_sobject_fields_sync(user_id, sync_id, resource):
    user = User.objects.filter(id=user_id).select_related("salesforce_account").first()
    if not hasattr(user, "salesforce_account"):
        return
    sf = user.salesforce_account
    attempts = 1
    while True:
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
    sf = user.salesforce_account
    attempts = 1
    while True:
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
    sf = user.salesforce_account
    attempts = 1
    while True:
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


@background(schedule=0)
def _process_update_opportunity(user_id, meeting_review_id, attempts=1):
    user = (
        User.objects.filter(id=user_id)
        .select_related("zoom_account")
        .select_related("salesforce_account")
        .first()
    )
    if user and user.has_zoom_integration and user.has_slack_integration:
        meeting = user.zoom_account.meetings.filter(meeting_review__id=meeting_review_id).first()
        meeting_review = meeting.meeting_review
        if meeting_review:
            formatted_data = meeting_review.as_sf_update
            sf = user.salesforce_account
            try:
                return meeting.opportunity.update_in_salesforce(formatted_data)
            except TokenExpired:
                if attempts >= 5:
                    return logger.exception(
                        f"Failed to sync STAGE data for user {user_id} after {attempts} tries"
                    )
                else:
                    sf.regenerate_token()
                    attempts += 1
                    return _process_update_opportunity(user_id, meeting_review_id, attempts)

            # push to sf
    return

