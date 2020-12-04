import json
from django.db.models import Q

from managr.core.models import User
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


def process_zoom_meeting_great(payload, params):
    url = slack_const.SLACK_API_ROOT + slack_const.VIEWS_OPEN
    trigger_id = payload["trigger_id"]
    access_token = (
        Organization.objects.select_related("slack_integration")
        .get(pk=params["organization_id"])
        .slack_integration.access_token
    )
    private_metadata = {
        "original_message_channel": payload["channel"]["id"],
        "original_message_timestamp": payload["message"]["ts"],
    }
    private_metadata.update(params)
    data = {
        "trigger_id": trigger_id,
        "view": {
            "type": "modal",
            "callback_id": slack_const.ZOOM_MEETING__GREAT,
            "title": {"type": "plain_text", "text": "Log Meeting"},
            "blocks": get_block_set("zoom_meeting_complete_form", context=params),
            "submit": {"type": "plain_text", "text": "Submit"},
            "private_metadata": json.dumps(private_metadata),
        },
    }
    slack_requests.generic_request(url, data, access_token=access_token)


def process_zoom_meeting_not_well(payload, params):
    url = slack_const.SLACK_API_ROOT + slack_const.VIEWS_OPEN
    trigger_id = payload["trigger_id"]
    access_token = (
        Organization.objects.select_related("slack_integration")
        .get(pk=params["organization_id"])
        .slack_integration.access_token
    )
    private_metadata = {
        "original_message_channel": payload["channel"]["id"],
        "original_message_timestamp": payload["message"]["ts"],
    }
    private_metadata.update(params)
    data = {
        "trigger_id": trigger_id,
        "view": {
            "type": "modal",
            "callback_id": slack_const.ZOOM_MEETING__NOT_WELL,
            "title": {"type": "plain_text", "text": "Log Meeting"},
            "blocks": get_block_set("zoom_meeting_limited_form", context=params),
            "submit": {"type": "plain_text", "text": "Submit"},
            "private_metadata": json.dumps(private_metadata),
        },
    }
    slack_requests.generic_request(url, data, access_token=access_token)


def process_zoom_meeting_different_opportunity(payload, params):
    url = slack_const.SLACK_API_ROOT + slack_const.VIEWS_OPEN
    trigger_id = payload["trigger_id"]
    access_token = (
        Organization.objects.select_related("slack_integration")
        .get(pk=params["organization_id"])
        .slack_integration.access_token
    )

    private_metadata = {
        "original_message_channel": payload["channel"]["id"],
        "original_message_timestamp": payload["message"]["ts"],
    }
    private_metadata.update(params)

    data = {
        "trigger_id": trigger_id,
        "view": {
            "type": "modal",
            "callback_id": slack_const.ZOOM_MEETING__DIFFERENT_OPPORTUNITY,
            "title": {"type": "plain_text", "text": "Change Opportunity"},
            "blocks": get_block_set("select_different_opportunity", context=params),
            "submit": {"type": "plain_text", "text": "Submit"},
            "private_metadata": json.dumps(private_metadata),
        },
    }
    slack_requests.generic_request(url, data, access_token=access_token)


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

    # new_lead_id = selection["value"] if selection is not None
    if selection is None:
        # User did not select an option, show them error
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


def process_get_organization_stages(payload, params):
    organization = Organization.objects.get(pk=params["organization_id"])
    return {
        "options": [
            s.as_slack_option
            for s in Stage.objects.filter(
                Q(type="PUBLIC") | Q(organization=organization)
            )
        ],
    }


def process_get_organization_action_choices(payload, params):
    organization = Organization.objects.get(pk=params["organization_id"])
    return {
        "options": [ac.as_slack_option for ac in organization.action_choices.all()],
    }


def process_get_lead_forecasts(payload, params):
    return {
        "options": [
            block_builders.option(f[1], f[0]) for f in lead_const.FORECAST_CHOICES
        ],
    }


def process_get_user_opportunities(payload, params):
    user = User.objects.get(pk=params["user_id"])
    return {
        "options": [l.as_slack_option for l in user.claimed_leads.all()],
    }


def handle_block_actions(payload):
    """
    This takes place when user completes a general interaction,
    such as clicking a button.
    """
    switcher = {
        slack_const.ZOOM_MEETING__GREAT: process_zoom_meeting_great,
        slack_const.ZOOM_MEETING__NOT_WELL: process_zoom_meeting_not_well,
        slack_const.ZOOM_MEETING__DIFFERENT_OPPORTUNITY: process_zoom_meeting_different_opportunity,
    }
    action_query_string = payload["actions"][0]["action_id"]
    processed_string = slack_utils.process_action_id(action_query_string)
    action_id = processed_string.get("true_id")
    action_params = processed_string.get("params")
    print(f"ID: {action_query_string}")
    return switcher.get(action_id, slack_utils.NO_OP)(payload, action_params)


def handle_block_suggestion(payload):
    """
    This takes place when a select_field requires data from Managr
    to populate its options.
    """
    switcher = {
        slack_const.GET_ORGANIZATION_STAGES: process_get_organization_stages,
        slack_const.GET_ORGANIZATION_ACTION_CHOICES: process_get_organization_action_choices,
        slack_const.GET_LEAD_FORECASTS: process_get_lead_forecasts,
        slack_const.GET_USER_OPPORTUNITIES: process_get_user_opportunities,
    }
    action_query_string = payload["action_id"]
    processed_string = slack_utils.process_action_id(action_query_string)
    action_id = processed_string.get("true_id")
    action_params = processed_string.get("params")
    print(f"ID: {action_query_string}")
    return switcher.get(action_id, slack_utils.NO_OP)(payload, action_params)


def handle_view_submission(payload):
    """
    This takes place when a modal's Submit button is clicked.
    """
    switcher = {
        slack_const.ZOOM_MEETING__DIFFERENT_OPPORTUNITY: process_zoom_meeting_different_opportunity_submit,
    }
    callback_id = payload["view"]["callback_id"]
    return switcher.get(callback_id, slack_utils.NO_OP)(payload)


def handle_interaction(payload):
    switcher = {
        slack_const.BLOCK_ACTIONS: handle_block_actions,
        slack_const.BLOCK_SUGGESTION: handle_block_suggestion,
        slack_const.VIEW_SUBMISSION: handle_view_submission,
    }
    typ = payload["type"]
    print(f"TYPE: {typ}")
    return switcher.get(payload["type"], slack_utils.NO_OP)(payload)
