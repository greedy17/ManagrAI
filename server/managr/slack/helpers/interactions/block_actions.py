import json
import uuid
import logging
import pytz

from django.db.models import Q
from django.utils import timezone
from datetime import datetime, date

from managr.utils.misc import custom_paginator
from managr.slack.helpers.block_sets.command_views_blocksets import (
    custom_paginator_block,
    custom_meeting_paginator_block,
)
from managr.organization.models import (
    Organization,
    Stage,
    Account,
    OpportunityLineItem,
    Pricebook2,
    PricebookEntry,
)
from managr.opportunity.models import Opportunity, Lead
from managr.zoom.models import ZoomMeeting
from managr.slack import constants as slack_const
from managr.opportunity import constants as opp_consts
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
)
from managr.slack.helpers.block_sets import get_block_set
from managr.slack.helpers import block_builders
from managr.slack.helpers.interactions.commands import get_action
from managr.slack.models import OrgCustomSlackFormInstance, UserSlackIntegration, OrgCustomSlackForm
from managr.salesforce.models import MeetingWorkflow
from managr.core.models import User, MeetingPrepInstance
from managr.salesforce.background import emit_meeting_workflow_tracker, check_for_display_value
from managr.salesforce import constants as sf_consts
from managr.slack.helpers.exceptions import (
    UnHandeledBlocksException,
    InvalidBlocksFormatException,
    InvalidBlocksException,
    InvalidAccessToken,
)
from managr.core.cron import process_get_task_list
from managr.api.decorators import slack_api_exceptions
from managr.alerts.models import AlertTemplate, AlertInstance, AlertConfig
from managr.gong.models import GongCall, GongAuthAccount
from managr.gong.exceptions import InvalidRequest

logger = logging.getLogger("managr")


#########################################################
# MEETING REVIEW ACTIONS
#########################################################


@processor()
def process_meeting_review(payload, context):
    trigger_id = payload["trigger_id"]
    workflow_id = payload["actions"][0]["value"]
    workflow = MeetingWorkflow.objects.get(id=workflow_id)
    meeting = workflow.meeting
    organization = meeting.zoom_account.user.organization
    access_token = organization.slack_integration.access_token
    loading_view_data = send_loading_screen(
        access_token,
        "Salesforce is being a bit slow :sleeping:… please give it a few seconds",
        "open",
        str(workflow.user.id),
        trigger_id,
    )
    private_metadata = {
        "original_message_channel": payload["channel"]["id"],
        "original_message_timestamp": payload["message"]["ts"],
    }
    context = {
        "w": workflow_id,
        "f": str(workflow.forms.filter(template__form_type="UPDATE").first().id),
        "type": "meeting",
    }
    private_metadata.update(context)
    data = {
        "view_id": loading_view_data["view"]["id"],
        "view": {
            "type": "modal",
            "callback_id": slack_const.ZOOM_MEETING__PROCESS_MEETING_SENTIMENT,
            "title": {"type": "plain_text", "text": "Log Meeting"},
            "blocks": get_block_set("meeting_review_modal", context=context),
            "submit": {"type": "plain_text", "text": "Update Salesforce"},
            "private_metadata": json.dumps(private_metadata),
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
    slack_account = UserSlackIntegration.objects.get(slack_id=payload["user"]["id"])
    type = context.get("type", None)
    trigger_id = payload["trigger_id"]
    if type:
        workflow = MeetingPrepInstance.objects.get(id=context.get("w"))
    else:
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
    if type:
        workflow = MeetingPrepInstance.objects.get(id=context.get("w"))
        org = workflow.user.organization
    else:
        workflow = MeetingWorkflow.objects.get(id=context.get("w"))
        meeting = workflow.meeting
        org = meeting.zoom_account.user.organization
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
    # trigger_id = payload["trigger_id"]

    # salesforce_account = meeting.zoom_account.user.salesforce_account

    # view = payload["view"]
    # # retrieve original blocks, view will use the same blocks but change the submit action
    # blocks = view["blocks"]
    # view_id = view["id"]
    # title = view["title"]
    # actions = payload["actions"]
    # callback_id = None
    # submit_button_text = None
    # selected_action_block = actions[0] if len(actions) else None
    # if selected_action_block:
    #     action = process_action_id(selected_action_block["action_id"])
    #     block_id = selected_action_block["block_id"]
    #     index, selected_block = block_finder(block_id, blocks)
    #     if (
    #         action["true_id"] == slack_const.ZOOM_MEETING__EDIT_CONTACT
    #         and selected_block["elements"][0]["value"] == slack_const.ZOOM_MEETING__EDIT_CONTACT
    #     ):
    #         selected_block["elements"][0]["text"]["text"] = "Cancel Edit Contact"
    #         selected_block["elements"][0]["value"] = slack_const.ZOOM_MEETING__CANCEL_EDIT_CONTACT
    #         blocks[index] = selected_block
    #         callback_id = slack_const.ZOOM_MEETING__EDIT_CONTACT
    #         submit_button_text = "Edit Contact"
    #         # change the block to show it is selected
    #     elif (
    #         action["true_id"] == slack_const.ZOOM_MEETING__EDIT_CONTACT
    #         and selected_block["elements"][0]["value"]
    #         == slack_const.ZOOM_MEETING__CANCEL_EDIT_CONTACT
    #     ):
    #         selected_block["elements"][0]["text"]["text"] = "Click To Select For Editing"
    #         selected_block["elements"][0]["value"] = slack_const.ZOOM_MEETING__EDIT_CONTACT
    #         blocks[index] = selected_block
    #         callback_id = None
    #         submit_button_text = None
    #         # change the block to show it is selected

    # data = {
    #     "trigger_id": trigger_id,
    #     "view_id": view_id,
    #     "view": {
    #         "close": {"type": "plain_text", "text": "Close", "emoji": True},
    #         "type": "modal",
    #         "title": title,
    #         "blocks": blocks,
    #         "private_metadata": json.dumps(
    #             {"w": context.get("w"), "tracking_id": context.get("tracking_id"),}
    #         ),
    #     },
    # }
    # if callback_id:
    #     data["view"]["callback_id"] = callback_id

    # if submit_button_text:
    #     data["view"]["submit"] = {"type": "plain_text", "text": submit_button_text, "emoji": True}
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
        selected_value = action["selected_option"]["value"]

        # delete all existing stage forms
        workflow.forms.filter(template__form_type=slack_const.FORM_TYPE_STAGE_GATING).delete()
        stage_form = org.custom_slack_forms.filter(
            form_type=slack_const.FORM_TYPE_STAGE_GATING, stage=selected_value
        ).first()

        if stage_form:
            workflow.add_form(
                slack_const.FORM_RESOURCE_OPPORTUNITY,
                slack_const.FORM_TYPE_STAGE_GATING,
                stage=selected_value,
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
            callback_id = slack_const.COMMAND_FORMS__SUBMIT_FORM
        elif view_type == "update_alert_modal_block_set":
            callback_id = slack_const.PROCESS_SUBMIT_ALERT_RESOURCE_DATA
        else:
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
            context = {
                **context,
                "form_type": slack_const.FORM_TYPE_CREATE,
                "callback_id": slack_const.COMMAND_FORMS__SUBMIT_FORM,
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


@processor()
def process_disregard_meeting_review(payload, context):
    workflow_id = payload["actions"][0]["value"]
    workflow = MeetingWorkflow.objects.get(id=workflow_id)
    organization = workflow.user.organization
    access_token = organization.slack_integration.access_token
    try:
        res = slack_requests.update_channel_message(
            payload["channel"]["id"],
            payload["message"]["ts"],
            access_token,
            block_set=get_block_set("disregard_meeting_review", context={"w": workflow_id}),
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
    workflow.slack_interaction = f"{res['ts']}|{res['channel']}"
    workflow.save()


@processor()
def process_no_changes_made(payload, context):
    workflow_id = payload["actions"][0]["value"]
    workflow = MeetingWorkflow.objects.get(id=workflow_id)
    organization = workflow.user.organization
    access_token = organization.slack_integration.access_token
    blocks = [*get_block_set("loading", {"message": ":+1: Got it! Logging your activity"})]
    try:
        slack_requests.update_channel_message(
            payload["channel"]["id"], payload["message"]["ts"], access_token, block_set=blocks,
        )
    except Exception as e:
        return logger.exception(f"Bad request {e}")
    state = {"meeting_type": "No Update", "meeting_comments": "No Update"}
    form = workflow.forms.filter(template__form_type=slack_const.FORM_TYPE_UPDATE).first()
    form.is_submitted = True
    form.submission_date = timezone.now()
    form.update_source = "meeting"
    form.save_form(state, False)
    ops = [
        f"{sf_consts.MEETING_REVIEW__SAVE_CALL_LOG}.{str(workflow.id)}",
    ]
    contact_forms = workflow.forms.filter(template__resource=slack_const.FORM_RESOURCE_CONTACT)
    for form in contact_forms:
        if form.template.form_type == slack_const.FORM_TYPE_CREATE:
            ops.append(
                f"{sf_consts.MEETING_REVIEW__CREATE_CONTACTS}.{str(workflow.id)},{str(form.id)}"
            )
        else:
            ops.append(
                f"{sf_consts.MEETING_REVIEW__UPDATE_CONTACTS}.{str(workflow.id)},{str(form.id)}"
            )
    workflow.operations_list = ops
    workflow.save()
    workflow.begin_tasks()
    emit_meeting_workflow_tracker(str(workflow.id))
    return {"response_action": "clear"}


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
def process_meeting_selected_resource(payload, context):
    """opens a modal with the options to search or create"""
    url = slack_const.SLACK_API_ROOT + slack_const.VIEWS_OPEN
    trigger_id = payload["trigger_id"]
    type = context.get("type", None)
    if type:
        workflow = MeetingPrepInstance.objects.get(id=context.get("w"))
    else:
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
    workflow_id = json.loads(payload["view"]["private_metadata"])["w"]
    type = context.get("type", None)
    if type:
        workflow = MeetingPrepInstance.objects.get(id=workflow_id)
    else:
        workflow = MeetingWorkflow.objects.get(id=workflow_id)
    select = payload["actions"][0]["selected_option"]["value"]
    resource_type = context.get("resource")
    action = None
    external_id = ""
    try:
        action, resource_type = select.split(".")
    except ValueError:

        pass
    context = {
        "w": workflow_id,
        "resource": resource_type,
    }
    if type:
        context.update({"type": type})
    if not action:
        blocks = [block_finder("select_existing", payload["view"]["blocks"])[1]]
        context["action"] = "EXISTING"
    else:
        context["action"] = "CREATE_NEW"
        blocks = [
            block_finder("select_existing", payload["view"]["blocks"])[1],
            *get_block_set("create_modal_block_set", context,),
        ]
        try:
            index, stage_block = block_finder("StageName", blocks)
        except ValueError:
            # did not find the block
            stage_block = None
            pass

        if stage_block:
            stage_block = {
                **stage_block,
                "accessory": {
                    **stage_block["accessory"],
                    "action_id": f"{slack_const.COMMAND_FORMS__STAGE_SELECTED}?u={str(workflow.user.id)}&f={str(workflow.forms.filter(template__form_type='CREATE', template__resource=resource_type).first().id)}",
                },
            }
            blocks = [*blocks[:index], stage_block, *blocks[index + 1 :]]

        external_id = f"create_modal_block_set.{str(uuid.uuid4())}"

    organization = workflow.user.organization
    access_token = organization.slack_integration.access_token
    # change variables based on selection
    private_metadata = json.loads(payload["view"]["private_metadata"])
    private_metadata.update({**context})
    if action == "CREATE_NEW":
        callback_id = slack_const.COMMAND_FORMS__SUBMIT_FORM
        private_metadata = json.loads(payload["view"]["private_metadata"])
        private_metadata = {
            **private_metadata,
            "u": str(workflow.user.id),
            "f": str(
                workflow.forms.filter(
                    template__form_type="CREATE", template__resource=resource_type
                )
                .first()
                .id
            ),
        }

    else:
        callback_id = (
            slack_const.PROCESS_DIGEST_ATTACH_RESOURCE
            if type
            else slack_const.ZOOM_MEETING__SELECTED_RESOURCE
        )

    data = {
        "view_id": payload["view"]["id"],
        "view": {
            "type": "modal",
            "callback_id": callback_id,
            "title": {"type": "plain_text", "text": f"{resource_type}"},
            "blocks": blocks,
            "private_metadata": json.dumps(private_metadata),
            "submit": {"type": "plain_text", "text": "Submit",},
            "external_id": external_id,
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


@processor()
def process_create_or_search_selected(payload, context):
    """attaches a drop down to the message block for selecting a resource type"""
    workflow_id = payload["actions"][0]["value"]
    type = False
    if "type" in workflow_id:
        type = True
        prep_id = workflow_id.split("%")[1]
        workflow = MeetingPrepInstance.objects.get(id=prep_id)
    else:
        workflow = MeetingWorkflow.objects.get(id=workflow_id)
        meeting = workflow.meeting
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
            previous_blocks.insert(2, block_sets[0])
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
        workflow.meeting.save()


@processor()
def process_restart_flow(payload, context):
    workflow_id = payload["actions"][0]["value"]
    workflow = MeetingWorkflow.objects.get(id=workflow_id)
    organization = workflow.user.organization
    access_token = organization.slack_integration.access_token
    ts, channel = workflow.slack_interaction.split("|")
    try:
        res = slack_requests.update_channel_message(
            channel,
            ts,
            access_token,
            block_set=get_block_set("initial_meeting_interaction", context={"w": workflow_id}),
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
            Q(resource="OpportunityLineItem", form_type="CREATE", organization=user.organization)
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
        blocks.extend(product_form.generate_form(Pricebook2Id=f"{pricebook}"))
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
            index, block = block_finder("StageName", blocks)
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
        access_token = user.organization.slack_integration.access_token

        url = slack_const.SLACK_API_ROOT + slack_const.VIEWS_UPDATE
        data = {
            "view_id": payload["view"]["id"],
            "view": {
                "type": "modal",
                "callback_id": slack_const.COMMAND_FORMS__SUBMIT_FORM,
                "title": {"type": "plain_text", "text": f"Create {resource_type}"},
                "blocks": blocks,
                "submit": {"type": "plain_text", "text": "Create", "emoji": True},
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
    # get the forms associated with this slack
    external_id = payload.get("view", {}).get("external_id", None)
    try:
        view_type, __unique_id = external_id.split(".")
    except ValueError:
        view_type = external_id
        pass
    current_forms = user.custom_slack_form_instances.filter(id__in=current_form_ids)
    # delete any existing stage forms
    current_forms.exclude(template__form_type__in=["UPDATE", "CREATE"]).delete()
    main_form = current_forms.first()
    added_form_ids = []
    if len(payload["actions"]):
        action = payload["actions"][0]
        blocks = payload["view"]["blocks"]
        selected_value = action["selected_option"]["value"]
        # blockfinder returns a tuple of its index in the block and the object
        index, action_block = block_finder(action["block_id"], blocks)

        # find all stages previous to it
        stage_form = org.custom_slack_forms.filter(
            form_type=slack_const.FORM_TYPE_STAGE_GATING, stage=selected_value
        ).first()
        if stage_form:
            new_form = OrgCustomSlackFormInstance.objects.create(
                user=user, template=stage_form, resource_id=main_form.resource_id
            )
            added_form_ids.append(str(new_form.id))

        # gather and attach all forms
    context = {**context, "f": ",".join([str(main_form.id), *added_form_ids])}
    private_metadata.update(context)
    updated_view_title = view["title"]
    if len(added_form_ids):
        submit_button_message = "Next"
        callback_id = slack_const.COMMAND_FORMS__PROCESS_NEXT_PAGE
    elif not len(added_form_ids) and main_form.template.form_type == "UPDATE":
        submit_button_message = "Update"
        callback_id = slack_const.COMMAND_FORMS__SUBMIT_FORM
    elif not len(added_form_ids) and main_form.template.form_type == "CREATE":
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


@slack_api_exceptions(rethrow=True)
@processor(required_context=["resource", "u"])
def process_show_update_resource_form(payload, context):
    from managr.slack.models import OrgCustomSlackForm, OrgCustomSlackFormInstance

    user = User.objects.get(id=context.get("u"))
    access_token = user.organization.slack_integration.access_token
    is_update = payload.get("view", None)
    view_type = "update" if is_update else "open"
    view_id = is_update["id"] if is_update else None
    trigger_id = payload["trigger_id"]
    type = context.get("type", None)
    loading_view_data = send_loading_screen(
        access_token,
        "Salesforce is being a bit slow :sleeping:… please give it a few seconds",
        view_type,
        str(user.id),
        trigger_id,
        view_id,
    )
    resource_id = payload["actions"][0]["selected_option"]["value"]
    resource_type = context.get("resource")
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
            template=template, resource_id=resource_id, user=user,
        )

        if slack_form:
            current_stage = slack_form.resource_object.secondary_data.get("StageName")
            stage_template = (
                OrgCustomSlackForm.objects.filter(stage=current_stage).first()
                if current_stage
                else None
            )
            form_ids = [str(slack_form.id)]
            if stage_template:
                stage_form = OrgCustomSlackFormInstance.objects.create(
                    template=stage_template, resource_id=resource_id, user=user,
                )
                form_ids.append(str(stage_form.id))
            context.update({"f": ",".join(form_ids)})

    blocks = get_block_set(
        "update_modal_block_set",
        context={**context, "resource_type": resource_type, "resource_id": resource_id},
    )
    if slack_form:
        try:
            index, block = block_finder("StageName", blocks)
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
        params = [
            f"f={str(slack_form.id)}",
            f"u={str(user.id)}",
            "type=command",
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
                            slack_const.PROCESS_ADD_PRODUCTS_FORM, params=params,
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


@processor(requried_context="u")
def process_coming_soon(payload, context):
    url = slack_const.SLACK_API_ROOT + slack_const.VIEWS_OPEN
    trigger_id = payload["trigger_id"]
    u = User.objects.get(id=context.get("u"))
    org = u.organization

    data = {
        "trigger_id": trigger_id,
        "view": {
            "type": "modal",
            "callback_id": "NEXT",
            "title": {"type": "plain_text", "text": f"Coming Soon"},
            "blocks": get_block_set("coming_soon_modal", {}),
        },
    }
    try:
        slack_requests.generic_request(url, data, access_token=org.slack_integration.access_token)

    except InvalidBlocksException as e:
        return logger.exception(f"Failed To Generate Blocks {e}")
    except InvalidBlocksFormatException as e:
        return logger.exception(f"Failed To Generate Blocks {e}")
    except UnHandeledBlocksException as e:
        return logger.exception(f"Failed To Generate Blocks {e}")
    except InvalidAccessToken as e:
        return logger.exception(f"Failed To send slack {e}")


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


@processor()
def process_request_invite_from_home_tab(payload, context):
    """
    According to slack anyone can see the home tab if a user triggers the home event
    And is not a user we show a button to request access, this will ask the is_admin user to invite them
    """
    # get the org team
    team_id = payload["user"]["team_id"]
    new_user_slack_id = payload["actions"][0]["value"]
    # get the is_admin user
    o = Organization.objects.filter(slack_integration__team_id=team_id).first()
    u = o.users.filter(is_admin=True).first()
    # send a message to invite the user
    slack_requests.send_ephemeral_message(
        u.slack_integration.channel,
        o.slack_integration.access_token,
        u.slack_integration.slack_id,
        text="User requested an invite",
        block_set=[
            block_builders.simple_section(
                f"<@{new_user_slack_id}> has requested an invite to Managr", "mrkdwn"
            )
        ],
    )
    old_view = payload["view"]
    blocks = old_view["blocks"]
    # remove the request button
    index, block = block_finder("INVITE_BUTTON", blocks)
    new_blocks = [
        *blocks[0:index],
        block_builders.simple_section("Invite Sent"),
        *blocks[index + 1 :],
    ]
    view = {"type": "home", "blocks": new_blocks}
    slack_requests.publish_view(new_user_slack_id, o.slack_integration.access_token, view)
    # update the home tab of the user with message that it was sent


@slack_api_exceptions(rethrow=True)
@processor(required_context=["resource", "u"])
def process_check_is_owner(payload, context):
    # CHECK_IS_OWNER
    slack_id = payload.get("user", {}).get("id")
    user_id = context.get("u")
    type = context.pop("type", None)
    user_slack = UserSlackIntegration.objects.filter(slack_id=slack_id).first()
    if user_slack and str(user_slack.user.id) == user_id:
        if type == "alert":
            return process_show_alert_update_resource_form(payload, context)
        elif type == "prep":
            return process_show_digest_update_resource_form(payload, context)
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
            "blocks": get_block_set(view_type, {**context, "resource_type": selected_value}),
            "private_metadata": json.dumps(context),
            "external_id": f"{view_type}.{str(uuid.uuid4())}",
        },
    }
    if (payload["view"]["submit"] and form_id) or view_type == "create_task_modal":
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

    if len(actions) and actions[0]["type"] == "button":
        selected_option = actions[0]["value"]
    else:
        selected_option = None
    external_id = payload.get("view", {}).get("external_id", None)
    try:
        view_type, __unique_id = external_id.split(".")
    except ValueError:
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
        "f": selected_option,
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
    form_blocks = get_block_set(view_type, view_context)
    if main_form and not from_workflow:
        try:
            index, stage_block = block_finder("StageName", form_blocks)
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
        if view_type == "update_modal_block_set"
        else f"Create {resource_type}"
    )
    if type == "alert":
        callback_id = slack_const.PROCESS_SUBMIT_ALERT_RESOURCE_DATA
    elif type == "digest":
        callback_id = slack_const.PROCESS_SUBMIT_DIGEST_RESOURCE_DATA
    else:
        callback_id = slack_const.COMMAND_FORMS__SUBMIT_FORM
    submit_text = "Update" if view_type == "update_modal_block_set" else "Create"

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


@processor(required_context="u")
def process_show_cadence_modal(payload, context):
    u = User.objects.get(id=context.get("u"))
    trigger_id = payload["trigger_id"]
    org = u.organization
    access_token = org.slack_integration.access_token
    is_update = payload.get("view", None)
    view_id = is_update.get("id") if is_update is not None else None
    loading_view_data = send_loading_screen(
        access_token, "Putting together your cadences", "open", str(u.id), trigger_id, view_id
    )
    type = context.get("type", None)
    resource_name = (
        payload["view"]["state"]["values"]["select_existing"][
            f"{slack_const.GET_USER_ACCOUNTS}?u={u.id}&type=command&system=salesloft"
        ]["selected_option"]["text"]["text"]
        if type == "command"
        else context.get("resource_name")
    )
    resource_id = (
        payload["view"]["state"]["values"]["select_existing"][
            f"{slack_const.GET_USER_ACCOUNTS}?u={u.id}&type=command&system=salesloft"
        ]["selected_option"]["value"]
        if type == "command"
        else context.get("resource_id")
    )
    resource_type = "Account" if type == "command" else context.get("resource_type")
    if is_update:
        meta_data = json.loads(payload["view"]["private_metadata"])
    private_metadata = {
        "resource_name": resource_name,
        "resource_id": resource_id,
        "resource_type": resource_type,
    }
    if type != "command":
        private_metadata.update({"channel_id": payload["channel"]["id"]})
    private_metadata.update(context)

    data = {
        "view_id": loading_view_data["view"]["id"],
        "view": {
            "type": "modal",
            "callback_id": slack_const.ADD_TO_CADENCE,
            "title": {"type": "plain_text", "text": "Add to a Cadence"},
            "blocks": get_block_set(
                "cadence_modal_blockset",
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
def process_show_sequence_modal(payload, context):
    u = User.objects.get(id=context.get("u"))
    trigger_id = payload["trigger_id"]
    org = u.organization
    access_token = org.slack_integration.access_token
    is_update = payload.get("view", None)
    view_id = is_update.get("id") if is_update is not None else None
    loading_view_data = send_loading_screen(
        access_token, "Putting together your sequences", "open", str(u.id), trigger_id, view_id
    )
    type = context.get("type", None)
    resource_name = (
        payload["view"]["state"]["values"]["select_existing"][
            f"{slack_const.GET_USER_ACCOUNTS}?u={u.id}&type=command&system=outreach"
        ]["selected_option"]["text"]["text"]
        if type == "command"
        else context.get("resource_name")
    )
    resource_id = (
        payload["view"]["state"]["values"]["select_existing"][
            f"{slack_const.GET_USER_ACCOUNTS}?u={u.id}&type=command&system=outreach"
        ]["selected_option"]["value"]
        if type == "command"
        else context.get("resource_id")
    )
    resource_type = "Account" if type == "command" else context.get("resource_type")
    if is_update:
        meta_data = json.loads(payload["view"]["private_metadata"])
    private_metadata = {
        "resource_name": resource_name,
        "resource_id": resource_id,
        "resource_type": resource_type,
    }
    if type != "command":
        private_metadata.update({"channel_id": payload["channel"]["id"]})
    private_metadata.update(context)
    data = {
        "view_id": loading_view_data["view"]["id"],
        "view": {
            "type": "modal",
            "callback_id": slack_const.ADD_TO_SEQUENCE,
            "title": {"type": "plain_text", "text": "Add to a Sequence"},
            "blocks": get_block_set(
                "sequence_modal_blockset",
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


def process_show_engagement_modal(payload, context):
    system = context.get("system", None)
    if system == "outreach":
        process_show_sequence_modal(payload, context)
    else:
        process_show_cadence_modal(payload, context)


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
        context.get("resource_id", None)
        if type != "command"
        else payload["view"]["state"]["values"]["select_opp"][
            f"GET_NOTES?u={u.id}&resource=Opportunity&type=command"
        ]["selected_option"]["value"]
    )
    if resource_type == "Opportunity":
        resource = Opportunity.objects.get(id=resource_id)
    elif resource_type == "Account":
        resource = Account.objects.get(id=context.get("resource_id"))
    elif resource_type == "Lead":
        resource = Lead.objects.get(id=context.get("resource_id"))
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
        block_builders.header_block(f"Notes for {resource.name}")
        if note_data
        else block_builders.header_block(
            f"No notes for {resource.name}, start leaving notes! :smiley:"
        )
    ]
    if note_data:
        for note in note_data:
            date = note[0].date() if note[0] is not None else " "
            current_stage = note[3]
            previous_stage = note[4]
            block_message = f"*{date} - {note[1]}*\n"
            if current_stage and previous_stage:
                if current_stage != previous_stage:
                    block_message += f"Stage: ~{previous_stage}~ :arrow_right: {current_stage} \n"
            block_message += f"\nNotes:\n {note[2]}"
            note_blocks.append(block_builders.simple_section(block_message, "mrkdwn"))
            note_blocks.append({"type": "divider"})
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
    user = User.objects.get(id=context.get("u"))
    access_token = user.organization.slack_integration.access_token
    trigger_id = payload["trigger_id"] if "trigger_id" in payload else None
    view_type = "open" if type == "alert" else "push"
    try:
        view_id = payload["view"]["id"]
    except KeyError:
        view_id = None
    loading_view_data = send_loading_screen(
        access_token, "Checking for a call details...", view_type, str(user.id), trigger_id, view_id
    )
    resource_id = context.get("resource_id", None)
    url = slack_const.SLACK_API_ROOT + slack_const.VIEWS_UPDATE
    if resource_id is None and type != "recap":
        timestamp = datetime.fromtimestamp(float(payload["actions"][0]["action_ts"]))
        resource_type = payload["view"]["state"]["values"]["managr_task_related_to_resource"][
            f"UPDATE_TASK_SELECTED_RESOURCE?u={context.get('u')}"
        ]["selected_option"]["value"]
        resource_id = payload["view"]["state"]["values"]["select_existing"][
            f"GONG_CALL_RECORDING?u={context.get('u')}&resource={resource_type}"
        ]["selected_option"]["value"]
    else:
        resource_type = context.get("resource_type")
        timestamp = datetime.fromtimestamp(float(payload["actions"][0]["action_ts"]))

    user_tz = datetime.now(pytz.timezone(user.timezone)).strftime("%z")
    user_timezone = pytz.timezone(user.timezone)
    gong_auth = GongAuthAccount.objects.get(organization=user.organization)
    resource_ids = []
    resource = None
    opps = Opportunity.objects.filter(id=resource_id)
    if opps:
        resource_ids.append(opps.first().integration_id)
        acc = Account.objects.filter(opportunities__in=[opps.first().id]).first()
        resource = opps.first()
        if acc:
            resource_ids.append(acc.integration_id)
    else:
        accs = Account.objects.filter(id=resource_id)
        if accs:
            resource_ids.append(accs.first().integration_id)
            resource = accs.first()
    call = GongCall.objects.filter(crm_id=resource.secondary_data["Id"]).first()
    current = pytz.utc.localize(timestamp).astimezone(user_timezone).date()
    blocks = []
    if type == "recap" and datetime.now().date() == current:
        curr_date = date.today()
        curr_date_str = curr_date.isoformat() + "T01:00:00" + f"{user_tz[:3]}:{user_tz[3:]}"
        try:
            call_res = gong_auth.helper_class.check_for_current_call(curr_date_str)
            call_details = generate_call_block(call_res, resource_ids)
            if call_details:
                blocks = [*call_details]
            else:
                if call:
                    call_details = generate_call_block(call_res)
                    blocks = [*call_details]
                    blocks.append(
                        block_builders.context_block(
                            "Gong may still be processing this call, check back in a bit"
                        )
                    )
                else:
                    logger.info("Gong call recap without call")
                    blocks = [
                        block_builders.simple_section("No call associated with this opportunity")
                    ]
        except InvalidRequest as e:
            logger.exception(f"Gong invalid request: {e}")
            if call:
                call_res = call.helper_class.get_call_details(call.auth_account.access_token)
                call_details = generate_call_block(call_res)
                blocks = [*call_details]
                blocks.append(
                    block_builders.context_block(
                        "Gong may still be processing this call, check back in a bit"
                    )
                )
            else:
                blocks = [
                    block_builders.simple_section("No call associated with this opportunity*"),
                    block_builders.context_block(
                        "*Gong may still be processing this call, check back in a bit"
                    ),
                ]
    else:
        if call:
            call_res = call.helper_class.get_call_details(call.auth_account.access_token)
            call_details = generate_call_block(call_res)
            blocks = [*call_details]
        else:
            logger.info("Gong details from non recap")
            blocks = [
                block_builders.simple_section("No call associated with this opportunity*"),
                block_builders.context_block(
                    "*Gong may still be processing this call, check back in a bit"
                ),
            ]
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
def process_call_error(payload, context):
    u = User.objects.get(id=context.get("u"))

    org = u.organization
    access_token = org.slack_integration.access_token
    blocks = [block_builders.header_block(f"Call analysis still in progress ")]
    url = slack_const.SLACK_API_ROOT + slack_const.VIEWS_OPEN
    trigger_id = payload["trigger_id"]
    data = {
        "trigger_id": trigger_id,
        "view": {
            "type": "modal",
            "callback_id": "NONE",
            "title": {"type": "plain_text", "text": "Call Details"},
            "blocks": blocks,
        },
    }
    slack_requests.generic_request(url, data, access_token=access_token)
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
    if not user:
        return
    access_token = user.organization.slack_integration.access_token
    invocation = context.get("invocation")
    channel = context.get("channel")
    config_id = context.get("config_id")
    alert_instances = AlertInstance.objects.filter(
        invocation=invocation, channel=channel, config_id=config_id
    ).filter(completed=False)
    alert_instance = alert_instances.first()
    if not alert_instance:
        # check if the config was deleted
        config = AlertConfig.objects.filter(id=config_id).first()
        if not config:
            error_blocks = get_block_set(
                "error_modal",
                {
                    "message": ":no_entry: The settings for these instances was deleted the data is no longer available"
                },
            )
            slack_requests.update_channel_message(
                channel_id, ts, access_token, text="Error", block_set=error_blocks
            )
        return
    alert_template = alert_instance.template
    alert_text = alert_template.title
    blocks = [
        block_builders.header_block(f"{len(alert_instances)} results for workflow {alert_text}"),
    ]
    alert_instances = custom_paginator(alert_instances, page=int(context.get("new_page", 0)))
    for alert_instance in alert_instances.get("results", []):
        blocks = [
            *blocks,
            *get_block_set(
                "alert_instance",
                {
                    "instance_id": str(alert_instance.id),
                    "current_page": int(context.get("new_page", 0)),
                },
            ),
        ]
        alert_instance.rendered_text = alert_instance.render_text()
        alert_instance.save()
    if len(blocks):
        blocks = [
            *blocks,
            *custom_paginator_block(alert_instances, invocation, channel, config_id),
        ]
    slack_requests.update_channel_message(
        channel_id, ts, access_token, text=alert_text, block_set=blocks
    )

    return


@slack_api_exceptions(rethrow=True)
@processor(required_context=["resource", "u"])
def process_show_alert_update_resource_form(payload, context):
    from managr.slack.models import OrgCustomSlackForm, OrgCustomSlackFormInstance

    user = User.objects.get(id=context.get("u"))
    access_token = user.organization.slack_integration.access_token
    trigger_id = payload["trigger_id"]
    loading_view_data = send_loading_screen(
        access_token,
        "Salesforce is being a bit slow :sleeping:… please give it a few seconds",
        "open",
        str(user.id),
        trigger_id,
    )
    resource_id = payload["actions"][0]["value"]
    alert_instance = AlertInstance.objects.get(id=context.get("alert_id"))
    resource_type = context.get("resource")
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
            template=template, resource_id=resource_id, user=user, alert_instance_id=alert_instance,
        )
    if slack_form:
        current_stage = slack_form.resource_object.secondary_data.get("StageName")
        stage_template = (
            OrgCustomSlackForm.objects.filter(stage=current_stage).first()
            if current_stage
            else None
        )
        form_ids = [str(slack_form.id)]
        if stage_template:
            stage_form = OrgCustomSlackFormInstance.objects.create(
                template=stage_template, resource_id=resource_id, user=user,
            )
            form_ids.append(str(stage_form.id))
        context.update({"f": ",".join(form_ids)})
    blocks = get_block_set(
        "update_modal_block_set",
        context={**context, "resource_type": resource_type, "resource_id": resource_id},
    )
    if slack_form:
        try:
            index, block = block_finder("StageName", blocks)
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
    private_metadata = {
        "channel_id": payload.get("container").get("channel_id"),
        "message_ts": payload.get("container").get("message_ts"),
    }
    private_metadata.update(context)
    if user.organization.has_products and resource_type == "Opportunity":
        params = [
            f"f={str(slack_form.id)}",
            f"u={str(user.id)}",
            "type=command",
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


@processor(required_context="u")
def process_mark_complete(payload, context):
    user = User.objects.get(id=context.get("u"))
    access_token = user.organization.slack_integration.access_token
    instance = AlertInstance.objects.get(id=context.get("instance_id"))
    instance.completed = True
    instance.save()
    alert_instances = AlertInstance.objects.filter(
        invocation=instance.invocation,
        channel=payload["channel"]["id"],
        config_id=instance.config_id,
    ).filter(completed=False)
    alert_instance = alert_instances.first()
    alert_template = alert_instance.template
    text = alert_template.title
    if not alert_instance:
        blocks = [
            block_builders.simple_section("You're all caught up with this workflows! Great job!"),
        ]
        slack_requests.update_channel_message(
            payload["channel"]["id"],
            payload["message"]["ts"],
            access_token,
            text="Error",
            block_set=blocks,
        )
        return

    blocks = [
        block_builders.header_block(f"{len(alert_instances)} results for workflow {text}"),
    ]
    alert_instances = custom_paginator(alert_instances, page=int(context.get("page")))
    for alert_instance in alert_instances.get("results", []):
        blocks = [
            *blocks,
            *get_block_set(
                "alert_instance",
                {"instance_id": str(alert_instance.id), "current_page": int(context.get("page")),},
            ),
        ]
        alert_instance.rendered_text = alert_instance.render_text()
        alert_instance.save()
    if len(blocks):
        blocks = [
            *blocks,
            *custom_paginator_block(
                alert_instances, instance.invocation, payload["channel"]["id"], instance.config_id
            ),
        ]

    res = slack_requests.update_channel_message(
        payload["channel"]["id"], payload["message"]["ts"], access_token, block_set=blocks,
    )
    return


#########################################################
# MORNING/AFTERNOON DIGEST ACTIONS
#########################################################


@slack_api_exceptions(rethrow=True)
@processor()
def process_paginate_meetings(payload, context):
    channel_id = payload.get("channel", {}).get("id", None)
    ts = payload.get("message", {}).get("ts", None)
    user_slack_id = payload.get("user", {}).get("id", None)
    user = User.objects.filter(slack_integration__slack_id=user_slack_id).first()
    if not user:
        return
    access_token = user.organization.slack_integration.access_token
    invocation = context.get("invocation")
    channel = context.get("channel")
    meeting_instances = MeetingPrepInstance.objects.filter(user=user.id).filter(
        invocation=invocation
    )
    meeting_instance = meeting_instances.first()
    if not meeting_instance:
        return
    # NOTE replace [3:8]
    blocks = payload["message"]["blocks"]
    meeting_instances = custom_paginator(
        meeting_instances, count=1, page=int(context.get("new_page", 0))
    )
    paginate_results = meeting_instances.get("results", [])
    if len(paginate_results):
        current_instance = paginate_results[0]
        replace_blocks = [
            *get_block_set(
                "calendar_reminders_blockset",
                {
                    "prep_id": str(current_instance.id),
                    "u": str(user.id),
                    "current_page": context.get("new_page", 1),
                },
            ),
            *custom_meeting_paginator_block(meeting_instances, invocation, channel),
        ]
        blocks[3:7] = replace_blocks
        slack_requests.update_channel_message(channel_id, ts, access_token, block_set=blocks)
    return


@slack_api_exceptions(rethrow=True)
@processor()
def process_paginate_tasks(payload, context):
    channel_id = payload.get("channel", {}).get("id", None)
    ts = payload.get("message", {}).get("ts", None)
    user_slack_id = payload.get("user", {}).get("id", None)
    user = User.objects.filter(slack_integration__slack_id=user_slack_id).first()
    if not user:
        return
    access_token = user.organization.slack_integration.access_token
    channel = context.get("channel")
    # NOTE replace [3:8]
    blocks = payload["message"]["blocks"]
    header_index, header_block = block_finder("task_header", blocks)
    divider_index, divider_block = block_finder("task_divider", blocks)
    replace_blocks = process_get_task_list(user.id, page=int(context.get("new_page", 0)))
    blocks[header_index:divider_index] = replace_blocks
    slack_requests.update_channel_message(channel_id, ts, access_token, block_set=blocks)
    return


@slack_api_exceptions(rethrow=True)
@processor(required_context=["resource", "u"])
def process_show_digest_update_resource_form(payload, context):
    from managr.slack.models import OrgCustomSlackForm, OrgCustomSlackFormInstance

    user = User.objects.get(id=context.get("u"))
    access_token = user.organization.slack_integration.access_token
    trigger_id = payload["trigger_id"]
    loading_view_data = send_loading_screen(
        access_token,
        "Salesforce is being a bit slow :sleeping:… please give it a few seconds",
        "open",
        str(user.id),
        trigger_id,
    )
    resource_id = payload["actions"][0]["value"]
    resource_type = context.get("resource")
    show_submit_button_if_fields_added = False
    stage_form = None
    prep_instance = MeetingPrepInstance.objects.get(id=context.get("prep_id"))
    # HACK forms are generated with a helper fn currently stagename takes a special action id to update forms
    # we need to manually change this action_id
    if prep_instance.form:
        slack_form = prep_instance.form
    else:
        template = (
            OrgCustomSlackForm.objects.for_user(user)
            .filter(Q(resource=resource_type, form_type="UPDATE"))
            .first()
        )
        slack_form = OrgCustomSlackFormInstance.objects.create(
            template=template, resource_id=resource_id, user=user,
        )
        prep_instance.form = slack_form
        prep_instance.save()
    if slack_form:
        current_stage = slack_form.resource_object.secondary_data.get("StageName")
        stage_template = (
            OrgCustomSlackForm.objects.filter(stage=current_stage).first()
            if current_stage
            else None
        )
        form_ids = [str(slack_form.id)]
        if stage_template:
            stage_form = OrgCustomSlackFormInstance.objects.create(
                template=stage_template, resource_id=resource_id, user=user,
            )
            form_ids.append(str(stage_form.id))
        context.update({"f": ",".join(form_ids)})

    blocks = get_block_set(
        "update_modal_block_set",
        context={**context, "resource_type": resource_type, "resource_id": resource_id},
    )
    if slack_form:
        try:
            index, block = block_finder("StageName", blocks)
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
    private_metadata = {
        "channel_id": payload.get("container").get("channel_id"),
        "message_ts": payload.get("container").get("message_ts"),
    }
    private_metadata.update(context)
    if user.organization.has_products and resource_type == "Opportunity":
        params = [
            f"f={str(slack_form.id)}",
            f"u={str(user.id)}",
            "type=command",
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

    data = {
        "view_id": loading_view_data["view"]["id"],
        "view": {
            "type": "modal",
            "title": {"type": "plain_text", "text": f"Update {resource_type}"},
            "blocks": blocks,
            "private_metadata": json.dumps(private_metadata),
            "external_id": f"update_modal_block_set.{str(uuid.uuid4())}",
        },
    }
    if show_submit_button_if_fields_added:
        if stage_form:
            submit_button_text = "Next"
            callback_id = slack_const.COMMAND_FORMS__PROCESS_NEXT_PAGE
        else:
            submit_button_text = "Update"
            callback_id = slack_const.PROCESS_SUBMIT_DIGEST_RESOURCE_DATA

        data["view"]["submit"] = {"type": "plain_text", "text": submit_button_text, "emoji": True}
        data["view"]["callback_id"] = callback_id

    slack_requests.generic_request(
        slack_const.SLACK_API_ROOT + slack_const.VIEWS_UPDATE, data, access_token=access_token
    )


#########################################################
# RECAP ACTIONS
#########################################################


@processor()
def process_send_recap_modal(payload, context):
    url = slack_const.SLACK_API_ROOT + slack_const.VIEWS_UPDATE
    user = User.objects.get(id=context.get("u"))
    access_token = user.organization.slack_integration.access_token
    trigger_id = payload["trigger_id"]
    loading_data = send_loading_screen(
        access_token, "Loading users and channels", "open", str(user.id), trigger_id
    )
    type = context.get("type")
    if type == "meeting":
        workflow = MeetingWorkflow.objects.get(id=context.get("workflow_id"))
        params = {"u": context.get("u"), "workflow_id": workflow.id}
    else:
        params = {"u": context.get("u"), "form_id": context.get("form_id")}

    data = {
        "view_id": loading_data["view"]["id"],
        "view": {
            "type": "modal",
            "callback_id": slack_const.PROCESS_SEND_RECAPS,
            "title": {"type": "plain_text", "text": "Send Recaps"},
            "blocks": get_block_set("send_recap_block_set", params),
            "submit": {"type": "plain_text", "text": "Send"},
            "private_metadata": json.dumps(context),
        },
    }
    try:
        res = slack_requests.generic_request(url, data, access_token=access_token)
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
            f"Failed To Generate Slack Workflow Interaction for user with workflow {str(user.id)} email {user.email} {e}"
        )


@processor(required_context="u")
def process_view_recap(payload, context):
    form_id_str = context.get("form_ids")
    form_ids = form_id_str.split(".")
    submitted_forms = OrgCustomSlackFormInstance.objects.filter(id__in=form_ids).exclude(
        template__resource="OpportunityLineItem"
    )
    main_form = submitted_forms.filter(
        template__form_type__in=["CREATE", "UPDATE", "MEETING_REVIEW"]
    ).first()
    user = main_form.user
    access_token = user.organization.slack_integration.access_token
    loading_view_data = send_loading_screen(
        access_token, "Processing your recap", "open", str(user.id), payload["trigger_id"]
    )
    old_data = dict()
    if main_form.template.form_type == "UPDATE" or main_form.template.form_type == "MEETING_REVIEW":
        for additional_stage_form in submitted_forms:
            old_data = {**old_data, **additional_stage_form.previous_data}
    new_data = dict()
    form_fields = None
    for form in submitted_forms:
        new_data = {**new_data, **form.saved_data}
        if form_fields:
            form_fields = form_fields | form.template.formfield_set.filter(include_in_recap=True)
        else:
            form_fields = form.template.formfield_set.filter(include_in_recap=True)
    blocks = []

    message_string_for_recap = ""
    for key, new_value in new_data.items():
        field = form_fields.filter(field__api_name=key).first()
        if not field:
            continue
        field_label = field.field.reference_display_label
        if main_form.template.form_type == "UPDATE":
            # Only sends values for fields that have been updated
            # all fields on update form are included by default users cannot edit
            if key in old_data:
                if str(old_data.get(key)) != str(new_value):
                    old_value = old_data.get(key)
                    if field.field.is_public and field.field.data_type == "Reference":
                        old_value = check_for_display_value(field.field, old_value)
                        new_value = check_for_display_value(field.field, new_value)

                    message_string_for_recap += (
                        f"\n*{field_label}:* ~{old_data.get(key)}~ :arrow_right: {new_value}"
                    )
        elif main_form.template.form_type == "MEETING_REVIEW":
            old_value = old_data.get(key)
            if key in old_data and str(old_value) != str(new_value):

                if field.field.is_public and field.field.data_type == "Reference":
                    old_value = check_for_display_value(field.field, old_value)
                    new_value = check_for_display_value(field.field, new_value)
                message_string_for_recap += (
                    f"\n*{field_label}:* ~{old_value}~ :arrow_right: {new_value}"
                )
            else:
                if field.field.is_public and field.field.data_type == "Reference":
                    new_value = check_for_display_value(field.field, new_value)
                message_string_for_recap += f"\n*{field_label}:* {new_value}"

        elif main_form.template.form_type == "CREATE":

            if new_value:
                if field.field.is_public and field.field.data_type == "Reference":
                    new_value = check_for_display_value(field.field, new_value)
                message_string_for_recap += f"\n*{field_label}:* {new_value}"
    if not len(message_string_for_recap):
        message_string_for_recap = "No Data to show from form"

    blocks.append(block_builders.simple_section(message_string_for_recap, "mrkdwn"))
    action_blocks = [
        block_builders.simple_button_block(
            "View Notes",
            "get_notes",
            action_id=action_with_params(
                slack_const.GET_NOTES,
                params=[
                    f"u={str(user.id)}",
                    f"resource_id={str(main_form.resource_id)}",
                    "type=recap",
                    f"resource_type={main_form.template.resource}",
                ],
            ),
        ),
    ]
    if main_form.template.resource != "Lead":
        action_blocks.append(
            block_builders.simple_button_block(
                "Call Details",
                "call_details",
                action_id=action_with_params(
                    slack_const.GONG_CALL_RECORDING,
                    params=[
                        f"u={str(user.id)}",
                        f"resource_id={main_form.resource_id}",
                        f"resource_type={main_form.template.resource}",
                        "type=recap",
                    ],
                ),
                style="primary",
            ),
        )
    blocks.append(block_builders.actions_block(action_blocks))

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
        slack_const.ZOOM_MEETING__PROCESS_NO_CHANGES: process_no_changes_made,
        slack_const.ZOOM_MEETING__DISREGARD_REVIEW: process_disregard_meeting_review,
        slack_const.ZOOM_MEETING__RESTART_MEETING_FLOW: process_restart_flow,
        slack_const.ZOOM_MEETING__INIT_REVIEW: process_meeting_review,
        slack_const.ZOOM_MEETING__STAGE_SELECTED: process_stage_selected,
        slack_const.ZOOM_MEETING__CREATE_TASK: process_create_task,
        slack_const.ZOOM_MEETING__CONVERT_LEAD: process_coming_soon,
        slack_const.ZOOM_MEETING__MEETING_DETAILS: process_meeting_details,
        slack_const.COMMAND_FORMS__GET_LOCAL_RESOURCE_OPTIONS: process_show_update_resource_form,
        slack_const.PROCESS_SHOW_ALERT_UPDATE_RESOURCE_FORM: process_show_alert_update_resource_form,
        slack_const.PROCESS_SHOW_DIGEST_UPDATE_RESOURCE_FORM: process_show_digest_update_resource_form,
        slack_const.COMMAND_FORMS__STAGE_SELECTED: process_stage_selected_command_form,
        slack_const.COMMAND_FORMS__PROCESS_ADD_CREATE_FORM: process_add_create_form,
        slack_const.UPDATE_TASK_SELECTED_RESOURCE: process_resource_selected_for_task,
        slack_const.HOME_REQUEST_SLACK_INVITE: process_request_invite_from_home_tab,
        slack_const.RETURN_TO_FORM_MODAL: process_return_to_form_modal,
        slack_const.CHECK_IS_OWNER_FOR_UPDATE_MODAL: process_check_is_owner,
        slack_const.PAGINATE_ALERTS: process_paginate_alerts,
        slack_const.PAGINATE_MEETINGS: process_paginate_meetings,
        slack_const.PAGINATE_TASKS: process_paginate_tasks,
        slack_const.ADD_TO_CADENCE_MODAL: process_show_cadence_modal,
        slack_const.ADD_TO_SEQUENCE_MODAL: process_show_sequence_modal,
        slack_const.GET_USER_ACCOUNTS: process_show_engagement_modal,
        slack_const.GET_NOTES: process_get_notes,
        slack_const.CALL_ERROR: process_call_error,
        slack_const.GONG_CALL_RECORDING: process_get_call_recording,
        slack_const.MARK_COMPLETE: process_mark_complete,
        slack_const.PROCESS_SEND_RECAP_MODAL: process_send_recap_modal,
        slack_const.COMMAND_MANAGR_ACTION: process_managr_action,
        slack_const.PROCESS_SHOW_EDIT_PRODUCT_FORM: process_show_edit_product_form,
        slack_const.PROCESS_ADD_PRODUCTS_FORM: process_add_products_form,
        slack_const.VIEW_RECAP: process_view_recap,
        slack_const.GET_PRICEBOOK_ENTRY_OPTIONS: process_pricebook_selected,
    }
    action_query_string = payload["actions"][0]["action_id"]
    processed_string = process_action_id(action_query_string)
    action_id = processed_string.get("true_id")
    action_params = processed_string.get("params")
    # added special key __block_action to allow us to override the defaults since the action_id is used for both the suggestions and the actions
    if action_params.get("__block_action", None):
        action_id = action_params.get("__block_action")

    return switcher.get(action_id, NO_OP)(payload, action_params)
