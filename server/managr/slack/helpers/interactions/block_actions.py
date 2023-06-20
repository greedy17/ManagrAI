import json
import uuid
import logging
import pytz
from django.db.models import Q
from django.utils import timezone
from datetime import datetime, date
from managr.organization.models import Organization, Pricebook2, PricebookEntry
from managr.slack import constants as slack_const
from managr.slack.helpers import requests as slack_requests
from managr.slack.helpers.utils import (
    process_action_id,
    NO_OP,
    processor,
    block_finder,
    generate_call_block,
    check_contact_last_name,
    action_with_params,
    send_loading_screen,
    USER_APP_OPTIONS,
)
from managr.slack.helpers.block_sets import get_block_set
from managr.slack.helpers import block_builders
from managr.slack.helpers.interactions.commands import get_action
from managr.slack.models import OrgCustomSlackFormInstance, UserSlackIntegration, OrgCustomSlackForm
from managr.slack.background import (
    emit_send_paginated_alerts,
    emit_send_paginated_inline_alerts,
    emit_send_next_page_paginated_inline_alerts,
    emit_send_paginated_notes,
    emit_process_paginated_engagement_state,
    emit_process_paginated_call_recordings,
    emit_process_paginated_engagement_details,
    emit_process_paginate_deal_reviews,
    emit_process_alert_send_deal_review,
)
from managr.salesforce.models import MeetingWorkflow
from managr.core.models import User
from managr.core.background import (
    emit_process_calendar_meetings,
    emit_process_send_email_draft,
    emit_process_send_next_steps,
    emit_process_send_call_analysis_to_dm,
    emit_process_send_regenerate_email_message,
)
from managr.core.utils import get_summary_completion
from managr.salesforce.background import (
    replace_tags,
    emit_process_slack_inline_sf_update,
)
from managr.hubspot.tasks import emit_process_slack_inline_hs_update
from managr.slack.helpers.exceptions import (
    UnHandeledBlocksException,
    InvalidBlocksFormatException,
    InvalidBlocksException,
    InvalidAccessToken,
)
from managr.api.decorators import slack_api_exceptions
from managr.alerts.models import AlertTemplate, AlertInstance, AlertConfig
from managr.gong.models import GongCall, GongAuthAccount
from managr.gong import exceptions as gong_exceptions
from managr.crm.models import ObjectField
from managr.salesforce.routes import routes as sf_routes
from managr.hubspot.routes import routes as hs_routes
from managr.outreach.exceptions import TokenExpired as OutreachTokenExpired
from managr.zoom.background import emit_process_get_transcript_and_update_crm

CRM_SWITCHER = {"SALESFORCE": sf_routes, "HUBSPOT": hs_routes}
logger = logging.getLogger("managr")


def INLINE_UPDATE_FUNCTION(crm):
    if crm == "SALESFORCE":
        return emit_process_slack_inline_sf_update
    else:
        return emit_process_slack_inline_hs_update


#########################################################
# MEETING REVIEW ACTIONS
#########################################################
@processor()
def show_initial_meeting_interaction(payload, context):
    workflow = MeetingWorkflow.objects.get(id=context.get("w"))
    user = workflow.user
    access_token = user.organization.slack_integration.access_token
    ts, channel = workflow.slack_interaction.split("|")
    try:
        res = slack_requests.update_channel_message(
            channel,
            ts,
            access_token,
            block_set=get_block_set(
                "initial_meeting_interaction", context={"w": str(workflow.id)},
            ),
        )
    except InvalidBlocksException as e:
        return logger.exception(
            f"Failed To Generate Slack Workflow Interaction for user with workflow {str(workflow.id)} email {workflow.user.email} {e}"
        )
    except InvalidBlocksFormatException as e:
        return logger.exception(
            f"Failed To Generate Slack Workflow Interaction for user with workflow {str(workflow.id)} email {workflow.user.email} {e}"
        )
    except UnHandeledBlocksException as e:
        return logger.exception(
            f"Failed To Generate Slack Workflow Interaction for user with workflow {str(workflow.id)} email {workflow.user.email} {e}"
        )
    except InvalidAccessToken as e:
        return logger.exception(
            f"Failed To Generate Slack Workflow Interaction for user with workflow {str(workflow.id)} email {workflow.user.email} {e}"
        )
    return


@processor()
def process_meeting_review(payload, context):
    trigger_id = payload["trigger_id"]
    workflow_id = context.get("w")
    workflow = MeetingWorkflow.objects.get(id=workflow_id)
    main_form = workflow.forms.filter(template__form_type__in=["CREATE", "UPDATE"]).first()
    organization = workflow.user.organization
    access_token = organization.slack_integration.access_token
    crm = "Salesforce" if workflow.user.crm == "SALESFORCE" else "HubSpot"
    loading_view_data = send_loading_screen(
        access_token,
        f"{crm} is being a bit slow :sleeping:… please give it a few seconds",
        "open",
        str(workflow.user.id),
        trigger_id,
    )
    context = {
        "w": workflow_id,
        "type": "meeting",
    }
    stage_form_check = workflow.forms.filter(template__form_type=slack_const.FORM_TYPE_STAGE_GATING)
    if len(stage_form_check):
        callback_id = slack_const.ZOOM_MEETING__PROCESS_STAGE_NEXT_PAGE
        submit_text = "Next"
        context["form_type"] = main_form.template.form_type
    else:
        callback_id = slack_const.ZOOM_MEETING__PROCESS_MEETING_SENTIMENT
        submit_text = "Submit"
    data = {
        "view_id": loading_view_data["view"]["id"],
        "view": {
            "type": "modal",
            "callback_id": callback_id,
            "title": {"type": "plain_text", "text": "Log Meeting"},
            "blocks": get_block_set("meeting_review_modal", context=context),
            "submit": {"type": "plain_text", "text": submit_text},
            "private_metadata": json.dumps(context),
            "external_id": f"meeting_review_modal.{str(uuid.uuid4())}",
        },
    }
    try:
        res = slack_requests.generic_request(
            slack_const.SLACK_API_ROOT + slack_const.VIEWS_UPDATE, data, access_token=access_token
        )
    except InvalidBlocksException as e:
        return logger.exception(
            f"Failed To Generate Slack Workflow Interaction for user with workflow {str(workflow.id)} email {workflow.user.email} {e}"
        )
    except InvalidBlocksFormatException as e:
        return logger.exception(
            f"Failed To Generate Slack Workflow Interaction for user with workflow {str(workflow.id)} email {workflow.user.email} {e}"
        )
    except UnHandeledBlocksException as e:
        return logger.exception(
            f"Failed To Generate Slack Workflow Interaction for user with workflow {str(workflow.id)} email {workflow.user.email} {e}"
        )
    except InvalidAccessToken as e:
        return logger.exception(
            f"Failed To Generate Slack Workflow Interaction for user with workflow {str(workflow.user.id)} email {workflow.user.email} {e}"
        )
    view_id = res["view"]["id"]
    workflow.slack_view = view_id
    workflow.save()


@processor(required_context=["w"], action=slack_const.VIEWS_OPEN)
def process_show_meeting_contacts(payload, context, action=slack_const.VIEWS_OPEN):
    view_id = payload["view"]["id"] if action == slack_const.VIEWS_UPDATE else None
    view_type = "open" if action == slack_const.VIEWS_OPEN else "push"
    type = context.get("type", None)
    trigger_id = payload["trigger_id"]
    workflow = MeetingWorkflow.objects.get(id=context.get("w"))
    org = workflow.user.organization
    access_token = org.slack_integration.access_token
    refresh = context.get("tracking_id", None)
    if refresh is None:
        loading_view_data = send_loading_screen(
            access_token,
            "Gathering attendee info...",
            view_type,
            str(workflow.user.id),
            trigger_id,
            view_id,
        )
    private_metadata = {
        "original_message_channel": payload["channel"]["id"]
        if "channel" in payload
        else context.get("original_message_channel"),
        "original_message_timestamp": payload["message"]["ts"]
        if "message" in payload
        else context.get("original_message_channel"),
    }
    private_metadata.update(context)
    blocks = get_block_set("show_meeting_contacts", private_metadata)
    view_id = loading_view_data["view"]["id"] if refresh is None else payload["view"]["id"]
    data = {
        "view_id": view_id,
        "view": {
            "type": "modal",
            "title": {"type": "plain_text", "text": "Contacts"},
            "blocks": blocks,
            "private_metadata": json.dumps(private_metadata),
        },
    }
    try:
        res = slack_requests.generic_request(
            slack_const.SLACK_API_ROOT + slack_const.VIEWS_UPDATE, data, access_token=access_token
        )
    except InvalidBlocksException as e:
        return logger.exception(
            f"Failed To Generate Slack Workflow Interaction for user with workflow {str(workflow.id)} email {workflow.user.email} {e}"
        )
    except InvalidBlocksFormatException as e:
        return logger.exception(
            f"Failed To Generate Slack Workflow Interaction for user with workflow {str(workflow.id)} email {workflow.user.email} {e}"
        )
    except UnHandeledBlocksException as e:
        return logger.exception(
            f"Failed To Generate Slack Workflow Interaction for user with workflow {str(workflow.id)} email {workflow.user.email} {e}"
        )
    except InvalidAccessToken as e:
        return logger.exception(
            f"Failed To Generate Slack Workflow Interaction for user with workflow {str(workflow.id)} email {workflow.user.email} {e}"
        )
    except Exception as e:
        return logger.exception(f"Failed to send message for {e}")
    if not type:
        workflow.slack_view = res.get("view").get("id")
        workflow.save()


@processor()
def process_edit_meeting_contact(payload, context):
    trigger_id = payload["trigger_id"]
    view = payload["view"]
    view_id = view["id"]
    type = context.get("type", None)
    workflow = MeetingWorkflow.objects.get(id=context.get("w"))
    org = workflow.user.organization
    access_token = org.slack_integration.access_token
    loading_view_data = send_loading_screen(
        access_token,
        "Gathering current attendee values...",
        "push",
        str(workflow.user.id),
        trigger_id,
        view_id,
    )
    edit_block_context = {
        "w": context.get("w"),
        "tracking_id": context.get("tracking_id"),
        "current_view_id": view_id,
    }
    private_metadata = {
        "w": context.get("w"),
        "tracking_id": context.get("tracking_id"),
        "current_view_id": view_id,
        "original_message_channel": context.get("original_message_channel"),
        "original_message_timestamp": context.get("original_message_timestamp"),
    }
    if type:
        edit_block_context.update({"type": type})
        private_metadata.update({"type": type})
    data = {
        "view_id": loading_view_data["view"]["id"],
        "view": {
            "type": "modal",
            "title": {"type": "plain_text", "text": "Edit Contact"},
            "submit": {"type": "plain_text", "text": "Save"},
            "blocks": get_block_set("edit_meeting_contacts", edit_block_context),
            "callback_id": slack_const.ZOOM_MEETING__UPDATE_PARTICIPANT_DATA,
            "private_metadata": json.dumps(private_metadata),
        },
    }
    url = slack_const.SLACK_API_ROOT + slack_const.VIEWS_UPDATE
    try:
        res = slack_requests.generic_request(url, data, access_token=access_token)
    except InvalidBlocksException as e:
        return logger.exception(
            f"Failed To Generate Slack Workflow Interaction for user  with workflow {str(workflow.id)} email {workflow.user.email} {e}"
        )
    except InvalidBlocksFormatException as e:
        return logger.exception(
            f"Failed To Generate Slack Workflow Interaction for user  with workflow {str(workflow.id)} email {workflow.user.email} {e}"
        )
    except UnHandeledBlocksException as e:
        return logger.exception(
            f"Failed To Generate Slack Workflow Interaction for user  with workflow {str(workflow.id)} email {workflow.user.email} {e}"
        )
    except InvalidAccessToken as e:
        return logger.exception(
            f"Failed To Generate Slack Workflow Interaction for user  with workflow {str(workflow.id)} email {workflow.user.email} {e}"
        )
    # workflow.slack_view = res["view"]["id"]
    # workflow.save()


@processor(required_context=[])
def process_stage_selected(payload, context):
    url = slack_const.SLACK_API_ROOT + slack_const.VIEWS_UPDATE
    workflow = MeetingWorkflow.objects.filter(id=context.get("w")).first()
    user = workflow.user
    org = user.organization
    access_token = org.slack_integration.access_token
    trigger_id = payload["trigger_id"]
    view_id = payload["view"]["id"]
    private_metadata = json.loads(payload["view"]["private_metadata"])
    if len(payload["actions"]):
        action = payload["actions"][0]
        blocks = payload["view"]["blocks"]
        selected_value = (
            action["selected_option"]["value"]
            if user.crm == "SALESFORCE"
            else action["selected_option"]["text"]["text"]
        )
        # delete all existing stage forms
        workflow.forms.filter(template__form_type=slack_const.FORM_TYPE_STAGE_GATING).delete()
        stage_form = (
            org.custom_slack_forms.for_user(user)
            .filter(form_type=slack_const.FORM_TYPE_STAGE_GATING, stage=selected_value)
            .first()
        )
        if stage_form:
            resource = (
                slack_const.FORM_RESOURCE_OPPORTUNITY
                if user.crm == "SALESFORCE"
                else slack_const.FORM_RESOURCE_DEAL
            )
            workflow.add_form(
                resource, slack_const.FORM_TYPE_STAGE_GATING, stage=selected_value,
            )
        # gather and attach all forms

    external_id = payload.get("view", {}).get("external_id", None)
    try:
        view_type, __unique_id = external_id.split(".")
    except ValueError:
        pass
    if not stage_form:
        submit_text = "Submit"
        if view_type == "create_modal_block_set":
            callback_id = callback_id = (
                slack_const.ZOOM_MEETING__PROCESS_MEETING_SENTIMENT
                if workflow
                else slack_const.COMMAND_FORMS__SUBMIT_FORM
            )
        elif view_type == "update_alert_modal_block_set":
            callback_id = slack_const.PROCESS_SUBMIT_ALERT_RESOURCE_DATA
        else:
            submit_text = "Submit"
            callback_id = slack_const.ZOOM_MEETING__PROCESS_MEETING_SENTIMENT
    else:
        submit_text = "Next"
        callback_id = slack_const.ZOOM_MEETING__PROCESS_STAGE_NEXT_PAGE
        if view_type == "meeting_review_modal":
            context = {
                **context,
                "form_type": slack_const.FORM_TYPE_UPDATE,
                "callback_id": slack_const.ZOOM_MEETING__PROCESS_MEETING_SENTIMENT,
            }
        else:
            call_id = (
                slack_const.ZOOM_MEETING__PROCESS_MEETING_SENTIMENT
                if workflow
                else slack_const.COMMAND_FORMS__SUBMIT_FORM
            )
            context = {
                **context,
                "form_type": slack_const.FORM_TYPE_CREATE,
                "callback_id": call_id,
            }
    private_metadata.update(context)
    data = {
        "trigger_id": trigger_id,
        "view_id": view_id,
        "view": {
            "type": "modal",
            "callback_id": callback_id,
            "title": {"type": "plain_text", "text": payload["view"]["title"]["text"]},
            "blocks": blocks,
            "submit": {"type": "plain_text", "text": submit_text},
            "private_metadata": json.dumps(private_metadata),
            "external_id": f"{view_type}.{__unique_id}",
        },
    }
    try:
        res = slack_requests.generic_request(url, data, access_token=access_token)
    except InvalidBlocksException as e:
        return logger.exception(
            f"Failed To Generate Slack Workflow Interaction for user  with workflow {str(workflow.id)} email {workflow.user.email} {e}"
        )
    except InvalidBlocksFormatException as e:
        return logger.exception(
            f"Failed To Generate Slack Workflow Interaction for user  with workflow {str(workflow.id)} email {workflow.user.email} {e}"
        )
    except UnHandeledBlocksException as e:
        return logger.exception(
            f"Failed To Generate Slack Workflow Interaction for user  with workflow {str(workflow.id)} email {workflow.user.email} {e}"
        )
    except InvalidAccessToken as e:
        return logger.exception(
            f"Failed To Generate Slack Workflow Interaction for user  with workflow {str(workflow.id)} email {workflow.user.email} {e}"
        )
    workflow.slack_view = res.get("view").get("id")
    workflow.save()


@processor(required_context=["w", "tracking_id"])
def process_remove_contact_from_meeting(payload, context):
    workflow = MeetingWorkflow.objects.get(id=context.get("w"))
    meeting = workflow.meeting
    org = workflow.user.organization
    access_token = org.slack_integration.access_token
    for i, part in enumerate(meeting.participants):
        if part["_tracking_id"] == context.get("tracking_id"):
            # remove its form if it exists
            if part["_form"] not in [None, ""]:
                workflow.forms.filter(id=part["_form"]).delete()
            del meeting.participants[i]
            break
    meeting.save()
    if check_contact_last_name(workflow.id):
        update_res = slack_requests.update_channel_message(
            context.get("original_message_channel"),
            context.get("original_message_timestamp"),
            access_token,
            block_set=get_block_set("initial_meeting_interaction", {"w": context.get("w")}),
        )

    return process_show_meeting_contacts(payload, context, action=slack_const.VIEWS_UPDATE)


@processor(required_context=["w"])
def process_show_meeting_resource(payload, context):
    user = User.objects.get(id=context.get("u"))
    blocks = get_block_set("update_meeting_block_set", context,)
    access_token = user.organization.slack_integration.access_token
    url = slack_const.SLACK_API_ROOT + slack_const.VIEWS_UPDATE
    trigger_id = payload["trigger_id"]

    view_id = payload["view"]["id"]
    data = {
        "view_id": view_id,
        "view": {
            "type": "modal",
            "callback_id": slack_const.ZOOM_MEETING__SELECTED_RESOURCE,
            "title": {"type": "plain_text", "text": f"Choose CRM Record"},
            "blocks": blocks,
            "external_id": f"update_meeting_block_set.{str(uuid.uuid4())}",
            "private_metadata": json.dumps(context),
        },
    }
    try:
        res = slack_requests.generic_request(url, data, access_token=access_token)
    except InvalidBlocksException as e:
        return logger.exception(
            f"Failed To Generate Slack Workflow Interaction for user  with workflow {str(workflow.id)} email {workflow.user.email} {e}"
        )
    except InvalidBlocksFormatException as e:
        return logger.exception(
            f"Failed To Generate Slack Workflow Interaction for user  with workflow {str(workflow.id)} email {workflow.user.email} {e}"
        )
    except UnHandeledBlocksException as e:
        return logger.exception(
            f"Failed To Generate Slack Workflow Interaction for user  with workflow {str(workflow.id)} email {workflow.user.email} {e}"
        )
    except InvalidAccessToken as e:
        return logger.exception(
            f"Failed To Generate Slack Workflow Interaction for user  with workflow {str(workflow.id)} email {workflow.user.email} {e}"
        )
    return


@processor(required_context=["w"])
def process_show_meeting_chat_modal(payload, context):
    from managr.core.models import NoteTemplate

    workflow = MeetingWorkflow.objects.get(id=context.get("w"))
    user_id = context.get("u")
    user = User.objects.get(id=user_id)
    access_token = user.organization.slack_integration.access_token
    url = slack_const.SLACK_API_ROOT + slack_const.VIEWS_OPEN
    trigger_id = payload["trigger_id"]
    data = {
        "trigger_id": trigger_id,
        "view": {
            "type": "modal",
            "callback_id": slack_const.MEETING___SUBMIT_CHAT_PROMPT,
            "title": {"type": "plain_text", "text": f"Log Meeting"},
            "submit": {"type": "plain_text", "text": "Submit"},
            "blocks": get_block_set("chat_meeting_blockset", context=context),
            "private_metadata": json.dumps(context),
        },
    }
    try:
        res = slack_requests.generic_request(url, data, access_token=access_token)
    except InvalidBlocksException as e:
        return logger.exception(
            f"Failed To Generate Slack Workflow Interaction for user  with workflow {str(workflow.id)} email {workflow.user.email} {e}"
        )
    except InvalidBlocksFormatException as e:
        return logger.exception(
            f"Failed To Generate Slack Workflow Interaction for user  with workflow {str(workflow.id)} email {workflow.user.email} {e}"
        )
    except UnHandeledBlocksException as e:
        return logger.exception(
            f"Failed To Generate Slack Workflow Interaction for user  with workflow {str(workflow.id)} email {workflow.user.email} {e}"
        )
    except InvalidAccessToken as e:
        return logger.exception(
            f"Failed To Generate Slack Workflow Interaction for user  with workflow {str(workflow.id)} email {workflow.user.email} {e}"
        )
    return


@processor(required_context=["w"])
def process_meeting_selected_resource(payload, context):
    """opens a modal with the options to search or create"""
    url = slack_const.SLACK_API_ROOT + slack_const.VIEWS_OPEN
    trigger_id = payload["trigger_id"]
    type = context.get("type", None)
    workflow = MeetingWorkflow.objects.get(id=context.get("w"))
    select = payload["actions"][0]["selected_option"]
    selected_option = select["value"]
    organization = workflow.user.organization
    access_token = organization.slack_integration.access_token
    private_metadata = {
        "original_message_channel": payload["channel"]["id"],
        "original_message_timestamp": payload["message"]["ts"],
    }

    context = {
        "w": context.get("w"),
        "resource": str(selected_option),
    }
    if type:
        context.update({"type": type})

    private_metadata.update(context)
    data = {
        "trigger_id": trigger_id,
        "view": {
            "type": "modal",
            "callback_id": slack_const.ZOOM_MEETING__SELECTED_RESOURCE,
            "title": {"type": "plain_text", "text": f"{selected_option}"},
            "blocks": get_block_set("create_or_search_modal", context=context),
            "private_metadata": json.dumps(private_metadata),
        },
    }
    try:
        res = slack_requests.generic_request(url, data, access_token=access_token)
    except InvalidBlocksException as e:
        return logger.exception(
            f"Failed To Generate Slack Workflow Interaction for user  with workflow {str(workflow.id)} email {workflow.user.email} {e}"
        )
    except InvalidBlocksFormatException as e:
        return logger.exception(
            f"Failed To Generate Slack Workflow Interaction for user  with workflow {str(workflow.id)} email {workflow.user.email} {e}"
        )
    except UnHandeledBlocksException as e:
        return logger.exception(
            f"Failed To Generate Slack Workflow Interaction for user  with workflow {str(workflow.id)} email {workflow.user.email} {e}"
        )
    except InvalidAccessToken as e:
        return logger.exception(
            f"Failed To Generate Slack Workflow Interaction for user  with workflow {str(workflow.id)} email {workflow.user.email} {e}"
        )
    if type is None:
        workflow.slack_view = res.get("view").get("id")
        workflow.save()


@processor(required_context=[])
def process_meeting_selected_resource_option(payload, context):
    """depending on the selection on the meeting review form (create new) this will open a create form or an empty block set"""
    url = slack_const.SLACK_API_ROOT + slack_const.VIEWS_UPDATE
    private_metadata = json.loads(payload["view"]["private_metadata"])
    private_metadata.update({**context})
    workflow = MeetingWorkflow.objects.get(id=private_metadata.get("w"))
    user = workflow.user
    select = payload["actions"][0]["selected_option"]["value"]
    resource_type = context.get("resource_type")
    action = None
    try:
        action, r = select.split(".")
    except ValueError:
        pass
    if not action:
        blocks = []
        try:
            resource = CRM_SWITCHER[user.crm][resource_type]["model"].objects.get(
                integration_id=select
            )
            resource_id = resource.id
        except CRM_SWITCHER[user.crm][resource_type]["model"].DoesNotExist:
            try:
                remove_owner = True if resource_type in ["Lead", "Contact"] else False
                resource_res = user.crm_account.adapter_class.list_resource_data(
                    resource_type,
                    filter=CRM_FILTERS(user.crm, select),
                    remove_owner=remove_owner,
                    limit=25,
                )
                serializer = CRM_SWITCHER[user.crm][resource_type]["serializer"](
                    data=resource_res[0].as_dict
                )
                serializer.is_valid(raise_exception=True)
                serializer.save()
                resource_id = serializer.instance.id
            except Exception as e:
                logger.exception(f"Failed to sync new resource with id {select} for {user.email}")
                return {
                    "response_action": "push",
                    "view": {
                        "type": "modal",
                        "title": {"type": "plain_text", "text": "An Error Occured"},
                        "blocks": get_block_set(
                            "error_modal",
                            {
                                "message": f":no_entry: We could not sync the {resource_type} because of :\n *Error* : _{e}_"
                            },
                        ),
                    },
                }
        workflow.resource_id = resource_id
        workflow.resource_type = resource_type
        workflow.save()
        workflow.forms.exclude(
            template__resource__in=[
                slack_const.FORM_RESOURCE_CONTACT,
                slack_const.FORM_RESOURCE_OPPORTUNITYLINEITEM,
            ]
        ).delete()
        workflow.add_form(resource_type, slack_const.FORM_TYPE_UPDATE, resource_id=resource_id)
        blocks = get_block_set("meeting_review_modal", context=private_metadata)
        view = "meeting_review_modal"
    else:
        view = "create_modal_block_set"
        private_metadata.update({**context})
        blocks = [
            *get_block_set("create_modal_block_set", {**private_metadata}),
        ]
        try:
            stage_name = "StageName" if workflow.user.crm == "SALESFORCE" else "dealstage"
            index, block = block_finder(stage_name, blocks)
        except ValueError:
            # did not find the block
            block = None
            pass
        if workflow.user.crm == "HUBSPOT" and resource_type == "Deal" and action == "CREATE_NEW":
            try:
                pipeline_index, pipeline_block = block_finder("pipeline", blocks)
            except ValueError:
                # did not find the block
                pipeline_index = False
                pipeline_block = None
                pass
            if pipeline_block is None:
                pipeline_field = ObjectField.objects.filter(
                    crm_object="Deal", api_name="pipeline", user=workflow.user
                ).first()
                if pipeline_field:
                    pipeline_block = pipeline_field.to_slack_field(None, workflow.user, "Deal")
            pipeline_block = {
                **pipeline_block,
                "accessory": {
                    **pipeline_block["accessory"],
                    "action_id": f"{slack_const.COMMAND_FORMS__PIPELINE_SELECTED}?u={str(workflow.user.id)}&w={str(workflow.id)}&field={str(pipeline_field.id)}&type=meeting",
                },
            }
            if block:
                if pipeline_index:
                    del blocks[index]
                else:
                    blocks[index] = pipeline_block
        else:
            if block:
                block = {
                    **block,
                    "accessory": {
                        **block["accessory"],
                        "action_id": f"{slack_const.ZOOM_MEETING__STAGE_SELECTED}?u={str(workflow.user.id)}&w={str(workflow.id)}",
                    },
                }
                blocks = [*blocks[:index], block, *blocks[index + 1 :]]
        workflow.resource_type = resource_type
        workflow.save()
    slack_access_token = user.organization.slack_integration.access_token
    url = slack_const.SLACK_API_ROOT + slack_const.VIEWS_UPDATE
    # get state - state contains the values based on the block_id

    context = {
        "w": str(workflow.id),
        "type": "meeting",
    }
    data = {
        "view_id": payload["view"]["id"],
        "view": {
            "type": "modal",
            "callback_id": slack_const.ZOOM_MEETING__PROCESS_MEETING_SENTIMENT,
            "title": {"type": "plain_text", "text": "Log Meeting"},
            "blocks": blocks,
            "submit": {"type": "plain_text", "text": "Submit"},
            "private_metadata": json.dumps(context),
            "external_id": f"{view}.{str(uuid.uuid4())}",
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
def process_create_or_search_selected(payload, context):
    """attaches a drop down to the message block for selecting a resource type"""
    workflow_id = payload["actions"][0]["value"]
    type = False
    workflow = MeetingWorkflow.objects.get(id=workflow_id)
    organization = workflow.user.organization
    access_token = organization.slack_integration.access_token
    # get current blocks
    previous_blocks = payload["message"]["blocks"]
    # check if the dropdown option has been added already
    select_block = block_finder(slack_const.ZOOM_MEETING__ATTACH_RESOURCE_SECTION, previous_blocks)
    if type:
        if select_block:
            previous_blocks.pop(select_block[0])
        prep_block = block_finder(workflow_id, previous_blocks)
        block_sets = get_block_set(
            "attach_resource_interaction", {"w": str(workflow.id), "type": "prep"}
        )
        previous_blocks.insert(prep_block[0], block_sets[0])
    # create new block including the resource type
    else:
        if not select_block:
            block_sets = get_block_set("attach_resource_interaction", {"w": workflow_id})
            previous_blocks.insert(6, block_sets[0])
    try:
        res = slack_requests.update_channel_message(
            payload["channel"]["id"],
            payload["message"]["ts"],
            access_token,
            block_set=previous_blocks,
        )
    except InvalidBlocksException as e:
        return logger.exception(
            f"Failed To Generate Slack Workflow Interaction for user  with workflow {str(workflow.id)} email {workflow.user.email} {e}"
        )
    except InvalidBlocksFormatException as e:
        return logger.exception(
            f"Failed To Generate Slack Workflow Interaction for user  with workflow {str(workflow.id)} email {workflow.user.email} {e}"
        )
    except UnHandeledBlocksException as e:
        return logger.exception(
            f"Failed To Generate Slack Workflow Interaction for user  with workflow {str(workflow.id)} email {workflow.user.email} {e}"
        )
    except InvalidAccessToken as e:
        return logger.exception(
            f"Failed To Generate Slack Workflow Interaction for user  with workflow {str(workflow.id)} email {workflow.user.email} {e}"
        )
    if type is False:
        workflow.slack_interaction = f"{res['ts']}|{res['channel']}"
        workflow.save()


@processor(required_context="u")
def process_show_edit_product_form(payload, context):
    slack_account = UserSlackIntegration.objects.get(slack_id=payload["user"]["id"])
    user = slack_account.user
    access_token = user.organization.slack_integration.access_token
    loading_view_data = send_loading_screen(
        access_token,
        "Gathering current product info...",
        "push",
        str(user.id),
        payload["trigger_id"],
        payload["view"]["id"],
    )
    blocks = get_block_set(
        "edit_product_block_set", {"u": str(user.id), "opp_item_id": context.get("opp_item_id")}
    )

    data = {
        "view_id": loading_view_data["view"]["id"],
        "view": {
            "type": "modal",
            "callback_id": slack_const.PROCESS_UPDATE_PRODUCT,
            "title": {"type": "plain_text", "text": "Edit Product"},
            "blocks": blocks,
            "submit": {"type": "plain_text", "text": "Submit"},
            "private_metadata": json.dumps(context),
        },
    }
    try:
        slack_requests.generic_request(
            slack_const.SLACK_API_ROOT + slack_const.VIEWS_UPDATE, data, access_token=access_token,
        )
    except InvalidBlocksException as e:
        return logger.exception(
            f"Failed To Generate Slack Product form with {context.get('opp_item_id')} email {user.email} {e}"
        )
    except InvalidBlocksFormatException as e:
        return logger.exception(
            f"Failed To Generate Slack Product form with {context.get('opp_item_id')} email {user.email} {e}"
        )
    except UnHandeledBlocksException as e:
        return logger.exception(
            f"Failed To Generate Slack Product form with {context.get('opp_item_id')} email {user.email} {e}"
        )
    except InvalidAccessToken as e:
        return logger.exception(
            f"Failed To Generate Slack Product form with {str(user.id)} email {user.email} {e}"
        )


def process_add_products_form(payload, context):
    user = User.objects.get(slack_integration__slack_id=payload["user"]["id"])
    view = payload["view"]
    state = view["state"]["values"]
    pricebook = context.get("pricebook", None)
    private_metadata = json.loads(view["private_metadata"])
    loading_view_data = send_loading_screen(
        user.organization.slack_integration.access_token,
        "Putting together your form...:file_cabinet:",
        "push",
        str(user.id),
        payload["trigger_id"],
        view["id"],
    )
    main_form = OrgCustomSlackFormInstance.objects.get(id=context.get("f"))
    main_form.save_form(state)
    product_form_id = context.get("product_form", None)
    if product_form_id is None:
        product_template = OrgCustomSlackForm.objects.filter(
            Q(resource="OpportunityLineItem", form_type="CREATE", team=user.team)
        ).first()
        product_form = OrgCustomSlackFormInstance.objects.create(
            template=product_template, user=user
        )
        product_form_id = str(product_form.id)
    else:
        product_form = OrgCustomSlackFormInstance.objects.get(id=product_form_id)
    private_metadata.update({**context, "view_id": view["id"], "product_form": product_form_id})
    # currently only for update
    blocks = []
    if pricebook is None:
        blocks.append(
            block_builders.external_select(
                f"*Pricebook*",
                action_with_params(
                    slack_const.GET_PRICEBOOK_ENTRY_OPTIONS,
                    params=[f"org={str(user.organization.id)}", f"product_form={product_form_id}"],
                ),
                block_id="PRICEBOOKS",
                initial_option=None,
            )
        )
        blocks.extend(product_form.generate_form())
    else:
        blocks.extend(product_form.generate_form(fields=f"Pricebook2Id:'{pricebook}'"))
    if len(blocks):
        data = {
            "view_id": loading_view_data["view"]["id"],
            "view": {
                "type": "modal",
                "title": {"type": "plain_text", "text": "Add Products Form"},
                "submit": {"type": "plain_text", "text": "Submit"},
                "blocks": blocks,
                "private_metadata": json.dumps(private_metadata),
                "callback_id": slack_const.PROCESS_SUBMIT_PRODUCT,
            },
        }
    else:
        data = {
            "view_id": loading_view_data["view"]["id"],
            "view": {
                "type": "modal",
                "title": {"type": "plain_text", "text": "Product Form error"},
                "blocks": block_builders.simple_section("Failed to generate your products form"),
                "private_metadata": json.dumps(private_metadata),
            },
        }
    try:
        slack_requests.generic_request(
            slack_const.SLACK_API_ROOT + slack_const.VIEWS_UPDATE,
            data,
            access_token=user.organization.slack_integration.access_token,
        )
    except Exception as e:
        return logger.exception(
            f"Failed to show product form for user {str(user.id)} email {user.email} {e}"
        )


@slack_api_exceptions(rethrow=True)
def process_add_custom_object_form(payload, context):
    user = User.objects.get(id=context.get("u"))
    selected_object = payload["actions"][0]["selected_option"]["value"]
    template = (
        OrgCustomSlackForm.objects.for_user(user).filter(custom_object=selected_object).first()
    )
    if template:
        form = OrgCustomSlackFormInstance.objects.create(template=template, user=user,)
        blocks = form.generate_form()
        if context.get("w", None):
            workflow = MeetingWorkflow.objects.get(id=context.get("w"))
            form.workflow = workflow
            form.save()
    context = {**context, "f": str(form.id)}
    data = {
        "view_id": payload["view"]["id"],
        "trigger_id": payload["trigger_id"],
        "view": {
            "type": "modal",
            "title": {"type": "plain_text", "text": "Create Custom Object"},
            "submit": {"type": "plain_text", "text": "Submit"},
            "blocks": blocks,
            "private_metadata": json.dumps(context),
            "callback_id": slack_const.SUBMIT_CUSTOM_OBJECT_DATA,
        },
    }
    try:
        slack_requests.generic_request(
            slack_const.SLACK_API_ROOT + slack_const.VIEWS_UPDATE,
            data,
            access_token=user.organization.slack_integration.access_token,
        )
    except Exception as e:
        return logger.exception(
            f"Failed to show product form for user {str(user.id)} email {user.email} {e}"
        )
    return


@slack_api_exceptions(rethrow=True)
def process_pick_custom_object(payload, context):
    user = User.objects.get(slack_integration__slack_id=payload["user"]["id"])
    custom_objects = user.crm_account.custom_objects
    options = [
        block_builders.option(custom_object, custom_object) for custom_object in custom_objects
    ]
    params = [f"u={str(user.id)}"]
    if context.get("w", None):
        params.append(f"w={str(context.get('w'))}")
    action_id = action_with_params(slack_const.PROCESS_ADD_CUSTOM_OBJECT_FORM, params=params)
    blocks = [
        block_builders.static_select(
            "Choose a custom object to add", options=options, action_id=action_id
        )
    ]
    data = {
        "view_id": payload["view"]["id"],
        "trigger_id": payload["trigger_id"],
        "view": {
            "type": "modal",
            "title": {"type": "plain_text", "text": "Add Custom Object"},
            "blocks": blocks,
        },
    }
    try:
        slack_requests.generic_request(
            slack_const.SLACK_API_ROOT + slack_const.VIEWS_PUSH,
            data,
            access_token=user.organization.slack_integration.access_token,
        )
    except Exception as e:
        return logger.exception(
            f"Failed to show product form for user {str(user.id)} email {user.email} {e}"
        )
    return


@processor()
def process_sync_calendar(payload, context):
    user = User.objects.get(id=context.get("u"))
    date = context.get("date", None)
    ts = payload["container"]["message_ts"]
    channel = payload["container"]["channel_id"]
    slack_interaction = f"{ts}|{channel}"
    if date:
        message_date = datetime.strptime(date, "%Y-%m-%d")
    else:
        user_timezone = pytz.timezone(user.timezone)
        message_date = pytz.utc.localize(datetime.today()).astimezone(user_timezone)
    date_string = f":calendar: Today's Meetings: *{message_date.month}/{message_date.day}/{message_date.year}*"
    blocks = [
        block_builders.section_with_button_block(
            "Sync Calendar",
            "sync_calendar",
            date_string,
            action_id=action_with_params(
                slack_const.MEETING_REVIEW_SYNC_CALENDAR,
                [f"u={str(user.id)}", f"date={str(message_date.date())}"],
            ),
        ),
        {"type": "divider"},
        *get_block_set("loading", {"message": "Checking for new calendar events..."}),
    ]
    try:
        slack_res = slack_requests.update_channel_message(
            channel, ts, user.organization.slack_integration.access_token, block_set=blocks,
        )
    except Exception as e:
        logger.exception(f"Failed to loading calendar sync message for {user.email} due to {e}")
    emit_process_calendar_meetings(
        context.get("u"),
        slack_interaction=slack_interaction,
        date=date,
        verbose_name=f"calendar-meetings-{user.email}-{str(uuid.uuid4())}",
    )
    return


#########################################################
# COMMAND ACTIONS
#########################################################


def process_managr_action(payload, context):
    view = payload.get("view", None)
    if view:
        state = payload["view"]["state"]
        data = {"view_id": payload["view"]["id"]}
    else:
        state = payload["state"]
        data = {"trigger_id": payload["trigger_id"]}
    command_value = state["values"]["select_action"][f"COMMAND_MANAGR_ACTION?u={context.get('u')}"][
        "selected_option"
    ]["value"]
    data.update(context)

    get_action(command_value, data)
    return


def process_insert_chat_template(payload, context):
    from managr.core.models import NoteTemplate

    from_workflow = True if "w" in context.keys() else False
    user = User.objects.get(id=context.get("u"))
    blocks = payload["view"]["blocks"]
    template_value = payload["actions"][0]["selected_option"]["text"]["text"]
    if template_value == "NONE":
        return
    template = NoteTemplate.objects.for_user(user).filter(subject=template_value).first()

    try:
        index, block = block_finder("CHAT_PROMPT", blocks)
    except ValueError:
        # did not find the block
        block = None
    title = "Log Meeting" if from_workflow else "Update CRM"
    callback_id = (
        slack_const.MEETING___SUBMIT_CHAT_PROMPT
        if from_workflow
        else slack_const.COMMAND_FORMS__SUBMIT_CHAT
    )
    if block:
        blocks[index]["element"]["initial_value"] = replace_tags(template.body)
        access_token = user.organization.slack_integration.access_token
        url = slack_const.SLACK_API_ROOT + slack_const.VIEWS_UPDATE
        data = {
            "view_id": payload["view"]["id"],
            "view": {
                "type": "modal",
                "callback_id": callback_id,
                "title": {"type": "plain_text", "text": title},
                "blocks": blocks,
                "submit": {"type": "plain_text", "text": "Submit", "emoji": True},
                "private_metadata": json.dumps(context),
            },
        }
        try:
            slack_requests.generic_request(url, data, access_token=access_token)
        except Exception as e:
            logger.exception(e)
    return


def GET_ACTION_TEMPLATE(user, template_value):
    object_type = "Deal" if user.crm == "HUBSPOT" else "Opportunity"
    action_switcher = {
        "GET_SUMMARY": f"Get summary for {object_type} Pied Piper",
        "DEAL_REVIEW": f"Run a review for {object_type} Pied Piper",
        "CALL_SUMMARY": f"Get the call summary for {object_type} Pied Piper",
        "CALL_ANALYSIS": f"Get the call analysis for {object_type} Pied Piper",
        "ASK_MANAGR": f"Ask Managr ... for {object_type} Pied Piper",
    }
    return action_switcher[template_value]


def process_insert_action_template(payload, context):
    user = User.objects.get(id=context.get("u"))
    blocks = payload["view"]["blocks"]
    template_value = payload["actions"][0]["selected_option"]["value"]
    template = GET_ACTION_TEMPLATE(user, template_value)
    try:
        index, block = block_finder("CHAT_PROMPT", blocks)
    except ValueError:
        # did not find the block
        block = None
    if block:
        blocks[index]["element"]["initial_value"] = template
        access_token = user.organization.slack_integration.access_token
        url = slack_const.SLACK_API_ROOT + slack_const.VIEWS_UPDATE
        data = {
            "view_id": payload["view"]["id"],
            "view": {
                "type": "modal",
                "callback_id": slack_const.PROCESS_CHAT_ACTION,
                "title": {"type": "plain_text", "text": "Take Action"},
                "blocks": blocks,
                "submit": {"type": "plain_text", "text": "Submit", "emoji": True},
                "private_metadata": json.dumps(context),
            },
        }
        try:
            slack_requests.generic_request(url, data, access_token=access_token)
        except Exception as e:
            logger.exception(e)
    return


@processor(required_context="u")
def process_add_create_form(payload, context):
    user = User.objects.get(id=context.get("u"))
    resource_type = payload["view"]["state"]["values"]["ATTACH_RESOURCE_SECTION"][
        f"COMMAND_FORMS__PROCESS_ADD_CREATE_FORM?u={context.get('u')}"
    ]["selected_option"]["value"]
    template = (
        OrgCustomSlackForm.objects.for_user(user)
        .filter(Q(resource=resource_type, form_type="CREATE"))
        .first()
    )
    slack_form = OrgCustomSlackFormInstance.objects.create(template=template, user=user,)
    if slack_form:
        context = {
            "resource_type": resource_type,
            "f": str(slack_form.id),
            "u": str(user.id),
            "type": "command",
        }
        blocks = get_block_set("create_modal", context,)
        try:
            stage_name = "StageName" if user.crm == "SALESFORCE" else "dealstage"
            index, block = block_finder(stage_name, blocks)
        except ValueError:
            # did not find the block
            block = None
            pass
        if user.crm == "HUBSPOT" and resource_type == "Deal":
            try:
                pipeline_index, pipeline_block = block_finder("pipeline", blocks)
            except ValueError:
                # did not find the block
                pipeline_index = False
                pipeline_block = None
                pass
            if pipeline_block is None:
                pipeline_field = ObjectField.objects.filter(
                    crm_object="Deal", api_name="pipeline", user=user
                ).first()
                if pipeline_field:
                    pipeline_block = pipeline_field.to_slack_field(None, user, "Deal")
            pipeline_block = {
                **pipeline_block,
                "accessory": {
                    **pipeline_block["accessory"],
                    "action_id": f"{slack_const.COMMAND_FORMS__PIPELINE_SELECTED}?u={str(user.id)}&f={str(slack_form.id)}&field={str(pipeline_field.id)}",
                },
            }
            if block:
                if pipeline_index:
                    del blocks[index]
                else:
                    blocks[index] = pipeline_block
        else:
            if block:
                block = {
                    **block,
                    "accessory": {
                        **block["accessory"],
                        "action_id": f"{slack_const.COMMAND_FORMS__STAGE_SELECTED}?u={str(user.id)}&f={str(slack_form.id)}",
                    },
                }
                blocks = [*blocks[:index], block, *blocks[index + 1 :]]
        access_token = user.organization.slack_integration.access_token
        private_metadata = {**context}
        url = slack_const.SLACK_API_ROOT + slack_const.VIEWS_UPDATE
        data = {
            "view_id": payload["view"]["id"],
            "view": {
                "type": "modal",
                "callback_id": slack_const.COMMAND_FORMS__SUBMIT_FORM,
                "title": {"type": "plain_text", "text": f"Create {resource_type}"},
                "blocks": blocks,
                "submit": {"type": "plain_text", "text": "Create", "emoji": True},
                "private_metadata": json.dumps(private_metadata),
                "external_id": f"create_modal.{str(uuid.uuid4())}",
            },
        }

        slack_requests.generic_request(url, data, access_token=access_token)


@processor(required_context=["u", "f"])
def process_stage_selected_command_form(payload, context):
    url = slack_const.SLACK_API_ROOT + slack_const.VIEWS_UPDATE
    current_form_ids = context.get("f").split(",")
    user = User.objects.get(id=context.get("u"))
    org = user.organization
    access_token = org.slack_integration.access_token
    trigger_id = payload["trigger_id"]
    view = payload["view"]
    view_id = payload["view"]["id"]
    private_metadata = json.loads(payload["view"]["private_metadata"])
    external_id = payload.get("view", {}).get("external_id", None)
    try:
        view_type, __unique_id = external_id.split(".")
    except ValueError:
        view_type = external_id
        pass
    current_forms = user.custom_slack_form_instances.filter(id__in=current_form_ids)
    current_forms.exclude(template__form_type__in=["UPDATE", "CREATE"]).delete()
    main_form = current_forms.first()
    added_form_ids = []
    if len(payload["actions"]):
        action = payload["actions"][0]
        blocks = payload["view"]["blocks"]
        selected_value = (
            action["selected_option"]["value"]
            if user.crm == "SALESFORCE"
            else action["selected_option"]["text"]["text"]
        )
        stage_form = (
            org.custom_slack_forms.for_user(user)
            .filter(form_type=slack_const.FORM_TYPE_STAGE_GATING, stage=selected_value)
            .first()
        )
        if stage_form:
            new_form = OrgCustomSlackFormInstance.objects.create(
                user=user,
                template=stage_form,
                resource_id=main_form.resource_id,
                update_source="command",
            )
            added_form_ids.append(str(new_form.id))

        # gather and attach all forms
    private_metadata.update({**context, "f": ",".join([str(main_form.id), *added_form_ids])})
    if len(added_form_ids):
        submit_button_message = "Next"
        callback_id = slack_const.COMMAND_FORMS__PROCESS_NEXT_PAGE
    else:
        callback_id = (
            slack_const.PROCESS_SUBMIT_ALERT_RESOURCE_DATA
            if context.get("type", None) == "alert"
            else slack_const.COMMAND_FORMS__SUBMIT_FORM
        )
        submit_button_message = "Update" if main_form.template.form_type == "UPDATE" else "Create"
    data = {
        "trigger_id": trigger_id,
        "view_id": view_id,
        "view": {
            "type": "modal",
            "callback_id": callback_id,
            "title": view["title"],
            "blocks": blocks,
            "submit": {"type": "plain_text", "text": submit_button_message},
            "private_metadata": json.dumps(private_metadata),
            "external_id": f"{view_type}.{str(uuid.uuid4())}",
        },
    }
    try:
        res = slack_requests.generic_request(url, data, access_token=access_token)
    except InvalidBlocksException as e:
        return logger.exception(f"Failed To Generate Slack {e}")
    except InvalidBlocksFormatException as e:
        return logger.exception(f"Failed To Generate Slack  {e}")
    except UnHandeledBlocksException as e:
        return logger.exception(f"Failed To Generate Slack  {e}")
    except InvalidAccessToken as e:
        return logger.exception(f"Failed To Generate Slack Workflow Interaction for user {e}")


@processor(required_context=["u", "f"])
def process_alert_inline_stage_selected(payload, context):
    selected_stage_text = payload["actions"][0]["selected_option"]["text"]["text"]
    user = User.objects.get(id=context.get("u"))
    url = slack_const.SLACK_API_ROOT + slack_const.VIEWS_OPEN
    trigger_id = payload["trigger_id"]
    form = OrgCustomSlackFormInstance.objects.get(id=context.get("f"))
    stage_form_template = (
        user.organization.custom_slack_forms.for_user(user)
        .filter(form_type=slack_const.FORM_TYPE_STAGE_GATING, stage=selected_stage_text)
        .first()
    )
    if stage_form_template:
        stage_form = OrgCustomSlackFormInstance.objects.create(
            user=user, template=stage_form_template, resource_id=form.resource_id
        )
        blocks = []
        blocks.extend(stage_form.generate_form())
        data = {
            "trigger_id": trigger_id,
            "view": {
                "type": "modal",
                "private_metadata": json.dumps({**context, "stage_form_id": str(stage_form.id)}),
                "callback_id": slack_const.ALERT_INLINE_STAGE_SUBMITTED,
                "title": {"type": "plain_text", "text": f"Update {form.resource_type}"},
                "blocks": blocks,
                "submit": {"type": "plain_text", "text": "Save"},
            },
        }
        try:
            slack_requests.generic_request(
                url, data, access_token=user.organization.slack_integration.access_token
            )

        except InvalidBlocksException as e:
            return logger.exception(f"Failed To Generate Blocks {e}")
        except InvalidBlocksFormatException as e:
            return logger.exception(f"Failed To Generate Blocks {e}")
        except UnHandeledBlocksException as e:
            return logger.exception(f"Failed To Generate Blocks {e}")
        except InvalidAccessToken as e:
            return logger.exception(f"Failed To send slack {e}")
    return


@processor(required_context=["u"])
def process_pipeline_selected_command_form(payload, context):
    url = slack_const.SLACK_API_ROOT + slack_const.VIEWS_UPDATE
    type = context.get("type", None)
    user = User.objects.get(id=context.get("u"))
    org = user.organization
    access_token = org.slack_integration.access_token
    trigger_id = payload["trigger_id"]
    view = payload["view"]
    view_id = payload["view"]["id"]
    blocks = view["blocks"]
    # get the forms associated with this slack
    stage_field = user.object_fields.filter(api_name="dealstage", crm_object="Deal").first()
    external_id = payload.get("view", {}).get("external_id", None)
    try:
        view_type, __unique_id = external_id.split(".")
    except ValueError:
        view_type = external_id
        pass
    action_id = (
        f"{slack_const.ZOOM_MEETING__STAGE_SELECTED}?w={context.get('w')}"
        if type == "meeting"
        else f"{slack_const.COMMAND_FORMS__STAGE_SELECTED}?u={str(user.id)}&f={context.get('f')}"
    )
    if len(payload["actions"]):
        action = payload["actions"][0]
        blocks = payload["view"]["blocks"]
        selected_value = action["selected_option"]["value"]
        # blockfinder returns a tuple of its index in the block and the object
        index, action_block = block_finder(action["block_id"], blocks)
        # find all stages previous to it
        pipeline_index, pipeline_block = block_finder("pipeline", blocks)
        stage_block = stage_field.to_slack_field(pipeline_id=selected_value)
        stage_block = {
            **stage_block,
            "accessory": {**stage_block["accessory"], "action_id": action_id,},
        }
    blocks[pipeline_index] = stage_block
    updated_view_title = view["title"]
    submit_button_message = "Create"
    callback_id = slack_const.COMMAND_FORMS__SUBMIT_FORM
    data = {
        "trigger_id": trigger_id,
        "view_id": view_id,
        "view": {
            "type": "modal",
            "callback_id": callback_id,
            "title": updated_view_title,
            "blocks": blocks,
            "submit": {"type": "plain_text", "text": submit_button_message},
            "private_metadata": json.dumps(context),
            "external_id": f"{view_type}.{str(uuid.uuid4())}",
        },
    }
    try:
        res = slack_requests.generic_request(url, data, access_token=access_token)
    except InvalidBlocksException as e:
        return logger.exception(f"Failed To Generate Slack {e}")
    except InvalidBlocksFormatException as e:
        return logger.exception(f"Failed To Generate Slack  {e}")
    except UnHandeledBlocksException as e:
        return logger.exception(f"Failed To Generate Slack  {e}")
    except InvalidAccessToken as e:
        return logger.exception(f"Failed To Generate Slack Workflow Interaction for user {e}")


def CRM_FILTERS(crm, integration_id):
    filters = {
        "HUBSPOT": [{"propertyName": "hs_object_id", "operator": "EQ", "value": integration_id},],
        "SALESFORCE": [f"AND Id = '{integration_id}'"],
    }
    return filters[crm]


@slack_api_exceptions(rethrow=True)
@processor(required_context=["resource_type", "u"])
def process_show_update_resource_form(payload, context):
    from managr.slack.models import OrgCustomSlackForm, OrgCustomSlackFormInstance

    user = User.objects.get(id=context.get("u"))
    access_token = user.organization.slack_integration.access_token
    is_update = payload.get("view", None)
    view_type = "update" if is_update else "open"
    view_id = is_update["id"] if is_update else None
    trigger_id = payload["trigger_id"]
    crm = "Salesforce" if user.crm == "SALESFORCE" else "HubSpot"
    loading_view_data = send_loading_screen(
        access_token,
        f"{crm} is being a bit slow :sleeping:… please give it a few seconds",
        view_type,
        str(user.id),
        trigger_id,
        view_id,
    )
    integration_id = payload["actions"][0]["selected_option"]["value"]
    resource_type = context.get("resource_type")
    try:
        resource = CRM_SWITCHER[user.crm][resource_type]["model"].objects.get(
            integration_id=integration_id
        )
        resource_id = resource.id
    except CRM_SWITCHER[user.crm][resource_type]["model"].DoesNotExist:
        try:
            remove_owner = True if resource_type in ["Contact", "Lead"] else False
            resource_res = user.crm_account.adapter_class.list_resource_data(
                resource_type,
                filter=CRM_FILTERS(user.crm, integration_id),
                remove_owner=remove_owner,
                owners=[str(user.crm_account.crm_id)],
            )
            serializer = CRM_SWITCHER[user.crm][resource_type]["serializer"](
                data=resource_res[0].as_dict
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            resource_id = serializer.instance.id
        except Exception as e:
            logger.exception(
                f"Failed to sync new resource with id {integration_id} for {user.email} due to <{e}>"
            )
    show_submit_button_if_fields_added = False
    stage_form = None
    # HACK forms are generated with a helper fn currently stagename takes a special action id to update forms
    # we need to manually change this action_id
    if resource_id:
        template = (
            OrgCustomSlackForm.objects.for_user(user)
            .filter(Q(resource=resource_type, form_type="UPDATE"))
            .first()
        )
        slack_form = OrgCustomSlackFormInstance.objects.create(
            template=template, resource_id=resource_id, user=user, update_source="command",
        )
        if slack_form:
            stage_name = "StageName" if user.crm == "SALESFORCE" else "dealstage"
            current_stage = slack_form.resource_object.secondary_data.get(stage_name)
            stage_template = (
                OrgCustomSlackForm.objects.for_user(user).filter(stage=current_stage).first()
                if current_stage
                else None
            )
            form_ids = [str(slack_form.id)]
            if stage_template:
                stage_form = OrgCustomSlackFormInstance.objects.create(
                    template=stage_template,
                    resource_id=resource_id,
                    user=user,
                    update_source="command",
                )
                form_ids.append(str(stage_form.id))
            context.update({"f": ",".join(form_ids)})

    blocks = get_block_set(
        "update_modal_block_set",
        context={**context, "resource_type": resource_type, "resource_id": resource_id},
    )
    if slack_form:
        try:
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
                    "action_id": f"{slack_const.COMMAND_FORMS__STAGE_SELECTED}?u={str(user.id)}&f={str(slack_form.id)}",
                },
            }
            blocks = [*blocks[:index], block, *blocks[index + 1 :]]

        try:
            index, block = block_finder(slack_const.NO_FORM_FIELDS, blocks)
        except ValueError:
            # did not find the block
            show_submit_button_if_fields_added = True
            pass

    else:
        blocks.append(
            block_builders.simple_section("Please re-select your salesforce resource to update")
        )
        show_submit_button_if_fields_added = False
    if user.organization.has_products and resource_type == "Opportunity":
        buttons = []
        params = [
            f"f={str(slack_form.id)}",
            f"u={str(user.id)}",
            "type=command",
        ]
        if slack_form.resource_object.secondary_data["Pricebook2Id"]:
            params.append(f"pricebook={slack_form.resource_object.secondary_data['Pricebook2Id']}")
        buttons.append(
            block_builders.simple_button_block(
                "Add Product",
                "ADD_PRODUCT",
                action_id=action_with_params(slack_const.PROCESS_ADD_PRODUCTS_FORM, params=params,),
            )
        )
        if len(user.crm_account.custom_objects) > 0:
            buttons.append(
                block_builders.simple_button_block(
                    "Add Custom Object",
                    "ADD_CUSTOM_OBJECT",
                    action_id=action_with_params(
                        slack_const.PROCESS_PICK_CUSTOM_OBJECT, params=params,
                    ),
                )
            )
        blocks.append(block_builders.actions_block(buttons, block_id="ADD_EXTRA_OBJECTS_BUTTON",),)
        current_products = user.salesforce_account.list_resource_data(
            "OpportunityLineItem",
            0,
            filter=[
                "AND IsDeleted = false",
                f"AND OpportunityId = '{slack_form.resource_object.integration_id}'",
            ],
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
                        "main_form": str(slack_form.id),
                    },
                )
                blocks.append(product_block)

    data = {
        "view_id": loading_view_data["view"]["id"],
        "view": {
            "type": "modal",
            "title": {"type": "plain_text", "text": f"Update {resource_type}"},
            "blocks": blocks,
            "private_metadata": json.dumps(context),
            "external_id": f"update_modal_block_set.{str(uuid.uuid4())}",
        },
    }
    if show_submit_button_if_fields_added:
        if stage_form:
            submit_button_text = "Next"
            callback_id = slack_const.COMMAND_FORMS__PROCESS_NEXT_PAGE
        else:
            submit_button_text = "Update"
            callback_id = slack_const.COMMAND_FORMS__SUBMIT_FORM

        data["view"]["submit"] = {"type": "plain_text", "text": submit_button_text, "emoji": True}
        data["view"]["callback_id"] = callback_id
        data["view_id"] = loading_view_data["view"]["id"]

    slack_requests.generic_request(
        slack_const.SLACK_API_ROOT + slack_const.VIEWS_UPDATE, data, access_token=access_token
    )


@processor(required_context="u")
def process_create_task(payload, context):
    type = context.get("type", None)
    url = (
        slack_const.SLACK_API_ROOT + slack_const.VIEWS_UPDATE
        if type
        else slack_const.SLACK_API_ROOT + slack_const.VIEWS_OPEN
    )
    trigger_id = payload["trigger_id"]
    u = User.objects.get(id=context.get("u"))
    org = u.organization
    data = {
        "view": {
            "type": "modal",
            "callback_id": slack_const.COMMAND_CREATE_TASK,
            "title": {"type": "plain_text", "text": f"Create a Task"},
            "blocks": get_block_set(
                "create_task_modal",
                context={
                    "u": context.get("u"),
                    "resource_type": context.get("resource_type"),
                    "resource_id": context.get("resource_id"),
                },
            ),
            "submit": {"type": "plain_text", "text": "Submit", "emoji": True},
            "private_metadata": json.dumps(context),
        },
    }
    if type == "command":
        data["view_id"] = payload["view"]["id"]
        data["view"]["external_id"] = f"create_task_modal.{str(uuid.uuid4())}"
    else:
        data["trigger_id"] = trigger_id
    try:
        slack_requests.generic_request(url, data, access_token=org.slack_integration.access_token)
    except InvalidBlocksException as e:
        return logger.exception(
            f"Failed To Generate Slack Workflow Interaction for user {u.full_name} email {u.email} {e}"
        )
    except InvalidBlocksFormatException as e:
        return logger.exception(
            f"Failed To Generate Slack Workflow Interaction for user {u.full_name} email {u.email} {e}"
        )
    except UnHandeledBlocksException as e:
        return logger.exception(
            f"Failed To Generate Slack Workflow Interaction for user {u.full_name} email {u.email} {e}"
        )
    except InvalidAccessToken as e:
        return logger.exception(
            f"Failed To Generate Slack Workflow Interaction for user {u.full_name} email {u.email} {e}"
        )


@slack_api_exceptions(rethrow=True)
@processor(required_context=["resource_type", "u"])
def process_check_is_owner(payload, context):
    # CHECK_IS_OWNER
    slack_id = payload.get("user", {}).get("id")
    user_id = context.get("u")
    type = context.pop("type", None)
    user = User.objects.get(slack_integration__slack_id=slack_id)
    user_slack = UserSlackIntegration.objects.filter(slack_id=slack_id).first()
    if user.user_level in ["MANAGER", "SDR"] or user_slack and str(user_slack.user.id) == user_id:
        if type == "alert":
            return process_show_alert_update_resource_form(payload, context)
        else:
            return process_show_update_resource_form(payload, context)
    else:
        error_blocks = get_block_set(
            "error_modal", {"message": "You are not the Opportunity owner"}
        )
        url = slack_const.SLACK_API_ROOT + slack_const.VIEWS_OPEN
        trigger_id = payload.get("trigger_id")
        slack_access_token = user_slack.user.organization.slack_integration.access_token

        data = {
            "trigger_id": trigger_id,
            "view": {
                "type": "modal",
                "title": {"type": "plain_text", "text": "Error",},
                "blocks": error_blocks,
                "external_id": f"error_modal.{str(uuid.uuid4())}",
            },
        }
    try:
        slack_requests.generic_request(url, data, access_token=slack_access_token)
    except Exception as e:
        # exception will only be thrown for caught errors using decorator
        return logger.exception(f"Failed To show error message for user or show update form")
    return


@processor(required_context="u")
def process_resource_selected_for_task(payload, context):
    url = slack_const.SLACK_API_ROOT + slack_const.VIEWS_UPDATE
    trigger_id = payload["trigger_id"]
    u = User.objects.get(id=context.get("u"))
    org = u.organization
    selected_value = None
    # if this is coming from the create form delete the old form
    form_id = context.get("f", None)
    if form_id:
        OrgCustomSlackFormInstance.objects.get(id=form_id).delete()
    if len(payload["actions"]):
        action = payload["actions"][0]
        selected_value = action["selected_option"]["value"]
    external_id = payload.get("view", {}).get("external_id", None)
    try:
        view_type, __unique_id = external_id.split(".")
    except ValueError:
        pass
    data = {
        "trigger_id": trigger_id,
        "view_id": payload.get("view").get("id"),
        "view": {
            "type": "modal",
            "callback_id": payload["view"]["callback_id"],
            "title": payload.get("view").get("title"),
            "blocks": get_block_set(view_type, {**context, "resource_type": selected_value}),
            "private_metadata": json.dumps(context),
            "external_id": f"{view_type}.{str(uuid.uuid4())}",
        },
    }
    if (
        (payload["view"]["submit"] and form_id)
        or view_type == "create_task_modal"
        or view_type == "create_event_modal"
    ):
        data["view"]["submit"] = payload["view"]["submit"]

    try:
        slack_requests.generic_request(url, data, access_token=org.slack_integration.access_token)
    except InvalidBlocksException as e:
        return logger.exception(
            f"Failed To Generate Slack Workflow Interaction for user {u.full_name} email {u.email} {e}"
        )
    except InvalidBlocksFormatException as e:
        return logger.exception(
            f"Failed To Generate Slack Workflow Interaction for user {u.full_name} email {u.email} {e}"
        )
    except UnHandeledBlocksException as e:
        return logger.exception(
            f"Failed To Generate Slack Workflow Interaction for user {u.full_name} email {u.email} {e}"
        )
    except InvalidAccessToken as e:
        return logger.exception(
            f"Failed To Generate Slack Workflow Interaction for user {u.full_name} email {u.email} {e}"
        )


@processor(required_context="u")
def process_select_resource(payload, context):
    url = slack_const.SLACK_API_ROOT + slack_const.VIEWS_UPDATE
    trigger_id = payload["trigger_id"]
    u = User.objects.get(id=context.get("u"))
    org = u.organization
    selected_value = None
    # if this is coming from the create form delete the old form
    form_id = context.get("f", None)
    if form_id:
        OrgCustomSlackFormInstance.objects.get(id=form_id).delete()
    if len(payload["actions"]):
        action = payload["actions"][0]
        blocks = payload["view"]["blocks"]
        selected_value = action["selected_option"]["value"]
    external_id = payload.get("view", {}).get("external_id", None)
    try:
        view_type, __unique_id = external_id.split(".")
    except ValueError:
        pass
    data = {
        "trigger_id": trigger_id,
        "view_id": payload.get("view").get("id"),
        "view": {
            "type": "modal",
            "callback_id": payload["view"]["callback_id"],
            "title": payload.get("view").get("title"),
            "blocks": get_block_set(
                view_type,
                {**context, "resource_type": selected_value, "options": context.get("options")},
            ),
            "private_metadata": payload["view"]["private_metadata"],
            "external_id": f"{view_type}.{str(uuid.uuid4())}",
        },
    }

    try:
        slack_requests.generic_request(url, data, access_token=org.slack_integration.access_token)
    except InvalidBlocksException as e:
        return logger.exception(
            f"Failed To Generate Slack Workflow Interaction for user {u.full_name} email {u.email} {e}"
        )
    except InvalidBlocksFormatException as e:
        return logger.exception(
            f"Failed To Generate Slack Workflow Interaction for user {u.full_name} email {u.email} {e}"
        )
    except UnHandeledBlocksException as e:
        return logger.exception(
            f"Failed To Generate Slack Workflow Interaction for user {u.full_name} email {u.email} {e}"
        )
    except InvalidAccessToken as e:
        return logger.exception(
            f"Failed To Generate Slack Workflow Interaction for user {u.full_name} email {u.email} {e}"
        )


@slack_api_exceptions(rethrow=True)
@processor()
def process_return_to_form_modal(payload, context):
    """if an error occurs on create/update commands when the return button is clicked regen form"""
    pm = json.loads(payload["view"]["private_metadata"])
    url = slack_const.SLACK_API_ROOT + slack_const.VIEWS_UPDATE
    from_workflow = pm.get("w", False) not in [None, False]
    trigger_id = payload["trigger_id"]
    view_id = payload["view"]["id"]
    actions = payload["actions"]
    type = pm.get("type", None)
    if len(actions) and actions[0]["type"] == "button":
        selected_option = actions[0]["value"]
    else:
        selected_option = None
    external_id = payload.get("view", {}).get("external_id", None)
    try:
        view_type, __unique_id = external_id.split(".")
    except ValueError:
        view_type = None
        pass
    main_form = OrgCustomSlackFormInstance.objects.filter(id=selected_option).first()
    resource_id = None
    resource_type = main_form.template.resource
    if main_form.template.form_type == "UPDATE":
        resource_id = str(main_form.resource_object.id)
    user = main_form.user
    organization = user.organization
    slack_access_token = organization.slack_integration.access_token
    context.pop("type", None)
    view_context = {
        **context,
        "resource_type": resource_type,
        "resource_id": resource_id,
        "f": pm.get("f", selected_option),
        "u": str(user.id),
    }
    if from_workflow:
        view_context["w"] = pm.get("w")
        view_context["resource"] = resource_type
    if view_type == "add_product" or view_type == "update_product":
        product_id = pm.get("product_form")
        product_form = OrgCustomSlackFormInstance.objects.get(id=product_id)
        if view_type == "add_product":
            pricebookentry = PricebookEntry.objects.get(
                integration_id=product_form.saved_data["PricebookEntryId"]
            )
            blocks = main_form.generate_form(
                product_form.saved_data, Pricebook2Id=pricebookentry.pricebook.integration_id
            )
            title = "Add Product"
            callback_id = slack_const.PROCESS_SUBMIT_PRODUCT
        else:
            title = "Edit Product"
            callback_id = slack_const.PROCESS_UPDATE_PRODUCT
            blocks = main_form.generate_form(product_form.saved_data)
        if len(blocks):
            data = {
                "trigger_id": trigger_id,
                "view_id": view_id,
                "view": {
                    "type": "modal",
                    "title": {"type": "plain_text", "text": title},
                    "submit": {"type": "plain_text", "text": "Submit"},
                    "blocks": blocks,
                    "private_metadata": json.dumps(pm),
                    "callback_id": callback_id,
                },
            }
        try:
            slack_requests.generic_request(url, data, access_token=slack_access_token)
        except Exception as e:
            # exception will only be thrown for caught errors using decorator
            return logger.exception(
                f"Failed To Update via command for user  {str(user.id)} email {user.email} {e}"
            )
        return
    form_blocks = (
        get_block_set(view_type, view_context)
        if view_type
        else main_form.generate_form(main_form.saved_data)
    )
    if main_form and not from_workflow:
        try:
            stage_name = "StageName" if user.crm == "SALESFORCE" else "dealstage"
            index, stage_block = block_finder(stage_name, form_blocks)
        except ValueError:
            # did not find the block
            stage_block = None
            pass

        if stage_block:
            stage_block = {
                **stage_block,
                "accessory": {
                    **stage_block["accessory"],
                    "action_id": f"{slack_const.COMMAND_FORMS__STAGE_SELECTED}?u={str(user.id)}&f={str(main_form.id)}",
                },
            }
            form_blocks = [*form_blocks[:index], stage_block, *form_blocks[index + 1 :]]

    private_metadata = {
        "channel_id": payload.get("container").get("channel_id"),
        "f": str(main_form.id),
        "u": str(user.id),
    }

    title_text = (
        f"Update {resource_type}"
        if (view_type == "update_modal_block_set" or not view_type)
        else f"Create {resource_type}"
    )
    if type == "alert":
        callback_id = slack_const.PROCESS_SUBMIT_ALERT_RESOURCE_DATA
        submit_text = "Update"
    elif type == "digest":
        callback_id = slack_const.PROCESS_SUBMIT_DIGEST_RESOURCE_DATA
    else:
        callback_id = slack_const.COMMAND_FORMS__SUBMIT_FORM
        submit_text = (
            "Update" if (view_type == "update_modal_block_set" or not view_type) else "Create"
        )

    private_metadata.update(view_context)
    data = {
        "trigger_id": trigger_id,
        "view_id": view_id,
        "view": {
            "type": "modal",
            "callback_id": callback_id,
            "title": {"type": "plain_text", "text": title_text,},
            "blocks": form_blocks,
            "submit": {"type": "plain_text", "text": submit_text, "emoji": True},
            "private_metadata": json.dumps(private_metadata),
            "external_id": f"{view_type}.{str(uuid.uuid4())}",
        },
    }
    try:
        slack_requests.generic_request(url, data, access_token=slack_access_token)
    except Exception as e:
        # exception will only be thrown for caught errors using decorator
        return logger.exception(
            f"Failed To Update via command for user  {str(user.id)} email {user.email} {e}"
        )
    return


@slack_api_exceptions(rethrow=True)
@processor()
def process_return_to_form_button(payload, context):
    """if an error occurs on create/update commands when the return button is clicked regen form"""
    form_ids = context.get("f").split(",")
    trigger_id = payload["trigger_id"]
    forms = OrgCustomSlackFormInstance.objects.filter(id__in=form_ids)
    main_form = forms.filter(
        template__form_type__in=[slack_const.FORM_TYPE_CREATE, slack_const.FORM_TYPE_UPDATE]
    ).first()
    stage_form = forms.filter(template__form_type="STAGE_GATING").first()
    blocks = main_form.generate_form(main_form.saved_data)
    title = (
        f"Update {main_form.template.resource}"
        if main_form.template.form_type == "UPDATE"
        else f"Create {main_form.template.resource}"
    )
    if stage_form:
        submit_button_text = "Next"
        callback_id = slack_const.COMMAND_FORMS__PROCESS_NEXT_PAGE
    else:
        submit_button_text = "Submit"
        callback_id = slack_const.COMMAND_FORMS__SUBMIT_FORM
    message_ref = f"{payload['channel']['id']}|{payload['message']['ts']}"
    context.update({"message_ref": message_ref})
    data = {
        "trigger_id": trigger_id,
        "view": {
            "type": "modal",
            "callback_id": callback_id,
            "title": {"type": "plain_text", "text": title},
            "blocks": blocks,
            "submit": {"type": "plain_text", "text": submit_button_text},
            "private_metadata": json.dumps(context),
        },
    }
    try:
        slack_requests.generic_request(
            slack_const.SLACK_API_ROOT + slack_const.VIEWS_OPEN,
            data,
            access_token=main_form.user.organization.slack_integration.access_token,
        )
    except InvalidBlocksException as e:
        return logger.exception(
            f"Failed To Generate Slack Workflow Interaction for user {u.full_name} email {u.email} {e}"
        )
    except InvalidBlocksFormatException as e:
        return logger.exception(
            f"Failed To Generate Slack Workflow Interaction for user {u.full_name} email {u.email} {e}"
        )
    except UnHandeledBlocksException as e:
        return logger.exception(
            f"Failed To Generate Slack Workflow Interaction for user {u.full_name} email {u.email} {e}"
        )
    except InvalidAccessToken as e:
        return logger.exception(
            f"Failed To Generate Slack Workflow Interaction for user {u.full_name} email {u.email} {e}"
        )


@processor(required_context="u")
def process_show_engagement_modal(payload, context):
    u = User.objects.get(id=context.get("u"))
    trigger_id = payload["trigger_id"]
    org = u.organization
    access_token = org.slack_integration.access_token
    state = None
    system = context.get("system", None)
    view_id = None
    if "view" in payload:
        state = payload["view"]["state"]["values"]
        view_id = payload["view"]["id"]
        pm = json.loads(payload["view"]["private_metadata"])
        system = pm.get("system")
    if system == "salesloft":
        callback_id = slack_const.ADD_TO_CADENCE
        title = "Add to a Cadence"
        blockset = "cadence_modal_blockset"
    else:
        callback_id = slack_const.ADD_TO_SEQUENCE
        title = "Add to a Sequence"
        blockset = "sequence_modal_blockset"
    loading_view_data = send_loading_screen(
        access_token,
        f"Putting together your {'cadences' if system == 'salesloft' else 'sequences'}",
        f"{'update' if state else 'open'}",
        str(u.id),
        trigger_id,
        view_id,
    )
    resource_id = (
        [value.get("selected_option") for value in state.get("selected_object", {}).values()][
            0
        ].get("value")
        if state
        else context.get("resource_id")
    )
    resource_type = context.get("resource_type")
    resource_name = CRM_SWITCHER[u.crm][resource_type]["model"].objects.get(id=resource_id).name
    private_metadata = {
        "resource_name": resource_name,
        "resource_id": resource_id,
        "resource_type": resource_type,
    }
    if state is None:
        private_metadata.update({"channel_id": payload["channel"]["id"]})
    private_metadata.update(context)

    data = {
        "view_id": loading_view_data["view"]["id"],
        "view": {
            "type": "modal",
            "callback_id": callback_id,
            "title": {"type": "plain_text", "text": title},
            "blocks": get_block_set(
                blockset,
                context={
                    "u": context.get("u"),
                    "resource_name": resource_name,
                    "resource_id": resource_id,
                    "resource_type": resource_type,
                },
            ),
            "submit": {"type": "plain_text", "text": "Submit", "emoji": True},
            "private_metadata": json.dumps(private_metadata),
        },
    }
    try:
        slack_requests.generic_request(
            slack_const.SLACK_API_ROOT + slack_const.VIEWS_UPDATE, data, access_token=access_token
        )
    except InvalidBlocksException as e:
        return logger.exception(
            f"Failed To Generate Slack Workflow Interaction for user {u.full_name} email {u.email} {e}"
        )
    except InvalidBlocksFormatException as e:
        return logger.exception(
            f"Failed To Generate Slack Workflow Interaction for user {u.full_name} email {u.email} {e}"
        )
    except UnHandeledBlocksException as e:
        return logger.exception(
            f"Failed To Generate Slack Workflow Interaction for user {u.full_name} email {u.email} {e}"
        )
    except InvalidAccessToken as e:
        return logger.exception(
            f"Failed To Generate Slack Workflow Interaction for user {u.full_name} email {u.email} {e}"
        )


@processor(required_context="u")
def process_get_notes(payload, context):
    u = User.objects.get(id=context.get("u"))
    type = context.get("type", None)
    org = u.organization
    access_token = org.slack_integration.access_token
    trigger_id = payload["trigger_id"]

    try:
        view_id = (
            payload["container"]["view_id"] if "container" in payload else payload["view"]["id"]
        )
    except KeyError:
        view_id = None
    view_action = "open" if type in ["alert", "prep"] else "push"
    loading_view_data = send_loading_screen(
        access_token, "Putting your notes together", view_action, str(u.id), trigger_id, view_id
    )
    resource_type = context.get("resource_type", "Opportunity")
    resource_id = (
        context.get("resource_id")
        if type in ["alert", "recap"]
        else payload["view"]["state"]["values"]["selected_object"][
            f"GET_NOTES?u={u.id}&resource_type={resource_type}"
        ]["selected_option"]["value"]
    )
    resource = CRM_SWITCHER[u.crm][resource_type]["model"].objects.get(id=resource_id)
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
    note_blocks = [
        block_builders.header_block(
            f"Notes for {resource.name if resource_type not in ['Lead', 'Contact'] else resource.email}"
        )
        if note_data
        else block_builders.header_block(
            f"No notes for {resource.name}, start leaving notes! :smiley:"
        )
    ]
    if note_data:
        for note in note_data:
            note_title = "N/A" if note[1] is None else note[1]
            if note[2] is None and note_title == "N/A":
                continue
            date = note[0].date() if note[0] is not None else " "
            current_stage = note[3]
            previous_stage = note[4]
            block_message = f"*{date} - {note_title}*\n"
            if current_stage and previous_stage:
                if current_stage != previous_stage:
                    block_message += f"Stage: ~{previous_stage}~ :arrow_right: {current_stage} \n"
            try:
                note_message = replace_tags(note[2])
            except Exception:
                note_message = note[2]
            if note_message and len(note_message) > 255:
                note_message = str(note_message)[:255] + "..."
            block_message += f"\nNotes:\n {note_message}"
            note_blocks.append(block_builders.simple_section(block_message, "mrkdwn"))
            note_blocks.append({"type": "divider"})
    if len(note_blocks) == 1:
        note_blocks = [
            block_builders.header_block(
                f"No notes for {resource.name}, start leaving notes! :smiley:"
            )
        ]
    data = {
        "view_id": loading_view_data["view"]["id"],
        "view": {
            "type": "modal",
            "callback_id": "NONE",
            "title": {"type": "plain_text", "text": "Notes"},
            "blocks": note_blocks,
        },
    }
    url = slack_const.SLACK_API_ROOT + slack_const.VIEWS_UPDATE
    slack_requests.generic_request(url, data, access_token=access_token)
    return


@processor(required_context="u")
def process_get_call_recording(payload, context):
    type = context.get("type", None)
    resource_id = context.get("resource_id", None)
    resource_type = context.get("resource_type", None)
    user = User.objects.get(id=context.get("u"))
    access_token = user.organization.slack_integration.access_token
    trigger_id = payload["trigger_id"] if "trigger_id" in payload else None
    state = None
    view_id = None
    if "view" in payload:
        state = payload["view"]["state"]["values"]
        view_id = payload["view"]["id"]
    loading_view_data = send_loading_screen(
        access_token,
        "Checking for call details...",
        f"{'push' if state is not None else 'open'}",
        str(user.id),
        trigger_id,
        view_id,
    )
    form_id = context.get("form_id", None)
    url = slack_const.SLACK_API_ROOT + slack_const.VIEWS_UPDATE
    if form_id is None:
        if resource_id is None:
            resource_type = [
                value.get("selected_option")
                for value in state.get("selected_object_type", {}).values()
            ][0].get("value")

            resource_id = [
                value.get("selected_option") for value in state.get("selected_object", {}).values()
            ][0].get("value")
    else:
        form = OrgCustomSlackFormInstance.objects.get(id=form_id)
        resource_type = form.template.resource
    user_tz = datetime.now(pytz.timezone(user.timezone)).strftime("%z")
    gong_auth = GongAuthAccount.objects.get(organization=user.organization)
    curr_date_str = (
        str((date.today() - timezone.timedelta(days=90)))
        + "T01:00:00"
        + f"{user_tz[:3]}:{user_tz[3:]}"
    )
    if type == "recap":
        resource = form.resource_object
    else:
        resource = CRM_SWITCHER[user.crm][resource_type]["model"].objects.get(id=resource_id)
        if resource_type in ["Opportunity", "Contact"]:
            resource_ids = [resource.secondary_data["Id"]]
            if resource.account:
                resource_ids.append(resource.account.secondary_data["Id"])
        else:
            resource_ids = [resource.secondary_data["Id"]]
    attempts = 1
    while True:
        try:
            call_res = gong_auth.helper_class.check_for_current_call(
                curr_date_str, resource.owner.gong_account.gong_id
            )
            blocks = generate_call_block(call_res, resource.integration_id, resource_type)
            break
        except gong_exceptions.TokenExpired:
            if attempts >= 5:
                return
            else:
                gong_auth.regenerate_token()
                attempts += 1
        except gong_exceptions.InvalidRequest:
            blocks = [
                block_builders.simple_section(
                    f"There was no calls associated with this {resource_type}"
                ),
                block_builders.context_block(
                    "*Gong may still be processing this call, check back in a bit"
                ),
            ]
            break
        except Exception as e:
            logger.exception(f"Gong call error: {e}")
            blocks = [
                block_builders.simple_section("There was an error retreiving your call"),
                block_builders.context_block(
                    "*Gong may still be processing this call, check back in a bit"
                ),
            ]
            break
    modal_data = {
        "view_id": loading_view_data["view"]["id"],
        "view": {
            "type": "modal",
            "title": {"type": "plain_text", "text": "Call Details"},
            "blocks": blocks,
        },
    }
    try:
        res = slack_requests.generic_request(url, modal_data, access_token=access_token)
    except Exception as e:
        return logger.exception(f"Get call recording error ----- {e}")
    return


@processor(required_context="u")
def process_meeting_details(payload, context):
    url = slack_const.SLACK_API_ROOT + slack_const.VIEWS_OPEN
    trigger_id = payload["trigger_id"]
    u = User.objects.get(id=context.get("u"))
    org = u.organization
    blocks = payload["message"]["blocks"]
    blocks.pop()
    blocks.append({"type": "section", "text": {"type": "mrkdwn", "text": "Meeting Booked :+1:"}})
    private_metadata = {
        "original_message_channel": payload["channel"]["id"],
        "original_message_timestamp": payload["message"]["ts"],
        "current_block": blocks,
    }
    private_metadata.update(context)
    data = {
        "trigger_id": trigger_id,
        "view": {
            "type": "modal",
            "callback_id": slack_const.ZOOM_MEETING__SCHEDULE_MEETING,
            "title": {"type": "plain_text", "text": "Zoom Meeting Scheduler"},
            "blocks": get_block_set("schedule_meeting_modal", context=context),
            "submit": {"type": "plain_text", "text": "Save",},
            "private_metadata": json.dumps(private_metadata),
        },
    }
    try:
        slack_requests.generic_request(url, data, access_token=org.slack_integration.access_token)
    except InvalidBlocksException as e:
        return logger.exception(
            f"Failed To Generate Slack Workflow Interaction for user {u.full_name} email {u.email} {e}"
        )
    except InvalidBlocksFormatException as e:
        return logger.exception(
            f"Failed To Generate Slack Workflow Interaction for user {u.full_name} email {u.email} {e}"
        )
    except UnHandeledBlocksException as e:
        return logger.exception(
            f"Failed To Generate Slack Workflow Interaction for user {u.full_name} email {u.email} {e}"
        )
    except InvalidAccessToken as e:
        return logger.exception(
            f"Failed To Generate Slack Workflow Interaction for user {u.full_name} email {u.email} {e}"
        )


@slack_api_exceptions(rethrow=True)
@processor()
def choose_reset_meeting_day(payload, context):
    user = User.objects.get(id=context.get("u"))
    if user.slack_integration:
        slack = UserSlackIntegration.objects.filter(
            slack_id=user.slack_integration.slack_id
        ).first()
        if not slack:
            return
    access_token = user.organization.slack_integration.access_token
    state = payload["view"]["state"]["values"]
    selected_day = state["selected_day"][
        f"{slack_const.CHOOSE_RESET_MEETING_DAY}?u={context.get('u')}"
    ]["selected_option"]["value"]
    url = slack_const.SLACK_API_ROOT + slack_const.VIEWS_UPDATE
    data = {
        "view_id": payload["view"]["id"],
        "view": {
            "type": "modal",
            "title": {"type": "plain_text", "text": "Reset Meetings"},
            "blocks": get_block_set(
                "reset_meeting_block_set", {"u": str(user.id), "meeting_day": selected_day},
            ),
            "external_id": f"reset_meeting_block_set.{str(uuid.uuid4())}",
            "callback_id": slack_const.RESET_SELECTED_MEETING_DAYS,
            "submit": {"type": "plain_text", "text": "Submit",},
            "private_metadata": json.dumps(context),
        },
    }
    slack_requests.generic_request(url, data, access_token=access_token)
    return


#########################################################
# ALERT ACTIONS
#########################################################


@slack_api_exceptions(rethrow=True)
@processor()
def process_paginate_alerts(payload, context):
    channel_id = payload.get("channel", {}).get("id", None)
    ts = payload.get("message", {}).get("ts", None)
    user_slack_id = payload.get("user", {}).get("id", None)
    user = User.objects.filter(slack_integration__slack_id=user_slack_id).first()
    loading_block = get_block_set("loading", {"message": "Gathering workflow data..."})
    blocks = payload.get("message").get("blocks")[:3]
    blocks.append({"type": "divider"})
    blocks.extend(loading_block)
    slack_requests.update_channel_message(
        channel_id, ts, user.organization.slack_integration.access_token, block_set=blocks
    )
    emit_send_paginated_alerts(payload, context)
    return


@slack_api_exceptions(rethrow=True)
@processor()
def process_paginate_inline_alerts(payload, context):
    emit_send_next_page_paginated_inline_alerts(payload, context)
    channel_id = payload.get("channel", {}).get("id", None)
    ts = payload.get("message", {}).get("ts", None)
    user_slack_id = payload.get("user", {}).get("id", None)
    user = User.objects.filter(slack_integration__slack_id=user_slack_id).first()
    loading_block = get_block_set("loading", {"message": "Gathering workflow data..."})
    blocks = payload.get("message").get("blocks")[:3]
    blocks.append({"type": "divider"})
    blocks.extend(loading_block)
    slack_requests.update_channel_message(
        channel_id, ts, user.organization.slack_integration.access_token, block_set=blocks
    )

    return


@slack_api_exceptions(rethrow=True)
@processor()
def process_paginate_notes(payload, context):
    channel_id = payload.get("channel", {}).get("id", None)
    ts = payload.get("message", {}).get("ts", None)
    user_slack_id = payload.get("user", {}).get("id", None)
    user = User.objects.filter(slack_integration__slack_id=user_slack_id).first()
    loading_block = get_block_set("loading", {"message": "Gathering workflow data..."})
    blocks = payload.get("message").get("blocks")[:3]
    blocks.append({"type": "divider"})
    blocks.extend(loading_block)
    slack_requests.update_channel_message(
        channel_id, ts, user.organization.slack_integration.access_token, block_set=blocks
    )
    emit_send_paginated_notes(payload, context)
    return


@slack_api_exceptions(rethrow=True)
@processor()
def process_switch_alert_message(payload, context):
    channel_id = payload.get("channel", {}).get("id", None)
    ts = payload.get("message", {}).get("ts", None)
    user = User.objects.get(id=context.get("u"))
    config_id = context.get("config_id")
    config = AlertConfig.objects.get(id=config_id)
    invocation = context.get("invocation")
    form = user.team.team_forms.filter(
        form_type="UPDATE", resource=config.template.resource_type
    ).first()
    switch_to = context.get("switch_to")
    header_block = payload["message"]["blocks"][0]
    blocks = [
        header_block,
        get_block_set(
            "initial_inline_blockset",
            context={
                "u": str(user.id),
                "invocation": invocation,
                "config_id": str(config_id),
                "channel": channel_id,
                "switch_to": f"{'message' if switch_to == 'inline' else 'inline'}",
            },
        ),
    ]
    if context.get("switch_to") == "inline":
        fields = form.to_slack_options()
        blocks.append(
            block_builders.static_select(
                "Choose Field",
                fields,
                action_id=action_with_params(
                    slack_const.PROCESS_INLINE_FIELD_SELECTED,
                    params=[f"invocation={invocation}", f"config_id={config_id}",],
                ),
            ),
        )

    else:
        options = USER_APP_OPTIONS(user, config.template.resource_type)
        blocks.append(
            block_builders.static_select(
                "Pick an action",
                options,
                action_id=action_with_params(
                    slack_const.PROCESS_SHOW_APP_SELECT,
                    params=[
                        f"invocation={invocation}",
                        f"config_id={config_id}",
                        f"u={str(user.id)}",
                    ],
                ),
                placeholder="Connected Apps",
            ),
        )
        # process_paginate_alerts(payload, context)
    slack_requests.update_channel_message(
        channel_id, ts, user.organization.slack_integration.access_token, block_set=blocks
    )
    return


@slack_api_exceptions(rethrow=True)
@processor()
def process_inline_field_selected(payload, context):
    emit_send_paginated_inline_alerts(payload, context)
    channel_id = payload.get("channel", {}).get("id", None)
    ts = payload.get("message", {}).get("ts", None)
    user_slack_id = payload.get("user", {}).get("id", None)
    user = User.objects.filter(slack_integration__slack_id=user_slack_id).first()
    loading_block = get_block_set("loading", {"message": "Gathering workflow data..."})
    blocks = payload.get("message").get("blocks")[:3]
    blocks.append({"type": "divider"})
    blocks.extend(loading_block)
    slack_requests.update_channel_message(
        channel_id, ts, user.organization.slack_integration.access_token, block_set=blocks
    )
    return


@slack_api_exceptions(rethrow=True)
@processor()
def process_paginate_engagement_state(payload, context):
    channel_id = payload.get("channel", {}).get("id", None)
    ts = payload.get("message", {}).get("ts", None)
    user_slack_id = payload.get("user", {}).get("id", None)
    user = User.objects.filter(slack_integration__slack_id=user_slack_id).first()
    loading_block = get_block_set("loading", {"message": "Gathering workflow data..."})
    blocks = payload.get("message").get("blocks")[:3]
    blocks.append({"type": "divider"})
    blocks.extend(loading_block)
    slack_requests.update_channel_message(
        channel_id, ts, user.organization.slack_integration.access_token, block_set=blocks
    )
    emit_process_paginated_engagement_state(payload, context)
    return


@slack_api_exceptions(rethrow=True)
@processor()
def process_paginate_call_recordings(payload, context):
    channel_id = payload.get("channel", {}).get("id", None)
    ts = payload.get("message", {}).get("ts", None)
    user_slack_id = payload.get("user", {}).get("id", None)
    user = User.objects.filter(slack_integration__slack_id=user_slack_id).first()
    loading_block = get_block_set("loading", {"message": "Gathering workflow data..."})
    blocks = payload.get("message").get("blocks")[:3]
    blocks.append({"type": "divider"})
    blocks.extend(loading_block)
    slack_requests.update_channel_message(
        channel_id, ts, user.organization.slack_integration.access_token, block_set=blocks
    )
    emit_process_paginated_call_recordings(payload, context)
    return


@slack_api_exceptions(rethrow=True)
@processor()
def process_engagement_details(payload, context):
    channel_id = payload.get("channel", {}).get("id", None)
    ts = payload.get("message", {}).get("ts", None)
    user_slack_id = payload.get("user", {}).get("id", None)
    user = User.objects.filter(slack_integration__slack_id=user_slack_id).first()
    loading_block = get_block_set("loading", {"message": "Gathering workflow data..."})
    blocks = payload.get("message").get("blocks")[:3]
    blocks.append({"type": "divider"})
    blocks.extend(loading_block)
    slack_requests.update_channel_message(
        channel_id, ts, user.organization.slack_integration.access_token, block_set=blocks
    )
    emit_process_paginated_engagement_details(payload, context)
    return


CONNECTED_APPS_SWITCHER = {
    "view_notes": process_paginate_notes,
    "update_crm": process_paginate_alerts,
    "engagement_state": process_paginate_engagement_state,
    "engagement_details": process_engagement_details,
    "call_recordings": process_paginate_call_recordings,
}


@slack_api_exceptions(rethrow=True)
@processor()
def process_connected_app_selected(payload, context):
    context_app = context.get("app", None)
    app = payload["actions"][0]["selected_option"]["value"] if context_app is None else context_app
    app_func = CONNECTED_APPS_SWITCHER[app]
    app_func(payload, context)
    return


@slack_api_exceptions(rethrow=True)
@processor()
def process_submit_inline_alert_data(payload, context):
    user_slack_id = payload.get("user", {}).get("id", None)
    user = User.objects.filter(slack_integration__slack_id=user_slack_id).first()
    update_function = INLINE_UPDATE_FUNCTION(user.crm)
    update_function(payload, context)
    channel_id = payload.get("channel", {}).get("id", None)
    ts = payload.get("message", {}).get("ts", None)

    loading_block = get_block_set("loading", {"message": "Submitting data..."})
    blocks = payload.get("message").get("blocks")[:3]
    blocks.append({"type": "divider"})
    blocks.extend(loading_block)
    slack_requests.update_channel_message(
        channel_id, ts, user.organization.slack_integration.access_token, block_set=blocks
    )
    return


@slack_api_exceptions(rethrow=True)
@processor(required_context=["resource_type", "u"])
def process_show_alert_update_resource_form(payload, context):
    from managr.slack.models import OrgCustomSlackForm, OrgCustomSlackFormInstance

    user = User.objects.get(id=context.get("u"))
    access_token = user.organization.slack_integration.access_token
    trigger_id = payload["trigger_id"]
    crm = "Salesforce" if user.crm == "SALESFORCE" else "HubSpot"
    loading_view_data = send_loading_screen(
        access_token,
        f"{crm} is being a bit slow :sleeping:… please give it a few seconds",
        "open",
        str(user.id),
        trigger_id,
    )
    resource_id = context.get("resource_id")
    alert_instance = AlertInstance.objects.get(id=context.get("alert_id"))
    resource_type = context.get("resource_type")
    show_submit_button_if_fields_added = False
    stage_form = None
    # HACK forms are generated with a helper fn currently stagename takes a special action id to update forms
    # we need to manually change this action_id
    if alert_instance.form_instance.all():
        slack_form = user.custom_slack_form_instances.filter(
            alert_instance_id=alert_instance, template__resource=resource_type
        ).first()
    else:
        template = (
            OrgCustomSlackForm.objects.for_user(user)
            .filter(Q(resource=resource_type, form_type="UPDATE"))
            .first()
        )
        slack_form = OrgCustomSlackFormInstance.objects.create(
            template=template,
            resource_id=resource_id,
            user=user,
            alert_instance_id=alert_instance,
            update_source="alert",
        )
    if slack_form:
        stage_name = "StageName" if user.crm == "SALESFORCE" else "dealstage"
        current_stage = slack_form.resource_object.secondary_data.get(stage_name)
        stage_template = (
            OrgCustomSlackForm.objects.for_user(user).filter(stage=current_stage).first()
            if current_stage
            else None
        )
        form_ids = [str(slack_form.id)]
        if stage_template:
            stage_form = OrgCustomSlackFormInstance.objects.create(
                template=stage_template, resource_id=resource_id, user=user, update_source="alert"
            )
            form_ids.append(str(stage_form.id))
        context.update({"f": ",".join(form_ids)})
    blocks = get_block_set(
        "update_modal_block_set",
        context={**context, "resource_type": resource_type, "resource_id": resource_id},
    )
    if slack_form:
        try:
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
                    "action_id": f"{slack_const.COMMAND_FORMS__STAGE_SELECTED}?u={str(user.id)}&f={str(slack_form.id)}&type=alert",
                },
            }
            blocks = [*blocks[:index], block, *blocks[index + 1 :]]

        try:
            index, block = block_finder(slack_const.NO_FORM_FIELDS, blocks)
        except ValueError:
            # did not find the block
            show_submit_button_if_fields_added = True
            pass

    else:
        blocks.append(
            block_builders.simple_section("Please re-select your salesforce resource to update")
        )
        show_submit_button_if_fields_added = False
    private_metadata = {
        "channel_id": payload.get("container").get("channel_id"),
        "message_ts": payload.get("container").get("message_ts"),
    }
    private_metadata.update(context)
    if user.organization.has_products and resource_type == "Opportunity":
        params = [
            f"f={str(slack_form.id)}",
            f"u={str(user.id)}",
            "type=alert",
        ]
        if slack_form.resource_object.secondary_data["Pricebook2Id"]:
            params.append(f"pricebook={slack_form.resource_object.secondary_data['Pricebook2Id']}")
        blocks.append(
            block_builders.actions_block(
                [
                    block_builders.simple_button_block(
                        "Add Product",
                        "ADD_PRODUCT",
                        action_id=action_with_params(
                            slack_const.PROCESS_ADD_PRODUCTS_FORM,
                            params=[
                                f"f={str(slack_form.id)}",
                                f"u={str(user.id)}",
                                "type=command",
                            ],
                        ),
                    )
                ],
                block_id="ADD_PRODUCT_BUTTON",
            ),
        )
        current_products = user.salesforce_account.list_resource_data(
            "OpportunityLineItem",
            0,
            filter=[
                "AND IsDeleted = false",
                f"AND OpportunityId = '{slack_form.resource_object.integration_id}'",
            ],
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
                        "main_form": str(slack_form.id),
                    },
                )
                blocks.append(product_block)
    private_metadata.update(
        {"alert_id": str(alert_instance.id), "current_page": context.get("current_page")}
    )

    data = {
        "view_id": loading_view_data["view"]["id"],
        "view": {
            "type": "modal",
            "title": {"type": "plain_text", "text": f"Update {resource_type}"},
            "blocks": blocks,
            "private_metadata": json.dumps(private_metadata),
            "external_id": f"update_alert_modal_block_set.{str(uuid.uuid4())}",
        },
    }
    if show_submit_button_if_fields_added:
        if stage_form:
            submit_button_text = "Next"
            callback_id = slack_const.COMMAND_FORMS__PROCESS_NEXT_PAGE
        else:
            submit_button_text = "Update"
            callback_id = slack_const.PROCESS_SUBMIT_ALERT_RESOURCE_DATA

        data["view"]["submit"] = {"type": "plain_text", "text": submit_button_text, "emoji": True}
        data["view"]["callback_id"] = callback_id
    slack_requests.generic_request(
        slack_const.SLACK_API_ROOT + slack_const.VIEWS_UPDATE, data, access_token=access_token
    )


@slack_api_exceptions(rethrow=True)
@processor(required_context=["u"])
def process_alert_actions(payload, context):
    state = payload["actions"]
    select_check = state[0].get("selected_option", None)
    if select_check:
        selected = select_check.get("value")
        alert_action_switcher = {
            "update_crm": process_show_alert_update_resource_form,
            "call_details": process_get_call_recording,
            "get_notes": process_get_notes,
            "add_to_sequence": process_show_engagement_modal,
            "add_to_cadence": process_show_engagement_modal,
        }
        if selected in ["add_to_sequence", "add_to_cadence"]:
            context["system"] = "salesloft" if selected == "add_to_cadence" else "outreach"
        else:
            context["type"] = "alert"
        return alert_action_switcher[selected](payload, context)
    return


@slack_api_exceptions(rethrow=True)
@processor()
def process_show_bulk_update_form(payload, context):
    user = User.objects.get(id=context.get("u"))
    config_id = context.get("config_id")
    invocation = context.get("invocation")
    config = AlertConfig.objects.get(id=config_id)
    config_list = list(
        AlertInstance.objects.filter(config_id=config_id, invocation=invocation).values_list(
            "resource_id", flat=True
        )
    )
    model_object = CRM_SWITCHER[user.crm][config.template.resource_type]["model"]
    resource_list = model_object.objects.filter(id__in=config_list)
    resource_options = [resource.as_slack_option for resource in resource_list]
    form = user.team.team_forms.filter(
        form_type="UPDATE", resource=config.template.resource_type
    ).first()
    fields = form.to_slack_options()
    blocks = [
        block_builders.static_select(
            "Fields",
            options=fields,
            action_id=action_with_params(
                slack_const.CHOOSE_CRM_FIELD,
                params=[f"u={str(user.id)}", f"resource_type={config.template.resource_type}"],
            ),
            block_id="CRM_FIELDS",
        ),
        block_builders.multi_static_select(
            label=config.template.resource_type,
            options=resource_options,
            initial_options=resource_options,
            block_id="RESOURCES",
            action_id="SELECTED_RESOURCES",
        ),
    ]
    data = {
        "message_ts": payload["container"]["message_ts"],
        "channel_id": payload["container"]["channel_id"],
        "resource_type": config.template.resource_type,
    }
    loading_view_data = {
        "trigger_id": payload["trigger_id"],
        "view": {
            "type": "modal",
            "title": {"type": "plain_text", "text": "Bulk Update"},
            "blocks": blocks,
            "private_metadata": json.dumps(data),
        },
    }

    slack_requests.generic_request(
        slack_const.SLACK_API_ROOT + slack_const.VIEWS_OPEN,
        loading_view_data,
        access_token=user.organization.slack_integration.access_token,
    )
    return


@slack_api_exceptions(rethrow=True)
@processor()
def process_select_crm_field(payload, context):
    user = User.objects.get(id=context.get("u"))
    pm = json.loads(payload["view"]["private_metadata"])
    view_id = payload["view"]["id"]
    action = payload["actions"][0]
    blocks = payload["view"]["blocks"]
    selected_value = action["selected_option"]["value"]
    field = user.object_fields.filter(
        api_name=selected_value, crm_object=context.get("resource_type")
    ).first()
    try:
        f_index, f_block = block_finder("CRM_FIELD", blocks)
    except ValueError:
        # did not find the block
        f_block = None
        pass
    index, block = block_finder("CRM_FIELDS", blocks)
    slack_field = field.to_slack_field()
    if f_block:
        blocks = [*blocks[:f_index], slack_field, *blocks[f_index + 1 :]]
    else:
        blocks.insert(index + 1, slack_field)
    pm.update(**context)
    loading_view_data = {
        "view_id": view_id,
        "view": {
            "type": "modal",
            "title": {"type": "plain_text", "text": "Bulk Update"},
            "blocks": blocks,
            "submit": {"type": "plain_text", "text": "Bulk Update", "emoji": True},
            "private_metadata": json.dumps(pm),
            "callback_id": slack_const.PROCESS_SUBMIT_BULK_UPDATE,
        },
    }
    slack_requests.generic_request(
        slack_const.SLACK_API_ROOT + slack_const.VIEWS_UPDATE,
        loading_view_data,
        access_token=user.organization.slack_integration.access_token,
    )
    return


@slack_api_exceptions(rethrow=True)
@processor()
def process_get_summary_fields(payload, context):
    user = User.objects.get(id=context.get("u"))
    config_id = context.get("config_id")
    config = AlertConfig.objects.get(id=config_id)
    form = user.team.team_forms.filter(
        form_type="UPDATE", resource=config.template.resource_type
    ).first()
    fields = form.custom_fields.all().exclude(
        Q(data_type__in=["Reference", "String", "TextArea"]) | Q(api_name="Amount")
    )
    if len(fields):
        fields_options = [block_builders.option(field.label, field.api_name) for field in fields]
        blocks = [
            block_builders.multi_static_select(
                "Fields to Summarize",
                options=fields_options,
                action_id=action_with_params(
                    slack_const.CHOOSE_CRM_FIELDS, params=[f"u={str(user.id)}",],
                ),
                block_id="CRM_FIELDS",
            ),
            block_builders.context_block("*Amount total will be auto calculated"),
        ]
    else:
        blocks = [
            block_builders.simple_section(
                "You do not have any fields on your form that allow summarization"
            )
        ]
    data = {
        **context,
        "message_ts": payload["container"]["message_ts"],
        "channel_id": payload["container"]["channel_id"],
        "trigger_id": payload["trigger_id"],
    }
    loading_view_data = {
        "trigger_id": payload["trigger_id"],
        "view": {
            "type": "modal",
            "title": {"type": "plain_text", "text": "Workflow Summary"},
            "blocks": blocks,
            "private_metadata": json.dumps(data),
            "callback_id": slack_const.GET_SUMMARY,
        },
    }
    if len(fields):
        loading_view_data["view"]["submit"] = {
            "type": "plain_text",
            "text": "Get Summary",
            "emoji": True,
        }
    slack_requests.generic_request(
        slack_const.SLACK_API_ROOT + slack_const.VIEWS_OPEN,
        loading_view_data,
        access_token=user.organization.slack_integration.access_token,
    )
    return


@processor()
def process_get_engagement_details(payload, context):
    user = User.objects.get(id=context.get("u"))
    loading_view_data = send_loading_screen(
        user.organization.slack_integration.access_token,
        f"Checking Outreach for contacts",
        "open",
        str(user.id),
        payload["trigger_id"],
    )
    route = CRM_SWITCHER[user.crm][context.get("resource_type")]["model"]
    resource = route.objects.filter(id=context.get("resource_id")).first()
    account = resource.account.name if (hasattr(resource, "account") and resource.account) else None
    contacts = []
    while True:
        try:
            if context.get("resource_type") == "Lead":
                contacts = user.engagement_account.helper_class.get_contacts_by_email(
                    resource.email
                ).get("data", [])
            else:
                if account:
                    contacts = user.engagement_account.helper_class.get_contacts_for_account(
                        account
                    ).get("data", [])
            break
        except OutreachTokenExpired:
            user.engagement_account.regenerate_token()
        except Exception as e:
            logger.exception(f"Contact detail error: <{e}>")
            break
    blocks = []
    if len(contacts):
        for contact in contacts:
            contact_data = contact["attributes"]
            contact_string = f"Name: {contact_data['name']}\nEmails: {','.join(contact_data['emails'])}\nStage: {contact_data['stageName']}\nOpens: {contact_data['openCount']}\nReplies: {contact_data['replyCount']}\nLast Touched: {contact_data['touchedAt']}\n<{user.engagement_account.instance_url}/prospects/{contact['id']}/overview|Open in Outreach>"
            blocks.extend(
                [block_builders.simple_section(contact_string, "mrkdwn"), {"type": "divider"}]
            )
    else:
        blocks.append(
            block_builders.simple_section(
                f"Look like there's no contacts for this {context.get('resource_type')} :mag:"
            )
        )
    data = {
        "view_id": loading_view_data["view"]["id"],
        "view": {
            "type": "modal",
            "title": {"type": "plain_text", "text": "Contact Details"},
            "blocks": blocks,
        },
    }
    slack_requests.generic_request(
        slack_const.SLACK_API_ROOT + slack_const.VIEWS_UPDATE,
        data,
        access_token=user.organization.slack_integration.access_token,
    )
    return


#########################################################
# RECAP ACTIONS
#########################################################
@processor()
def process_send_recap_modal(payload, context):
    url = slack_const.SLACK_API_ROOT + slack_const.VIEWS_UPDATE
    user = User.objects.get(id=context.get("u"))
    access_token = user.organization.slack_integration.access_token
    trigger_id = payload.get("trigger_id", None)
    view_id = payload.get("view", []).get("id", None)
    action_type = "update" if view_id else "open"
    loading_data = send_loading_screen(
        access_token, "Loading users and channels", action_type, str(user.id), trigger_id, view_id
    )
    data = {
        "view_id": loading_data["view"]["id"],
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


@processor(required_context="u")
def process_show_meeting_convert_lead_form(payload, context):
    slack_account = UserSlackIntegration.objects.get(slack_id=payload["user"]["id"])
    user = slack_account.user
    blocks = get_block_set(
        "convert_meeting_lead_block_set", {"u": str(user.id), "w": context.get("w")}
    )
    private_metadata = {
        **context,
        "original_message_channel": payload["channel"]["id"],
        "original_message_timestamp": payload["message"]["ts"],
    }
    data = {
        "trigger_id": payload["trigger_id"],
        "view": {
            "type": "modal",
            "callback_id": slack_const.ZOOM_MEETING__CONVERT_LEAD,
            "title": {"type": "plain_text", "text": "Convert Lead"},
            "blocks": blocks,
            "submit": {"type": "plain_text", "text": "Convert"},
            "private_metadata": json.dumps(private_metadata),
        },
    }
    try:
        slack_requests.generic_request(
            slack_const.SLACK_API_ROOT + slack_const.VIEWS_OPEN,
            data,
            access_token=user.organization.slack_integration.access_token,
        )
    except InvalidBlocksException as e:
        return logger.exception(
            f"Failed To Generate Slack Convert Lead form for email {user.email} {e}"
        )
    except InvalidBlocksFormatException as e:
        return logger.exception(
            f"Failed To Generate Slack Convert Lead form for email {user.email} {e}"
        )
    except UnHandeledBlocksException as e:
        return logger.exception(
            f"Failed To Generate Slack Convert Lead form for email {user.email} {e}"
        )
    except InvalidAccessToken as e:
        return logger.exception(
            f"Failed To Generate Slack Convert Lead form with {str(user.id)} email {user.email} {e}"
        )
    return


@processor(required_context="u")
def process_show_convert_lead_form(payload, context):
    slack_account = UserSlackIntegration.objects.get(slack_id=payload["user"]["id"])
    user = slack_account.user
    selected_lead = payload["view"]["state"]["values"]["select_lead"][
        f"COMMAND_FORMS__CONVERT_LEAD?u={str(user.id)}&resource_type=Lead"
    ]["selected_option"]["value"]
    blocks = get_block_set(
        "convert_lead_block_set", {"u": str(user.id), "resource_id": selected_lead}
    )
    private_metadata = {**context, "resource_id": selected_lead}
    data = {
        "view_id": payload["view"]["id"],
        "view": {
            "type": "modal",
            "callback_id": slack_const.COMMAND_FORMS__CONVERT_LEAD,
            "title": {"type": "plain_text", "text": "Convert Lead"},
            "blocks": blocks,
            "submit": {"type": "plain_text", "text": "Convert"},
            "private_metadata": json.dumps(private_metadata),
        },
    }
    try:
        slack_requests.generic_request(
            slack_const.SLACK_API_ROOT + slack_const.VIEWS_UPDATE,
            data,
            access_token=user.organization.slack_integration.access_token,
        )
    except InvalidBlocksException as e:
        return logger.exception(
            f"Failed To Generate Slack Convert Lead form for email {user.email} {e}"
        )
    except InvalidBlocksFormatException as e:
        return logger.exception(
            f"Failed To Generate Slack Convert Lead form for email {user.email} {e}"
        )
    except UnHandeledBlocksException as e:
        return logger.exception(
            f"Failed To Generate Slack Convert Lead form for email {user.email} {e}"
        )
    except InvalidAccessToken as e:
        return logger.exception(
            f"Failed To Generate Slack Convert Lead form with {str(user.id)} email {user.email} {e}"
        )
    return


@processor(required_context="u")
def process_view_recap(payload, context):
    form_id_str = context.get("form_ids")
    form_ids = form_id_str.split(",")
    submitted_forms = OrgCustomSlackFormInstance.objects.filter(id__in=form_ids).exclude(
        template__resource="OpportunityLineItem"
    )
    main_form = submitted_forms.filter(
        template__form_type__in=["CREATE", "UPDATE", "MEETING_REVIEW"]
    ).first()
    main_form.add_to_recap_data(user=payload["user"]["username"])
    main_form.save()
    user = main_form.user
    access_token = user.organization.slack_integration.access_token
    loading_view_data = send_loading_screen(
        access_token,
        ":robot_face: Processing your recap",
        "open",
        str(user.id),
        payload["trigger_id"],
    )
    old_data = dict()
    if main_form.template.form_type == "UPDATE":
        for additional_stage_form in submitted_forms:
            old_data = {**old_data, **additional_stage_form.previous_data}
    new_data = dict()
    form_fields = None
    for form in submitted_forms:
        new_data = {**new_data, **form.saved_data}
        if form_fields:
            form_fields = form_fields | form.template.customformfield_set.filter(
                include_in_recap=True
            )
        else:
            form_fields = form.template.customformfield_set.filter(include_in_recap=True)
    blocks = []
    cleaned_data = clean_data_for_summary(str(user.id), new_data)
    completions_prompt = get_summary_completion(user, cleaned_data)
    message_string_for_recap = completions_prompt["choices"][0]["text"]
    # for key, new_value in new_data.items():
    #     field = form_fields.filter(field__api_name=key).first()
    #     if not field:
    #         continue
    #     field_label = field.field.reference_display_label.capitalize()
    #     if main_form.template.form_type == "UPDATE":
    #         # Only sends values for fields that have been updated
    #         # all fields on update form are included by default users cannot edit
    #         if key in old_data:
    #             if str(old_data.get(key)) != str(new_value):
    #                 old_value = old_data.get(key)
    #                 if field.field.is_public and field.field.data_type == "Reference":
    #                     old_value = check_for_display_value(field.field, old_value)
    #                     new_value = check_for_display_value(field.field, new_value)
    #                 if len(str(new_value)) > 255:
    #                     new_value = str(new_value)[:256] + "..."
    #                 if len(str(old_value)) > 255:
    #                     old_value = str(old_value)[:256] + "..."
    #                 if user.crm == "HUBSPOT":
    #                     if field.field.data_type in ["DateTime", "Date"]:
    #                         new_value = str(new_value)[:10]
    #                         old_value = str(old_value)[:10]
    #                     if field.field.api_name == "dealstage":
    #                         deal_stages = field.field.options[0][
    #                             main_form.resource_object.secondary_data.get("pipeline")
    #                         ]["stages"]
    #                         new_value = [
    #                             stage["label"] for stage in deal_stages if stage["id"] == new_value
    #                         ][0]
    #                         old_value = [
    #                             stage["label"] for stage in deal_stages if stage["id"] == old_value
    #                         ][0]
    #                 message_string_for_recap += (
    #                     f"\n*{field_label}:* ~{old_value}~ :arrow_right: {new_value}"
    #                 )
    #     elif main_form.template.form_type == "CREATE":
    #         if new_value:
    #             if field.field.is_public and field.field.data_type == "Reference":
    #                 new_value = check_for_display_value(field.field, new_value)
    #             if len(str(new_value)) > 255:
    #                 new_value = str(new_value)[:256]
    #             if user.crm == "HUBSPOT":
    #                 if field.field.data_type in ["DateTime", "Date"]:
    #                     new_value = str(new_value)[:10]
    #                 if field.field.api_name == "dealstage":
    #                     deal_stages = field.field.options[0][
    #                         main_form.resource_object.secondary_data.get("pipeline")
    #                     ]["stages"]
    #                     new_value = [
    #                         stage["label"] for stage in deal_stages if stage["id"] == new_value
    #                     ][0]
    #             message_string_for_recap += f"\n*{field_label}:* {new_value}"
    # if not len(message_string_for_recap):
    #     message_string_for_recap = "No Data to show from form"

    blocks.append(block_builders.simple_section(message_string_for_recap, "mrkdwn"))
    blocks.append(block_builders.context_block("Powered by ChatGPT © :robot_face:"))
    data = {
        "view_id": loading_view_data["view"]["id"],
        "view": {
            "type": "modal",
            "callback_id": "None",
            "title": {"type": "plain_text", "text": "Meeting Recap"},
            "blocks": blocks,
        },
    }
    try:
        slack_requests.generic_request(
            slack_const.SLACK_API_ROOT + slack_const.VIEWS_UPDATE, data, access_token=access_token,
        )
    except InvalidBlocksException as e:
        return logger.exception(
            f"Failed To Generate Slack Product form with {str(opp_item.id)} email {user.email} {e}"
        )
    except InvalidBlocksFormatException as e:
        return logger.exception(
            f"Failed To Generate Slack Product form with {str(opp_item.id)} email {user.email} {e}"
        )
    except UnHandeledBlocksException as e:
        return logger.exception(
            f"Failed To Generate Slack Product form with {str(opp_item.id)} email {user.email} {e}"
        )
    except InvalidAccessToken as e:
        return logger.exception(
            f"Failed To Generate Slack Product form with {str(user.id)} email {user.email} {e}"
        )
    return


@processor(required_context="u")
def process_lead_input_switch(payload, context):
    user = User.objects.get(id=context.get("u"))
    access_token = user.organization.slack_integration.access_token
    actions = payload["actions"][0]
    blocks = payload["view"]["blocks"]
    pm = json.loads(payload["view"]["private_metadata"])
    pm.update(**context)
    w = context.get("w", None)
    try:
        selected_options = actions["selected_options"][0]["value"]
    except IndexError:
        selected_options = None
    block_id = actions["block_id"]
    to_change_input = context.get("input")
    input_id = f"{to_change_input}_NAME_INPUT"
    index, action_block = block_finder(input_id, blocks)
    if selected_options:
        block = block_builders.external_select(
            f"Choose your {to_change_input}",
            action_with_params(
                slack_const.GET_SOBJECT_LIST,
                params=[f"u={str(user.id)}", f"resource_type={to_change_input}",],
            ),
            block_id=input_id,
        )
    else:
        if to_change_input in ["Account", "Contact"]:
            text = (
                "Create new Account based off your Lead's company"
                if to_change_input == "Account"
                else "Create new Contact based off your Lead information"
            )
            block = block_builders.simple_section(text, block_id=input_id)
        else:
            block = block_builders.input_block(
                f"Create New", block_id=input_id, placeholder=f"New {to_change_input}",
            )
    callback_id = (
        slack_const.ZOOM_MEETING__CONVERT_LEAD if w else slack_const.COMMAND_FORMS__CONVERT_LEAD
    )
    blocks[index] = block
    data = {
        "view_id": payload["view"]["id"],
        "view": {
            "type": "modal",
            "callback_id": callback_id,
            "title": {"type": "plain_text", "text": "Convert Lead"},
            "blocks": blocks,
            "submit": {"type": "plain_text", "text": "Convert"},
            "private_metadata": json.dumps(pm),
        },
    }
    try:
        slack_requests.generic_request(
            slack_const.SLACK_API_ROOT + slack_const.VIEWS_UPDATE, data, access_token=access_token,
        )
    except InvalidBlocksException as e:
        return logger.exception(
            f"Failed to switch input type on convert lead form for {user.email} {e}"
        )
    except InvalidBlocksFormatException as e:
        return logger.exception(
            f"Failed to switch input type on convert lead form for {user.email} {e}"
        )
    except UnHandeledBlocksException as e:
        return logger.exception(
            f"Failed to switch input type on convert lead form for {user.email} {e}"
        )
    except InvalidAccessToken as e:
        return logger.exception(
            f"Failed to switch input type on convert lead form for {user.email} {e}"
        )
    return


def process_pricebook_selected(payload, context):
    view = payload["view"]
    state = view["state"]
    private_metadata = json.loads(view["private_metadata"])
    org = Organization.objects.get(id=context.get("org"))
    current_value = state["values"]["PRICEBOOKS"][
        f"GET_PRICEBOOK_ENTRY_OPTIONS?org={context.get('org')}&product_form={context.get('product_form')}"
    ]["selected_option"]["value"]
    pricebook = Pricebook2.objects.get(id=current_value)
    product_form = OrgCustomSlackFormInstance.objects.get(id=context.get("product_form"))
    blocks = []
    blocks.extend(product_form.generate_form(Pricebook2Id=f"{pricebook.integration_id}"))
    data = {
        "view_id": view["id"],
        "view": {
            "type": "modal",
            "title": {"type": "plain_text", "text": "Add Products Form"},
            "submit": {"type": "plain_text", "text": "Submit"},
            "blocks": blocks,
            "private_metadata": json.dumps(private_metadata),
            "callback_id": slack_const.PROCESS_SUBMIT_PRODUCT,
        },
    }
    try:
        slack_requests.generic_request(
            slack_const.SLACK_API_ROOT + slack_const.VIEWS_UPDATE,
            data,
            access_token=org.slack_integration.access_token,
        )
    except InvalidBlocksException as e:
        return logger.exception(f"Failed To Generate Slack Product form with {str(org.id)} {e}")
    except InvalidBlocksFormatException as e:
        return logger.exception(f"Failed To Generate Slack Product form with {str(org.id)} {e}")
    except UnHandeledBlocksException as e:
        return logger.exception(f"Failed To Generate Slack Product form with {str(org.id)} {e}")
    except InvalidAccessToken as e:
        return logger.exception(f"Failed To Generate Slack Product form with {e}")
    return


def process_log_activity(payload, context):
    state = payload["view"]["state"]["values"]
    pm = json.loads(payload["view"]["private_metadata"])

    modal_type = [
        value.get("selected_option") for value in state.get("selected_activity", {}).values()
    ][0].get("value")
    user = User.objects.get(id=pm.get("u"))
    if user.slack_integration:
        slack = UserSlackIntegration.objects.filter(slack_id=user.slack_integration.id).first()
        if not slack:
            data = {
                "response_type": "ephemeral",
                "text": "Sorry I cant find your managr account",
            }
        access_token = user.organization.slack_integration.access_token
        url = slack_const.SLACK_API_ROOT + slack_const.VIEWS_PUSH
        callback_id = (
            slack_const.COMMAND_CREATE_TASK
            if modal_type == "create_task_modal"
            else slack_const.COMMAND_CREATE_EVENT
        )
        title = "Create Task" if modal_type == "create_task_modal" else "Create Event"
        data = {
            "view_id": payload["view"]["id"],
            "trigger_id": payload["trigger_id"],
            "view": {
                "type": "modal",
                "callback_id": callback_id,
                "title": {"type": "plain_text", "text": title},
                "blocks": get_block_set(modal_type, {"u": pm.get("u")}),
                "submit": {"type": "plain_text", "text": "Submit", "emoji": True},
                "private_metadata": json.dumps(pm),
                "external_id": f"{modal_type}.{str(uuid.uuid4())}",
            },
        }
        slack_requests.generic_request(url, data, access_token=access_token)
    return


def process_insert_note_templates_dropdown(payload, context):
    slack_account = UserSlackIntegration.objects.get(slack_id=payload["user"]["id"])

    user = slack_account.user
    view_id = payload["view"]["id"]
    blocks = payload["view"]["blocks"]
    pm = json.loads(payload["view"]["private_metadata"])
    workflow_id = pm.get("w", None)
    pm.update({"u": str(user.id)})
    try:
        index, block = block_finder("note_templates", blocks)
    except ValueError:
        # did not find the block
        block = None
        pass
    if block:
        template_options = [template.as_slack_option for template in user.note_templates]
        template_dropdown = block_builders.static_select(
            "*Note Template*",
            options=template_options,
            action_id=slack_const.INSERT_NOTE_TEMPLATE,
            block_id="note_templates",
        )
        blocks = [*blocks[:index], template_dropdown, *blocks[index + 1 :]]
    if workflow_id:
        workflow = MeetingWorkflow.objects.get(id=workflow_id)
        current_forms = workflow.forms.all()
    else:
        current_form_ids = pm.get("f").split(",")
        current_forms = user.custom_slack_form_instances.filter(id__in=current_form_ids)
    current_stage = current_forms.first().resource_object.secondary_data.get("StageName")
    stage_template = (
        OrgCustomSlackForm.objects.for_user(user).filter(stage=current_stage).first()
        if current_stage
        else None
    )
    data = {
        "view_id": view_id,
        "view": {
            "type": "modal",
            "title": payload["view"]["title"],
            "blocks": blocks,
            "private_metadata": json.dumps(pm),
            "external_id": payload["view"]["external_id"],
        },
    }
    if stage_template:
        submit_button_text = "Next"
        callback_id = slack_const.COMMAND_FORMS__PROCESS_NEXT_PAGE
    else:
        submit_button_text = "Update"
        callback_id = slack_const.COMMAND_FORMS__SUBMIT_FORM

    data["view"]["submit"] = {"type": "plain_text", "text": submit_button_text, "emoji": True}
    data["view"]["callback_id"] = callback_id

    try:
        res = slack_requests.generic_request(
            slack_const.SLACK_API_ROOT + slack_const.VIEWS_UPDATE,
            data,
            access_token=user.organization.slack_integration.access_token,
        )
    except InvalidBlocksException as e:
        return logger.exception(
            f"Failed To Insert Note Template Dropdown for user {user.email} {e}"
        )
    except InvalidBlocksFormatException as e:
        return logger.exception(
            f"Failed To Insert Note Template Dropdown for user {user.email} {e}"
        )
    except UnHandeledBlocksException as e:
        return logger.exception(
            f"Failed To Insert Note Template Dropdown for user {user.email} {e}"
        )
    except InvalidAccessToken as e:
        return logger.exception(
            f"Failed To Insert Note Template Dropdown for user {user.email} {e}"
        )
    except Exception as e:
        return logger.exception(f"Failed to send message for {e}")
    return


def process_insert_note_template(payload, context):
    from managr.salesforce.background import replace_tags

    slack_account = UserSlackIntegration.objects.get(slack_id=payload["user"]["id"])
    user = slack_account.user
    view_id = payload["view"]["id"]
    blocks = payload["view"]["blocks"]
    pm = json.loads(payload["view"]["private_metadata"])
    type = pm.get("type", None)
    pm.update({"u": str(user.id)})
    workflow_id = pm.get("w", None)
    state = payload["view"]["state"]["values"]
    selected_template = state["note_templates"]["INSERT_NOTE_TEMPLATE"]["selected_option"]["text"][
        "text"
    ]
    template = user.note_templates.filter(subject=selected_template).first()
    try:
        index, block = block_finder("note_templates", blocks)

    except ValueError:
        # did not find the block
        block = None
        pass
    if block:
        template_section = block_builders.section_with_button_block(
            "Insert",
            "note_templates",
            "*Note Templates*",
            block_id="note_templates",
            action_id=slack_const.INSERT_NOTE_TEMPLATE_DROPDOWN,
        )
        blocks = [*blocks[:index], template_section, *blocks[index + 1 :]]
    try:
        s_index, s_block = block_finder("meeting_type", blocks)
        m_index, m_block = block_finder("meeting_comments", blocks)
    except ValueError:
        # did not find the block
        block = None
        pass
    if m_block:
        m_block["element"]["initial_value"] = replace_tags(template.body)
        m_block["block_id"] = "meeting_comment"
        s_block["element"]["initial_value"] = template.subject
        s_block["block_id"] = "meeting_title"
        blocks = [*blocks[:s_index], s_block, *blocks[s_index + 1 :]]
        blocks = [*blocks[:m_index], m_block, *blocks[m_index + 1 :]]
    if workflow_id:
        workflow = MeetingWorkflow.objects.get(id=workflow_id)
        current_forms = workflow.forms.all()
    else:
        current_form_ids = pm.get("f").split(",")
        current_forms = user.custom_slack_form_instances.filter(id__in=current_form_ids)
    main_form = current_forms.first()
    current_stage = main_form.resource_object.secondary_data.get("StageName")
    stage_template = (
        OrgCustomSlackForm.objects.for_user(user).filter(stage=current_stage).first()
        if current_stage
        else None
    )
    if stage_template:
        if type == "meeting":
            workflow = MeetingWorkflow.objects.filter(id=pm.get("w")).first()
            workflow.add_form(
                slack_const.FORM_RESOURCE_OPPORTUNITY,
                slack_const.FORM_TYPE_STAGE_GATING,
                stage=current_stage,
            )
        else:
            if not len(current_forms.filter(template__form_type="STAGE_GATING")):
                stage_form = OrgCustomSlackFormInstance.objects.create(
                    template=stage_template, resource_id=main_form.resource_id, user=user,
                )
                current_form_ids.append(str(stage_form.id))
                pm.update({"f": ",".join(current_form_ids)})
    if stage_template:
        submit_button_text = "Next"
        callback_id = slack_const.COMMAND_FORMS__PROCESS_NEXT_PAGE
    else:
        submit_button_text = "Submit"
        callback_id = slack_const.COMMAND_FORMS__SUBMIT_FORM
    if type == "meeting":
        callback_id = (
            slack_const.ZOOM_MEETING__PROCESS_STAGE_NEXT_PAGE
            if stage_template
            else slack_const.ZOOM_MEETING__PROCESS_MEETING_SENTIMENT
        )
        pm.update({"form_type": main_form.template.form_type})
    data = {
        "view_id": view_id,
        "view": {
            "type": "modal",
            "title": payload["view"]["title"],
            "blocks": blocks,
            "private_metadata": json.dumps(pm),
            "external_id": payload["view"]["external_id"],
        },
    }
    data["view"]["submit"] = {"type": "plain_text", "text": submit_button_text, "emoji": True}
    data["view"]["callback_id"] = callback_id

    try:
        res = slack_requests.generic_request(
            slack_const.SLACK_API_ROOT + slack_const.VIEWS_UPDATE,
            data,
            access_token=user.organization.slack_integration.access_token,
        )
    except InvalidBlocksException as e:
        return logger.exception(
            f"Failed To Insert Note Template Dropdown for user {user.email} {e}"
        )
    except InvalidBlocksFormatException as e:
        return logger.exception(
            f"Failed To Insert Note Template Dropdown for user {user.email} {e}"
        )
    except UnHandeledBlocksException as e:
        return logger.exception(
            f"Failed To Insert Note Template Dropdown for user {user.email} {e}"
        )
    except InvalidAccessToken as e:
        return logger.exception(
            f"Failed To Insert Note Template Dropdown for user {user.email} {e}"
        )
    except Exception as e:
        return logger.exception(f"Failed to send message for {e}")
    return


@processor()
def reopen_chat_modal(payload, context):
    channel_id = payload["channel"]["id"]
    message_ts = payload["message"]["ts"]
    form_id = context.get("form_id", None)
    form = OrgCustomSlackFormInstance.objects.get(id=form_id)
    user = User.objects.get(slack_integration__slack_id=payload["user"]["id"])
    context.update(u=str(user.id), ts=message_ts, channel=channel_id)
    crm = "Salesforce" if user.crm == "SALESFORCE" else "HubSpot"
    if user.slack_integration:
        slack = (
            UserSlackIntegration.objects.filter(slack_id=user.slack_integration.slack_id)
            .select_related("user")
            .first()
        )
        if not slack:
            data = {
                "response_type": "ephemeral",
                "text": "Sorry I cant find your managr account",
            }
        blocks = [
            block_builders.input_block(
                f"Update {crm} by sending a message",
                initial_value=form.chat_submission,
                block_id="CHAT_PROMPT",
                multiline=True,
                optional=False,
            ),
            block_builders.context_block("Powered by ChatGPT © :robot_face:"),
        ]
        access_token = user.organization.slack_integration.access_token
        trigger_id = payload["trigger_id"]
        url = slack_const.SLACK_API_ROOT + slack_const.VIEWS_OPEN
        data = {
            "trigger_id": trigger_id,
            "view": {
                "type": "modal",
                "callback_id": slack_const.COMMAND_FORMS__SUBMIT_CHAT,
                "title": {"type": "plain_text", "text": "Update CRM",},
                "blocks": blocks,
                "submit": {"type": "plain_text", "text": "Submit", "emoji": True},
                "private_metadata": json.dumps(context),
            },
        }
        slack_requests.generic_request(url, data, access_token=access_token)
        return


@processor()
def process_open_generative_action_modal(payload, context):
    user = User.objects.get(slack_integration__slack_id=payload["user"]["id"])
    if user.slack_integration:
        slack = (
            UserSlackIntegration.objects.filter(slack_id=user.slack_integration.slack_id)
            .select_related("user")
            .first()
        )
        if not slack:
            data = {
                "response_type": "ephemeral",
                "text": "Sorry I cant find your managr account",
            }
        options = [
            block_builders.option("Draft Follow-up Email", "DRAFT_EMAIL"),
            block_builders.option("Suggest Next Steps", "NEXT_STEPS"),
            block_builders.option("Get Summary", "SEND_SUMMARY"),
        ]
        blocks = [
            block_builders.static_select(
                "Select the type of content to generate",
                options=options,
                block_id="GENERATIVE_ACTION",
            ),
            block_builders.context_block("Powered by ManagrGPT © :robot_face:"),
        ]
        access_token = user.organization.slack_integration.access_token
        trigger_id = payload["trigger_id"]
        url = slack_const.SLACK_API_ROOT + slack_const.VIEWS_OPEN
        data = {
            "trigger_id": trigger_id,
            "view": {
                "type": "modal",
                "callback_id": slack_const.PROCESS_SELECTED_GENERATIVE_ACTION,
                "title": {"type": "plain_text", "text": "Generate Content",},
                "blocks": blocks,
                "submit": {"type": "plain_text", "text": "Submit"},
                "private_metadata": json.dumps(context),
            },
        }
        slack_requests.generic_request(url, data, access_token=access_token)
    return


GENERATIVE_ACTION_SWITCHER = {
    "DRAFT_EMAIL": emit_process_send_email_draft,
    "SEND_SUMMARY": process_send_recap_modal,
    "NEXT_STEPS": emit_process_send_next_steps,
}


def process_selected_generative_action(payload, context):
    user = User.objects.get(id=context.get("u"))
    pm = json.loads(payload.get("view").get("private_metadata"))
    resource_type = context.get("resource_type", None)
    resource_id = None
    if resource_type:
        action = "ASK_MANAGR"
        if (
            len(payload["actions"])
            and slack_const.PROCESS_SELECTED_GENERATIVE_ACTION in payload["actions"][0]["action_id"]
        ):
            resource_id = payload["actions"][0]["selected_option"]["value"]
    else:
        generative_action_values = payload["view"]["state"]["values"]["GENERATIVE_ACTION"]
        action = generative_action_values.get(list(generative_action_values.keys())[0])[
            "selected_option"
        ]["value"]
    if action == "ASK_MANAGR":
        resource_list = (
            ["Opportunity", "Account", "Contact", "Lead"]
            if user.crm == "SALESFORCE"
            else ["Company", "Deal", "Contact"]
        )
        options = "%".join(resource_list)
        blocks = [
            *get_block_set(
                "ask_managr_blockset",
                {
                    "u": str(user.id),
                    "options": options,
                    "action_id": slack_const.PROCESS_SELECTED_GENERATIVE_ACTION,
                    "resource_type": resource_type,
                    "resource_id": resource_id,
                },
            )
        ]
        user = User.objects.get(id=pm.get("u"))
        data = {
            "view_id": payload["view"]["id"],
            "view": {
                "type": "modal",
                "callback_id": slack_const.PROCESS_ASK_MANAGR,
                "title": {"type": "plain_text", "text": "Generate Content"},
                "blocks": blocks,
                "submit": {"type": "plain_text", "text": "Submit"},
                "private_metadata": json.dumps(context),
                "external_id": f"ask_managr_blockset.{str(uuid.uuid4())}",
            },
        }
        try:
            slack_requests.generic_request(
                slack_const.SLACK_API_ROOT + slack_const.VIEWS_UPDATE,
                data,
                access_token=user.organization.slack_integration.access_token,
            )
        except InvalidBlocksException as e:
            return logger.exception(
                f"Failed To Generate Slack Product form with {context.get('opp_item_id')} email {user.email} {e}"
            )
        except InvalidBlocksFormatException as e:
            return logger.exception(
                f"Failed To Generate Slack Product form with {context.get('opp_item_id')} email {user.email} {e}"
            )
        except UnHandeledBlocksException as e:
            return logger.exception(
                f"Failed To Generate Slack Product form with {context.get('opp_item_id')} email {user.email} {e}"
            )
        except InvalidAccessToken as e:
            return logger.exception(
                f"Failed To Generate Slack Product form with {str(user.id)} email {user.email} {e}"
            )
        return
    else:
        action_func = GENERATIVE_ACTION_SWITCHER[action]
        loading_block = [
            *get_block_set("loading", {"message": ":robot_face: Generating content..."})
        ]
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


REGENERATE_ACTION_SWITCHER = {
    "DRAFT_EMAIL": emit_process_send_regenerate_email_message,
    "SEND_SUMMARY": process_send_recap_modal,
    "NEXT_STEPS": emit_process_send_next_steps,
}


def process_regenerate_action(payload, context):
    user = User.objects.get(id=context.get("u"))
    action = payload.get("actions")[0].get("value")
    channel_id = payload["channel"]["id"]
    ts = payload["message"]["ts"]
    context.update(channel_id=channel_id, ts=ts)
    blocks = payload["message"]["blocks"][:2]
    loading_block = get_block_set("loading", {"message": ":robot_face: Regenerating content..."})
    blocks.extend(loading_block)
    try:
        res = slack_requests.update_channel_message(
            channel_id, ts, user.organization.slack_integration.access_token, block_set=blocks
        )
        action_func = REGENERATE_ACTION_SWITCHER[action]
        action_func(payload, context)
    except Exception as e:
        logger.exception(e)
    return


@processor(required_context=["u", "invocation", "config_id"])
def process_switch_to_deal_reviews(payload, context):
    user = User.objects.get(id=context.get("u"))
    channel_id = payload["channel"]["id"]
    ts = payload["message"]["ts"]
    context.update(channel=channel_id, ts=ts)
    loading_block = get_block_set("loading", {"message": "Processing workflows..."})
    blocks = payload["message"]["blocks"][:2]
    blocks.extend(loading_block)
    try:
        res = slack_requests.update_channel_message(
            channel_id, ts, user.organization.slack_integration.access_token, block_set=blocks
        )
        emit_process_paginate_deal_reviews(payload, context)
    except Exception as e:
        logger.exception(e)
    return


@processor(required_context=["alert_id"])
def process_send_deal_review(payload, context):
    user_slack_id = payload.get("user", {}).get("id", None)
    user = User.objects.filter(slack_integration__slack_id=user_slack_id).first()
    channel_id = payload["channel"]["id"]
    ts = payload["message"]["ts"]
    context.update(channel=channel_id, ts=ts)
    loading_block = get_block_set("loading", {"message": "Processing workflows..."})
    blocks = payload["message"]["blocks"][:2]
    blocks.extend(loading_block)
    try:
        res = slack_requests.update_channel_message(
            channel_id, ts, user.organization.slack_integration.access_token, block_set=blocks
        )
        emit_process_alert_send_deal_review(payload, context)
    except Exception as e:
        logger.exception(e)
    return


@processor(required_context=["invocation", "config_id"])
def process_paginate_deal_reviews(payload, context):
    user_slack_id = payload.get("user", {}).get("id", None)
    user = User.objects.filter(slack_integration__slack_id=user_slack_id).first()
    channel_id = payload["channel"]["id"]
    ts = payload["message"]["ts"]
    context.update(channel=channel_id, ts=ts, new_page=context.get("new_page"), u=str(user.id))
    loading_block = get_block_set("loading", {"message": "Processing workflows..."})
    blocks = payload["message"]["blocks"][:2]
    blocks.extend(loading_block)
    try:
        res = slack_requests.update_channel_message(
            channel_id, ts, user.organization.slack_integration.access_token, block_set=blocks
        )
        emit_process_paginate_deal_reviews(payload, context)
    except Exception as e:
        logger.exception(e)
    return


@processor(required_context=["w", "u"])
def process_show_transcript_message(payload, context):
    user = User.objects.get(id=context.get("u"))
    access_token = user.organization.slack_integration.access_token
    trigger_id = payload["trigger_id"]
    url = slack_const.SLACK_API_ROOT + slack_const.VIEWS_OPEN
    blocks = [
        block_builders.static_select(
            "Use AI to summarize the call & autofill CRM fields?",
            [block_builders.option("Yes", "YES"), block_builders.option("No", "NO")],
            action_id=action_with_params(
                slack_const.MEETING__UPDATE_TRANSCRIPT_MESSAGE,
                [f"u={context.get('u')}", f"w={context.get('w')}"],
            ),
        )
    ]
    data = {
        "trigger_id": trigger_id,
        "view": {
            "type": "modal",
            "title": {"type": "plain_text", "text": "Log Meeting",},
            "blocks": blocks,
            "private_metadata": json.dumps(context),
        },
    }
    slack_requests.generic_request(url, data, access_token=access_token)
    return


@processor(required_context=["w", "u"])
def process_update_transcript_message(payload, context):
    user = User.objects.get(id=context.get("u"))
    access_token = user.organization.slack_integration.access_token
    url = slack_const.SLACK_API_ROOT + slack_const.VIEWS_UPDATE
    select_option = payload["actions"][0].get("selected_option").get("value")
    options = (
        ["Contact", "Opportunity", "Account", "Lead"]
        if user.crm == "SALESFORCE"
        else ["Contact", "Deal", "Company"]
    )
    action_id = (
        slack_const.MEETING___SUBMIT_CHAT_PROMPT
        if select_option == "NO"
        else slack_const.MEETING__PROCESS_TRANSCRIPT_TASK
    )
    context.update(options="%".join(options), action_id=action_id)
    blockset = "chat_meeting_blockset" if select_option == "NO" else "pick_resource_modal_block_set"
    blocks = [*get_block_set(blockset, context=context)]
    data = {
        "view_id": payload["view"]["id"],
        "view": {
            "type": "modal",
            "title": {"type": "plain_text", "text": "Log Meeting",},
            "callback_id": action_id,
            "blocks": blocks,
            "private_metadata": json.dumps(context),
            "external_id": f"{blockset}.{str(uuid.uuid4())}",
        },
    }
    if select_option == "NO":
        data["view"]["submit"] = {"type": "plain_text", "text": "Submit"}
    slack_requests.generic_request(url, data, access_token=access_token)
    return


def process_meeting_transcript_task(payload, context):
    emit_process_get_transcript_and_update_crm(payload, context, schedule=datetime.now())
    user = User.objects.get(id=context.get("u"))
    url = slack_const.SLACK_API_ROOT + slack_const.VIEWS_UPDATE
    blocks = [
        block_builders.simple_section(f":robot_face: Processing AI call summary. Check your DM!")
    ]
    data = {
        "view_id": payload["view"]["id"],
        "view": {
            "type": "modal",
            "title": {"type": "plain_text", "text": "Log Meeting",},
            "blocks": blocks,
            "private_metadata": json.dumps(context),
        },
    }
    slack_requests.generic_request(
        url, data, access_token=user.organization.slack_integration.access_token
    )
    return


def process_launch_call_summary_review(payload, context):
    form = OrgCustomSlackFormInstance.objects.get(id=context.get("form_id"))
    workflow = MeetingWorkflow.objects.get(id=context.get("w"))
    user = form.user
    blocks = []
    resource = "Task" if user.crm == "SALESFORCE" else "Meeting"
    field = "Type" if user.crm == "SALESFORCE" else "hs_meeting_outcome"
    type_text = "Note Type" if user.crm == "SALESFORCE" else "Meeting Outcome"
    try:
        note_options = user.crm_account.get_individual_picklist_values(resource, field)
        note_options = note_options.values if user.crm == "SALESFORCE" else note_options.values()
        note_options_list = [
            block_builders.option(opt.get("label"), opt.get("value")) for opt in note_options
        ]
        blocks.append(
            block_builders.static_select(
                type_text, options=note_options_list, block_id="managr_task_type"
            )
        )
    except Exception as e:
        logger.exception(f"Could not pull note type for {user.email} due to <{e}>")
    blocks.extend(form.generate_form(form.saved_data))
    context.update(ts=payload["container"]["message_ts"])
    stage_name = "StageName" if user.crm == "SALESFORCE" else "dealstage"
    try:
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
                "action_id": f"{slack_const.ZOOM_MEETING__STAGE_SELECTED}?u={str(user.id)}&f={str(form.id)}&w={str(workflow.id)}",
            },
        }
        blocks = [*blocks[:index], block, *blocks[index + 1 :]]
    data = {
        "trigger_id": payload["trigger_id"],
        "view": {
            "type": "modal",
            "title": {"type": "plain_text", "text": "Call Summary Review"},
            "blocks": blocks,
            "callback_id": slack_const.ZOOM_MEETING__PROCESS_MEETING_SENTIMENT,
            "private_metadata": json.dumps(context),
            "submit": {"type": "plain_text", "text": "Submit"},
            "external_id": f"meeting_review_modal.{str(uuid.uuid4())}",
        },
    }
    try:
        res = slack_requests.generic_request(
            slack_const.SLACK_API_ROOT + slack_const.VIEWS_OPEN,
            data,
            access_token=user.organization.slack_integration.access_token,
        )
    except Exception as e:
        return logger.exception(f"Failed to send message for {e}")
    return


def process_open_review_chat_update_modal(payload, context):
    form = OrgCustomSlackFormInstance.objects.get(id=context.get("f"))
    user = form.user
    blocks = form.generate_form(form.saved_data)
    context.update(
        message_ref=f"{user.slack_integration.channel}|{payload['container']['message_ts']}"
    )
    stage_name = "StageName" if user.crm == "SALESFORCE" else "dealstage"
    try:
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
                "action_id": f"{slack_const.COMMAND_FORMS__STAGE_SELECTED}?u={str(user.id)}&f={str(form.id)}&type=chat",
            },
        }
        blocks = [*blocks[:index], block, *blocks[index + 1 :]]

    try:
        index, block = block_finder(slack_const.NO_FORM_FIELDS, blocks)
    except ValueError:
        # did not find the block
        show_submit_button_if_fields_added = True
        pass

    callback_id = slack_const.COMMAND_FORMS__SUBMIT_FORM
    if "meeting" in form.update_source:
        callback_id = slack_const.ZOOM_MEETING__PROCESS_MEETING_SENTIMENT
        context.update(ts=payload["container"]["message_ts"])
    data = {
        "trigger_id": payload["trigger_id"],
        "view": {
            "type": "modal",
            "title": {"type": "plain_text", "text": "Chat Update Review"},
            "blocks": blocks,
            "callback_id": callback_id,
            "private_metadata": json.dumps(context),
            "submit": {"type": "plain_text", "text": "Submit"},
            "external_id": f"update_modal_block_set.{str(uuid.uuid4())}",
        },
    }
    try:
        res = slack_requests.generic_request(
            slack_const.SLACK_API_ROOT + slack_const.VIEWS_OPEN,
            data,
            access_token=user.organization.slack_integration.access_token,
        )
    except Exception as e:
        return logger.exception(f"Failed to send message for {e}")
    return


def process_send_call_analysis_to_dm(payload, context):
    user_slack_id = payload.get("user", {}).get("id", None)
    user = User.objects.filter(slack_integration__slack_id=user_slack_id).first()
    channel_id = payload["channel"]["id"]
    loading_block = get_block_set(
        "loading", {"message": ":robot_face: Processing your call analysis..."}
    )
    blocks = payload["message"]["blocks"][:2]
    blocks.extend(loading_block)
    try:
        res = slack_requests.send_channel_message(
            channel_id, user.organization.slack_integration.access_token, block_set=blocks
        )
        ts = res["ts"]
        context.update(ts=ts)
        emit_process_send_call_analysis_to_dm(payload, context)
    except Exception as e:
        logger.exception(e)
    return


def handle_block_actions(payload):
    """
    This takes place when user completes a general interaction,
    such as clicking a button.
    """
    switcher = {
        slack_const.ZOOM_MEETING__VIEW_MEETING_CONTACTS: process_show_meeting_contacts,
        slack_const.ZOOM_MEETING__EDIT_CONTACT: process_edit_meeting_contact,
        slack_const.ZOOM_MEETING__REMOVE_CONTACT: process_remove_contact_from_meeting,
        slack_const.ZOOM_MEETING__CREATE_OR_SEARCH: process_create_or_search_selected,
        slack_const.ZOOM_MEETING__SELECTED_RESOURCE: process_meeting_selected_resource,
        slack_const.ZOOM_MEETING__SELECTED_RESOURCE_OPTION: process_meeting_selected_resource_option,
        slack_const.ZOOM_MEETING__INIT_REVIEW: process_meeting_review,
        slack_const.ZOOM_MEETING__STAGE_SELECTED: process_stage_selected,
        slack_const.ZOOM_MEETING__CREATE_TASK: process_create_task,
        slack_const.ZOOM_MEETING__CONVERT_LEAD: process_show_meeting_convert_lead_form,
        slack_const.ZOOM_MEETING__MEETING_DETAILS: process_meeting_details,
        slack_const.MEETING_REVIEW_SYNC_CALENDAR: process_sync_calendar,
        slack_const.MEETING_ATTACH_RESOURCE_MODAL: process_show_meeting_resource,
        slack_const.MEETING__PROCESS_SHOW_CHAT_MODEL: process_show_meeting_chat_modal,
        slack_const.COMMAND_FORMS__GET_LOCAL_RESOURCE_OPTIONS: process_show_update_resource_form,
        slack_const.GET_CRM_RESOURCE_OPTIONS: process_show_update_resource_form,
        slack_const.PROCESS_SHOW_ALERT_UPDATE_RESOURCE_FORM: process_show_alert_update_resource_form,
        slack_const.COMMAND_FORMS__STAGE_SELECTED: process_stage_selected_command_form,
        slack_const.COMMAND_FORMS__PIPELINE_SELECTED: process_pipeline_selected_command_form,
        slack_const.COMMAND_FORMS__PROCESS_ADD_CREATE_FORM: process_add_create_form,
        slack_const.COMMAND_FORMS__CONVERT_LEAD: process_show_convert_lead_form,
        slack_const.UPDATE_TASK_SELECTED_RESOURCE: process_resource_selected_for_task,
        slack_const.RETURN_TO_FORM_MODAL: process_return_to_form_modal,
        slack_const.CHECK_IS_OWNER_FOR_UPDATE_MODAL: process_check_is_owner,
        slack_const.PAGINATE_ALERTS: process_paginate_alerts,
        slack_const.PAGINATE_INLINE_ALERTS: process_paginate_inline_alerts,
        slack_const.PROCESS_SWITCH_ALERT_MESSAGE: process_switch_alert_message,
        slack_const.PROCESS_INLINE_FIELD_SELECTED: process_inline_field_selected,
        slack_const.ALERT_INLINE_STAGE_SELECTED: process_alert_inline_stage_selected,
        slack_const.PROCESS_SHOW_APP_SELECT: process_connected_app_selected,
        slack_const.PAGINATE_APP_ALERTS: process_connected_app_selected,
        slack_const.PROCESS_SUBMIT_INLINE_ALERT_DATA: process_submit_inline_alert_data,
        slack_const.PROCESS_SHOW_ENGAGEMENT_MODEL: process_show_engagement_modal,
        slack_const.GET_NOTES: process_get_notes,
        slack_const.GONG_CALL_RECORDING: process_get_call_recording,
        slack_const.PROCESS_SEND_RECAP_MODAL: process_send_recap_modal,
        slack_const.COMMAND_MANAGR_ACTION: process_managr_action,
        slack_const.PROCESS_SHOW_EDIT_PRODUCT_FORM: process_show_edit_product_form,
        slack_const.PROCESS_ADD_PRODUCTS_FORM: process_add_products_form,
        slack_const.PROCESS_ADD_CUSTOM_OBJECT_FORM: process_add_custom_object_form,
        slack_const.PROCESS_PICK_CUSTOM_OBJECT: process_pick_custom_object,
        slack_const.VIEW_RECAP: process_view_recap,
        slack_const.PROCESS_SELECT_RESOURCE: process_select_resource,
        slack_const.PROCESS_LEAD_INPUT_SWITCH: process_lead_input_switch,
        slack_const.GET_PRICEBOOK_ENTRY_OPTIONS: process_pricebook_selected,
        slack_const.COMMAND_LOG_NEW_ACTIVITY: process_log_activity,
        slack_const.PROCESS_ALERT_ACTIONS: process_alert_actions,
        slack_const.SHOW_INITIAL_MEETING_INTERACTION: show_initial_meeting_interaction,
        slack_const.PROCESS_BULK_UPDATE: process_show_bulk_update_form,
        slack_const.CHOOSE_CRM_FIELD: process_select_crm_field,
        slack_const.INSERT_NOTE_TEMPLATE_DROPDOWN: process_insert_note_templates_dropdown,
        slack_const.INSERT_NOTE_TEMPLATE: process_insert_note_template,
        slack_const.GET_SUMMARY: process_get_summary_fields,
        slack_const.RETURN_TO_FORM_BUTTON: process_return_to_form_button,
        slack_const.PROCESS_SHOW_ENGAGEMENT_DETAILS: process_get_engagement_details,
        slack_const.REOPEN_CHAT_MODAL: reopen_chat_modal,
        slack_const.OPEN_GENERATIVE_ACTION_MODAL: process_open_generative_action_modal,
        slack_const.PROCESS_REGENERATE_ACTION: process_regenerate_action,
        slack_const.PROCESS_SWITCH_TO_DEAL_REVIEW: process_switch_to_deal_reviews,
        slack_const.PROCESS_PAGINATE_DEAL_REVIEW: process_paginate_deal_reviews,
        slack_const.PROCESS_SEND_DEAL_REVIEW: process_send_deal_review,
        slack_const.PROCESS_INSERT_CHAT_TEMPLATE: process_insert_chat_template,
        slack_const.PROCESS_INSERT_ACTION_TEMPLATE: process_insert_action_template,
        slack_const.MEETING__SHOW_TRANSCRIPT_MESSAGE: process_show_transcript_message,
        slack_const.MEETING__UPDATE_TRANSCRIPT_MESSAGE: process_update_transcript_message,
        slack_const.MEETING__PROCESS_TRANSCRIPT_TASK: process_meeting_transcript_task,
        slack_const.CALL_LAUNCH_SUMMARY_REVIEW: process_launch_call_summary_review,
        slack_const.OPEN_REVIEW_CHAT_UPDATE_MODAL: process_open_review_chat_update_modal,
        slack_const.SEND_CALL_ANALYSIS_TO_DM: process_send_call_analysis_to_dm,
        slack_const.PROCESS_SELECTED_GENERATIVE_ACTION: process_selected_generative_action,
        slack_const.CHOOSE_RESET_MEETING_DAY: choose_reset_meeting_day,
    }

    action_query_string = payload["actions"][0]["action_id"]
    processed_string = process_action_id(action_query_string)
    action_id = processed_string.get("true_id")
    action_params = processed_string.get("params")
    # added special key __block_action to allow us to override the defaults since the action_id is used for both the suggestions and the actions
    if action_params.get("__block_action", None):
        action_id = action_params.get("__block_action")
    return switcher.get(action_id, NO_OP)(payload, action_params)
