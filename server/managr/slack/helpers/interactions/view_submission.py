import json
import pdb

from managr.organization.models import Organization
from managr.opportunity.models import Opportunity
from managr.zoom.models import ZoomMeeting

from managr.slack import constants as slack_const
from managr.slack.helpers import requests as slack_requests
from managr.slack.helpers.utils import action_with_params, NO_OP, processor
from managr.slack.helpers.block_sets import get_block_set
from managr.salesforce.adapter.models import ContactAdapter
from managr.zoom import constants as zoom_consts
from managr.zoom.background import emit_save_meeting_review_data


@processor(
    required_context=["o", "opp", "m", "original_message_channel", "original_message_timestamp",]
)
def process_zoom_meeting_data(payload, context):
    # get context
    organization_id_param = "o=" + context["o"]
    zoom_meeting_id_param = "m=" + context.get("m")

    state = payload["view"]["state"]["values"]
    meeting_type_state = state["meeting_type"]
    stage_state = state["stage"]
    description_state = state["description"]
    next_step_state = state["next_step"]
    amount_state = state["amount"]

    sentiment = context.get("sentiment", None)
    a_id = action_with_params(
        slack_const.GET_ORGANIZATION_ACTION_CHOICES, params=[organization_id_param,],
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

    a_id = action_with_params(slack_const.GET_ORGANIZATION_STAGES, params=[organization_id_param,],)
    stage = stage_state[a_id]["selected_option"]
    if stage:
        stage = stage["value"]

    if sentiment != slack_const.ZOOM_MEETING__NOT_WELL:
        forecast_state = state["forecast_category"]
        close_date_state = state["close_date"]
        a_id = slack_const.GET_OPPORTUNITY_FORECASTS
        forecast_category = forecast_state[a_id]["selected_option"]
        forecast_category = forecast_category["value"] if forecast_category else None
        a_id = slack_const.DEFAULT_ACTION_ID
        close_date = close_date_state[a_id]["selected_date"]
    else:
        forecast_category = None
        close_date = None
    a_id = slack_const.DEFAULT_ACTION_ID
    description = description_state[a_id]["value"]

    next_step = next_step_state[a_id]["value"]
    amount = amount_state[a_id]["value"]

    data = {
        "sentiment": sentiment,
        "meeting_id": context.get("m", None),
        "meeting_type": meeting_type,
        "stage": stage,
        "forecast_category": forecast_category if forecast_category else None,
        "description": description,
        "close_date": close_date if close_date else None,
        "next_step": next_step,
        "amount": amount if amount else None,
    }
    emit_save_meeting_review_data(context.get("m"), data=json.dumps(data))

    # NOTE: stage/forecast may be the original stage and therefore unchanged.
    # NOTE: if forecast is an ID, it corresponds to pre-existing lead forecast.
    #       if it is one of lead_const.FORECAST_CHOICES then it is a new selection.

    block_set_context = {"opp": context["opp"], "m": context["m"]}

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
    required_context=["u", "opp", "o", "original_message_channel", "original_message_timestamp",]
)
def process_zoom_meeting_different_opportunity_submit(payload, context):
    state = payload["view"]["state"]["values"]
    new_opportunity_state = state["new_opportunity"]

    user_id_param = "u=" + context["u"]
    a_id = action_with_params(slack_const.GET_USER_OPPORTUNITIES, params=[user_id_param,],)

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
        "opp": new_opportunity,
        "u": context["u"],
        "o": context["o"],
        "m": context["m"],
    }

    meeting = ZoomMeeting.objects.filter(id=context["m"]).select_related("opportunity").first()

    new_lead = Opportunity.objects.filter(id=new_opportunity).first()

    meeting.opportunity = new_lead
    meeting.save()
    # remove newly added leads that are in the meeting participants but are not common with the new_lead contacts

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


@processor()
def process_update_meeting_contact(payload, context):
    state = payload["view"]["state"]["values"]
    data = {}
    for k, v in state.items():
        data[k] = v["plain_input"]["value"]
    meeting = ZoomMeeting.objects.filter(id=context.get("m")).first()
    index = int(context.get("contact_index"))
    participant = meeting.participants[index]
    integration_id = participant.get("integration_id")
    instance_url = meeting.zoom_account.user.salesforce_account.instance_url
    access_token = meeting.zoom_account.user.salesforce_account.access_token
    if participant.get("integration_id", None):
        ContactAdapter.update_contact(data, access_token, instance_url, integration_id)
    else:
        res = ContactAdapter.create_new_contact(participant, access_token, instance_url)
        participant["integration_id"] = res["id"]
        participant["integration_source"] = "SALESFORCE"
        meeting.opportunity.add_contact_role(
            access_token, instance_url, participant["integration_id"]
        )
    meeting.participants[index] = {**meeting.participants[index], **data}
    meeting.save()
    return


def handle_view_submission(payload):
    """
    This takes place when a modal's Submit button is clicked.
    """
    switcher = {
        slack_const.ZOOM_MEETING__PROCESS_MEETING_SENTIMENT: process_zoom_meeting_data,
        slack_const.ZOOM_MEETING__DIFFERENT_OPPORTUNITY: process_zoom_meeting_different_opportunity_submit,
        slack_const.ZOOM_MEETING__EDIT_CONTACT: process_update_meeting_contact,
    }
    callback_id = payload["view"]["callback_id"]
    view_context = json.loads(payload["view"]["private_metadata"])
    return switcher.get(callback_id, NO_OP)(payload, view_context)
