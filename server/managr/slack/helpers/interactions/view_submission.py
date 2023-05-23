import json
import logging
import uuid
import time
from django.utils import timezone
from managr.api.decorators import log_all_exceptions
from managr.crm.exceptions import (
    FieldValidationError,
    RequiredFieldError,
    TokenExpired,
    UnhandledCRMError,
    SFNotFoundError,
)
from managr.alerts.models import AlertInstance, AlertConfig
from managr.organization.models import Contact, OpportunityLineItem, PricebookEntry
from managr.crm.routes import adapter_routes as crm_routes
from managr.core.background import (
    emit_create_calendar_event,
    emit_process_calendar_meetings,
    emit_process_submit_chat_prompt,
    emit_process_send_email_draft,
    emit_process_send_next_steps,
    emit_process_send_summary_to_dm,
)
from managr.outreach.tasks import emit_add_sequence_state
from managr.opportunity.models import Opportunity, Lead
from managr.salesforce.models import MeetingWorkflow
from managr.salesforce import constants as sf_consts
from managr.slack import constants as slack_const
from managr.slack.models import OrgCustomSlackFormInstance
from managr.slack.helpers import block_builders
from managr.slack.helpers import requests as slack_requests
from managr.slack.helpers.utils import (
    action_with_params,
    NO_OP,
    processor,
    block_finder,
    check_contact_last_name,
    send_loading_screen,
)
from managr.crm.models import BaseOpportunity
from managr.hubspot.routes import routes as hs_routes
from managr.salesforce.routes import routes as model_routes
from managr.salesforce.background import (
    _process_create_new_resource,
    _process_create_task,
    _process_create_event,
    emit_meeting_workflow_tracker,
    emit_add_update_to_sf,
    _send_recap,
    _send_instant_alert,
    _send_convert_recap,
    emit_process_slack_bulk_update,
    emit_process_convert_lead,
)

from managr.slack.helpers.block_sets import get_block_set
from managr.slack.background import emit_process_submit_resource_data, emit_process_chat_action
from managr.salesloft.models import People
from managr.salesloft.background import emit_add_cadence_membership
from managr.zoom.background import emit_process_schedule_zoom_meeting
from managr.slack.tasks import emit_update_slack_message
from managr.slack.helpers.exceptions import (
    UnHandeledBlocksException,
    InvalidBlocksFormatException,
    InvalidBlocksException,
    InvalidAccessToken,
)
from managr.api.decorators import slack_api_exceptions
from managr.salesforce.adapter.models import PricebookEntryAdapter
from managr.hubspot.tasks import (
    _process_create_new_hs_resource,
    emit_add_update_to_hs,
    emit_process_slack_hs_bulk_update,
)
from managr.core.models import User
from managr.crm.utils import CRM_SWITCHER

logger = logging.getLogger("managr")


def swap_public_fields(state):
    if "meeting_comment" in state.keys():
        state["meeting_comments"] = state["meeting_comment"]
        state.pop("meeting_comment")
    if "meeting_title" in state.keys():
        state["meeting_type"] = state["meeting_title"]
        state.pop("meeting_title")
    return state


def background_create_resource(crm):
    if crm == "SALESFORCE":
        return _process_create_new_resource
    else:
        return _process_create_new_hs_resource


def BULK_UPDATE_FUNCTION(crm):
    if crm == "SALESFORCE":
        return emit_process_slack_bulk_update
    else:
        return emit_process_slack_hs_bulk_update


def ADD_UPDATE_TO_CRM_FUNCTION(crm):
    if crm == "SALESFORCE":
        return emit_add_update_to_sf
    else:
        return emit_add_update_to_hs


@log_all_exceptions
@processor(required_context=["w", "form_type"])
def process_stage_next_page(payload, context):
    workflow = MeetingWorkflow.objects.get(id=context.get("w"))
    view = payload["view"]
    # if there are additional stage gating forms aggregate them and push them in 1 view
    # save current data to its form we will close all views at the end

    state = swap_public_fields(view["state"]["values"])
    managr_task_values = [
        value.get("selected_option") for value in state.get("managr_task_type", {}).values()
    ]
    task_selection = managr_task_values[0] if len(managr_task_values) else None
    task_type = task_selection.get("value") if task_selection is not None else "None"
    private_metadata = json.loads(view["private_metadata"])
    private_metadata["task_type"] = task_type
    review_form = workflow.forms.filter(template__form_type=context.get("form_type")).first()
    review_form.save_form(state)
    forms = workflow.forms.filter(template__form_type=slack_const.FORM_TYPE_STAGE_GATING).all()
    if len(forms):
        next_blocks = []
        for form in forms:
            next_blocks.extend(form.generate_form(form.saved_data))
        private_metadata.update({**context})
        if context.get("form_type") == "CREATE":
            callback_id = (
                slack_const.ZOOM_MEETING__PROCESS_MEETING_SENTIMENT
                if workflow
                else slack_const.COMMAND_FORMS__SUBMIT_FORM
            )
        elif context.get("type") == "alert":
            callback_id = slack_const.PROCESS_SUBMIT_ALERT_RESOURCE_DATA
        else:
            callback_id = slack_const.ZOOM_MEETING__PROCESS_MEETING_SENTIMENT
        return {
            "response_action": "push",
            "view": {
                "type": "modal",
                "title": {"type": "plain_text", "text": "Stage Related Fields"},
                "submit": {"type": "plain_text", "text": "Submit"},
                "blocks": next_blocks,
                "private_metadata": json.dumps(private_metadata),
                "callback_id": callback_id,
            },
        }
    return  # closes all views by default


@log_all_exceptions
@slack_api_exceptions(rethrow=True)
@processor(
    required_context=["w",]
)
def process_zoom_meeting_data(payload, context):
    # get context
    workflow = MeetingWorkflow.objects.get(id=context.get("w"))
    private_metadata = json.loads(payload["view"]["private_metadata"])
    ts = context.get("ts", None)
    user = workflow.user
    slack_access_token = user.organization.slack_integration.access_token
    view = payload["view"]
    url = slack_const.SLACK_API_ROOT + slack_const.VIEWS_UPDATE
    loading_view_data = {
        "view_id": view["id"],
        "view": {
            "type": "modal",
            "title": {"type": "plain_text", "text": "Loading"},
            "blocks": get_block_set(
                "loading",
                {
                    "message": ":exclamation: Please wait a few seconds :zany_face:, then click '*try again*'",
                    "fill": True,
                },
            ),
            "private_metadata": view["private_metadata"],
        },
    }
    try:
        loading_res = slack_requests.generic_request(
            url, loading_view_data, access_token=slack_access_token
        )
    except Exception as e:
        return logger.exception(
            f"Failed To Show Loading Screen for user  {str(user.id)} email {user.email} {e}"
        )

    # get state - state contains the values based on the block_id
    state = swap_public_fields(view["state"]["values"])
    task_type = private_metadata.get("task_type", None)
    if not task_type:
        task_name = "managr_task_type"
        task_selection = [
            value.get("selected_option") for value in state.get(task_name, {}).values()
        ]
        task_type = (
            task_selection[0].get("value") if (len(task_selection) and task_selection[0]) else None
        )
    # if we had a next page the form data for the review was already saved
    forms = workflow.forms.filter(template__form_type=slack_const.FORM_TYPE_STAGE_GATING)
    current_form_ids = []
    if len(forms):
        for form in forms:
            current_form_ids.append(str(form.id))
            form.save_form(state)
    # otherwise we save the meeting review form
    else:
        form = workflow.forms.filter(
            template__form_type__in=[slack_const.FORM_TYPE_UPDATE, slack_const.FORM_TYPE_CREATE]
        ).first()
        current_form_ids.append(str(form.id))
        form.save_form(state)
    # contact_forms = workflow.forms.filter(template__resource=slack_const.FORM_RESOURCE_CONTACT)
    create_form_check = workflow.forms.filter(
        template__form_type=slack_const.FORM_TYPE_CREATE
    ).first()
    if len(workflow.failed_task_description):
        workflow.build_retry_list()
    else:
        main_operation = (
            f"{sf_consts.MEETING_REVIEW__CREATE_RESOURCE}.{str(workflow.id)}"
            if create_form_check
            else f"{sf_consts.MEETING_REVIEW__UPDATE_RESOURCE}.{str(workflow.id)}"
        )
        ops = [
            main_operation,
        ]
        if workflow.resource_type not in user.crm_account.custom_objects:
            ops.append(f"{sf_consts.MEETING_REVIEW__SAVE_CALL_LOG}.{str(workflow.id)},{task_type}")
        if len(workflow.operations_list):
            workflow.operations_list = [*workflow.operations_list, *ops]
        else:
            workflow.operations_list = ops
        workflow.operations_list = ops
    if len(user.slack_integration.realtime_alert_configs):
        _send_instant_alert(current_form_ids)
    emit_process_calendar_meetings(
        str(user.id),
        f"calendar-meetings-{user.email}-{str(uuid.uuid4())}",
        workflow.slack_interaction,
        date=str(workflow.datetime_created.date()),
    )
    workflow.save()
    workflow.begin_tasks()
    emit_meeting_workflow_tracker(str(workflow.id))
    if ts is not None:
        blocks = [block_builders.simple_section(f":white_check_mark: Meeting logged")]
        try:
            res = slack_requests.send_channel_message(
                user.slack_integration.channel, block_set=blocks, access_token=slack_access_token
            )
        except Exception as e:
            return logger.exception(
                f"Failed To Show Loading Screen for user  {str(user.id)} email {user.email} {e}"
            )
    return {"response_action": "clear"}


@log_all_exceptions
@processor(required_context=["f"])
def process_next_page_slack_commands_form(payload, context):
    # get context
    user = User.objects.get(id=context.get("u"))
    current_form_ids = context.get("f").split(",")
    view = payload["view"]
    state = swap_public_fields(view["state"]["values"])
    alert_check = context.get("alert_id", None)
    current_forms = user.custom_slack_form_instances.filter(id__in=current_form_ids)
    # save the main form
    main_form = current_forms.filter(template__form_type__in=["UPDATE", "CREATE"]).first()
    main_form.save_form(state)
    stage_forms = current_forms.exclude(template__form_type__in=["UPDATE", "CREATE"])
    slack_access_token = user.organization.slack_integration.access_token
    # currently only for update
    blocks = []
    for form in stage_forms:
        blocks.extend(form.generate_form(form.saved_data))
    if alert_check is not None:
        callback_id = slack_const.PROCESS_SUBMIT_ALERT_RESOURCE_DATA
    else:
        callback_id = slack_const.COMMAND_FORMS__SUBMIT_FORM
    if len(blocks):
        return {
            "response_action": "push",
            "view": {
                "type": "modal",
                "title": {"type": "plain_text", "text": "Stage Related Fields"},
                "submit": {"type": "plain_text", "text": "Submit"},
                "blocks": blocks,
                "private_metadata": view["private_metadata"],
                "callback_id": callback_id,
            },
        }
    return


@log_all_exceptions
@processor(required_context=["f"])
def process_alert_inline_stage_submitted(payload, context):
    state = payload["view"]["state"]["values"]
    form = OrgCustomSlackFormInstance.objects.get(id=context.get("f"))
    stage_form = OrgCustomSlackFormInstance.objects.get(id=context.get("stage_form_id"))
    stage_form.save_form(state)
    if len(form.saved_data):
        form.saved_data.update(stage_form.saved_data)
    else:
        form.saved_data = stage_form.saved_data
    form.is_submitted = True
    form.submission_date = timezone.now()
    form.save()
    return {"response_action": "clear"}


@log_all_exceptions
@processor(required_context=["f"])
def process_add_products_form(payload, context):
    # get context
    user = User.objects.get(slack_integration__slack_id=payload["user"]["id"])
    current_form_ids = context.get("f").split(",")
    view = payload["view"]
    state = view["state"]["values"]
    type = context.get("type", None)
    private_metadata = json.loads(view["private_metadata"])
    if type == "meeting":
        workflow = MeetingWorkflow.objects.get(id=context.get("w"))
        callback_id = slack_const.ZOOM_MEETING__PROCESS_MEETING_SENTIMENT
        product_form = workflow.forms.filter(template__resource="OpportunityLineItem").first()
    else:
        product_form = user.custom_slack_form_instances.get(id=context.get("product_form"))
        callback_id = slack_const.COMMAND_FORMS__SUBMIT_FORM
        private_metadata.update({"product_form_id": str(product_form.id)})
    current_forms = user.custom_slack_form_instances.filter(id__in=current_form_ids)
    # save the main form
    main_form = (
        current_forms.filter(template__form_type__in=["UPDATE", "CREATE"])
        .exclude(template__resource="OpportunityLineItem")
        .first()
    )
    main_form.save_form(state)

    # currently only for update
    blocks = []
    blocks.extend(product_form.generate_form())
    if len(blocks):

        return {
            "response_action": "push",
            "view": {
                "type": "modal",
                "title": {"type": "plain_text", "text": "Add Products Form"},
                "submit": {"type": "plain_text", "text": "Submit"},
                "blocks": blocks,
                "private_metadata": json.dumps(private_metadata),
                "callback_id": callback_id,
            },
        }
    return


@log_all_exceptions
@slack_api_exceptions(rethrow=True)
@processor(required_context=["f"])
def process_submit_resource_data(payload, context):
    user = User.objects.get(id=context.get("u"))
    slack_access_token = user.organization.slack_integration.access_token
    try:
        loading_data = {
            "trigger_id": payload["trigger_id"],
            "view_id": payload["view"]["id"],
            "view": {
                "type": "modal",
                "title": {"type": "plain_text", "text": "Loading"},
                "blocks": get_block_set(
                    "loading", {"message": ":rocket: Sending your data", "fill": True,},
                ),
            },
        }
        slack_requests.generic_request(
            slack_const.SLACK_API_ROOT + slack_const.VIEWS_UPDATE,
            loading_data,
            access_token=slack_access_token,
        )
    except Exception as e:
        logger.exception(f"Failed to send updating message to {user.email} due to {e}")
    emit_process_submit_resource_data(payload, context)
    return {"response_action": "clear"}


@log_all_exceptions
@slack_api_exceptions(rethrow=True)
@processor(required_context=["u"])
def process_submit_custom_object(payload, context):
    user = User.objects.get(id=context.get("u"))
    form = OrgCustomSlackFormInstance.objects.get(id=context.get("f"))
    state = payload["view"]["state"]["values"]
    form.save_form(state)
    data = form.saved_data
    attempts = 1
    has_error = False
    while True:
        crm = user.crm_account
        try:
            res = crm.create_custom_object(
                data,
                crm.access_token,
                crm.instance_url,
                crm.salesforce_id,
                form.template.custom_object,
            )
            form.is_submitted = True
            form.update_source = "meeting" if context.get("w", None) else "command"
            form.submission_date = timezone.now()
            form.save()
            break
        except FieldValidationError as e:
            has_error = True
            blocks = get_block_set(
                "error_modal",
                {
                    "message": f":no_entry: Uh-Ohhh it looks like we found an error, this error is based on Validations set up by your org\n *Error* : _{e}_"
                },
            )
            break

        except RequiredFieldError as e:
            has_error = True
            blocks = get_block_set(
                "error_modal",
                {
                    "message": f":no_entry: Uh-Ohhh it looks like we found an error, this error is based on Required fields from Salesforce\n *Error* : _{e}_"
                },
            )
            break
        except UnhandledCRMError as e:
            has_error = True
            blocks = get_block_set(
                "error_modal",
                {
                    "message": f":no_entry: Uh-Ohhh it looks like we found an error, this error is new to us please see below\n *Error* : _{e}_"
                },
            )
            break

        except SFNotFoundError as e:
            has_error = True
            blocks = get_block_set(
                "error_modal",
                {
                    "message": f":no_entry: Uh-Ohhh it looks like we found an error, this error one of the resources does not exist\n *Error* : _{e}_"
                },
            )
            break

        except TokenExpired as e:
            if attempts >= 5:
                logger.exception(
                    f"Failed to Update data for user {str(user.id)} after {attempts} tries"
                )
                has_error = True
                blocks = get_block_set(
                    "error_modal",
                    {
                        "message": f":no_entry: Uh-Ohhh it looks like we've had an issue with your token\n *Error* : _{e}_"
                    },
                )
                break
            else:
                crm.regenerate_token()
                attempts += 1

        except ConnectionResetError:
            if attempts >= 5:
                logger.exception(
                    f"Failed to Update data for user {str(user.id)} after {attempts} tries because of connection error"
                )
                has_error = True
                blocks = get_block_set(
                    "error_modal",
                    {
                        "message": f":no_entry: Uh-Ohhh we had an error connecting to your salesforce instance please try again"
                    },
                )
                break
            else:
                time.sleep(2)
                attempts += 1
        except Exception as e:
            logger.exception(
                f"Failed to Update data for user {str(user.id)} after {attempts} tries because of {e}"
            )
            has_error = True
            blocks = get_block_set(
                "error_modal",
                {"message": f":no_entry: Uh-Ohhh we had an error updating your Salesforce {e}"},
            )
            break
    if has_error:
        form_id = str(form.id)
        blocks = [
            *blocks,
            block_builders.actions_block(
                [
                    block_builders.simple_button_block(
                        "return to form",
                        form_id,
                        style="primary",
                        action_id=action_with_params(
                            slack_const.RETURN_TO_FORM_MODAL, [f"f={form_id}", f"u={str(user.id)}"]
                        ),
                    )
                ]
            ),
        ]
        new_context = {**context, "type": "command"}
        url = slack_const.SLACK_API_ROOT + slack_const.VIEWS_UPDATE
        error_view_data = {
            "view_id": payload["view"]["id"],
            "view": {
                "type": "modal",
                "title": {"type": "plain_text", "text": "Error"},
                "blocks": blocks,
                "private_metadata": json.dumps(new_context),
            },
        }
        try:
            return slack_requests.generic_request(
                url, error_view_data, access_token=user.organization.slack_integration.access_token
            )
        except Exception as e:
            return logger.exception(
                f"Failed To Update via command for user  {str(user.id)} email {user.email} {e}"
            )

    return


def CRM_FILTERS(crm, integration_id):
    filters = {
        "HUBSPOT": [{"propertyName": "hs_object_id", "operator": "EQ", "value": integration_id},],
        "SALESFORCE": [f"AND Id = '{integration_id}'"],
    }
    return filters[crm]


@log_all_exceptions
@processor(required_context=["w"])
def process_zoom_meeting_attach_resource(payload, context):
    workflow = MeetingWorkflow.objects.get(id=context.get("w"))
    user = workflow.user
    slack_access_token = user.organization.slack_integration.access_token
    url = slack_const.SLACK_API_ROOT + slack_const.VIEWS_UPDATE
    # get state - state contains the values based on the block_id

    state_values = payload["view"]["state"]["values"]
    meeting_resource = context.get("resource_type")
    if context.get("action") == "EXISTING":
        selected_action = [
            val.get("selected_option", {}).get("value", [])
            for val in state_values["select_existing"].values()
        ]
        integration_id = selected_action[0] if len(selected_action) else None
        try:
            resource = CRM_SWITCHER[user.crm][meeting_resource]["model"].objects.get(
                integration_id=integration_id
            )
            resource_id = resource.id
        except CRM_SWITCHER[user.crm][meeting_resource]["model"].DoesNotExist:
            try:
                resource_res = user.crm_account.adapter_class.list_resource_data(
                    meeting_resource, filter=CRM_FILTERS(user.crm, integration_id),
                )
                serializer = CRM_SWITCHER[user.crm][meeting_resource]["serializer"](
                    data=resource_res[0].as_dict
                )
                serializer.is_valid(raise_exception=True)
                serializer.save()
                resource_id = serializer.instance.id
            except Exception as e:
                logger.exception(
                    f"Failed to sync new resource with id {integration_id} for {user.email}"
                )
                return {
                    "response_action": "push",
                    "view": {
                        "type": "modal",
                        "title": {"type": "plain_text", "text": "An Error Occured"},
                        "blocks": get_block_set(
                            "error_modal",
                            {
                                "message": f":no_entry: We could not sync the {meeting_resource} because of :\n *Error* : _{e}_"
                            },
                        ),
                    },
                }
        workflow.resource_id = resource_id
        workflow.resource_type = meeting_resource
        workflow.save()
        # update the forms to the correct type

    else:
        # check to see if it already has the create form added and save that instead
        main_form = (
            workflow.forms.filter(template__form_type=slack_const.FORM_TYPE_CREATE,)
            .exclude(template__resource__in=["Contact", "OpportunityLineItem"])
            .first()
        )
        if main_form:
            stage_forms = workflow.forms.filter(
                template__form_type=slack_const.FORM_TYPE_STAGE_GATING
            ).exclude(template__resource=slack_const.FORM_RESOURCE_CONTACT)
            # if there are stage gating forms we need to save their data we already saved the main form's data

            if not len(stage_forms):
                main_form.save_form(state_values)
            else:
                # assume we already saved the forms for create
                for form in stage_forms:
                    form.save_form(state_values)
            try:
                resource = _process_create_new_resource.now(context.get("w"), meeting_resource)

            except FieldValidationError as e:

                return {
                    "response_action": "push",
                    "view": {
                        "type": "modal",
                        "title": {"type": "plain_text", "text": "An Error Occured"},
                        "blocks": get_block_set(
                            "error_modal",
                            {
                                "message": f":no_entry: Uh-Ohhh it looks like we found an error, this error is based on Validations set up by your org for {meeting_resource} objects\n *Error* : _{e}_"
                            },
                        ),
                    },
                }
            except RequiredFieldError as e:

                return {
                    "response_action": "push",
                    "view": {
                        "type": "modal",
                        "title": {"type": "plain_text", "text": "An Error Occurred"},
                        "blocks": get_block_set(
                            "error_modal",
                            {
                                "message": f":no_entry: Uh-Ohhh it looks like we found an error, this error is based on Required fields from Salesforce for {meeting_resource} objects\n *Error* : _{e}_"
                            },
                        ),
                    },
                }

            workflow.resource_id = str(resource.id)
            workflow.resource_type = meeting_resource

            workflow.save()
    workflow.forms.exclude(
        template__resource__in=[
            slack_const.FORM_RESOURCE_CONTACT,
            slack_const.FORM_RESOURCE_OPPORTUNITYLINEITEM,
        ]
    ).delete()
    workflow.add_form(meeting_resource, slack_const.FORM_TYPE_UPDATE, resource_id=resource_id)
    main_form = workflow.forms.first()
    context = {
        "w": str(workflow.id),
        "f": str(main_form.id),
        "type": "meeting",
    }
    data = {
        "view_id": payload["view"]["id"],
        "view": {
            "type": "modal",
            "callback_id": slack_const.ZOOM_MEETING__PROCESS_MEETING_SENTIMENT,
            "title": {"type": "plain_text", "text": "Log Meeting"},
            "blocks": get_block_set("meeting_review_modal", context=context),
            "submit": {"type": "plain_text", "text": "Submit"},
            "private_metadata": json.dumps(context),
            "external_id": f"meeting_review_modal.{str(uuid.uuid4())}",
        },
    }
    try:
        # update initial interaction workflow with new resource
        res = slack_requests.generic_request(url, data, slack_access_token)

    # add a message for user's if this failed
    except InvalidBlocksException as e:
        return logger.exception(
            f"Failed To Attach resource for user {str(workflow.id)} email {workflow.user.email} {e}"
        )
    except InvalidBlocksFormatException as e:
        return logger.exception(
            f"Failed To Attach resource for user {str(workflow.id)} email {workflow.user.email} {e}"
        )
    except UnHandeledBlocksException as e:
        return logger.exception(
            f"Failed To Attach resource for user {str(workflow.id)} email {workflow.user.email} {e}"
        )
    except InvalidAccessToken as e:
        return logger.exception(
            f"Failed To Attach resource for user {str(workflow.id)} email {workflow.user.email} {e}"
        )
    return


@processor()
def process_update_meeting_contact(payload, context):
    state = payload["view"]["state"]["values"]
    type = context.get("type", None)
    workflow = MeetingWorkflow.objects.get(id=context.get("w"))
    meeting = workflow.meeting
    contact = dict(
        *filter(
            lambda contact: contact["_tracking_id"] == context.get("tracking_id"),
            meeting.participants,
        )
    )
    form = (
        workflow.forms.get(id=contact["_form"])
        if workflow.meeting
        else OrgCustomSlackFormInstance.objects.get(id=contact.get("_form"))
    )
    form.save_form(state)
    user_id = workflow.user.id if type else workflow.user_id
    # reconstruct the current data with the updated data
    adapter_class = crm_routes[workflow.user.crm]["Contact"]
    adapter = adapter_class.from_api(
        {**contact.get("secondary_data", {}), **form.saved_data}, str(user_id)
    )
    url = slack_const.SLACK_API_ROOT + slack_const.VIEWS_UPDATE
    trigger_id = payload["trigger_id"]
    view_id = context.get(str("current_view_id"))
    new_contact = {
        **contact,
        **adapter.as_dict,
        "id": contact.get("id", None),
        "__has_changes": True,
    }
    if type:
        part_index = None
        for index, participant in enumerate(workflow.participants):
            if participant["_tracking_id"] == new_contact["_tracking_id"]:
                part_index = index
                break
        workflow.participants = [
            *workflow.participants[:part_index],
            new_contact,
            *workflow.participants[part_index + 1 :],
        ]
        workflow.save()
        user = User.objects.get(id=user_id)
        org = user.organization
        access_token = org.slack_integration.access_token
        show_meeting_context = {"w": context.get("w"), "type": workflow.resource_type}
        # return {"response_action": "clear"}
    else:
        # replace the contact in the participants list
        part_index = None
        for index, participant in enumerate(meeting.participants):
            if participant["_tracking_id"] == new_contact["_tracking_id"]:
                part_index = index
                break
        meeting.participants = [
            *meeting.participants[:part_index],
            new_contact,
            *meeting.participants[part_index + 1 :],
        ]
        meeting.save()
        workflow = MeetingWorkflow.objects.get(id=context.get("w"))
        org = workflow.user.organization
        access_token = org.slack_integration.access_token
        show_meeting_context = {
            "w": context.get("w"),
            "original_message_channel": context.get("original_message_channel"),
            "original_message_timestamp": context.get("original_message_timestamp"),
        }
        if check_contact_last_name(workflow.id):
            update_res = slack_requests.update_channel_message(
                context.get("original_message_channel"),
                context.get("original_message_timestamp"),
                access_token,
                block_set=get_block_set("initial_meeting_interaction", {"w": context.get("w")}),
            )
    blocks = get_block_set("show_meeting_contacts", show_meeting_context,)
    # replace the contact in the participants list
    data = {
        "trigger_id": trigger_id,
        "view_id": view_id,
        "view": {
            "type": "modal",
            "callback_id": slack_const.ZOOM_MEETING__VIEW_MEETING_CONTACTS,
            "title": {"type": "plain_text", "text": "Contacts"},
            "blocks": blocks,
        },
    }
    try:
        res = slack_requests.generic_request(url, data, access_token=access_token)
    except InvalidBlocksException as e:
        return logger.exception(
            f"Failed To load update meeting contact modal for user with workflow {str(workflow.id)} email {workflow.user.email} {e}"
        )
    except InvalidBlocksFormatException as e:
        return logger.exception(
            f"Failed To load update meeting contact modal for user with workflow {str(workflow.id)} email {workflow.user.email} {e}"
        )
    except UnHandeledBlocksException as e:
        return logger.exception(
            f"Failed To load update meeting contact modal for user with workflow {str(workflow.id)} email {workflow.user.email} {e}"
        )
    except InvalidAccessToken as e:
        return logger.exception(
            f"Failed To load update meeting contact modal for user with workflow {str(workflow.id)} email {workflow.user.email} {e}"
        )

    return


@processor()
def process_edit_meeting_contact(payload, context):
    """This Submission returns the update form stacked on top of the view contacts form"""

    return {
        "response_action": "push",
        "view": {
            "type": "modal",
            "title": {"type": "plain_text", "text": "Edit Contact"},
            "submit": {"type": "plain_text", "text": "Save"},
            "blocks": get_block_set("edit_meeting_contacts", context,),
            "callback_id": slack_const.ZOOM_MEETING__UPDATE_PARTICIPANT_DATA,
            "private_metadata": json.dumps(context),
        },
    }


@processor()
def process_save_contact_data(payload, context):
    workflow = MeetingWorkflow.objects.get(id=context.get("w"))
    # update the old view to change edit contact to submit again

    state = payload["view"]["state"]["values"]
    ## save the checked contacts to the operations list
    create = []
    update = []
    for val in state.values():
        if val.get("CREATE") and len(val["CREATE"]["selected_options"]):
            create.append(val["CREATE"]["selected_options"][0]["value"])
        elif val.get("UPDATE") and len(val["UPDATE"]["selected_options"]):
            update.append(val["UPDATE"]["selected_options"][0]["value"])

    if not len(workflow.operations_list):
        workflow.operations_list = []
    if len(create):

        workflow.operations_list = [
            *workflow.operations_list,
            *[
                f"{sf_consts.MEETING_REVIEW__CREATE_CONTACTS}.{str(workflow.id)},{form}"
                for form in create
            ],
        ]

    if len(update):
        workflow.operations_list = [
            *workflow.operations_list,
            *[
                f"{sf_consts.MEETING_REVIEW__UPDATE_CONTACTS}.{str(workflow.id)},{form}"
                for form in update
            ],
        ]

    workflow.save()

    return


@log_all_exceptions
@processor(required_context=[])
def process_create_task(payload, context):
    pm = json.loads(payload["view"]["private_metadata"])

    user = User.objects.get(id=pm.get("u"))
    slack_access_token = user.organization.slack_integration.access_token
    # get state - state contains the values based on the block_id

    state = payload["view"]["state"]["values"]
    description = state.get("managr_task_description", {}).get("plain_input", {}).get("value", None)
    activity_date = [
        value.get("selected_date") for value in state.get("managr_task_datetime", {}).values()
    ]
    owner_id = [
        value.get("selected_option") for value in state.get("managr_task_assign_to", {}).values()
    ]
    status = [
        value.get("selected_option") for value in state.get("managr_task_status", {}).values()
    ]

    if status[0] == None:
        status = "Not Started"
    else:
        status = status[0].get("value")

    related_to_type = [
        value.get("selected_option")
        for value in state.get("managr_task_related_to_resource", {}).values()
    ]
    related_to = [
        value.get("selected_option") for value in state.get("managr_task_related_to", {}).values()
    ]
    if len(related_to) and len(related_to_type):
        related_to = (
            model_routes.get(related_to_type[0].get("value"))
            .get("model")
            .objects.get(id=related_to[0].get("value"))
            .integration_id
        )

    data = {
        "Subject": state.get("managr_task_subject", {}).get("plain_input", {}).get("value"),
        "ActivityDate": activity_date[0] if len(activity_date) else None,
        "OwnerId": owner_id[0].get("value") if len(owner_id) else None,
        "Status": status,
    }
    if description:
        data["Description"] = description
    if related_to and related_to_type:

        if related_to_type[0].get("value") not in [
            sf_consts.RESOURCE_SYNC_CONTACT,
            sf_consts.RESOURCE_SYNC_LEAD,
        ]:
            data["WhatId"] = related_to
        else:
            data["WhoId"] = related_to

    try:
        _process_create_task.now(str(user.id), data)

    except FieldValidationError as e:

        return {
            "response_action": "push",
            "view": {
                "type": "modal",
                "title": {"type": "plain_text", "text": "An Error Occured"},
                "blocks": get_block_set(
                    "error_modal",
                    {
                        "message": f":no_entry: Uh-Ohhh it looks like we found an error, this error is based on Validations set up by your org\n *Error* : _{e}_"
                    },
                ),
            },
        }
    except RequiredFieldError as e:

        return {
            "response_action": "push",
            "view": {
                "type": "modal",
                "title": {"type": "plain_text", "text": "An Error Occurred"},
                "blocks": get_block_set(
                    "error_modal",
                    {
                        "message": f":no_entry: Uh-Ohhh it looks like we found an error, this error is based on Required fields from Salesforce\n *Error* : _{e}_"
                    },
                ),
            },
        }
    except SFNotFoundError as e:

        return {
            "response_action": "push",
            "view": {
                "type": "modal",
                "title": {"type": "plain_text", "text": "An Error Occurred"},
                "blocks": get_block_set(
                    "error_modal",
                    {
                        "message": f":no_entry: Uh-Ohhh it looks like we found an error, this error one of the resources does not exist\n *Error* : _{e}_"
                    },
                ),
            },
        }

    except UnhandledCRMError as e:

        return {
            "response_action": "push",
            "view": {
                "type": "modal",
                "title": {"type": "plain_text", "text": "An Error Occurred"},
                "blocks": get_block_set(
                    "error_modal",
                    {
                        "message": f":no_entry: Uh-Ohhh it looks like we found an error, this error is new to us\n *Error* : _{e}_"
                    },
                ),
            },
        }

    # TODO: [MGR-830] Change this to be api.update method instead PB 03/31/21
    return {
        "response_action": "update",
        "view": {
            "type": "modal",
            "title": {"type": "plain_text", "text": "Task Created"},
            "blocks": [
                block_builders.simple_section(
                    ":white_check_mark: Successfully created task!", "mrkdwn"
                )
            ],
        },
    }


@log_all_exceptions
@processor(required_context=[])
def process_create_event(payload, context):
    user = User.objects.get(id=context.get("u"))

    slack_access_token = user.organization.slack_integration.access_token
    # get state - state contains the values based on the block_id

    state = payload["view"]["state"]["values"]
    activity_date = [
        value.get("selected_date") for value in state.get("managr_event_date", {}).values()
    ]
    activity_time = [
        value.get("selected_time") for value in state.get("managr_event_time", {}).values()
    ]
    owner_id = [
        value.get("selected_option") for value in state.get("managr_event_assign_to", {}).values()
    ]
    duration = state.get("managr_event_duration", {}).get("plain_input", {}).get("value")

    related_to_type = [
        value.get("selected_option")
        for value in state.get("managr_event_related_to_resource", {}).values()
    ]
    related_to = [
        value.get("selected_option") for value in state.get("managr_event_related_to", {}).values()
    ]
    if len(related_to) and len(related_to_type):
        related_to = (
            model_routes.get(related_to_type[0].get("value"))
            .get("model")
            .objects.get(id=related_to[0].get("value"))
            .integration_id
        )
    data = {
        "Subject": state.get("managr_event_subject", {}).get("plain_input", {}).get("value"),
        "ActivityDate": activity_date[0] if len(activity_date) else None,
        "OwnerId": owner_id[0].get("value") if len(owner_id) else None,
        "DurationInMinutes": duration[0] if len(duration) else None,
        "ActivityDateTime": f"{activity_date[0]}T{activity_time[0]+':00'  if len(activity_time) else ''}",
    }

    if related_to and related_to_type:

        if related_to_type[0].get("value") not in [
            sf_consts.RESOURCE_SYNC_CONTACT,
            sf_consts.RESOURCE_SYNC_LEAD,
        ]:
            data["WhatId"] = related_to
        else:
            data["WhoId"] = related_to

    try:

        _process_create_event.now(context.get("u"), data)

    except FieldValidationError as e:

        return {
            "response_action": "push",
            "view": {
                "type": "modal",
                "title": {"type": "plain_text", "text": "An Error Occured"},
                "blocks": get_block_set(
                    "error_modal",
                    {
                        "message": f":no_entry: Uh-Ohhh it looks like we found an error, this error is based on Validations set up by your org\n *Error* : _{e}_"
                    },
                ),
            },
        }
    except RequiredFieldError as e:

        return {
            "response_action": "push",
            "view": {
                "type": "modal",
                "title": {"type": "plain_text", "text": "An Error Occurred"},
                "blocks": get_block_set(
                    "error_modal",
                    {
                        "message": f":no_entry: Uh-Ohhh it looks like we found an error, this error is based on Required fields from Salesforce\n *Error* : _{e}_"
                    },
                ),
            },
        }
    except SFNotFoundError as e:

        return {
            "response_action": "push",
            "view": {
                "type": "modal",
                "title": {"type": "plain_text", "text": "An Error Occurred"},
                "blocks": get_block_set(
                    "error_modal",
                    {
                        "message": f":no_entry: Uh-Ohhh it looks like we found an error, this error one of the resources does not exist\n *Error* : _{e}_"
                    },
                ),
            },
        }

    except UnhandledCRMError as e:

        return {
            "response_action": "push",
            "view": {
                "type": "modal",
                "title": {"type": "plain_text", "text": "An Error Occurred"},
                "blocks": get_block_set(
                    "error_modal",
                    {
                        "message": f":no_entry: Uh-Ohhh it looks like we found an error, this error is new to us\n *Error* : _{e}_"
                    },
                ),
            },
        }

    # TODO: [MGR-830] Change this to be api.update method instead PB 03/31/21
    return {
        "response_action": "update",
        "view": {
            "type": "modal",
            "title": {"type": "plain_text", "text": "Event Created"},
            "blocks": [
                block_builders.simple_section(
                    ":white_check_mark: Successfully created event!", "mrkdwn"
                )
            ],
        },
    }


@log_all_exceptions
@slack_api_exceptions(rethrow=True)
@processor(required_context=[])
def process_schedule_meeting(payload, context):
    u = User.objects.get(id=context.get("u"))
    data = payload["view"]["state"]["values"]
    trigger_id = payload["trigger_id"]
    view_id = payload["view"]["id"]
    org = u.organization
    access_token = org.slack_integration.access_token
    description = data["meeting_description"]["meeting_data"]["value"]
    url = slack_const.SLACK_API_ROOT + slack_const.VIEWS_UPDATE
    participants = []
    if data["meeting_participants"][f"GET_USER_CONTACTS?u={u.id}"]["selected_options"]:
        query_data = Contact.objects.filter(
            id__in=list(
                map(
                    lambda val: val["value"],
                    data["meeting_participants"][f"GET_USER_CONTACTS?u={u.id}"]["selected_options"],
                )
            )
        ).values("email", "secondary_data")
        for participant in query_data:
            participants.append(
                {
                    "email": participant["email"],
                    "name": participant["secondary_data"]["Name"],
                    "status": "noreply",
                }
            )
    if data["meeting_internals"][f"GET_LOCAL_RESOURCE_OPTIONS?u={u.id}&resource_type=User"][
        "selected_options"
    ]:
        query_data = User.objects.filter(
            id__in=list(
                map(
                    lambda val: val["value"],
                    data["meeting_internals"][
                        f"GET_LOCAL_RESOURCE_OPTIONS?u={u.id}&resource_type=User"
                    ]["selected_options"],
                )
            )
        ).values("email", "first_name", "last_name")
        for participant in query_data:
            participants.append(
                {
                    "email": participant["email"],
                    "name": f"{participant['first_name']} {participant['last_name']}",
                    "status": "noreply",
                }
            )
    if data["meeting_extras"]["plain_input"]["value"]:
        for participant in data["meeting_extras"]["plain_input"]["value"].split(","):
            participants.append({"email": participant})
    zoom_data = {
        "meeting_topic": data["meeting_topic"]["meeting_data"]["value"],
        "meeting_date": data["meeting_date"]["meeting_data"]["selected_date"],
        "meeting_hour": data["meeting_hour"]["meeting_data"]["selected_option"]["value"],
        "meeting_minute": data["meeting_minute"]["meeting_data"]["selected_option"]["value"],
        "meeting_time": data["meeting_time"]["meeting_data"]["selected_option"]["value"],
        "meeting_duration": data["meeting_duration"]["meeting_data"]["selected_option"]["value"],
    }
    loading_data = {
        "trigger_id": trigger_id,
        "view_id": view_id,
        "view": {
            "type": "modal",
            "title": {"type": "plain_text", "text": "Loading"},
            "blocks": get_block_set(
                "loading",
                {
                    "message": ":rocket: Creating your Zoom meeting and inviting contacts!",
                    "fill": True,
                },
            ),
        },
    }
    try:
        res = slack_requests.generic_request(url, loading_data, access_token=access_token)
        zoom_res = emit_process_schedule_zoom_meeting(u, zoom_data)
        cal_res = emit_create_calendar_event(
            u,
            zoom_res["topic"],
            zoom_res["start_time"],
            participants,
            zoom_res["join_url"],
            description,
        )
        return {
            "response_action": "update",
            "view": {
                "type": "modal",
                "title": {"type": "plain_text", "text": "Success"},
                "blocks": [block_builders.simple_section("Zoom meeting successfully scheduled")],
            },
        }
    except InvalidBlocksException as e:
        return logger.exception(
            f"Faild to update Zoom Schedule Meeting modal for user {u.email}, {e}"
        )
    except InvalidBlocksFormatException as e:
        return logger.exception(
            f"Faild to update Zoom Schedule Meeting modal for user {u.email}, {e}"
        )
    except UnHandeledBlocksException as e:
        return logger.exception(
            f"Faild to update Zoom Schedule Meeting modal for user {u.email}, {e}"
        )
    except InvalidAccessToken as e:
        return logger.exception(
            f"Faild to update Zoom Schedule Meeting modal for user {u.email}, {e}"
        )
    return


@log_all_exceptions
@slack_api_exceptions(rethrow=True)
@processor(required_context=["u"])
def process_add_contacts_to_cadence(payload, context):
    pm = json.loads(payload["view"]["private_metadata"])
    u = User.objects.get(id=context.get("u"))
    cadence_id = payload["view"]["state"]["values"]["select_cadence"][
        f"GET_CADENCE_OPTIONS?u={context.get('u')}"
    ]["selected_option"]["value"]
    trigger_id = payload["trigger_id"]
    view_id = payload["view"]["id"]
    org = u.organization
    access_token = org.slack_integration.access_token
    url = slack_const.SLACK_API_ROOT + slack_const.VIEWS_UPDATE
    if pm.get("resource_type", None) == "Contact":
        contacts = [context.get("resource_id")]
    else:
        contacts = [
            option["value"]
            for option in payload["view"]["state"]["values"]["select_people"][
                f"{slack_const.GET_CONTACT_OPTIONS}?u={u.id}&resource_id={context.get('resource_id')}&resource_type={context.get('resource_type')}"
            ]["selected_options"]
        ]
    loading_data = {
        "trigger_id": trigger_id,
        "view_id": view_id,
        "view": {
            "type": "modal",
            "title": {"type": "plain_text", "text": "Loading"},
            "blocks": get_block_set(
                "loading",
                {"message": ":rocket: Putting contacts into your Cadence", "fill": True,},
            ),
        },
    }
    if len(contacts):
        res = slack_requests.generic_request(url, loading_data, access_token=access_token)
        success = 0
        failed = 0
        created = 0
        errors = []
        for person in contacts:
            person_res = emit_add_cadence_membership(person, cadence_id, str(u.id))
            if person_res["status"] == "Success":
                success += 1
            elif person_res["status"] == "Created":
                success += 1
                created += 1
            else:
                failed += 1
                errors.append(person_res["errors"])
        message = (
            f"{success}/{success + failed} added to cadence ({created} new People imported to Salesloft)"
            if created > 0
            else f"{success}/{success + failed} added to cadence"
        )
        if len(errors):
            message = f"Validation error adding contact to cadence: {','.join(errors)}"

        return {
            "response_action": "update",
            "view": {
                "type": "modal",
                "title": {"type": "plain_text", "text": "Add To Cadence"},
                "blocks": [block_builders.simple_section(message)],
            },
        }

    else:
        return {
            "response_action": "update",
            "view": {
                "type": "modal",
                "title": {"type": "plain_text", "text": "Add To Cadence"},
                "blocks": [
                    block_builders.simple_section(
                        f"No people associated for {context.get('resource_name')}"
                    )
                ],
            },
        }


@log_all_exceptions
@slack_api_exceptions(rethrow=True)
@processor(required_context=["u"])
def process_add_contacts_to_sequence(payload, context):
    pm = json.loads(payload["view"]["private_metadata"])
    meta_data = json.loads(payload["view"]["private_metadata"])
    u = User.objects.get(id=context.get("u"))
    sequence_id = payload["view"]["state"]["values"]["select_sequence"][
        f"GET_SEQUENCE_OPTIONS?u={context.get('u')}"
    ]["selected_option"]["value"]
    trigger_id = payload["trigger_id"]
    view_id = payload["view"]["id"]

    org = u.organization
    access_token = org.slack_integration.access_token
    url = slack_const.SLACK_API_ROOT + slack_const.VIEWS_UPDATE
    if pm.get("resource_type", None) == "Contact":
        contacts = [context.get("resource_id")]
    else:
        contacts = [
            option["value"]
            for option in payload["view"]["state"]["values"]["select_people"][
                f"{slack_const.GET_CONTACT_OPTIONS}?u={u.id}&resource_id={context.get('resource_id')}&resource_type={context.get('resource_type')}"
            ]["selected_options"]
        ]
    loading_data = {
        "trigger_id": trigger_id,
        "view_id": view_id,
        "view": {
            "type": "modal",
            "title": {"type": "plain_text", "text": "Loading"},
            "blocks": get_block_set(
                "loading",
                {"message": ":rocket: Putting contacts into your Cadence", "fill": True,},
            ),
        },
    }
    if len(contacts):
        res = slack_requests.generic_request(url, loading_data, access_token=access_token)
        success = 0
        failed = 0
        created = 0
        for contact in contacts:
            prospect_res = emit_add_sequence_state(contact, sequence_id)
            if prospect_res["status"] == "Success":
                success += 1
            elif prospect_res["status"] == "Created":
                success += 1
                created += 1
            else:
                failed += 1
        message = (
            f"{success}/{success + failed} added to sequence ({created} new Prospects imported to Outreach)"
            if created > 0
            else f"{success}/{success + failed} added to sequence"
        )
        return {
            "response_action": "update",
            "view": {
                "type": "modal",
                "title": {"type": "plain_text", "text": "Success"},
                "blocks": [block_builders.simple_section(message)],
            },
        }
    else:
        update_res = slack_requests.send_ephemeral_message(
            u.slack_integration.channel,
            access_token,
            meta_data["slack_id"],
            block_set=[block_builders.simple_section(f"No people associated for {resource_id}")],
        )
        return


@log_all_exceptions
@slack_api_exceptions(rethrow=True)
@processor(required_context=["u"])
def process_get_notes(payload, context):
    u = User.objects.get(id=context.get("u"))
    view_id = payload["view"]["id"]
    org = u.organization
    access_token = org.slack_integration.access_token
    resource_id = payload["view"]["state"]["values"]["select_opp"][
        f"{slack_const.GET_LOCAL_RESOURCE_OPTIONS}?u={u.id}&resource_type=Opportunity"
    ]["selected_option"]["value"]
    opportunity = Opportunity.objects.get(id=resource_id)
    note_data = (
        OrgCustomSlackFormInstance.objects.filter(resource_id=resource_id)
        .filter(is_submitted=True)
        .values_list(
            "submission_date",
            "saved_data__meeting_type",
            "saved_data__meeting_comments",
            "saved_data__StageName",
            "previous_data__StageName",
        )
    )
    note_blocks = [block_builders.header_block(f"Notes for {opportunity.name}")]
    if note_data:
        for note in note_data:
            if note[1] is None:
                continue
            date = note[0].date()
            current_stage = note[3]
            previous_stage = note[4]

            block_message = f"*{date} - {note[1]}*\n"
            if current_stage and previous_stage:
                if current_stage != previous_stage:
                    block_message += f"Stage: ~{previous_stage}~ :arrow_right: {current_stage} \n"
            block_message += f"\nNotes:\n {note[2]}"
            note_blocks.append(block_builders.simple_section(block_message, "mrkdwn"))
            note_blocks.append({"type": "divider"})
    url = slack_const.SLACK_API_ROOT + slack_const.VIEWS_OPEN
    # loading_data = {
    #     "trigger_id": trigger_id,
    #     "view_id": view_id,
    #     "view": {
    #         "type": "modal",
    #         "title": {"type": "plain_text", "text": "Loading"},
    #         "blocks": get_block_set(
    #             "loading",
    #             {
    #                 "message": ":notebook_with_decorative_cover: Putting your notes together",
    #                 "fill": True,
    #             },
    #         ),
    #     },
    # }
    data = {
        "trigger_id": context.get("trigger_id"),
        "view_id": view_id,
        "view": {
            "type": "modal",
            "callback_id": "NONE",
            "title": {"type": "plain_text", "text": "Notes"},
            "blocks": note_blocks,
        },
    }
    loading_res = slack_requests.generic_request(url, data, access_token=access_token)
    # update_res = slack_requests.send_channel_message(
    #     u.slack_integration.channel, access_token, block_set=note_blocks,
    # )
    return


@log_all_exceptions
@slack_api_exceptions(rethrow=True)
@processor(required_context=["u"])
def process_send_recaps(payload, context):
    values = payload["view"]["state"]["values"]
    pm = json.loads(payload["view"]["private_metadata"])
    type = context.get("type", None)
    bulk_status = pm.get("bulk_status")
    channels = list(values["__send_recap_to_channels"].values())[0]["selected_conversations"]
    leadership = [
        option["value"]
        for option in values["__send_recap_to_leadership"][
            f"GET_LOCAL_RESOURCE_OPTIONS?u={context.get('u')}&resource_type=User&field_id=e286d1d5-5447-47e6-ad55-5f54fdd2b00d"
        ]["selected_options"]
    ]
    reps = [
        option["value"]
        for option in values["__send_recap_to_reps"][
            f"GET_LOCAL_RESOURCE_OPTIONS?u={context.get('u')}&resource_type=User&field_id=fae88a10-53cc-470e-86ec-32376c041893"
        ]["selected_options"]
    ]
    send_to_recaps = {"channels": channels, "leadership": leadership, "reps": reps}
    if type == "meeting":
        workflow = MeetingWorkflow.objects.get(id=context.get("workflow_id"))
        # collect forms for resource meeting_review and if stages any stages related forms
        meeting_forms = workflow.forms.filter(
            template__form_type__in=[
                slack_const.FORM_TYPE_UPDATE,
                slack_const.FORM_TYPE_CREATE,
                slack_const.FORM_TYPE_STAGE_GATING,
            ]
        )
        form_ids = [str(form.id) for form in meeting_forms]
    elif type is None and pm.get("lead", None) is not None:
        _send_convert_recap(
            context.get("u", None),
            pm.get("lead"),
            pm.get("account"),
            pm.get("contact"),
            pm.get("opportunity", None),
            send_to_recaps,
        )
        return
    else:
        form_ids = context.get("form_ids").split(",")
    _send_recap(form_ids, send_to_recaps, bulk=bulk_status)
    return


@log_all_exceptions
@slack_api_exceptions(rethrow=True)
@processor(required_context=["opp_item_id"])
def process_update_product(payload, context):
    has_error = False
    state = payload["view"]["state"]["values"]
    user = User.objects.get(id=context.get("u"))
    view_id = payload["view"]["id"]
    type = context.get("type", None)
    pm = json.loads(payload["view"]["private_metadata"])

    main_form = OrgCustomSlackFormInstance.objects.get(id=context.get("main_form"))
    product_form = user.custom_slack_form_instances.filter(
        template__resource="OpportunityLineItem"
    ).first()
    opp_line_item = OpportunityLineItem.objects.filter(id=product_form.resource_id).first()
    if (
        "HasSchedule" in opp_line_item.secondary_data
        and opp_line_item.secondary_data["HasSchedule"]
    ):
        state.pop("Quantity")
    product_form.save_form(state)
    slack_access_token = user.organization.slack_integration.access_token
    url = slack_const.SLACK_API_ROOT + slack_const.VIEWS_PUSH
    attempts = 1
    while True:
        sf = user.salesforce_account
        try:
            resource = product_form.resource_object.update_in_salesforce(
                str(user.id), product_form.saved_data
            )
            product_form.is_submitted = True
            product_form.submission_date = timezone.now()
            product_form.update_source = type
            product_form.save()
            break
        except FieldValidationError as e:
            has_error = True
            blocks = (
                get_block_set(
                    "error_modal",
                    {
                        "message": f":no_entry: Uh-Ohhh it looks like we found an error, this error is based on Validations set up by your org\n *Error* : _{e}_"
                    },
                ),
            )
            break
        except RequiredFieldError as e:
            has_error = True
            blocks = get_block_set(
                "error_modal",
                {
                    "message": f":no_entry: Uh-Ohhh it looks like we found an error, this error is based on Required fields from Salesforce\n *Error* : _{e}_"
                },
            )
            break
        except UnhandledCRMError as e:
            has_error = True
            blocks = get_block_set(
                "error_modal",
                {
                    "message": f":no_entry: Uh-Ohhh it looks like we found an error, this error is new to us please see below\n *Error* : _{e}_"
                },
            )
            break
        except SFNotFoundError as e:
            has_error = True
            blocks = get_block_set(
                "error_modal",
                {
                    "message": f":no_entry: Uh-Ohhh it looks like we found an error, this error one of the resources does not exist\n *Error* : _{e}_"
                },
            )
            break
        except TokenExpired:
            if attempts >= 5:
                logger.exception(
                    f"Failed to Update data for user {str(user.id)} after {attempts} tries"
                )
                has_error = True
                blocks = get_block_set(
                    "error_modal",
                    {
                        "message": f":no_entry: Uh-Ohhh it looks like we've had an issue with your token\n *Error* : _{e}_"
                    },
                )
                break
            else:
                sf.regenerate_token()
                attempts += 1
        except ConnectionResetError:
            if attempts >= 5:
                logger.exception(
                    f"Failed to Update data for user {str(user.id)} after {attempts} tries because of connection error"
                )
                has_error = True
                blocks = get_block_set(
                    "error_modal",
                    {
                        "message": f":no_entry: Uh-Ohhh we had an error connecting to your salesforce instance please try again"
                    },
                )
                break
            else:
                time.sleep(2)
                attempts += 1
    if has_error:
        # add a special button to return the user back to edit their form
        # this is only required for single page forms
        blocks = [
            *blocks,
            block_builders.actions_block(
                [
                    block_builders.simple_button_block(
                        "return to form",
                        str(main_form.id),
                        style="primary",
                        action_id=slack_const.RETURN_TO_FORM_MODAL,
                    )
                ]
            ),
        ]
        url = slack_const.SLACK_API_ROOT + slack_const.VIEWS_UPDATE
        error_view_data = {
            "view_id": view_id,
            "view": {
                "type": "modal",
                "title": {"type": "plain_text", "text": "Error"},
                "blocks": blocks,
                "private_metadata": json.dumps(pm),
                "external_id": f"{'update_product'}.{str(uuid.uuid4())}",
            },
        }
        try:
            return slack_requests.generic_request(
                url, error_view_data, access_token=slack_access_token
            )
        except Exception as e:
            return logger.exception(
                f"Failed To Update via command for user  {str(user.id)} email {user.email} {e}"
            )
    message = ":white_check_mark: Successfully updated product"
    return {
        "response_action": "update",
        "view": {
            "type": "modal",
            "title": {"type": "plain_text", "text": "Success"},
            "blocks": get_block_set("success_text_modal", {"message": message}),
        },
    }


@log_all_exceptions
@slack_api_exceptions(rethrow=True)
@processor(required_context=["f"])
def process_submit_product(payload, context):
    # get context
    state = payload["view"]["state"]["values"]
    current_form_ids = context.get("f").split(",")
    type = context.get("type", None)
    workflow_id = context.get("w", None)
    if workflow_id:
        workflow = MeetingWorkflow.objects.get(id=workflow_id)
    has_error = False
    blocks = None
    pm = json.loads(payload["view"]["private_metadata"])
    user = User.objects.get(id=context.get("u"))
    trigger_id = payload["trigger_id"]
    view_id = payload["view"]["id"]
    product_form_id = context.get("product_form", None)
    current_forms = user.custom_slack_form_instances.filter(id__in=current_form_ids)
    main_form = (
        current_forms.filter(template__form_type__in=["UPDATE", "CREATE"])
        .exclude(template__resource="OpportunityLineItem")
        .first()
    )
    if product_form_id:
        product_form = user.custom_slack_form_instances.get(id=product_form_id)
        product_form.save_form(state)
    slack_access_token = user.organization.slack_integration.access_token
    url = slack_const.SLACK_API_ROOT + slack_const.VIEWS_UPDATE
    loading_view_data = {
        "trigger_id": trigger_id,
        "view_id": view_id,
        "view": {
            "type": "modal",
            "title": {"type": "plain_text", "text": "Loading"},
            "blocks": get_block_set(
                "loading",
                {
                    "message": ":exclamation: Please wait a few seconds :zany_face:, then click '*try again*'",
                    "fill": True,
                },
            ),
            "private_metadata": json.dumps(context),
        },
    }
    try:
        res = slack_requests.generic_request(
            url, loading_view_data, access_token=slack_access_token
        )
    except Exception as e:
        return logger.exception(
            f"Failed To Update via command for user  {str(user.id)} email {user.email} {e}"
        )
    attempts = 1
    while True:
        sf = user.salesforce_account
        try:
            opp = BaseOpportunity.objects.get(id=main_form.resource_id)
            try:
                entry = PricebookEntry.objects.get(
                    integration_id=product_form.saved_data["PricebookEntryId"]
                )
            except PricebookEntry.DoesNotExist:
                entry = PricebookEntryAdapter.get_current_values(
                    product_form.saved_data["PricebookEntryId"],
                    sf.access_token,
                    sf.instance_url,
                    str(user.id),
                )
            product_data = {
                **product_form.saved_data,
                "OpportunityId": opp.integration_id,
            }
            if "UnitPrice" not in product_form.saved_data:
                product_data["UnitPrice"] = str(entry.unit_price)
            if (
                "UnitPrice" in product_form.saved_data
                and product_form.saved_data["UnitPrice"] is None
            ):
                product_data["UnitPrice"] = str(entry.unit_price)
            resource = OpportunityLineItem.create_in_salesforce(product_data, context.get("u"))
            product_form.is_submitted = True
            product_form.submission_date = timezone.now()
            product_form.update_source = context.get("type")
            product_form.save()
            break
        except FieldValidationError as e:
            has_error = True
            blocks = (
                get_block_set(
                    "error_modal",
                    {
                        "message": f":no_entry: Uh-Ohhh it looks like we found an error, this error is based on Validations set up by your org\n *Error* : _{e}_"
                    },
                ),
            )
            break

        except RequiredFieldError as e:
            has_error = True
            blocks = get_block_set(
                "error_modal",
                {
                    "message": f":no_entry: Uh-Ohhh it looks like we found an error, this error is based on Required fields from Salesforce\n *Error* : _{e}_"
                },
            )
            break
        except UnhandledCRMError as e:
            has_error = True
            blocks = get_block_set(
                "error_modal",
                {
                    "message": f":no_entry: Uh-Ohhh it looks like we found an error, this error is new to us please see below\n *Error* : _{e}_"
                },
            )
            break

        except SFNotFoundError as e:
            has_error = True
            blocks = get_block_set(
                "error_modal",
                {
                    "message": f":no_entry: Uh-Ohhh it looks like we found an error, this error one of the resources does not exist\n *Error* : _{e}_"
                },
            )
            break

        except TokenExpired:
            if attempts >= 5:
                logger.exception(
                    f"Failed to Update data for user {str(user.id)} after {attempts} tries"
                )
                has_error = True
                blocks = get_block_set(
                    "error_modal",
                    {
                        "message": f":no_entry: Uh-Ohhh it looks like we've had an issue with your token\n *Error* : _{e}_"
                    },
                )
                break
            else:
                sf.regenerate_token()
                attempts += 1

        except ConnectionResetError:
            if attempts >= 5:
                logger.exception(
                    f"Failed to Update data for user {str(user.id)} after {attempts} tries because of connection error"
                )
                has_error = True
                blocks = get_block_set(
                    "error_modal",
                    {
                        "message": f":no_entry: Uh-Ohhh we had an error connecting to your salesforce instance please try again"
                    },
                )
                break
            else:
                time.sleep(2)
                attempts += 1
        except Exception as e:
            if attempts >= 5:
                logger.exception(
                    f"Failed to Update data for user {str(user.id)} after {attempts} tries because of connection error"
                )
                has_error = True
                blocks = get_block_set(
                    "error_modal",
                    {
                        "message": f":no_entry: Uh-Ohhh we had an unexpected error please try again: {e}"
                    },
                )
                break
            else:
                time.sleep(2)
                attempts += 1
    if has_error:
        blocks = [
            *blocks,
            block_builders.actions_block(
                [
                    block_builders.simple_button_block(
                        "return to form",
                        product_form_id,
                        style="primary",
                        action_id=slack_const.RETURN_TO_FORM_MODAL,
                    )
                ]
            ),
        ]
        url = slack_const.SLACK_API_ROOT + slack_const.VIEWS_UPDATE
        error_view_data = {
            "trigger_id": trigger_id,
            "view_id": view_id,
            "view": {
                "type": "modal",
                "title": {"type": "plain_text", "text": "Error"},
                "blocks": blocks,
                "private_metadata": json.dumps(pm),
                "external_id": f"{'add_product'}.{str(uuid.uuid4())}",
            },
        }
        try:
            return slack_requests.generic_request(
                url, error_view_data, access_token=slack_access_token
            )
        except Exception as e:
            return logger.exception(
                f"Failed To Update via command for user  {str(user.id)} email {user.email} {e}"
            )
    blocks = (
        get_block_set(
            "update_modal_block_set",
            context={
                "type": context.get("type"),
                "f": context.get("f"),
                "u": context.get("u"),
                "resource_type": main_form.template.resource,
                "resource_id": main_form.resource_id,
            },
        )
        if type == "command"
        else get_block_set(
            "meeting_review_modal",
            context={
                "w": workflow_id,
                "f": str(workflow.forms.filter(template__form_type="UPDATE").first().id),
                "type": "meeting",
            },
        )
    )
    try:
        stage_name = "StageName" if user.crm == "SALESFORCE" else "dealstage"
        index, block = block_finder(stage_name, blocks)
    except ValueError:
        # did not find the block
        block = None
        pass

    if block:
        block = {
            **block,
            "accessory": {
                **block["accessory"],
                "action_id": f"{slack_const.COMMAND_FORMS__STAGE_SELECTED}?u={str(user.id)}&f={str(main_form.id)}",
            },
        }
        blocks = [*blocks[:index], block, *blocks[index + 1 :]]

    params = [
        f"f={str(main_form.id)}",
        f"product_form={str(product_form.id)}",
        f"type={type}",
    ]
    if main_form.resource_object.secondary_data["Pricebook2Id"]:
        params.append(f"pricebook={main_form.resource_object.secondary_data['Pricebook2Id']}")
    if workflow_id:
        params.append(f"w={workflow_id}")

    if type != "meeting":
        blocks.append(
            block_builders.actions_block(
                [
                    block_builders.simple_button_block(
                        "Add Product",
                        "ADD_PRODUCT",
                        action_id=action_with_params(
                            slack_const.PROCESS_ADD_PRODUCTS_FORM, params=params,
                        ),
                    )
                ],
                block_id="ADD_PRODUCT_BUTTON",
            ),
        )
        try:
            current_products = user.salesforce_account.list_resource_data(
                "OpportunityLineItem",
                0,
                filter=["AND IsDeleted = false", f"AND OpportunityId = '{opp.integration_id}'"],
            )
        except Exception as e:
            logger.exception(
                f"Error retreiving products for user {user.email} during submit product refresh: {e}"
            )
            blocks.append(
                block_builders.simple_section(
                    "There was an error retreiving your products :exclamation:", "mrkdwn"
                )
            )
        if current_products:
            for product in current_products:
                product_block = get_block_set(
                    "current_product_blockset",
                    {
                        "opp_item_id": product.integration_id,
                        "product_data": {
                            "name": product.name,
                            "quantity": product.quantity,
                            "total": product.total_price,
                        },
                        "u": str(user.id),
                        "main_form": str(main_form.id),
                    },
                )
                blocks.append(product_block)
    if type == "meeting":
        external_id = f"meeting_review_modal.{str(uuid.uuid4())}"
        title = "Log Meeting"
        callback_id = slack_const.ZOOM_MEETING__PROCESS_MEETING_SENTIMENT
    else:
        external_id = f"update_modal_block_set.{str(uuid.uuid4())}"
        callback_id = slack_const.COMMAND_FORMS__SUBMIT_FORM
        title = f"Update {main_form.template.resource}"
    data = {
        "view_id": context.get("view_id"),
        "view": {
            "type": "modal",
            "callback_id": callback_id,
            "title": {"type": "plain_text", "text": title},
            "blocks": blocks,
            "private_metadata": json.dumps(pm),
            "external_id": external_id,
        },
    }

    data["view"]["submit"] = {"type": "plain_text", "text": "Submit", "emoji": True}
    slack_requests.generic_request(
        slack_const.SLACK_API_ROOT + slack_const.VIEWS_UPDATE,
        data={
            "view_id": loading_view_data["view_id"],
            "view": {
                "type": "modal",
                "title": {"type": "plain_text", "text": "Product Created"},
                "blocks": [
                    block_builders.simple_section(
                        ":white_check_mark: Successfully created product!", "mrkdwn"
                    )
                ],
            },
        },
        access_token=user.organization.slack_integration.access_token,
    )
    slack_requests.generic_request(
        slack_const.SLACK_API_ROOT + slack_const.VIEWS_UPDATE,
        data,
        access_token=user.organization.slack_integration.access_token,
    )


@log_all_exceptions
@slack_api_exceptions(rethrow=True)
@processor(required_context=["w"])
def process_meeting_convert_lead(payload, context):
    workflow = MeetingWorkflow.objects.get(id=context.get("w"))
    pm = json.loads(payload["view"]["private_metadata"])
    user = workflow.user
    state = payload["view"]["state"]["values"]
    loading_view_data = send_loading_screen(
        user.organization.slack_integration.access_token,
        "Converting your Lead :rocket:",
        "update",
        str(user.id),
        payload["trigger_id"],
        payload["view"]["id"],
    )
    convert_data = {}
    sobjects = ["Opportunity", "Account", "Contact"]
    for object in sobjects:
        if f"{object}_NAME_INPUT" in state:
            if "plain_input" in state[f"{object}_NAME_INPUT"]:
                value = state[f"{object}_NAME_INPUT"]["plain_input"]["value"]
            elif (
                state[f"{object}_NAME_INPUT"][
                    f"GET_SOBJECT_LIST?u={context.get('u')}&resource_type={object}"
                ]["selected_option"]
                is None
            ):
                value = None
            else:
                internal_value = state[f"{object}_NAME_INPUT"][
                    f"GET_SOBJECT_LIST?u={context.get('u')}&resource_type={object}"
                ]["selected_option"]["value"]
                model = model_routes[object]["model"].objects.get(id=internal_value)
                value = model.integration_id
            if value is not None:
                datakey = (
                    f"{object.lower()}Name"
                    if "plain_input" in state[f"{object}_NAME_INPUT"]
                    else f"{object.lower()}Id"
                )
                convert_data[datakey] = value

    convert_data["convertedStatus"] = list(state["Status"].values())[0]["selected_option"]["value"]
    owner_id = list(state["RECORD_OWNER"].values())[0]["selected_option"]["value"]
    assigned_owner = User.objects.get(id=owner_id)
    convert_data["ownerId"] = assigned_owner.salesforce_account.salesforce_id
    lead = Lead.objects.get(id=workflow.resource_id)
    convert_data["leadId"] = lead.integration_id
    attempts = 1
    blocks = None
    has_error = False
    while True:
        try:
            res = lead.convert_in_salesforce(convert_data)
            break
        except FieldValidationError as e:
            has_error = True
            blocks = (
                get_block_set(
                    "error_modal",
                    {
                        "message": f":no_entry: Uh-Ohhh it looks like we found an error, this error is based on Validations set up by your org\n *Error* : _{e}_"
                    },
                ),
            )
            break

        except RequiredFieldError as e:
            has_error = True
            blocks = get_block_set(
                "error_modal",
                {
                    "message": f":no_entry: Uh-Ohhh it looks like we found an error, this error is based on Required fields from Salesforce\n *Error* : _{e}_"
                },
            )
            break
        except UnhandledCRMError as e:
            has_error = True
            blocks = get_block_set(
                "error_modal",
                {
                    "message": f":no_entry: Uh-Ohhh it looks like we found an error, this error is new to us please see below\n *Error* : _{e}_"
                },
            )
            break

        except SFNotFoundError as e:
            has_error = True
            blocks = get_block_set(
                "error_modal",
                {
                    "message": f":no_entry: Uh-Ohhh it looks like we found an error, this error one of the resources does not exist\n *Error* : _{e}_"
                },
            )
            break

        except TokenExpired:
            if attempts >= 5:
                logger.exception(
                    f"Failed to Update data for user {str(user.id)} after {attempts} tries"
                )
                has_error = True
                blocks = get_block_set(
                    "error_modal",
                    {
                        "message": f":no_entry: Uh-Ohhh it looks like we've had an issue with your token\n *Error* : _{e}_"
                    },
                )
                break
            else:
                user.salesforce_account.regenerate_token()
                attempts += 1

        except ConnectionResetError:
            if attempts >= 5:
                logger.exception(
                    f"Failed to Update data for user {str(user.id)} after {attempts} tries because of connection error"
                )
                has_error = True
                blocks = get_block_set(
                    "error_modal",
                    {
                        "message": f":no_entry: Uh-Ohhh we had an error connecting to your salesforce instance please try again"
                    },
                )
                break
            else:
                time.sleep(2)
                attempts += 1
        except Exception as e:
            if attempts >= 5:
                has_error = True
                logger.exception(f"CONVERT LEAD EXCEPTION: {e}")
                blocks = [
                    block_builders.simple_section(
                        f":exclamation: There was an error converting your lead", "mrkdwn",
                    )
                ]
                break
            else:
                time.sleep(2)
                attempts += 1

    if has_error:
        return {
            "response_action": "update",
            "view": {
                "type": "modal",
                "title": {"type": "plain_text", "text": "Lead Convert Failed"},
                "blocks": blocks,
            },
        }
    if res["success"]:
        success_data = {
            "view_id": loading_view_data["view"]["id"],
            "view": {
                "type": "modal",
                "title": {"type": "plain_text", "text": "Lead Converted"},
                "blocks": [
                    block_builders.simple_section(
                        ":white_check_mark: Your Lead was successfully converted :clap:", "mrkdwn",
                    )
                ],
            },
        }
        success_res = slack_requests.generic_request(
            slack_const.SLACK_API_ROOT + slack_const.VIEWS_UPDATE,
            success_data,
            access_token=user.organization.slack_integration.access_token,
        )
        update_blocks = [
            block_builders.section_with_button_block(
                "Send Recap",
                "SEND_RECAP",
                f":white_check_mark: Successfully converted your Lead {lead.name}",
                action_id=action_with_params(
                    slack_const.PROCESS_SEND_RECAP_MODAL,
                    params=[
                        f"u={str(workflow.user.id)}",
                        f"workflow_id={str(workflow.id)}",
                        f"account={res['Account']}",
                        f"opportunity={res['Opportunity']}",
                        f"contact={res['Contact']}",
                    ],
                ),
            )
        ]
        slack_requests.update_channel_message(
            pm.get("original_message_channel"),
            pm.get("original_message_timestamp"),
            access_token=user.organization.slack_integration.access_token,
            block_set=update_blocks,
        )
    else:
        error = res["error"]
        return {
            "response_action": "update",
            "view": {
                "type": "modal",
                "title": {"type": "plain_text", "text": "Lead Convert Failed"},
                "blocks": [
                    block_builders.simple_section(
                        f":exclamation: There was an error converting your lead:\n{error}",
                        "mrkdwn",
                    )
                ],
            },
        }


@log_all_exceptions
@slack_api_exceptions(rethrow=True)
@processor(required_context=["resource_id"])
def process_convert_lead(payload, context):
    emit_process_convert_lead(payload, context)
    return {"response_action": "clear"}


@processor(required_context=["f"])
def process_submit_alert_resource_data(payload, context):
    # get context
    has_error = False
    state = swap_public_fields(payload["view"]["state"]["values"])
    current_form_ids = context.get("f").split(",")
    user = User.objects.get(id=context.get("u"))
    trigger_id = payload["trigger_id"]
    view_id = payload["view"]["id"]
    alert_id = context.get("alert_id", None)
    alert = AlertInstance.objects.filter(id=alert_id).first()
    external_id = payload.get("view", {}).get("external_id", None)
    try:
        view_type, __unique_id = external_id.split(".")
    except ValueError:
        view_type = external_id
        pass
    current_forms = user.custom_slack_form_instances.filter(id__in=current_form_ids)
    main_form = current_forms.filter(template__form_type__in=["UPDATE"]).first()
    stage_forms = current_forms.filter(
        template__form_type="STAGE_GATING", template__custom_object__isnull=True
    )
    custom_object_forms = current_forms.filter(
        template__form_type="STAGE_GATING", template__custom_object__isnull=False
    )
    stage_form_data_collector = {}
    for form in stage_forms:
        form.save_form(state)
        stage_form_data_collector = {**stage_form_data_collector, **form.saved_data}
    custom_object_data_collector = {}
    for custom_form in custom_object_forms:
        custom_form.save_form(state)
        custom_object_data_collector = {**custom_object_data_collector, **custom_form.saved_data}
    if not len(stage_forms):
        main_form.save_form(state)
    all_form_data = {**stage_form_data_collector, **main_form.saved_data}
    slack_access_token = user.organization.slack_integration.access_token
    url = slack_const.SLACK_API_ROOT + slack_const.VIEWS_UPDATE
    loading_view_data = send_loading_screen(
        slack_access_token,
        ":exclamation: Please wait a few seconds :zany_face:, then click '*try again*'",
        "update",
        str(user.id),
        trigger_id,
        view_id,
    )
    attempts = 1
    while True:
        crm = user.crm_account
        try:
            resource = main_form.resource_object.update(all_form_data)
            data = {
                "view_id": loading_view_data["view"]["id"],
                "view": {
                    "type": "modal",
                    "title": {"type": "plain_text", "text": "Success"},
                    "blocks": [
                        block_builders.simple_section(
                            f":white_check_mark: Successfully updated {main_form.resource_type} :clap:",
                            "mrkdwn",
                        ),
                        block_builders.context_block(
                            "*Disregard the red banner message, you can safely Close this window."
                        ),
                    ],
                },
            }

            slack_requests.generic_request(
                slack_const.SLACK_API_ROOT + slack_const.VIEWS_UPDATE,
                data,
                access_token=user.organization.slack_integration.access_token,
            )
            all_form_data.update(resource)
            break
        except FieldValidationError as e:
            has_error = True
            blocks = get_block_set(
                "error_modal",
                {
                    "message": f":no_entry: Uh-Ohhh it looks like we found an error, this error is based on Validations set up by your org\n *Error* : _{e}_"
                },
            )
            break

        except RequiredFieldError as e:
            has_error = True
            blocks = get_block_set(
                "error_modal",
                {
                    "message": f":no_entry: Uh-Ohhh it looks like we found an error, this error is based on Required fields from Salesforce\n *Error* : _{e}_"
                },
            )
            break
        except UnhandledCRMError as e:
            has_error = True
            blocks = get_block_set(
                "error_modal",
                {
                    "message": f":no_entry: Uh-Ohhh it looks like we found an error, this error is new to us please see below\n *Error* : _{e}_"
                },
            )
            break

        except SFNotFoundError as e:
            has_error = True
            blocks = get_block_set(
                "error_modal",
                {
                    "message": f":no_entry: Uh-Ohhh it looks like we found an error, this error one of the resources does not exist\n *Error* : _{e}_"
                },
            )
            break

        except TokenExpired:
            if attempts >= 5:
                logger.exception(
                    f"Failed to Update data for user {str(user.id)} after {attempts} tries"
                )
                has_error = True
                blocks = get_block_set(
                    "error_modal",
                    {
                        "message": f":no_entry: Uh-Ohhh it looks like we've had an issue with your token\n *Error* : _{e}_"
                    },
                )
                break
            else:
                if main_form.resource_object.owner == user:
                    sf.regenerate_token()
                else:
                    main_form.resource_object.owner.salesforce_account.regenerate_token()
                attempts += 1

        except ConnectionResetError:
            if attempts >= 5:
                logger.exception(
                    f"Failed to Update data for user {str(user.id)} after {attempts} tries because of connection error"
                )
                has_error = True
                blocks = get_block_set(
                    "error_modal",
                    {
                        "message": f":no_entry: Uh-Ohhh we had an error connecting to your salesforce instance please try again"
                    },
                )
                break
            else:
                time.sleep(2)
                attempts += 1

        except Exception as e:
            logger.exception(f"Uncaught Error {e}")
            has_error = True
            blocks = get_block_set(
                "error_modal",
                {
                    "message": f":no_entry: Uh-Ohhh it looks like we found an error, this error is new to us please see below\n *Error* : _{e}_"
                },
            )
            break

    if has_error:
        form_id = str(main_form.id) if not len(stage_forms) else str(stage_forms.first().id)
        # if not len(stage_forms):
        # add a special button to return the user back to edit their form
        # this is only required for single page forms
        blocks = [
            *blocks,
            block_builders.actions_block(
                [
                    block_builders.simple_button_block(
                        "return to form",
                        form_id,
                        style="primary",
                        action_id=slack_const.RETURN_TO_FORM_MODAL,
                    )
                ]
            ),
        ]

        new_context = {**context, "type": "alert"}
        url = slack_const.SLACK_API_ROOT + slack_const.VIEWS_UPDATE
        error_view_data = {
            "view_id": loading_view_data["view"]["id"],
            "view": {
                "type": "modal",
                "title": {"type": "plain_text", "text": "Error"},
                "blocks": blocks,
                "private_metadata": json.dumps(new_context),
                "external_id": f"{view_type}.{str(uuid.uuid4())}",
            },
        }
        try:
            return slack_requests.generic_request(
                url, error_view_data, access_token=slack_access_token
            )
        except Exception as e:
            return logger.exception(
                f"Failed To Update via command for user  {str(user.id)} email {user.email} {e}"
            )
    current_forms.update(is_submitted=True, update_source="alert", submission_date=timezone.now())
    if (
        all_form_data.get("meeting_comments") is not None
        or all_form_data.get("meeting_type") is not None
    ):
        if user.crm == "SALESFORCE":
            emit_add_update_to_sf(str(main_form.id))
        else:
            emit_add_update_to_hs(str(main_form.id))
    if len(user.slack_integration.realtime_alert_configs):
        _send_instant_alert(current_form_ids)
    # user.activity.add_workflow_activity(str(main_form.id), alert.template.title)
    emit_update_slack_message(context, str(main_form.id))
    main_form.resource_object.update_database_values(all_form_data)
    return {"response_action": "clear"}


@log_all_exceptions
@slack_api_exceptions(rethrow=True)
@processor(required_context=["u"])
def process_submit_bulk_update(payload, context):
    user = User.objects.get(id=context.get("u"))
    state = payload["view"]["state"]["values"]
    pm = json.loads(payload["view"]["private_metadata"])
    selected_resources = [
        option["value"] for option in state["RESOURCES"]["SELECTED_RESOURCES"]["selected_options"]
    ]
    channel = pm.get("channel_id")
    ts = pm.get("message_ts")
    resource_type = context.get("resource_type")
    BULK_UPDATE_FUNCTION(user.crm)(
        str(user.id), selected_resources, state, ts, channel, resource_type
    )

    block_set = [
        *get_block_set(
            "loading",
            {
                "message": f":rocket: We are saving your data to {'Salesforce' if user.crm == 'SALESFORCE' else 'HubSpot'}..."
            },
        ),
    ]
    try:
        res = slack_requests.update_channel_message(
            channel, ts, user.organization.slack_integration.access_token, block_set=block_set
        )
    except Exception as e:
        logger.exception(f"Failed To Bulk Update Salesforce Data {e}")
        return {"response_action": "clear"}
    return {"response_action": "clear"}


def create_summary_object(api_names, resources, resource_type):
    object = {}
    if resource_type in ["Opportunity", "Deal"]:
        amounts = [(resource.amount if resource.amount else 0) for resource in resources]
        amount_api = "Amount" if resource_type == "Opportunity" else "amount"
        object[amount_api] = round(sum(amounts), 2)
    for resource in resources:
        for api_name in api_names:
            value = resource.secondary_data[api_name]
            if api_name in object.keys():
                if value in object[api_name].keys():
                    object[api_name][value].append(resource.name)
                else:
                    object[api_name][value] = [resource.name]
            else:
                object[api_name] = {}
                object[api_name][value] = [resource.name]
    return object


@log_all_exceptions
@slack_api_exceptions(rethrow=True)
@processor(required_context=["u"])
def process_get_summary(payload, context):
    u = User.objects.get(id=context.get("u"))
    pm = json.loads(payload["view"]["private_metadata"])
    config = AlertConfig.objects.get(id=context.get("config_id"))
    instances = list(
        AlertInstance.objects.filter(
            config_id=config.id, invocation=pm.get("invocation")
        ).values_list("resource_id", flat=True)
    )
    values = payload["view"]["state"]["values"]["CRM_FIELDS"][
        f"CHOOSE_CRM_FIELDS?u={context.get('u')}"
    ]["selected_options"]
    value_list = [option["value"] for option in values]
    api_name_obj = {}
    for value in values:
        api_name_obj[value["value"]] = value["text"]["text"]
    resources = CRM_SWITCHER[u.crm][config.template.resource_type]["model"].objects.filter(
        id__in=instances
    )
    summary_object = create_summary_object(value_list, resources, config.template.resource_type)

    blocks = [
        block_builders.header_block(
            f"Workflow Summary for {len(instances)} {config.template.title}"
        ),
        {"type": "divider"},
    ]
    if config.template.resource_type == "Opportunity":
        summary_amount = f"*Total Amount:* ${'{:,}'.format(summary_object['Amount'])}"
        blocks.insert(1, block_builders.simple_section(summary_amount, "mrkdwn"))
        summary_object.pop("Amount")
    if config.template.resource_type == "Deal":
        summary_amount = f"*Total Amount:* ${'{:,}'.format(summary_object['amount'])}"
        blocks.insert(1, block_builders.simple_section(summary_amount, "mrkdwn"))
        summary_object.pop("amount")
    summary_text = ""
    for field in summary_object.keys():
        summary_text += f"\n\n*{api_name_obj[field]}:*\n"
        for key in summary_object[field]:
            summary_text += f"\n\t*{len(summary_object[field][key])} - {key}* ({', '.join(summary_object[field][key])})"
        blocks.append(block_builders.simple_section(summary_text, "mrkdwn"))
        blocks.append({"type": "divider"})
        summary_text = ""
    return {
        "response_action": "update",
        "view": {
            "type": "modal",
            "title": {"type": "plain_text", "text": "Workflow Summary"},
            "blocks": blocks,
        },
    }


@log_all_exceptions
@slack_api_exceptions(rethrow=True)
@processor(required_context=["u"])
def process_submit_chat_prompt(payload, context):
    user = User.objects.get(id=context.get("u"))
    resource_list = (
        ["Opportunity", "Account", "Contact", "Lead"]
        if user.crm == "SALESFORCE"
        else ["Deal", "Company", "Contact"]
    )
    state = payload["view"]["state"]
    task_selection = [
        value.get("selected_option")
        for value in state["values"].get("managr_task_type", {}).values()
    ]
    task_type = (
        task_selection[0].get("value") if (len(task_selection) and task_selection[0]) else None
    )
    context.update(task_type=task_type)
    prompt = state["values"]["CHAT_PROMPT"]["plain_input"]["value"]
    resource_check = None
    lowercase_prompt = prompt.lower()
    for resource in resource_list:
        lowered_resource = resource.lower()
        if lowered_resource in lowercase_prompt:
            resource_check = resource
            break
    block_set = [
        *get_block_set(
            "loading",
            {
                "message": f":rocket: We are saving your data to {'Salesforce' if user.crm == 'SALESFORCE' else 'HubSpot'}..."
            },
        ),
    ]
    try:
        if "w" in context.keys():
            workflow = MeetingWorkflow.objects.get(id=context.get("w"))
            workflow.operations_list = [slack_const.MEETING___SUBMIT_CHAT_PROMPT]
            workflow.operations = [slack_const.MEETING___SUBMIT_CHAT_PROMPT]
            workflow.save()
            emit_process_calendar_meetings(
                str(user.id),
                f"calendar-meetings-{user.email}-{str(uuid.uuid4())}",
                workflow.slack_interaction,
                date=str(workflow.datetime_created.date()),
            )
            emit_meeting_workflow_tracker(str(workflow.id))
        else:
            ts = context.get("ts", None)
            channel = context.get("channel", None)
            if ts and channel:
                res = slack_requests.update_channel_message(
                    channel,
                    ts,
                    user.organization.slack_integration.access_token,
                    block_set=block_set,
                )
            else:
                res = slack_requests.send_channel_message(
                    user.slack_integration.channel,
                    user.organization.slack_integration.access_token,
                    block_set=block_set,
                )
            context.update(channel=res["channel"], ts=res["ts"])
        if resource_check:
            emit_process_submit_chat_prompt(
                context.get("u"), prompt, resource_check, context,
            )
        else:
            res = slack_requests.update_channel_message(
                res["channel"],
                res["ts"],
                user.organization.slack_integration.access_token,
                block_set=[
                    block_builders.simple_section(
                        f":no_entry_sign: Invalid submission: Please include an object type like {'Opportunity' if user.crm == 'SALESFORCE' else 'Deal'} and try again.\n '{prompt}'",
                        "mrkdwn",
                    )
                ],
            )
    except Exception as e:
        logger.exception(f"Failed submit chat data {e}")
        return {"response_action": "clear"}
    return {"response_action": "clear"}


@processor()
def process_send_recap_modal(payload, context):
    url = slack_const.SLACK_API_ROOT + slack_const.VIEWS_UPDATE
    user = User.objects.get(id=context.get("u"))
    access_token = user.organization.slack_integration.access_token
    view_id = context.get("view_id")
    data = {
        "view_id": view_id,
        "view": {
            "type": "modal",
            "callback_id": slack_const.PROCESS_SEND_RECAPS,
            "title": {"type": "plain_text", "text": f"{'Send Summary'}",},
            "blocks": get_block_set("send_recap_block_set", {"u": context.get("u")}),
            "submit": {"type": "plain_text", "text": "Send"},
            "private_metadata": json.dumps(context),
        },
    }
    try:
        res = slack_requests.generic_request(url, data, access_token=access_token)
        return
    except InvalidBlocksException as e:
        logger.exception(f"Failed To Send Recap for user {user.email} because of: {e}")
    except InvalidBlocksFormatException as e:
        logger.exception(f"Failed To Send Recap for user {user.email} because of: {e}")
    except UnHandeledBlocksException as e:
        logger.exception(f"Failed To Send Recap for user {user.email} because of: {e}")
    except InvalidAccessToken as e:
        logger.exception(
            f"Failed To Generate Slack Workflow Interaction for user with workflow {str(user.id)} email {user.email} {e}"
        )
    except Exception as e:
        logger.exception(f"Failed to open recap modal due to {e}")
        data["view"]["blocks"] = block_builders.simple_section(
            f"An Error occured gathering your users and channels:\n{e}", "mrkdwn"
        )
    res = slack_requests.generic_request(url, data, access_token=access_token)
    return


GENERATIVE_ACTION_SWITCHER = {
    "DRAFT_EMAIL": emit_process_send_email_draft,
    "SEND_SUMMARY": emit_process_send_summary_to_dm,
    "NEXT_STEPS": emit_process_send_next_steps,
}


def process_selected_generative_action(payload, context):
    user = User.objects.get(id=context.get("u"))
    pm = json.loads(payload.get("view").get("private_metadata"))
    generative_action_values = payload["view"]["state"]["values"]["GENERATIVE_ACTION"]
    action = generative_action_values.get(list(generative_action_values.keys())[0])[
        "selected_option"
    ]["value"]
    action_func = GENERATIVE_ACTION_SWITCHER[action]
    loading_block = [*get_block_set("loading", {"message": "Generating content..."})]
    try:
        res = slack_requests.send_channel_message(
            user.slack_integration.channel,
            user.organization.slack_integration.access_token,
            block_set=loading_block,
        )
        pm.update(ts=res["ts"])
        action_res = action_func(payload, pm)
    except Exception as e:
        logger.exception(e)
    return {"response_action": "clear"}


def process_chat_action_submit(payload, context):
    user = User.objects.get(id=context.get("u"))
    try:
        res = slack_requests.send_channel_message(
            user.slack_integration.channel,
            user.organization.slack_integration.access_token,
            block_set=get_block_set("loading", {"message": "Processing your action submission..."}),
        )
    except Exception as e:
        logger.exception(f"Failed to send DM to {user.email} because of <{e}>")
    context.update(ts=res["ts"])
    emit_process_chat_action(payload, context)
    return {"response_action": "clear"}


def handle_view_submission(payload):
    """
    This takes place when a modal's Submit button is clicked.
    """
    switcher = {
        slack_const.ZOOM_MEETING__SELECTED_RESOURCE: process_zoom_meeting_attach_resource,
        slack_const.ZOOM_MEETING__PROCESS_MEETING_SENTIMENT: process_zoom_meeting_data,
        slack_const.ZOOM_MEETING__EDIT_CONTACT: process_edit_meeting_contact,
        slack_const.ZOOM_MEETING__PROCESS_STAGE_NEXT_PAGE: process_stage_next_page,
        slack_const.ZOOM_MEETING__UPDATE_PARTICIPANT_DATA: process_update_meeting_contact,
        slack_const.ZOOM_MEETING__SAVE_CONTACTS: process_save_contact_data,
        slack_const.COMMAND_FORMS__SUBMIT_FORM: process_submit_resource_data,
        slack_const.COMMAND_FORMS__PROCESS_NEXT_PAGE: process_next_page_slack_commands_form,
        slack_const.ALERT_INLINE_STAGE_SUBMITTED: process_alert_inline_stage_submitted,
        slack_const.PROCESS_SUBMIT_ALERT_RESOURCE_DATA: process_submit_alert_resource_data,
        slack_const.COMMAND_CREATE_TASK: process_create_task,
        slack_const.COMMAND_CREATE_EVENT: process_create_event,
        slack_const.ZOOM_MEETING__SCHEDULE_MEETING: process_schedule_meeting,
        slack_const.ADD_TO_CADENCE: process_add_contacts_to_cadence,
        slack_const.ADD_TO_SEQUENCE: process_add_contacts_to_sequence,
        slack_const.GET_NOTES: process_get_notes,
        slack_const.PROCESS_SEND_RECAPS: process_send_recaps,
        slack_const.PROCESS_ADD_PRODUCTS_FORM: process_add_products_form,
        slack_const.PROCESS_UPDATE_PRODUCT: process_update_product,
        slack_const.PROCESS_SUBMIT_PRODUCT: process_submit_product,
        slack_const.ZOOM_MEETING__CONVERT_LEAD: process_meeting_convert_lead,
        slack_const.COMMAND_FORMS__CONVERT_LEAD: process_convert_lead,
        slack_const.PROCESS_SUBMIT_BULK_UPDATE: process_submit_bulk_update,
        slack_const.GET_SUMMARY: process_get_summary,
        slack_const.SUBMIT_CUSTOM_OBJECT_DATA: process_submit_custom_object,
        slack_const.COMMAND_FORMS__SUBMIT_CHAT: process_submit_chat_prompt,
        slack_const.MEETING___SUBMIT_CHAT_PROMPT: process_submit_chat_prompt,
        slack_const.PROCESS_SELECTED_GENERATIVE_ACTION: process_selected_generative_action,
        slack_const.PROCESS_CHAT_ACTION: process_chat_action_submit,
    }

    callback_id = payload["view"]["callback_id"]
    view_context = json.loads(payload["view"]["private_metadata"])
    return switcher.get(callback_id, NO_OP)(payload, view_context)
