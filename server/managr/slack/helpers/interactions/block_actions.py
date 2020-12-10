import json
import pdb

from managr.organization.models import Organization
from managr.lead.models import Notification, Reminder

from managr.slack import constants as slack_const
from managr.slack.helpers import requests as slack_requests
from managr.slack.helpers.utils import process_action_id, NO_OP, processor
from managr.slack.helpers.block_sets import get_block_set


@processor(required_context=["o", "u", "l"])
def process_zoom_meeting_great(payload, context):
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
            "callback_id": slack_const.ZOOM_MEETING__GREAT,
            "title": {"type": "plain_text", "text": "Log Meeting"},
            "blocks": get_block_set("zoom_meeting_complete_form", context=context),
            "submit": {"type": "plain_text", "text": "Submit"},
            "private_metadata": json.dumps(private_metadata),
        },
    }
    slack_requests.generic_request(url, data, access_token=access_token)


@processor(required_context=["o", "u", "l"])
def process_zoom_meeting_not_well(payload, context):
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
            "callback_id": slack_const.ZOOM_MEETING__NOT_WELL,
            "title": {"type": "plain_text", "text": "Log Meeting"},
            "blocks": get_block_set("zoom_meeting_limited_form", context=context),
            "submit": {"type": "plain_text", "text": "Submit"},
            "private_metadata": json.dumps(private_metadata),
        },
    }
    slack_requests.generic_request(url, data, access_token=access_token)


@processor(required_context=["o", "u", "l"])
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


@processor(required_context=["r"])
def process_get_contacts(payload, context):
    url = slack_const.SLACK_API_ROOT + slack_const.VIEWS_OPEN
    trigger_id = payload["trigger_id"]
    reminder = Reminder.objects.filter(id=context.get("r")).first()
    org = reminder.created_by.organization
    access_token = org.slack_integration.access_token
    blocks = [
        get_block_set("reminder_contact_block_set", {"contact": contact})
        for contact in reminder.linked_contacts.all()
    ]
    private_metadata = {
        "original_message_channel": payload["channel"]["id"],
        "original_message_timestamp": payload["message"]["ts"],
    }
    empty_block = [
        {"type": "section", "text": {"type": "mrkdwn", "text": "No Contacts Attached"},}
    ]

    data = {
        "trigger_id": trigger_id,
        "view": {
            "type": "modal",
            "callback_id": slack_const.SHOW_REMINDER_CONTACTS,
            "title": {"type": "plain_text", "text": "Contacts"},
            "blocks": blocks if len(blocks) else empty_block,
            "private_metadata": json.dumps(private_metadata),
        },
    }

    private_metadata.update(context)

    slack_requests.generic_request(url, data, access_token=access_token)


def handle_block_actions(payload):
    """
    This takes place when user completes a general interaction,
    such as clicking a button.
    """
    switcher = {
        slack_const.ZOOM_MEETING__GREAT: process_zoom_meeting_great,
        slack_const.ZOOM_MEETING__NOT_WELL: process_zoom_meeting_not_well,
        slack_const.ZOOM_MEETING__DIFFERENT_OPPORTUNITY: process_zoom_meeting_different_opportunity,
        slack_const.SHOW_REMINDER_CONTACTS: process_get_contacts,
    }
    action_query_string = payload["actions"][0]["action_id"]
    processed_string = process_action_id(action_query_string)
    action_id = processed_string.get("true_id")
    action_params = processed_string.get("params")
    print(f"ID: {action_query_string}")
    return switcher.get(action_id, NO_OP)(payload, action_params)
