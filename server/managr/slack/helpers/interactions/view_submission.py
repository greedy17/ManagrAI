import json
import pdb
import pytz
from datetime import datetime


from managr.organization.models import Organization
from managr.opportunity.models import Opportunity
from managr.zoom.models import ZoomMeeting, MeetingReview
from managr.salesforce import constants as sf_consts
from managr.slack import constants as slack_const
from managr.slack.helpers import block_builders
from managr.slack.helpers import requests as slack_requests
from managr.slack.helpers.utils import action_with_params, NO_OP, processor, block_finder
from managr.slack.helpers.block_sets import get_block_set
from managr.salesforce.adapter.models import ContactAdapter
from managr.salesforce.background import _process_update_opportunity
from managr.zoom import constants as zoom_consts
from managr.zoom.background import _save_meeting_review_data


@processor(
    required_context=["o", "opp", "m", "original_message_channel", "original_message_timestamp",]
)
def process_zoom_meeting_data(payload, context):
    # get context
    meeting = ZoomMeeting.objects.filter(id=context.get("m")).first()
    slack_access_token = (
        Organization.objects.select_related("slack_integration")
        .get(pk=context["o"])
        .slack_integration.access_token
    )

    standard_values = {}
    custom_values = {}
    # get state - state contains the values based on the block_id
    state = payload["view"]["state"]["values"]
    # values are stored with block_id as key, block data as value
    # block data is also a dict with action_id as key -
    # loop is best non static method to retreive it
    for field, data in state.items():
        for value in data.values():
            current_value = None
            if value["type"] == "external_select":
                current_value = value["selected_option"]["value"]
            elif value["type"] == "plain_text_input":
                current_value = value["value"]
            elif value["type"] == "datepicker":
                # convert date to correct format and make aware
                date = value.get("selected_date", None)
                if date and len(date):
                    ## make it aware by adding utc
                    date = datetime.strptime(date, "%Y-%m-%d")
                    date = pytz.utc.localize(date)
                current_value = date
            if field in zoom_consts.STANDARD_MEETING_FIELDS:
                standard_values[field] = current_value
            else:
                custom_values[field] = current_value

        # get field name for dict
        # get field type to retrieve the correct value

    m_r = MeetingReview.objects.create(
        **{**standard_values, "meeting": meeting, "custom_data": custom_values}
    )

    meeting.interaction_status = zoom_consts.MEETING_INTERACTION_STATUS_COMPLETE
    meeting.is_closed = True
    meeting.save()
    formatted_data = m_r.as_sf_update
    res = meeting.opportunity.update_in_salesforce(formatted_data)
    # use this for errors
    block_set_context = {"opp": context["opp"], "m": context["m"]}
    ts, channel = meeting.slack_form.split("|")

    slack_requests.update_channel_message(
        context["original_message_channel"],
        context["original_message_timestamp"],
        slack_access_token,
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
