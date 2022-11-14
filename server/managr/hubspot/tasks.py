import logging
import re
import pytz
import time
import random
from datetime import datetime
from django.utils import timezone
from background_task import background

from managr.api.decorators import log_all_exceptions

from managr.core.models import User

from managr.hubspot.models import HSObjectFieldsOperation, HObjectField, HSResourceSync
from managr.hubspot.serializers import HObjectFieldSerializer
from managr.crm.models import ObjectField
from managr.crm.routes import adapter_routes as adapter_routes
from managr.crm.serializers import ObjectFieldSerializer
from managr.hubspot.routes import routes as routes
from managr.hubspot import constants as hs_consts
from managr.crm.exceptions import TokenExpired, CannotRetreiveObjectType, UnhandledCRMError
from managr.slack import constants as slack_consts
from managr.slack.models import OrgCustomSlackFormInstance, OrgCustomSlackForm
from managr.salesforce.models import MeetingWorkflow
from managr.hubspot.adapter.models import HubspotContactAdapter
from managr.crm.models import BaseAccount, BaseContact, BaseOpportunity

logger = logging.getLogger("managr")


def replace_tags(description):
    description = re.split("</.*?>", description)
    while "" in description:
        description.remove("")
    description = "\n".join(description)
    description = re.split("<br>", description)
    description = "\r".join(description)
    description = re.sub("<.*?>", "", description)
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
    for field in fields:
        existing = ObjectField.objects.filter(
            api_name=field.api_name, user=user, crm_object=resource,
        ).first()
        if field.api_name == "dealstage":
            values = hs.get_deal_stages("deals")
            sales_pipeline = [
                pipeline["stages"] for pipeline in values if pipeline["label"] == "Sales Pipeline"
            ]
            if len(sales_pipeline):
                field.options = sales_pipeline[0]
        if existing:
            serializer = ObjectFieldSerializer(data=field.as_dict, instance=existing)
        else:
            serializer = ObjectFieldSerializer(data=field.as_dict)
        serializer.is_valid(raise_exception=True)
        serializer.save()

    return


@background(schedule=0)
@log_all_exceptions
def _generate_form_template(user_id, delete_forms):
    user = User.objects.get(id=user_id)
    org = user.organization
    # delete all existing forms
    if delete_forms:
        org.custom_slack_forms.all().delete()
    form_check = user.team.team_forms.all()
    for form in slack_consts.INITIAL_HUBSPOT_FORMS:
        resource, form_type = form.split(".")
        if len(form_check) > 0:
            f = form_check.filter(resource=resource, form_type=form_type).first()
            f.recreate_form()
        else:
            f = OrgCustomSlackForm.objects.create(
                form_type=form_type, resource=resource, organization=org, team=user.team
            )
            public_fields = ObjectField.objects.filter(
                is_public=True,
                id__in=slack_consts.DEFAULT_PUBLIC_FORM_FIELDS.get(resource, {}).get(form_type, []),
            )
            note_subject = public_fields.filter(id="6407b7a1-a877-44e2-979d-1effafec5034").first()
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
                hs.regenerate_token()
                attempts += 1
        except Exception as e:
            return logger.warning(
                f"Failed to sync some data for resource {resource} for user {user_id} because of {e}"
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
        except Exception as e:
            logger.exception(
                f"Failed to save data for {resource} {item.name if hasattr(item, 'name') else 'N/A'} with hubspot id {item.integration_id} due to the following error {e}"
            )
            break
        serializer.save()

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
            # if len(user.slack_integration.recap_receivers):
            #     _send_recap(update_form_ids, None, True)
            raise e
    value_update = workflow.resource.update_database_values(data)
    # if user.has_slack_integration and len(user.slack_integration.recap_receivers):
    #     _send_recap(update_form_ids, None, True)
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


@background(schedule=0, queue=hs_consts.HUBSPOT_MEETING_REVIEW_WORKFLOW_QUEUE)
def _process_add_call_to_hs(workflow_id, *args):
    workflow = MeetingWorkflow.objects.get(id=workflow_id)
    user = workflow.user
    if not user:
        return logger.exception(f"User not found unable to log call {str(user.id)}")
    if not hasattr(user, "hubspot_account"):
        return logger.exception("User does not have a hubspot account cannot push to hs")
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
                hs.regenerate_token()
                attempts += 1
        except Exception as e:
            logger.exception(f"Creating meeting error: <{e}>")
    return


@background(schedule=0, queue=hs_consts.HUBSPOT_MEETING_REVIEW_WORKFLOW_QUEUE)
def _process_add_update_to_hs(form_id, *args):
    form = OrgCustomSlackFormInstance.objects.filter(id=form_id).first()
    resource = None
    if form.resource_type == "Deal":
        resource = BaseOpportunity.objects.get(id=form.resource_id)
    elif form.resource_type == "Company":
        resource = BaseAccount.objects.get(id=form.resource_id)
    else:
        resource = BaseContact.objects.get(id=form.resource_id)
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
    description = form.saved_data.get("meeting_comments")
    description = replace_tags(description)
    data = dict(
        Subject=f"{subject}",
        Description=description,
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
    if not hasattr(user, "salesforce_account"):
        return logger.exception("User does not have a salesforce account cannot push to sf")
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
        try:
            serializer = ContactSerializer(data=res.as_dict)
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
    if not hasattr(user, "salesforce_account"):
        return logger.exception("User does not have a salesforce account cannot push to sf")

    attempts = 1
    contact_forms = workflow.forms.filter(id__in=args[0])
    for form in contact_forms:
        # if the resource is an account we set it to that account
        # if it is an opp we create a contact role as well
        data = form.saved_data
        data = swap_public_fields(data)
        if data.get("meeting_comments") is not None and data.get("meeting_type") is not None:
            emit_add_update_to_hs(str(form.id))
        if workflow.resource_type == slack_consts.FORM_RESOURCE_ACCOUNT:
            data["AccountId"] = workflow.resource.integration_id
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

        # # if no data was saved the resource was not updated but we still add the contact role
        # if workflow.resource_type == slack_consts.FORM_RESOURCE_OPPORTUNITY:
        #     attempts = 1
        #     while True:
        #         sf = user.salesforce_account
        #         try:
        #             # check to see if it already has a contact role by checking linked_contacts
        #             is_linked = workflow.resource.contacts.filter(
        #                 integration_id=form.resource_object.integration_id
        #             ).first()
        #             if not is_linked:
        #                 workflow.resource.add_contact_role(
        #                     sf.access_token, sf.instance_url, form.resource_object.integration_id
        #                 )
        #                 attempts = 1
        #             break

        #         except TokenExpired as e:
        #             if attempts >= 5:
        #                 return logger.exception(
        #                     f"Failed to refresh user token for Salesforce operation add contact to sf failed {str(meeting.id)}"
        #                 )

        #             else:
        #                 sleep = 1 * 2 ** attempts + random.uniform(0, 1)
        #                 time.sleep(sleep)
        #                 sf.regenerate_token()
        #                 attempts += 1

        #         except UnableToUnlockRow as e:
        #             if attempts >= 5:
        #                 logger.exception(
        #                     f"Failed to add contact role from meeting for user {str(user.id)} for workflow {str(workflow.id)} with email {user.email} after {attempts} tries, {e}"
        #                 )
        #                 raise e
        #             else:
        #                 sleep = 1 * 2 ** attempts + random.uniform(0, 1)
        #                 time.sleep(sleep)
        #                 attempts += 1
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
            return logger.exception(f"Create failed for {e}")
        except Exception as e:
            return logger.exception(f"Create failed for {e}")

    return
