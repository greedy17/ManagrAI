import json
import pdb
import pytz
from datetime import datetime
import logging

from rest_framework.response import Response
from django.http import JsonResponse
from managr.salesforce.adapter.exceptions import FieldValidationError
from managr.organization.models import Organization
from managr.opportunity.models import Opportunity
from managr.zoom.models import ZoomMeeting, MeetingReview
from managr.salesforce import constants as sf_consts
from managr.slack import constants as slack_const
from managr.slack.helpers import block_builders
from managr.slack.helpers import requests as slack_requests
from managr.slack.helpers.utils import action_with_params, NO_OP, processor, block_finder
from managr.slack.helpers.block_sets import get_block_set
from managr.salesforce.adapter.models import ContactAdapter, OpportunityAdapter
from managr.salesforce.background import _process_update_opportunity
from managr.zoom import constants as zoom_consts
from managr.zoom.background import _save_meeting_review_data
from managr.salesforce.routes import routes as model_routes
from managr.salesforce.adapter.routes import routes as adapter_routes


logger = logging.getLogger("managr")


@processor(
    required_context=["m", "original_message_channel", "original_message_timestamp",]
)
def process_zoom_meeting_data(payload, context):
    # get context
    meeting = ZoomMeeting.objects.filter(id=context.get("m")).first()
    user = meeting.zoom_account.user
    slack_access_token = user.organization.slack_integration.access_token
    sentiment = context.get("sentiment", None)
    standard_values = {}
    custom_values = {}
    opportunity = meeting.opportunity
    meeting_resource_type = "Opportunity" if opportunity else "Account"
    # get state - state contains the values based on the block_id
    state = payload["view"]["state"]["values"]

    for field, data in state.items():
        for value in data.values():
            current_value = None
            if value["type"] == "external_select" or value["type"] == "static_select":
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
                # look up sf key and convert to mgr key
            mapping = OpportunityAdapter.reverse_integration_mapping()
            key = mapping.get(field, field)
            if key in zoom_consts.STANDARD_MEETING_FIELDS[meeting_resource_type]:
                standard_values[key] = current_value
            else:
                custom_values[key] = current_value

        # get field name for dict
        # get field type to retrieve the correct value

    m_r = MeetingReview.objects.create(
        **{
            **standard_values,
            "meeting": meeting,
            "custom_data": custom_values,
            "sentiment": sentiment,
        }
    )

    meeting.interaction_status = zoom_consts.MEETING_INTERACTION_STATUS_COMPLETE
    meeting.is_closed = True
    meeting.save()
    formatted_data = m_r.as_sf_update
    try:
        meeting.opportunity.update_in_salesforce(formatted_data)

    except FieldValidationError as e:
        # field errors in slack must contain the field name, in our case we are sending validations
        # therefore these need to be added as an element and removed manually

        print(e)
        return logger.exception(f"failed to log meeting {e}")

    # use this for errors
    block_set_context = {"m": context["m"]}
    ts, channel = meeting.slack_form.split("|")

    slack_requests.update_channel_message(
        context["original_message_channel"],
        context["original_message_timestamp"],
        slack_access_token,
        block_set=get_block_set("confirm_meeting_logged", context=block_set_context),
    )


@processor(required_context=["m"])
def process_zoom_meeting_attach_resource(payload, context):
    meeting = ZoomMeeting.objects.filter(id=context.get("m")).first()
    user = meeting.zoom_account.user
    slack_access_token = user.organization.slack_integration.access_token
    sf_account = user.salesforce_account
    vals = {}

    meeting_resource = (
        meeting.meeting_resource if meeting.meeting_resource else context.get("resource")
    )
    # get state - state contains the values based on the block_id
    state = payload["view"]["state"]["values"]

    for field, data in state.items():
        for value in data.values():
            current_value = None
            if value["type"] == "external_select" or value["type"] == "static_select":
                current_value = (
                    value.get("selected_option").get("value", None)
                    if value.get("selected_option", None)
                    else None
                )
            elif value["type"] == "plain_text_input":
                current_value = value["value"]
            elif value["type"] == "checkboxes":
                current_value = bool(len(value.get("selected_options", [])))
            elif value["type"] == "datepicker":
                # convert date to correct format and make aware
                date = value.get("selected_date", None)
                current_value = date
            vals[field] = current_value

    if "select_existing" in vals and vals["select_existing"]:
        if meeting_resource == "Opportunity":
            meeting.opportunity_id = vals["select_existing"]
        else:
            meeting.account_id = vals["select_existing"]

    else:
        # create new resource
        # get class
        model_class = model_routes.get(meeting_resource).get("model")
        serializer_class = model_routes.get(meeting_resource).get("serializer")
        # format as coming from api
        adapter_class = adapter_routes.get(meeting_resource)
        if meeting_resource == "Opportunity":
            data = adapter_class.create_opportunity(
                vals,
                sf_account.access_token,
                sf_account.instance_url,
                sf_account.object_fields.get(meeting_resource, dict()).get("fields"),
                str(user.id),
            )
        elif meeting_resource == "Account":
            data = adapter_class.create_account(
                vals,
                sf_account.access_token,
                sf_account.instance_url,
                sf_account.object_fields.get(meeting_resource, dict()).get("fields"),
                str(user.id),
            )
        serializer = serializer_class(data=data.as_dict)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        if meeting_resource == "Opportunity":
            meeting.opportunity_id = serializer.instance.id
        else:
            meeting.linked_account_id = serializer.instance.id

    meeting.save()

    ts, channel = meeting.slack_form.split("|")
    res = slack_requests.update_channel_message(
        channel,
        ts,
        slack_access_token,
        block_set=get_block_set("initial_meeting_interaction", context={"m": str(meeting.id)}),
    ).json()

    meeting.slack_form = f"{res['ts']}|{res['channel']}"
    meeting.save()


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

    res = slack_requests.update_channel_message(
        context["original_message_channel"],
        context["original_message_timestamp"],
        access_token,
        block_set=get_block_set("zoom_meeting_initial", context=block_set_context),
    )
    print(res.json())


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
        slack_const.ZOOM_MEETING__SELECTED_RESOURCE: process_zoom_meeting_attach_resource,
        slack_const.ZOOM_MEETING__PROCESS_MEETING_SENTIMENT: process_zoom_meeting_data,
        slack_const.ZOOM_MEETING__DIFFERENT_OPPORTUNITY: process_zoom_meeting_different_opportunity_submit,
        slack_const.ZOOM_MEETING__EDIT_CONTACT: process_update_meeting_contact,
    }
    callback_id = payload["view"]["callback_id"]
    view_context = json.loads(payload["view"]["private_metadata"])
    return switcher.get(callback_id, NO_OP)(payload, view_context)
