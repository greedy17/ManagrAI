import json
import pdb
import logging
from urllib.parse import urlencode
from managr.organization.models import Organization, Stage
from managr.opportunity.models import Opportunity
from managr.zoom.models import ZoomMeeting
from managr.slack import constants as slack_const
from managr.opportunity import constants as opp_consts
from managr.slack.helpers import requests as slack_requests
from managr.slack.helpers.utils import process_action_id, NO_OP, processor, block_finder
from managr.slack.helpers.block_sets import get_block_set
from managr.slack.helpers import block_builders
from managr.salesforce.models import MeetingWorkflow
from managr.core.models import User


logger = logging.getLogger("managr")


@processor()
def process_meeting_review(payload, context):
    url = slack_const.SLACK_API_ROOT + slack_const.VIEWS_OPEN
    trigger_id = payload["trigger_id"]
    workflow_id = payload["actions"][0]["value"]
    workflow = MeetingWorkflow.objects.get(id=workflow_id)
    meeting = workflow.meeting
    organization = meeting.zoom_account.user.organization
    access_token = organization.slack_integration.access_token
    private_metadata = {
        "original_message_channel": payload["channel"]["id"],
        "original_message_timestamp": payload["message"]["ts"],
    }
    context = {"w": workflow_id}

    private_metadata.update(context)
    data = {
        "trigger_id": trigger_id,
        "view": {
            "type": "modal",
            "callback_id": slack_const.ZOOM_MEETING__PROCESS_MEETING_SENTIMENT,
            "title": {"type": "plain_text", "text": "Log Meeting"},
            "blocks": get_block_set("meeting_review_modal", context=context),
            "submit": {"type": "plain_text", "text": "Submit"},
            "private_metadata": json.dumps(private_metadata),
        },
    }
    res = slack_requests.generic_request(url, data, access_token=access_token)
    print(res.json())
    view_id = res.json().get("view").get("id")
    workflow.slack_view = view_id
    # meeting.slack_form = view_id
    workflow.save()


@processor(required_context=["o", "u", "opp", "m"])
def process_zoom_meeting_different_opportunity(payload, context):
    url = slack_const.SLACK_API_ROOT + slack_const.VIEWS_OPEN
    trigger_id = payload["trigger_id"]
    access_token = (
        Organization.objects.select_related("slack_integration")
        .get(pk=context["o"])
        .slack_integration.access_token
    )

    private_metadata = {
        "original_message_channel": payload["channel"]["id"],
        "original_message_timestamp": payload["message"]["ts"],
    }
    private_metadata.update(context)

    data = {
        "trigger_id": trigger_id,
        "view": {
            "type": "modal",
            "callback_id": slack_const.ZOOM_MEETING__DIFFERENT_OPPORTUNITY,
            "title": {"type": "plain_text", "text": "Change Opportunity"},
            "blocks": get_block_set("select_different_opportunity", context=context),
            "submit": {"type": "plain_text", "text": "Submit"},
            "private_metadata": json.dumps(private_metadata),
        },
    }
    slack_requests.generic_request(url, data, access_token=access_token)


@processor(required_context=["w"], action=slack_const.VIEWS_OPEN)
def process_show_meeting_contacts(payload, context, action=slack_const.VIEWS_OPEN):
    url = slack_const.SLACK_API_ROOT + action
    trigger_id = payload["trigger_id"]
    # view_id = payload["view"]["id"]
    workflow = MeetingWorkflow.objects.get(id=context.get("w"))
    meeting = workflow.meeting
    org = workflow.user.organization

    access_token = org.slack_integration.access_token
    blocks = get_block_set("show_meeting_contacts", context,)

    data = {
        "trigger_id": trigger_id,
        # "view_id": view_id,
        "view": {
            "type": "modal",
            # "callback_id": slack_const.ZOOM_MEETING__SAVE_CONTACTS,
            "title": {"type": "plain_text", "text": "Contacts"},
            # "submit": {"type": "plain_text", "text": "Submit"},
            "blocks": blocks,
            "private_metadata": json.dumps(context),
        },
    }
    if action == slack_const.VIEWS_UPDATE:
        data["view_id"] = payload["view"]["id"]

    # private_metadata.update(context)

    res = slack_requests.generic_request(url, data, access_token=access_token)
    print(res.json())


@processor(required_context=["m"])
def process_get_meeting_score_components(payload, context):
    try:
        url = slack_const.SLACK_API_ROOT + slack_const.VIEWS_OPEN
        trigger_id = payload["trigger_id"]
        meeting = ZoomMeeting.objects.filter(id=context.get("m")).first()
        org = meeting.zoom_account.user.organization
        access_token = org.slack_integration.access_token
        sentiment = ""
        stage = ""
        forecast = ""
        close_date = ""
        attendance = ""
        duration = ""

        for comp in meeting.meeting_score_components:
            if comp["type"] == "sentiment":
                sentiment = comp.get("message", "N/A")
            if comp["type"] == "stage":
                stage = comp.get("message", "N/A")
            if comp["type"] == "forecast":
                forecast = comp.get("message", "N/A")
            if comp["type"] == "close_date":
                close_date = comp.get("message", "N/A")
            if comp["type"] == "attendance":
                attendance = comp.get("message", "N/A")
            if comp["type"] == "duration":
                duration = comp.get("message", "N/A")

        paragraph = f"{sentiment} \n {stage} {forecast} {close_date} \n {attendance} {duration}"

        private_metadata = {
            "original_message_channel": payload["channel"]["id"],
            "original_message_timestamp": payload["message"]["ts"],
        }
        empty_block = [
            {"type": "section", "text": {"type": "mrkdwn", "text": "No Scoring Data to show"},}
        ]
        blocks = [get_block_set("show_meeting_score_description", {"score_paragraph": paragraph})]

        data = {
            "trigger_id": trigger_id,
            "view": {
                "type": "modal",
                "callback_id": slack_const.SHOW_MEETING_SCORE_COMPONENTS,
                "title": {"type": "plain_text", "text": "Summary"},
                "blocks": blocks if len(blocks) else empty_block,
                "private_metadata": json.dumps(private_metadata),
            },
        }

        private_metadata.update(context)

        slack_requests.generic_request(url, data, access_token=access_token)
    except Exception as e:
        logger.warning(e)
        pass


@processor(required_context=["w", "tracking_id"])
def process_edit_meeting_contact(payload, context):
    url = slack_const.SLACK_API_ROOT + slack_const.VIEWS_UPDATE
    trigger_id = payload["trigger_id"]
    workflow = MeetingWorkflow.objects.get(id=context.get("w"))
    meeting = workflow.meeting

    org = meeting.zoom_account.user.organization

    access_token = org.slack_integration.access_token

    salesforce_account = meeting.zoom_account.user.salesforce_account

    view = payload["view"]
    # retrieve original blocks, view will use the same blocks but change the submit action
    blocks = view["blocks"]
    view_id = view["id"]
    title = view["title"]
    actions = payload["actions"]
    callback_id = None
    submit_button_text = None
    selected_action_block = actions[0] if len(actions) else None
    if selected_action_block:
        action = process_action_id(selected_action_block["action_id"])
        block_id = selected_action_block["block_id"]
        index, selected_block = block_finder(block_id, blocks)
        if (
            action["true_id"] == slack_const.ZOOM_MEETING__EDIT_CONTACT
            and selected_block["elements"][0]["value"] == slack_const.ZOOM_MEETING__EDIT_CONTACT
        ):
            selected_block["elements"][0]["text"]["text"] = "Cancel Edit Contact"
            selected_block["elements"][0]["value"] = slack_const.ZOOM_MEETING__CANCEL_EDIT_CONTACT
            blocks[index] = selected_block
            callback_id = slack_const.ZOOM_MEETING__EDIT_CONTACT
            submit_button_text = "Edit Contact"
            # change the block to show it is selected
        elif (
            action["true_id"] == slack_const.ZOOM_MEETING__EDIT_CONTACT
            and selected_block["elements"][0]["value"]
            == slack_const.ZOOM_MEETING__CANCEL_EDIT_CONTACT
        ):
            selected_block["elements"][0]["text"]["text"] = "Click To Select For Editing"
            selected_block["elements"][0]["value"] = slack_const.ZOOM_MEETING__EDIT_CONTACT
            blocks[index] = selected_block
            callback_id = None
            submit_button_text = None
            # change the block to show it is selected

    data = {
        "trigger_id": trigger_id,
        "view_id": view_id,
        "view": {
            "close": {"type": "plain_text", "text": "Close", "emoji": True},
            "type": "modal",
            "title": title,
            "blocks": blocks,
            "private_metadata": json.dumps(
                {"w": context.get("w"), "tracking_id": context.get("tracking_id"),}
            ),
        },
    }
    if callback_id:
        data["view"]["callback_id"] = callback_id

    if submit_button_text:
        data["view"]["submit"] = {"type": "plain_text", "text": submit_button_text, "emoji": True}

    res = slack_requests.generic_request(url, data, access_token=access_token)
    print(res.json())


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
        # blockfinder returns a tuple of its index in the block and the object
        index, action_block = block_finder(action["block_id"], blocks)
        # forecast_block =
        block_options = list(map(lambda opt: opt["value"], action_block["accessory"]["options"]))
        # find all stages previous to it
        # delete all existing stage forms
        workflow.forms.filter(template__form_type=slack_const.FORM_TYPE_STAGE_GATING).delete()
        new_forms_count = 0
        for opt in block_options:
            if opt == selected_value:

                f = workflow.add_form(
                    slack_const.FORM_RESOURCE_OPPORTUNITY,
                    slack_const.FORM_TYPE_STAGE_GATING,
                    stage=opt,
                )
                if f:
                    new_forms_count += 1
                break
            else:

                f = workflow.add_form(
                    slack_const.FORM_RESOURCE_OPPORTUNITY,
                    slack_const.FORM_TYPE_STAGE_GATING,
                    stage=opt,
                )
                if f:
                    new_forms_count += 1
        # gather and attach all forms

    submit_text = "Submit" if new_forms_count == 0 else "Next"

    if new_forms_count == 0:
        callback_id = payload["view"]["callback_id"]
    else:
        callback_id = slack_const.ZOOM_MEETING__PROCESS_STAGE_NEXT_PAGE
        if payload["view"]["callback_id"] == slack_const.ZOOM_MEETING__PROCESS_MEETING_SENTIMENT:
            context = {
                **context,
                "form_type": slack_const.FORM_TYPE_MEETING_REVIEW,
                "callback_id": slack_const.ZOOM_MEETING__PROCESS_MEETING_SENTIMENT,
            }
        else:
            context = {
                **context,
                "form_type": slack_const.FORM_TYPE_CREATE,
                "callback_id": slack_const.ZOOM_MEETING__PROCESS_MEETING_SENTIMENT,
            }
    private_metadata.update(context)
    data = {
        "trigger_id": trigger_id,
        "view_id": view_id,
        "view": {
            "type": "modal",
            "callback_id": callback_id,
            "title": {"type": "plain_text", "text": "Log Meeting"},
            "blocks": blocks,
            "submit": {"type": "plain_text", "text": submit_text},
            "private_metadata": json.dumps(private_metadata),
        },
    }

    res = slack_requests.generic_request(url, data, access_token=access_token)
    print(res.json())
    print(trigger_id)


@processor(required_context=["w", "tracking_id"])
def process_remove_contact_from_meeting(payload, context):
    workflow = MeetingWorkflow.objects.get(id=context.get("w"))
    meeting = workflow.meeting

    for i, part in enumerate(meeting.participants):
        if part["_tracking_id"] == context.get("tracking_id"):
            # remove its form if it exists
            if part["_form"] not in [None, ""]:
                workflow.forms.filter(id=part["_form"]).delete()
            del meeting.participants[i]
            break
    meeting.save()

    return process_show_meeting_contacts(payload, context, action=slack_const.VIEWS_UPDATE)


@processor(required_context=["w"])
def process_update_search_or_create(payload, context):
    """ Updates the form view to either a create form or a search box what is currently selected """
    url = slack_const.SLACK_API_ROOT + slack_const.VIEWS_UPDATE
    trigger_id = payload["trigger_id"]
    view_id = payload["view"]["id"]
    select = payload["actions"][0]["selected_option"]
    selected_option = select["value"]

    workflow = MeetingWorkflow.objects.get(id=context.get("w"))
    organization = workflow.user.organization
    access_token = organization.slack_integration.access_token
    c = {
        "w": context.get("w"),
        "resource": str(context.get("resource")),
        "selected_option": select,
    }
    current_block_sets = get_block_set("create_or_search_modal", context=c)
    if selected_option == "SEARCH":
        blocks = get_block_set("search_modal_block_set", context=c)
    elif selected_option == "CREATE":
        blocks = get_block_set("create_modal_block_set", context=c)
    ts, channel = workflow.slack_interaction.split("|")
    private_metadata = {
        "original_message_timestamp": ts,
        "original_message_channel": channel,
    }

    private_metadata.update(context)
    data = {
        "trigger_id": trigger_id,
        "view_id": view_id,
        "view": {
            "type": "modal",
            "callback_id": slack_const.ZOOM_MEETING__SELECTED_RESOURCE,
            "title": {"type": "plain_text", "text": c.get("resource")},
            "blocks": [*current_block_sets, *blocks],
            "submit": {"type": "plain_text", "text": "Attach"},
            "private_metadata": json.dumps(private_metadata),
        },
    }
    res = slack_requests.generic_request(url, data, access_token=access_token)


@processor(required_context=["w"])
def process_meeting_selected_resource(payload, context):
    """ opens a modal with the options to search or create """
    url = slack_const.SLACK_API_ROOT + slack_const.VIEWS_OPEN
    trigger_id = payload["trigger_id"]

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

    private_metadata.update(context)
    data = {
        "trigger_id": trigger_id,
        "view": {
            "type": "modal",
            "callback_id": slack_const.ZOOM_MEETING__SEARCH_OR_CREATE_NEXT_PAGE,
            "title": {"type": "plain_text", "text": f"{selected_option}"},
            "blocks": get_block_set("create_or_search_modal", context=context),
            "private_metadata": json.dumps(private_metadata),
            "submit": {"type": "plain_text", "text": "Next"},
        },
    }
    res = slack_requests.generic_request(url, data, access_token=access_token)
    print(res.json())


@processor()
def process_create_or_search_selected(payload, context):
    """ attaches a drop down to the message block for selecting a resource type """
    workflow_id = payload["actions"][0]["value"]
    workflow = MeetingWorkflow.objects.get(id=workflow_id)
    meeting = workflow.meeting

    organization = workflow.user.organization
    access_token = organization.slack_integration.access_token
    # get current blocks
    previous_blocks = payload["message"]["blocks"]
    # check if the dropdown option has been added already
    select_block = block_finder(slack_const.ZOOM_MEETING__ATTACH_RESOURCE_SECTION, previous_blocks)
    block_sets = []
    if not select_block:
        # create new block including the resource type
        block_sets = get_block_set("attach_resource_interaction", {"w": workflow_id})

    res = slack_requests.update_channel_message(
        payload["channel"]["id"],
        payload["message"]["ts"],
        access_token,
        block_set=[*previous_blocks, *block_sets],
    ).json()
    workflow.slack_interaction = f"{res['ts']}|{res['channel']}"
    workflow.meeting.save()


@processor()
def process_restart_flow(payload, context):
    workflow_id = payload["actions"][0]["value"]
    workflow = MeetingWorkflow.objects.get(id=workflow_id)
    organization = workflow.user.organization
    access_token = organization.slack_integration.access_token
    ts, channel = workflow.slack_interaction.split("|")
    res = slack_requests.update_channel_message(
        channel,
        ts,
        access_token,
        block_set=get_block_set("initial_meeting_interaction", context={"w": workflow_id}),
    ).json()

    workflow.slack_interaction = f"{res['ts']}|{res['channel']}"
    workflow.save()


@processor()
def process_disregard_meeting_review(payload, context):
    workflow_id = payload["actions"][0]["value"]
    workflow = MeetingWorkflow.objects.get(id=workflow_id)
    organization = workflow.user.organization
    access_token = organization.slack_integration.access_token
    res = slack_requests.update_channel_message(
        payload["channel"]["id"],
        payload["message"]["ts"],
        access_token,
        block_set=get_block_set("disregard_meeting_review", context={"w": workflow_id}),
    ).json()
    workflow.slack_interaction = f"{res['ts']}|{res['channel']}"
    workflow.save()


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
            "callback_id": slack_const.ZOOM_MEETING__SEARCH_OR_CREATE_NEXT_PAGE,
            "title": {"type": "plain_text", "text": f"Coming Soon"},
            "blocks": get_block_set("coming_soon_modal", {}),
        },
    }
    res = slack_requests.generic_request(url, data, access_token=org.slack_integration.access_token)
    print(res.json())


def handle_block_actions(payload):
    """
    This takes place when user completes a general interaction,
    such as clicking a button.
    """
    switcher = {
        slack_const.SHOW_MEETING_SCORE_COMPONENTS: process_get_meeting_score_components,
        slack_const.ZOOM_MEETING__VIEW_MEETING_CONTACTS: process_show_meeting_contacts,
        slack_const.ZOOM_MEETING__EDIT_CONTACT: process_edit_meeting_contact,
        slack_const.ZOOM_MEETING__REMOVE_CONTACT: process_remove_contact_from_meeting,
        slack_const.ZOOM_MEETING__CREATE_OR_SEARCH: process_create_or_search_selected,
        slack_const.ZOOM_MEETING__SELECTED_RESOURCE: process_meeting_selected_resource,
        slack_const.ZOOM_MEETING__SELECTED_CREATE_OR_SEARCH: process_update_search_or_create,
        slack_const.ZOOM_MEETING__DISREGARD_REVIEW: process_disregard_meeting_review,
        slack_const.ZOOM_MEETING__RESTART_MEETING_FLOW: process_restart_flow,
        slack_const.ZOOM_MEETING__INIT_REVIEW: process_meeting_review,
        slack_const.ZOOM_MEETING__STAGE_SELECTED: process_stage_selected,
        slack_const.ZOOM_MEETING__CREATE_TASK: process_coming_soon,
        slack_const.ZOOM_MEETING__CONVERT_LEAD: process_coming_soon,
    }
    action_query_string = payload["actions"][0]["action_id"]
    processed_string = process_action_id(action_query_string)
    action_id = processed_string.get("true_id")
    action_params = processed_string.get("params")
    print(f"ID: {action_query_string}")
    return switcher.get(action_id, NO_OP)(payload, action_params)
