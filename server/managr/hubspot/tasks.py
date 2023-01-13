import logging
import re
import pytz
import time
import random
from django.conf import settings

from datetime import datetime
from django.utils import timezone
from background_task import background
from managr.api.decorators import log_all_exceptions, slack_api_exceptions
from managr.core.models import User
from managr.hubspot.models import HSObjectFieldsOperation, HSResourceSync
from managr.crm.models import ObjectField
from managr.salesforce.background import _send_recap
from managr.crm.routes import adapter_routes as adapter_routes
from managr.crm.serializers import BaseContactSerializer, ObjectFieldSerializer
from managr.hubspot.routes import routes as routes
from managr.hubspot import constants as hs_consts
from managr.crm.exceptions import TokenExpired, CannotRetreiveObjectType, UnhandledCRMError
from managr.slack import constants as slack_consts
from managr.slack.models import OrgCustomSlackFormInstance, OrgCustomSlackForm
from managr.salesforce.models import MeetingWorkflow
from managr.hubspot.adapter.models import HubspotContactAdapter
from managr.crm.utils import create_form_instance, process_text_field_format
from managr.slack.helpers import block_builders
from managr.slack.helpers import requests as slack_requests

logger = logging.getLogger("managr")


def replace_tags(description):
    description = description.replace("\n", "<br>")
    return description


def emit_hs_sync(user_id, sync_id, resource):
    user_id = str(user_id)
    sync_id = str(sync_id)
    return _process_resource_sync(user_id, sync_id, resource)


def emit_gen_next_hubspot_field_sync(user_id, ops_list, schedule_time=timezone.now()):
    schedule = datetime.strptime(schedule_time, "%Y-%m-%dT%H:%M%Z")
    return _process_gen_next_hubspot_field_sync(user_id, ops_list, schedule=schedule)


def emit_gen_next_hubspot_sync(user_id, ops_list, schedule_time=timezone.now()):
    schedule = datetime.strptime(schedule_time, "%Y-%m-%dT%H:%M%Z")
    return _process_gen_next_hubspot_sync(user_id, ops_list, schedule=schedule)


def emit_sync_hobject_fields(user_id, sync_id, resource, scheduled_for=timezone.now()):
    return _process_hobject_fields_sync(user_id, sync_id, resource, schedule=scheduled_for)


def emit_generate_hs_form_template(user_id, delete_forms=False, schedule=timezone.now()):
    return _generate_form_template(user_id, delete_forms, schedule=schedule)


def emit_add_call_to_hs(workflow_id, *args):
    return _process_add_call_to_hs(workflow_id, *args)


def emit_add_update_to_hs(form_id, *args):
    return _process_add_update_to_hs(form_id, *args)


def emit_update_hs_contacts(workflow_id, *args):
    return _process_update_hs_contacts(workflow_id, *args)


def emit_create_new_hs_contacts(workflow_id, *args):
    return _process_create_new_hs_contacts(workflow_id, *args)


def emit_add_products_to_hs(workflow_id, *args):
    return _process_add_products_to_hs(workflow_id, *args)


def emit_hs_update_resource_from_meeting(workflow_id, *args):
    return _process_update_resource_from_meeting(workflow_id, *args)


def emit_process_slack_hs_bulk_update(
    user, resource_ids, data, message_ts, channel_id, resource_type
):
    return _process_slack_bulk_update(
        user, resource_ids, data, message_ts, channel_id, resource_type
    )


def emit_process_slack_inline_hs_update(payload, context):
    _process_slack_inline_update(payload, context)


@background(schedule=0)
@log_all_exceptions
def _process_pipeline_hs_sync(sync_id):
    sync = HSResourceSync.objects.get(id=sync_id)
    sync.begin_tasks()
    return sync.id


@background(schedule=0)
@log_all_exceptions
def _process_gen_next_hubspot_field_sync(user_id, operations_list):
    user = User.objects.filter(id=user_id).first()
    if not user:
        return logger.exception(f"User not found sync operation not created {user_id}")
    sync = HSObjectFieldsOperation.objects.create(
        user=user, operations_list=operations_list, operation_type=hs_consts.HUBSPOT_FIELD_SYNC
    )
    return sync.begin_tasks()


@background(schedule=0)
@log_all_exceptions
def _process_gen_next_hubspot_sync(user_id, operations_list):
    user = User.objects.filter(id=user_id).first()
    if not user:
        return logger.exception(f"User not found sync operation not created {user_id}")
    return HSResourceSync.objects.create(
        user=user, operations_list=operations_list, operation_type=hs_consts.HUBSPOT_RESOURCE_SYNC,
    ).begin_tasks()


@background(schedule=0, queue=hs_consts.HUBSPOT_FIELD_SYNC_QUEUE)
@log_all_exceptions
def _process_hobject_fields_sync(user_id, sync_id, resource):
    user = User.objects.filter(id=user_id).select_related("hubspot_account").first()
    if not hasattr(user, "hubspot_account"):
        return
    attempts = 1
    while True:
        hs = user.hubspot_account
        try:
            fields = hs.adapter_class.list_fields(resource)
            attempts = 1
            break
        except TokenExpired:
            if attempts >= 5:
                return logger.exception(
                    f"Failed to sync {resource} data for user {hs.user.id}-{hs.user.email} after {attempts} tries"
                )
            else:
                sleep = 1 * 2 ** attempts + random.uniform(0, 1)
                time.sleep(sleep)
                hs.regenerate_token()
                attempts += 1
        except CannotRetreiveObjectType:
            hs.hobjects[resource] = False
    errors = []
    for field in fields:
        existing = ObjectField.objects.filter(
            api_name=field.api_name, user=user, crm_object=resource,
        ).first()
        if field.api_name == "dealstage":
            values = hs.get_deal_stages("deals")
            pipelines = {pipeline["id"]: pipeline for pipeline in values}
            field.options = [pipelines]
        if field.api_name == "pipeline":
            values = hs.get_deal_stages("deals")
            pipelines = [
                {"value": pipeline["id"], "label": pipeline["label"]} for pipeline in values
            ]
            field.options = pipelines
        if existing:
            serializer = ObjectFieldSerializer(data=field.as_dict, instance=existing)
        else:
            serializer = ObjectFieldSerializer(data=field.as_dict)
        try:
            serializer.is_valid(raise_exception=True)
            serializer.save()
        except Exception as e:
            errors.append(f"{field.api_name} - {e}")
            continue
    if len(errors):
        logger.error(f"Error syncing fields for {user.email}: {errors}")
    return


DEV_FORM_CONFIGS = {
    "Deal": {
        "0": "meeting_type",
        "1": "meeting_comments",
        "2": "dealname",
        "3": "dealstage",
        "4": "closedate",
        "5": "hubspot_owner_id",
    },
    "Contact": {
        "0": "meeting_type",
        "1": "meeting_comments",
        "2": "email",
        "3": "firstname",
        "4": "lastname",
        "5": "hubspot_owner_id",
    },
    "Company": {
        "0": "meeting_type",
        "1": "meeting_comments",
        "2": "name",
        "3": "domain",
        "4": "closedate",
        "5": "hubspot_owner_id",
    },
}


@background(schedule=0)
@log_all_exceptions
def _generate_form_template(user_id, delete_forms):
    user = User.objects.get(id=user_id)
    team = user.team
    # delete all existing forms
    if delete_forms:
        team.team_forms.all().delete()
    form_check = user.team.team_forms.all()
    for form in slack_consts.INITIAL_HUBSPOT_FORMS:
        resource, form_type = form.split(".")
        if len(form_check) > 0:
            f = form_check.filter(resource=resource, form_type=form_type).first()
            f.recreate_form()
        else:
            if settings.IN_DEV:
                f = OrgCustomSlackForm.objects.create(
                    form_type=form_type,
                    resource=resource,
                    organization=user.organization,
                    team=user.team,
                    custom_object=None,
                    config=DEV_FORM_CONFIGS[resource],
                )
                f.recreate_form()
            else:
                f = OrgCustomSlackForm.objects.create(
                    form_type=form_type,
                    resource=resource,
                    organization=user.organization,
                    team=user.team,
                )
                public_fields = ObjectField.objects.filter(
                    is_public=True,
                    id__in=slack_consts.DEFAULT_PUBLIC_FORM_FIELDS.get(resource, {}).get(
                        form_type, []
                    ),
                )
                note_subject = public_fields.filter(
                    id="6407b7a1-a877-44e2-979d-1effafec5034"
                ).first()
                note = public_fields.filter(id="0bb152b5-aac1-4ee0-9c25-51ae98d55af2").first()
                for i, field in enumerate(public_fields):
                    if i == 0 and note_subject is not None:
                        f.custom_fields.add(note_subject, through_defaults={"order": i})
                    elif i == 1 and note is not None:
                        f.custom_fields.add(note, through_defaults={"order": i})
                f.save()


@background(schedule=0, queue=hs_consts.HUBSPOT_RESOURCE_SYNC_QUEUE)
@log_all_exceptions
def _process_resource_sync(user_id, sync_id, resource, attempts=1):
    user = User.objects.filter(id=user_id).select_related("hubspot_account").first()
    if not hasattr(user, "hubspot_account"):
        return

    # if route doesnt exist catch all will catch the value error here
    route = routes[resource]
    model_class = route["model"]
    serializer_class = route["serializer"]

    while True:
        hs = user.hubspot_account
        try:
            res = hs.list_resource_data(resource)

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
                hs.regenerate_token()
                attempts += 1
        except Exception as e:
            return logger.warning(
                f"Failed to sync some data for resource {resource} for user {user_id} because of {e}"
            )
    errors = []
    for item in res:
        existing = model_class.objects.filter(integration_id=item.integration_id).first()
        if existing:
            serializer = serializer_class(data=item.as_dict, instance=existing)
        else:
            serializer = serializer_class(data=item.as_dict)
        # check if already exists and update
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            errors.append(
                (
                    f"Failed to save data for {resource} {item.name if hasattr(item, 'name') else item.email}",
                    f"{str(e)}",
                )
            )
            continue
        serializer.save()
    if len(errors):
        logger.exception(f"Errors for syncing {resource} for user {user.email}: {errors}")
    return


@background(
    schedule=0, queue=hs_consts.HUBSPOT_MEETING_REVIEW_WORKFLOW_QUEUE,
)
def _process_update_resource_from_meeting(workflow_id, *args):
    # get workflow
    workflow = MeetingWorkflow.objects.get(id=workflow_id)
    user = workflow.user
    # collect forms for resource meeting_review and if stages any stages related forms
    update_forms = workflow.forms.filter(template__form_type__in=[slack_consts.FORM_TYPE_UPDATE,])
    update_form_ids = []
    # aggregate the data
    data = dict()
    for form in update_forms:
        update_form_ids.append(str(form.id))
        data = {**data, **form.saved_data}

    attempts = 1
    while True:
        hs = user.hubspot_account
        try:
            res = workflow.resource.update(data)
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
                hs.regenerate_token()
                attempts += 1
        except Exception as e:
            if len(user.slack_integration.recap_receivers):
                _send_recap(update_form_ids, None, True)
            raise e
    value_update = workflow.resource.update_database_values(data)
    if user.has_slack_integration and len(user.slack_integration.recap_receivers):
        _send_recap(update_form_ids, None, True)
    return res


@background(
    schedule=0, queue=hs_consts.HUBSPOT_MEETING_REVIEW_WORKFLOW_QUEUE,
)
def _process_add_products_to_hs(workflow_id, non_meeting=False, *args):
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


CALL_ASSOCIATIONS = {"company": 8, "deal": 212, "contact": 10}
NOTE_ASSOCIATIONS = {"company": 190, "deal": 214, "contact": 202}
RESOURCE_ASSOCIATIONS = {"deal": {"contact": 4}}


@background(schedule=0, queue=hs_consts.HUBSPOT_MEETING_REVIEW_WORKFLOW_QUEUE)
def _process_add_call_to_hs(workflow_id, *args):
    workflow = MeetingWorkflow.objects.get(id=workflow_id)
    user = workflow.user
    if not user:
        return logger.exception(f"User not found unable to log call {str(user.id)}")
    if not hasattr(user, "hubspot_account"):
        return logger.exception("User does not have a hubspot account cannot push to hs")
    meeting_outcome = args[0][0] if len(args[0]) else "None"
    review_form = workflow.forms.filter(template__form_type=slack_consts.FORM_TYPE_UPDATE).first()
    subject = review_form.saved_data.get("meeting_type")
    description = review_form.saved_data.get("meeting_comments")
    if description is not None:
        description = replace_tags(description)
    start_time = workflow.meeting.start_time
    end_time = workflow.meeting.end_time
    formatted_start = int(start_time.timestamp() * 1e3)
    formatted_end = int(end_time.timestamp() * 1e3)
    data = dict(
        hs_timestamp=formatted_start,
        hubspot_owner_id=user.crm_account.crm_id,
        hs_meeting_title=subject,
        hs_internal_meeting_notes=description,
        hs_meeting_start_time=formatted_start,
        hs_meeting_end_time=formatted_end,
    )
    if meeting_outcome != "None":
        data["hs_meeting_outcome"] = meeting_outcome
    attempts = 1
    while True:
        hs = user.hubspot_account
        try:
            create_res = hs.adapter_class.create_meeting_in_hubspot(data)
            meeting_id = create_res["id"]
            associate_res = hs.adapter_class.associate_objects(
                "meetings",
                meeting_id,
                workflow.resource_type,
                workflow.resource.integration_id,
                CALL_ASSOCIATIONS[workflow.resource_type.lower()],
            )
            break
        except TokenExpired as e:
            if attempts >= 5:
                return logger.exception(
                    f"Failed to refresh user token for Salesforce operation add contact as contact role to opportunity"
                )
            else:
                sleep = 1 * 2 ** attempts + random.uniform(0, 1)
                time.sleep(sleep)
                hs.regenerate_token()
                attempts += 1
        except Exception as e:
            logger.exception(f"Creating meeting error: <{e}>")
    return


@background(schedule=0, queue=hs_consts.HUBSPOT_MEETING_REVIEW_WORKFLOW_QUEUE)
def _process_add_update_to_hs(form_id, *args):
    form = OrgCustomSlackFormInstance.objects.filter(id=form_id).first()
    resource = routes[form.resource_type]["model"].objects.get(id=form.resource_id)
    user = form.user
    if not user:
        return logger.exception(f"User not found unable to log call {str(user.id)}")
    if not hasattr(user, "hubspot_account"):
        return logger.exception("User does not have a hubspot account cannot push to hs")
    formatted_time = datetime.strftime(form.submission_date, "%Y-%m-%dT%H:%M:%S.%fz")
    subject = (
        "No subject"
        if form.saved_data.get("meeting_type") is None
        else form.saved_data.get("meeting_type")
    )
    description = form.saved_data.get("meeting_comments")
    description = replace_tags(description)
    data = dict(
        hs_timestamp=formatted_time,
        hubspot_owner_id=user.crm_account.crm_id,
        hs_note_body=f"{subject} - {description}",
    )
    attempts = 1
    while True:
        hs = user.hubspot_account
        try:
            create_res = hs.adapter_class.create_note_in_hubspot(data)
            note_id = create_res["id"]
            associate_res = hs.adapter_class.associate_objects(
                "notes",
                note_id,
                form.resource_type,
                form.resource_object.integration_id,
                NOTE_ASSOCIATIONS[form.resource_type.lower()],
            )
            break
        except TokenExpired:
            if attempts >= 5:
                return logger.exception(
                    f"Failed to refresh user token for Salesforce operation add contact as contact role to opportunity"
                )
            else:
                sleep = 1 * 2 ** attempts + random.uniform(0, 1)
                time.sleep(sleep)
                hs.regenerate_token()
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


@background(schedule=0, queue=hs_consts.HUBSPOT_MEETING_REVIEW_WORKFLOW_QUEUE)
def _process_create_new_hs_contacts(workflow_id, *args):
    workflow = MeetingWorkflow.objects.get(id=workflow_id)
    user = workflow.user
    if not user:
        return logger.exception(f"User not found unable to log call {str(user.id)}")
    if not hasattr(user, "hubspot_account"):
        return logger.exception("User does not have a hubspot account cannot push to hs")
    meeting = workflow.meeting
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
        while True:
            hs = user.hubspot_account
            object_fields = user.object_fields.filter(crm_object="Contact").values_list(
                "api_name", flat=True
            )
            logger.info(f"Data from form {data}")
            try:
                res = HubspotContactAdapter.create(
                    data, hs.access_token, object_fields, str(user.id),
                )
                form.is_submitted = True
                form.update_source = "meeting"
                form.submission_date = timezone.now()
                form.save()
                break
            except TokenExpired as e:
                if attempts >= 5:
                    return logger.exception(
                        f"Failed to refresh user token for Salesforce operation add contact to sf failed {str(workflow.id)} <{e}>"
                    )

                else:
                    sleep = 1 * 2 ** attempts + random.uniform(0, 1)
                    time.sleep(sleep)
                    hs.regenerate_token()
                    attempts += 1
            except Exception as e:
                logger.info(f"Create exception <{e}>")
                if attempts >= 5:
                    logger.exception(
                        f"Failed to create contact for {str(user.id)} for workflow {str(workflow.id)} with email {user.email} after {attempts} tries, {e}"
                    )
                    raise e
                else:
                    sleep = 1 * 2 ** attempts + random.uniform(0, 1)
                    time.sleep(sleep)
                    attempts += 1
        if workflow.resource_type == slack_consts.FORM_RESOURCE_DEAL and res and res.integration_id:
            while True:
                hs = user.hubspot_account
                hs_adapter = hs.adapter_class
                logger.info(f"Adding Contact Role")
                try:

                    hs_adapter.associate_objects(
                        "contacts",
                        res.integration_id,
                        workflow.resource_type,
                        workflow.resource.integration_id,
                        RESOURCE_ASSOCIATIONS["deal"]["contact"],
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
                        hs.regenerate_token()
                        attempts += 1
        try:
            serializer = BaseContactSerializer(data=res.as_dict)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        except Exception as e:
            logger.exception(f"Failed to create contact in DB because of {e}")
            return
    return


def swap_public_fields(state):
    if "meeting_comment" in state.keys():
        state["meeting_comments"] = state["meeting_comment"]
        state.pop("meeting_comment")
    if "meeting_title" in state.keys():
        state["meeting_type"] = state["meeting_title"]
        state.pop("meeting_title")
    return state


@background(schedule=0, queue=hs_consts.HUBSPOT_MEETING_REVIEW_WORKFLOW_QUEUE)
def _process_update_hs_contacts(workflow_id, *args):
    workflow = MeetingWorkflow.objects.get(id=workflow_id)
    user = workflow.user
    if not user:
        return logger.exception(f"User not found unable to log call {str(user.id)}")
    if not hasattr(user, "hubspot_account"):
        return logger.exception("User does not have a hubspot account cannot push to hs")

    attempts = 1
    contact_forms = workflow.forms.filter(id__in=args[0])
    for form in contact_forms:
        # if the resource is an account we set it to that account
        # if it is an opp we create a contact role as well
        data = form.saved_data
        data = swap_public_fields(data)
        if data.get("meeting_comments") is not None and data.get("meeting_type") is not None:
            emit_add_update_to_hs(str(form.id))
        if data:
            while True:
                crm = user.crm_account
                try:
                    form.resource_object.update(data,)
                    attempts = 1
                    form.is_submitted = True
                    form.update_source = "meeting"
                    form.submission_date = timezone.now()
                    form.save()
                    if workflow.resource_type == slack_consts.FORM_RESOURCE_DEAL:
                        crm.adapter_class.associate_objects(
                            "contacts",
                            form.resource_object.integration_id,
                            workflow.resource_type,
                            workflow.resource.integration_id,
                            RESOURCE_ASSOCIATIONS["deal"]["contact"],
                        )
                    break
                except TokenExpired as e:
                    if attempts >= 5:
                        logger.exception(
                            f"Failed to refresh user token for Hubspot operation add contact to hs failed {str(workflow.id)} <{e}>"
                        )

                    else:
                        sleep = 1 * 2 ** attempts + random.uniform(0, 1)
                        time.sleep(sleep)
                        crm.regenerate_token()
                        attempts += 1
                except Exception as e:
                    logger.exception(f"Unhandled exception for updating contact: {e}")

    return


@background(schedule=0)
def _process_create_new_hs_resource(form_ids, *args):
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
        hs = user.hubspot_account
        try:

            object_fields = user.object_fields.filter(crm_object=resource).values_list(
                "api_name", flat=True
            )
            adpater_class = adapter_routes[user.crm][resource]
            res = adpater_class.create(data, hs.access_token, object_fields, str(user.id))
            serializer = routes.get(resource)["serializer"](data=res.as_dict)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return serializer.instance
        except TokenExpired as e:
            if attempts >= 5:
                return logger.exception(
                    f"Failed to create new resource for user {str(user.id)} after {attempts} tries because their token is expired"
                )
            else:
                hs.regenerate_token()
                attempts += 1
        except UnhandledCRMError as e:
            logger.exception(f"Create failed for {e}")
            raise UnhandledCRMError(str(e))
        except Exception as e:
            logger.exception(f"Create failed for {e}")
            raise Exception(str(e))

    return


@background(schedule=0)
@slack_api_exceptions(rethrow=0)
def _process_slack_bulk_update(user_id, resource_ids, data, message_ts, channel_id, resource_type):
    user = User.objects.get(id=user_id)
    instance_data = {
        "resource_type": resource_type,
        "form_type": "UPDATE",
        "user": user,
        "stage_name": None,
    }

    bulk_form_ids = []
    for id in resource_ids:
        instance_data["resource_id"] = id
        form_id = create_form_instance(**instance_data)
        bulk_form_ids.extend(form_id)
    forms = OrgCustomSlackFormInstance.objects.filter(id__in=bulk_form_ids)
    success_opps = 0
    error = False
    error_message = None
    for form in forms:
        form.save_form(data)
        all_form_data = form.saved_data
        formatted_saved_data = process_text_field_format(
            str(user.id), form.template.resource, all_form_data
        )
        attempts = 1

        while True:
            hs = user.hubspot_account
            try:
                resource = form.resource_object.update(all_form_data)
                form.is_submitted = True
                form.update_source = "slack-bulk"
                form.submission_date = timezone.now()
                form.save()
                value_update = form.resource_object.update_database_values(all_form_data)
                success_opps += 1
                break
            except UnhandledCRMError as e:
                logger.info(f"UPDATE UNHANDLED SF ERROR {e}")
                error = True
                error_message = str(e)
                break

            except TokenExpired as e:
                if attempts >= 5:
                    logger.info(f"UPDATE REFRESHING TOKEN ERROR {e}")
                    error = True
                    error_message = str(e)
                    break
                else:
                    if form.resource_object.owner == user:
                        hs.regenerate_token()
                    else:
                        form.resource_object.owner.hubspot_account.regenerate_token()
                    attempts += 1

            except ConnectionResetError as e:
                if attempts >= 5:
                    logger.info(f"UPDATE CONNECTION RESET ERROR {e}")
                    error = True
                    error_message = str(e)
                    break
                else:
                    time.sleep(2)
                    attempts += 1

            except Exception as e:
                logger.info(f"UPDATE ERROR {e}")
                error = True
                error_message = str(e)
                break
    if error:
        logger.info(
            f"Successfully updated {success_opps}/{len(forms)} {resource_type}s for user {user.email}"
        )
        block_set = [
            block_builders.simple_section(
                f":no_entry: Ugh-Ohhhh.. We've hit an error: {error_message}"
            )
        ]
    else:
        logger.info(
            f"Successfully updated {success_opps}/{len(forms)} {resource_type}s for user {user.email}"
        )
        block_set = [
            block_builders.simple_section(
                f":white_check_mark: Successfully bulk updated {success_opps}/{len(forms)} {resource_type}s",
                "mrkdwn",
            )
        ]
    try:
        res = slack_requests.update_channel_message(
            channel_id,
            message_ts,
            user.organization.slack_integration.access_token,
            block_set=block_set,
        )
    except Exception as e:
        logger.exception(f"Failed To Bulk Update Salesforce Data {e}")
    return


@background(schedule=0)
@slack_api_exceptions(rethrow=0)
def _process_slack_inline_update(payload, context):
    from managr.alerts.models import AlertInstance

    value = context.get("api_name")
    state = payload["state"]["values"]
    to_delete_keys = [id for id in state.keys() if value not in id]
    for id in to_delete_keys:
        del state[id]
    for key in state:
        block_id_values = key.split(".")
        form = OrgCustomSlackFormInstance.objects.get(alert_instance_id=block_id_values[2])
        saved_data_ref = None
        if len(form.saved_data):
            saved_data_ref = form.saved_data
        form.save_form({value: state[key]})
        if saved_data_ref:
            saved_data_ref.update(form.saved_data)
            form.save_form(saved_data_ref, False)
    user_slack_id = payload.get("user", {}).get("id", None)
    user = User.objects.filter(slack_integration__slack_id=user_slack_id).first()
    if not user:
        return
    access_token = user.organization.slack_integration.access_token
    invocation = context.get("invocation")
    config_id = context.get("config_id")
    instances = AlertInstance.objects.filter(user=user, invocation=invocation, config__id=config_id)
    blocks = payload.get("message").get("blocks")[:2]
    blocks.append({"type": "divider"})
    success_resources = 0
    failed_resources = 0
    error = False
    error_message = None
    for instance in instances:
        form = instance.form_instance.all().first()
        data = form.saved_data
        if len(data):
            attempts = 1
            while True:
                hs = user.hubspot_account
                try:
                    resource = form.resource_object.update(data)
                    form.is_submitted = True
                    form.update_source = "slack-inline"
                    form.submission_date = timezone.now()
                    form.save()
                    value_update = form.resource_object.update_database_values(data)
                    success_resources += 1
                    break
                except UnhandledCRMError as e:
                    logger.info(f"UPDATE UNHANDLED SF ERROR {e}")
                    error = True
                    error_message = str(e)
                    failed_resources += 1
                    break

                except TokenExpired as e:
                    if attempts >= 5:
                        logger.info(f"UPDATE REFRESHING TOKEN ERROR {e}")
                        error = True
                        error_message = str(e)
                        failed_resources += 1
                        break
                    else:
                        if form.resource_object.owner == user:
                            hs.regenerate_token()
                        else:
                            form.resource_object.owner.hubspot_account.regenerate_token()
                        attempts += 1

                except ConnectionResetError as e:
                    if attempts >= 5:
                        logger.info(f"UPDATE CONNECTION RESET ERROR {e}")
                        error = True
                        error_message = str(e)
                        failed_resources += 1
                        break
                    else:
                        time.sleep(2)
                        attempts += 1

                except Exception as e:
                    logger.info(f"UPDATE ERROR {e}")
                    error = True
                    error_message = str(e)
                    failed_resources += 1
                    break
    if error:
        logger.info(
            f"Successfully updated {success_resources}/{failed_resources + success_resources} {instances.first().template.resource_type}s for user {user.email}"
        )
        block_set = [
            block_builders.simple_section(
                f":no_entry: Ugh-Ohhhh.. We've hit an error: {error_message}"
            )
        ]
    else:
        logger.info(
            f"Successfully updated {success_resources}/{failed_resources + success_resources} {instances.first().template.resource_type}s for user {user.email}"
        )
        block_set = [
            block_builders.simple_section(
                f":white_check_mark: Successfully bulk updated {success_resources}/{failed_resources + success_resources} {instances.first().template.resource_type}s",
                "mrkdwn",
            )
        ]

    blocks.extend(block_set)
    try:
        res = slack_requests.generic_request(
            payload["response_url"],
            {"replace_original": True, "blocks": blocks},
            access_token=access_token,
        )
    except Exception as e:
        logger.exception(f"Failed to update inline alert message {e}")
    return
