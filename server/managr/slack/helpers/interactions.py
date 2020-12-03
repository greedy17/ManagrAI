from django.db.models import Q

from managr.organization.models import Organization, Stage
from managr.lead import constants as lead_const
from managr.lead.models import Lead

from managr.slack import constants as slack_const
from managr.slack.helpers import requests as slack_requests
from managr.slack.helpers import utils as slack_utils
from managr.slack.helpers import block_builders
from managr.slack.helpers.block_sets import get_block_set
import pdb

# NOTE:
# - The method handle_interaction is the entry point into this architecture.

# - HANDLERS (methods starting with handle_) leverage a switcher to route
#   payload towards proper processing method.
#   They may do some data preparation that gets passed on to the next method.
#   There may be some preparation of data to pass into a Processor.

# - PROCESSORS (methods starting with process_) do the actual processing of
#   the interaction.

# - The architecture is designed so that ultimately the return value of a
#   PROCESSOR is outputted to the view handling the request from the Slack API.
#   Therefore,  PROCESSORS are expected to return a dict, so that the view can
#   include data in its response or not, accordingly.
# - PROCESSORS whose output should be a part of the HttpResponse should format
#   their dict as follows: { "send_response_data": True, "data": data_here }


def process_zoom_meeting_great(payload, params):
    # TODO: somehow need to keep track of what lead etc (i.e. STATE across interactions)
    # such as with values (i.e. button value)
    # submit next UI
    url = slack_const.SLACK_API_ROOT + slack_const.VIEWS_OPEN
    trigger_id = payload["trigger_id"]
    access_token = slack_utils.get_access_token_from_user_slack_id(
        payload["user"]["id"]
    )
    data = {
        "trigger_id": trigger_id,
        "view": {
            "type": "modal",
            "callback_id": "modal-identifier",
            "title": {"type": "plain_text", "text": "Log Meeting"},
            "blocks": get_block_set("zoom_meeting_complete_form", context=params),
            "submit": {"type": "plain_text", "text": "Submit"},
        },
    }
    return {
        "send_response_data": False,
        "data": slack_requests.generic_request(url, data, access_token=access_token),
    }


def process_zoom_meeting_not_well(payload, params):
    url = slack_const.SLACK_API_ROOT + slack_const.VIEWS_OPEN
    trigger_id = payload["trigger_id"]
    access_token = slack_utils.get_access_token_from_user_slack_id(
        payload["user"]["id"]
    )
    data = {
        "trigger_id": trigger_id,
        "view": {
            "type": "modal",
            "callback_id": "modal-identifier",
            "title": {"type": "plain_text", "text": "Log Meeting"},
            "blocks": get_block_set("zoom_meeting_limited_form", context=params),
            "submit": {"type": "plain_text", "text": "Submit"},
        },
    }
    return {
        "send_response_data": False,
        "data": slack_requests.generic_request(url, data, access_token=access_token),
    }


def process_get_organization_stages(payload, params):
    organization = Organization.objects.get(pk=params["organization_id"])
    data = {
        "options": [
            s.as_slack_option
            for s in Stage.objects.filter(
                Q(type="PUBLIC") | Q(organization=organization)
            )
        ],
    }
    return {"send_response_data": True, "data": data}


def process_get_organization_action_choices(payload, params):
    organization = Organization.objects.get(pk=params["organization_id"])
    data = {
        "options": [ac.as_slack_option for ac in organization.action_choices.all()],
    }
    return {"send_response_data": True, "data": data}


def process_get_lead_forecasts(payload, params):
    data = {
        "options": [
            block_builders.option(f[1], f[0]) for f in lead_const.FORECAST_CHOICES
        ],
        # "initial_option": {},
    }

    return {"send_response_data": True, "data": data}


def handle_block_actions(payload):
    """
    This takes place when user completes a general interaction,
    such as clicking a button.
    """
    switcher = {
        slack_const.ZOOM_MEETING__GREAT: process_zoom_meeting_great,
        slack_const.ZOOM_MEETING__NOT_WELL: process_zoom_meeting_not_well,
    }
    action_query_string = payload["actions"][0]["action_id"]
    processed_string = slack_utils.process_action_id(action_query_string)
    action_id = processed_string.get("true_id")
    action_params = processed_string.get("params")
    return switcher.get(action_id)(payload, action_params)


def handle_block_suggestion(payload):
    """
    This takes place when a select_field requires data from Managr
    to populate its options.
    """
    switcher = {
        slack_const.GET_ORGANIZATION_STAGES: process_get_organization_stages,
        slack_const.GET_ORGANIZATION_ACTION_CHOICES: process_get_organization_action_choices,
        slack_const.GET_LEAD_FORECASTS: process_get_lead_forecasts,
    }
    action_query_string = payload["action_id"]
    processed_string = slack_utils.process_action_id(action_query_string)
    action_id = processed_string.get("true_id")
    action_params = processed_string.get("params")
    return switcher.get(action_id)(payload, action_params)


def handle_interaction(payload):
    switcher = {
        slack_const.BLOCK_ACTIONS: handle_block_actions,
        slack_const.BLOCK_SUGGESTION: handle_block_suggestion,
    }
    return switcher.get(payload["type"])(payload)
