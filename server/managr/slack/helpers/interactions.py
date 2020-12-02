from django.db.models import Q

from managr.organization.models import Stage
from managr.slack import constants as slack_const
from managr.slack.helpers import requests as slack_requests
from managr.slack.helpers.blocks import get_block_set
from managr.slack.models import UserSlackIntegration
import pdb

# NOTE:
# - The method handle_interaction is the entry point into this architecture,
#   and is essentially a Router
# - ROUTERS (methods starting with route_) leverage a switcher to route
#   payload towards proper processing method
# - PROCESSORS (methods starting with process_) do the actual processing of
#   the interaction
# - GETTERS (methods starting with get_) are helper methods that query DB and
#   return desired Model instance

# - The architecture is designed so that ultimately the return value of a
#   PROCESSOR is outputted to the view handling the request from the Slack API.
#   Therefore,  PROCESSORS are expected to return a dict, so that the view can
#   include data in its response or not, accordingly.
# - PROCESSORS whose output should be a part of the HttpResponse should format
#   their dict as follows: { "send_response_data": True, "data": data_here }


def get_access_token_from_user_slack_id(user_slack_id):
    return (
        UserSlackIntegration.objects.select_related(
            "user__organization__slack_integration"
        )
        .get(slack_id=user_slack_id)
        .user.organization.slack_integration.access_token
    )


def get_organization_from_user_slack_id(user_slack_id):
    return (
        UserSlackIntegration.objects.select_related("user__organization")
        .get(slack_id=user_slack_id)
        .user.organization
    )


def process_zoom_meeting_great(payload):
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
    return {
        "send_response_data": False,
        "data": slack_requests.generic_request(url, data, access_token=access_token),
    }


def process_zoom_meeting_not_well(payload):
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
    return {
        "send_response_data": False,
        "data": slack_requests.generic_request(url, data, access_token=access_token),
    }


def process_get_organization_stages(payload):
    organization = get_organization_from_user_slack_id(payload["user"]["id"])
    data = {
        "options": [
            s.as_slack_option
            for s in Stage.objects.filter(
                Q(type="PUBLIC") | Q(organization=organization)
            )
        ]
    }
    return {"send_response_data": True, "data": data}


def route_block_actions(payload):
    """
    This takes place when user completes a general interaction,
    such as clicking a button.
    """
    switcher = {
        slack_const.ZOOM_MEETING__GREAT: process_zoom_meeting_great,
        slack_const.ZOOM_MEETING__NOT_WELL: process_zoom_meeting_not_well,
    }
    action_id = payload["actions"][0]["action_id"]
    return switcher.get(action_id)(payload)


def route_block_suggestion(payload):
    """
    This takes place when a select_field requires data from Managr
    to populate its options.
    """
    switcher = {
        slack_const.GET_ORGANIZATION_STAGES: process_get_organization_stages,
    }
    action_id = payload["action_id"]
    return switcher.get(action_id)(payload)


def handle_interaction(payload):
    switcher = {
        slack_const.BLOCK_ACTIONS: route_block_actions,
        slack_const.BLOCK_SUGGESTION: route_block_suggestion,
    }
    return switcher.get(payload["type"])(payload)
