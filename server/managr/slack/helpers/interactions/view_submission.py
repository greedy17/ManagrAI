import json
import pdb

from managr.organization.models import Organization

from managr.slack import constants as slack_const
from managr.slack.helpers import requests as slack_requests
from managr.slack.helpers import utils as slack_utils
from managr.slack.helpers.block_sets import get_block_set


def process_zoom_meeting_different_opportunity_submit(payload):
    view_context = json.loads(payload["view"]["private_metadata"])
    user_id_param = "u=" + view_context["u"]
    lead_id_param = "l=" + view_context["l"]
    organization_id_param = "o=" + view_context["o"]

    target_action_id = slack_utils.action_with_params(
        slack_const.GET_USER_OPPORTUNITIES,
        params=[
            user_id_param,
        ],
    )

    selection = payload["view"]["state"]["values"]["select_new_opportunity"][
        target_action_id
    ]["selected_option"]

    if selection is None:
        # user did not select an option, show them error
        data = {
            "response_action": "errors",
            "errors": {"select_new_opportunity": "You must select an option."},
        }
        return data

    new_lead_id = selection["value"]

    original_message_channel = view_context["original_message_channel"]
    original_message_timestamp = view_context["original_message_timestamp"]

    access_token = (
        Organization.objects.select_related("slack_integration")
        .get(pk=view_context["o"])
        .slack_integration.access_token
    )

    context = {
        "l": new_lead_id,
        "u": view_context["u"],
        "o": view_context["o"],
    }

    slack_requests.update_channel_message(
        original_message_channel,
        original_message_timestamp,
        access_token,
        block_set=get_block_set("zoom_meeting_initial", context=context),
    )


def handle_view_submission(payload):
    """
    This takes place when a modal's Submit button is clicked.
    """
    switcher = {
        slack_const.ZOOM_MEETING__DIFFERENT_OPPORTUNITY: process_zoom_meeting_different_opportunity_submit,
    }
    callback_id = payload["view"]["callback_id"]
    return switcher.get(callback_id, slack_utils.NO_OP)(payload)
