import json
import pdb

from managr.organization.models import Organization

from managr.slack import constants as slack_const
from managr.slack.helpers import requests as slack_requests
from managr.slack.helpers.utils import action_with_params, NO_OP, processor
from managr.slack.helpers.block_sets import get_block_set


@processor(
    required_context=[
        "o",
        "l",
        "original_message_channel",
        "original_message_timestamp",
    ]
)
def process_zoom_meeting_great_submit(payload, context):
    state = payload["view"]["state"]["values"]
    meeting_type_state = state["meeting_type"]
    stage_state = state["stage"]
    forecast_state = state["forecast"]
    description_state = state["description"]
    expected_close_date_state = state["expected_close_date"]
    next_step_state = state["next_step"]

    organization_id_param = "o=" + context["o"]
    a_id = action_with_params(
        slack_const.GET_ORGANIZATION_ACTION_CHOICES,
        params=[
            organization_id_param,
        ],
    )
    meeting_type = meeting_type_state[a_id]["selected_option"]
    if meeting_type:
        meeting_type = meeting_type["value"]
    else:
        # user did not select an option, show them error
        data = {
            "response_action": "errors",
            "errors": {"meeting_type": "You must select an option."},
        }
        return data

    a_id = action_with_params(
        slack_const.GET_ORGANIZATION_STAGES,
        params=[
            organization_id_param,
        ],
    )
    stage = stage_state[a_id]["selected_option"]
    if stage:
        stage = stage["value"]

    a_id = slack_const.GET_LEAD_FORECASTS
    forecast = forecast_state[a_id]["selected_option"]
    if forecast:
        forecast = forecast["value"]

    a_id = slack_const.DEFAULT_ACTION_ID
    description = description_state[a_id]["value"]
    expected_close_date = expected_close_date_state[a_id]["selected_date"]
    next_step = next_step_state[a_id]["value"]

    data = {
        "meeting_type": meeting_type,
        "stage": stage,
        "forecast": forecast,
        "description": description,
        "expected_close_date": expected_close_date,
        "next_step": next_step,
    }

    # NOTE: stage/forecast may be the original stage and therefore unchanged.
    # NOTE: if forecast is an ID, it corresponds to pre-existing lead forecast.
    #       if it is one of lead_const.FORECAST_CHOICES then it is a new selection.

    block_set_context = {
        "l": context["l"],
    }

    access_token = (
        Organization.objects.select_related("slack_integration")
        .get(pk=context["o"])
        .slack_integration.access_token
    )

    slack_requests.update_channel_message(
        context["original_message_channel"],
        context["original_message_timestamp"],
        access_token,
        block_set=get_block_set("confirm_meeting_logged", context=block_set_context),
    )


@processor(
    required_context=[
        "o",
        "l",
        "original_message_channel",
        "original_message_timestamp",
    ]
)
def process_zoom_meeting_not_well_submit(payload, context):
    state = payload["view"]["state"]["values"]
    meeting_type_state = state["meeting_type"]
    stage_state = state["stage"]
    description_state = state["description"]
    next_step_state = state["next_step"]

    organization_id_param = "o=" + context["o"]
    a_id = action_with_params(
        slack_const.GET_ORGANIZATION_ACTION_CHOICES,
        params=[
            organization_id_param,
        ],
    )
    meeting_type = meeting_type_state[a_id]["selected_option"]
    if meeting_type:
        meeting_type = meeting_type["value"]
    else:
        # user did not select an option, show them error
        data = {
            "response_action": "errors",
            "errors": {"meeting_type": "You must select an option."},
        }
        return data

    a_id = action_with_params(
        slack_const.GET_ORGANIZATION_STAGES,
        params=[
            organization_id_param,
        ],
    )
    stage = stage_state[a_id]["selected_option"]
    if stage:
        stage = stage["value"]

    a_id = slack_const.DEFAULT_ACTION_ID
    description = description_state[a_id]["value"]
    next_step = next_step_state[a_id]["value"]

    data = {
        "meeting_type": meeting_type,
        "stage": stage,
        "description": description,
        "next_step": next_step,
    }

    # NOTE: stage may be the original stage and therefore unchanged.

    block_set_context = {
        "l": context["l"],
    }

    access_token = (
        Organization.objects.select_related("slack_integration")
        .get(pk=context["o"])
        .slack_integration.access_token
    )

    slack_requests.update_channel_message(
        context["original_message_channel"],
        context["original_message_timestamp"],
        access_token,
        block_set=get_block_set("confirm_meeting_logged", context=block_set_context),
    )


@processor(
    required_context=[
        "u",
        "l",
        "o",
        "original_message_channel",
        "original_message_timestamp",
    ]
)
def process_zoom_meeting_different_opportunity_submit(payload, context):
    state = payload["view"]["state"]["values"]
    new_opportunity_state = state["new_opportunity"]

    user_id_param = "u=" + context["u"]
    a_id = action_with_params(
        slack_const.GET_USER_OPPORTUNITIES,
        params=[
            user_id_param,
        ],
    )

    new_opportunity = new_opportunity_state[a_id]["selected_option"]

    if new_opportunity:
        new_opportunity = new_opportunity["value"]
    else:
        # user did not select an option, show them error
        data = {
            "response_action": "errors",
            "errors": {"new_opportunity": "You must select an option."},
        }
        return data

    block_set_context = {
        "l": new_opportunity,
        "u": context["u"],
        "o": context["o"],
    }

    access_token = (
        Organization.objects.select_related("slack_integration")
        .get(pk=context["o"])
        .slack_integration.access_token
    )

    slack_requests.update_channel_message(
        context["original_message_channel"],
        context["original_message_timestamp"],
        access_token,
        block_set=get_block_set("zoom_meeting_initial", context=block_set_context),
    )


def handle_view_submission(payload):
    """
    This takes place when a modal's Submit button is clicked.
    """
    switcher = {
        slack_const.ZOOM_MEETING__GREAT: process_zoom_meeting_great_submit,
        slack_const.ZOOM_MEETING__NOT_WELL: process_zoom_meeting_not_well_submit,
        slack_const.ZOOM_MEETING__DIFFERENT_OPPORTUNITY: process_zoom_meeting_different_opportunity_submit,
    }
    callback_id = payload["view"]["callback_id"]
    view_context = json.loads(payload["view"]["private_metadata"])
    return switcher.get(callback_id, NO_OP)(payload, view_context)
