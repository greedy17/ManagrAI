from managr.slack import constants as slack_const
from managr.slack.helpers import requests as slack_requests
from managr.slack.helpers.blocks import get_block_set
from managr.slack.models import UserSlackIntegration
import pdb


def get_access_token_from_user_slack_id(user_slack_id):
    return (
        UserSlackIntegration.objects.select_related(
            "user__organization__slack_integration"
        )
        .get(slack_id=user_slack_id)
        .user.organization.slack_integration.access_token
    )


def handle_zoom_meeting_great(payload):
    # TODO: somehow need to keep track of what lead etc (i.e. STATE across interactions)
    # such as with values (i.e. button value)
    # submit next UI
    url = slack_const.SLACK_API_ROOT + slack_const.VIEWS_OPEN
    trigger_id = payload["trigger_id"]
    access_token = get_access_token_from_user_slack_id(payload["user"]["id"])
    data = {
        "trigger_id": trigger_id,
        "view": {
            "type": "modal",
            "callback_id": "modal-identifier",
            "title": {"type": "plain_text", "text": "Log Meeting"},
            "blocks": get_block_set("zoom_meeting_complete_form"),
            "submit": {"type": "plain_text", "text": "Submit"},
        },
    }
    res = slack_requests.generic_request(url, data, access_token=access_token)
    print("-=-=-=-=--=-")
    print(res.status_code)
    print(res.json())
    return res


def handle_zoom_meeting_not_well(payload):
    url = slack_const.SLACK_API_ROOT + slack_const.VIEWS_OPEN
    trigger_id = payload["trigger_id"]
    access_token = get_access_token_from_user_slack_id(payload["user"]["id"])
    data = {
        "trigger_id": trigger_id,
        "view": {
            "type": "modal",
            "callback_id": "modal-identifier",
            "title": {"type": "plain_text", "text": "Log Meeting"},
            "blocks": get_block_set("zoom_meeting_limited_form"),
            "submit": {"type": "plain_text", "text": "Submit"},
        },
    }
    res = slack_requests.generic_request(url, data, access_token=access_token)
    print("-=-=-=-=--=-")
    print(res.status_code)
    print(res.json())
    return res


def handle_block_actions(payload):
    switcher = {
        slack_const.ZOOM_MEETING__GREAT: handle_zoom_meeting_great,
        slack_const.ZOOM_MEETING__NOT_WELL: handle_zoom_meeting_not_well,
    }
    action_id = payload["actions"][0]["action_id"]

    return switcher.get(action_id)(payload)


def handle_interaction(payload):
    switcher = {
        slack_const.BLOCK_ACTIONS: handle_block_actions,
    }
    return switcher.get(payload["type"])(payload)
