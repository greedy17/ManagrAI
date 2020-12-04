import json
import pdb

from managr.organization.models import Organization

from managr.slack import constants as slack_const
from managr.slack.helpers import requests as slack_requests
from managr.slack.helpers import utils as slack_utils
from managr.slack.helpers.block_sets import get_block_set


def process_zoom_meeting_different_opportunity_submit(payload):
    view_context = json.loads(payload["view"]["private_metadata"])
    user_id_param = "user_id=" + view_context["user_id"]
    lead_id_param = "lead_id=" + view_context["lead_id"]
    organization_id_param = "organization_id=" + view_context["organization_id"]

    target_action_id = slack_utils.action_with_params(
        slack_const.GET_USER_OPPORTUNITIES,
        params=[
            user_id_param,
            lead_id_param,
            organization_id_param,
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
        .get(pk=view_context["organization_id"])
        .slack_integration.access_token
    )

    context = {
        "lead_id": new_lead_id,
        "user_id": view_context["user_id"],
        "organization_id": view_context["organization_id"],
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
