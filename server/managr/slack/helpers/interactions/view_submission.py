import json
import pdb
import pytz
from datetime import datetime
import logging


from rest_framework.response import Response
from django.http import JsonResponse

from managr.api.decorators import log_all_exceptions
from managr.salesforce.adapter.exceptions import FieldValidationError
from managr.organization.models import Organization
from managr.opportunity.models import Opportunity
from managr.zoom.models import ZoomMeeting, MeetingReview
from managr.salesforce.models import MeetingWorkflow
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
from managr.salesforce.background import emit_fake_event_end

logger = logging.getLogger("managr")


@log_all_exceptions
@processor(
    required_context=["w", "resource", "original_message_channel", "original_message_timestamp",]
)
def process_search_or_create_next_page(payload, context):

    # check state for selected option
    view = payload["view"]
    private_metadata = json.loads(view["private_metadata"])
    state = payload["view"]["state"]["values"]
    selected_option = state["create_or_search"]["selected_option"]["selected_option"]["value"]
    private_metadata.update({"action": selected_option})
    private_metadata.update({"resource": context.get("resource")})

    # push the next view depending on selected option
    if selected_option == "SEARCH":
        blocks = get_block_set(
            "search_modal_block_set", {"w": context.get("w"), "resource": context.get("resource")}
        )
    elif selected_option == "CREATE":
        blocks = get_block_set(
            "create_modal_block_set", {"w": context.get("w"), "resource": context.get("resource")}
        )
    title_text = (
        f"Search {context.get('resource')}"
        if selected_option == "SEARCH"
        else f"Create {context.get('resource')}"
    )
    return {
        "response_action": "push",
        "view": {
            "type": "modal",
            "title": {"type": "plain_text", "text": title_text},
            "submit": {"type": "plain_text", "text": "Submit"},
            "blocks": blocks,
            "private_metadata": json.dumps(private_metadata),
            "callback_id": slack_const.ZOOM_MEETING__SELECTED_RESOURCE,
        },
    }


@log_all_exceptions
@processor(
    required_context=["w", "original_message_channel", "original_message_timestamp",]
)
def process_next_page(payload, context):
    # get context
    block_set_context = {"w": context["w"]}
    workflow = MeetingWorkflow.objects.get(id=context.get("w"))
    view = payload["view"]
    # if there are additional stage gating forms aggregate them and push them in 1 view
    # save current data to its form we will close all views at the end
    state = payload["view"]["state"]["values"]

    review_form = workflow.forms.filter(
        template__form_type=slack_const.FORM_TYPE_MEETING_REVIEW
    ).first()
    review_form.save_form(state)
    forms = workflow.forms.filter(template__form_type=slack_const.FORM_TYPE_STAGE_GATING).all()
    if len(forms):
        url = slack_const.SLACK_API_ROOT + slack_const.VIEWS_PUSH

        next_blocks = []
        for form in forms:
            next_blocks.extend(form.generate_form())

        return {
            "response_action": "push",
            "view": {
                "type": "modal",
                "title": {"type": "plain_text", "text": "Updated view"},
                "submit": {"type": "plain_text", "text": "Submit"},
                "blocks": next_blocks,
                "private_metadata": view["private_metadata"],
                "callback_id": slack_const.ZOOM_MEETING__PROCESS_MEETING_SENTIMENT,
            },
        }
        # access_token = workflow.user.organization.slack_integration.access_token
        # res = slack_requests.generic_request(url, data, access_token=access_token)
        # print(res.json())
    # first save the data to the form
    # check if there is a stage form to show
    # update to save
    # ts, channel = meeting.slack_interaction.split("|")
    return


@log_all_exceptions
@processor(
    required_context=["w", "original_message_channel", "original_message_timestamp",]
)
def process_zoom_meeting_data(payload, context):
    # get context
    workflow = MeetingWorkflow.objects.get(id=context.get("w"))
    user = workflow.user
    slack_access_token = user.organization.slack_integration.access_token
    # get state - state contains the values based on the block_id
    state = payload["view"]["state"]["values"]
    forms = workflow.forms.all().exclude(template__form_type=slack_const.FORM_TYPE_MEETING_REVIEW)
    for form in forms:
        form.save_form(state)

    ts, channel = workflow.slack_interaction.split("|")
    res = slack_requests.update_channel_message(
        channel, ts, slack_access_token, block_set=get_block_set("loading"),
    ).json()

    workflow.slack_interaction = f"{res['ts']}|{res['channel']}"
    workflow.save()

    # use this for errors
    return {"response_action": "clear"}


@log_all_exceptions
@processor(required_context=["w"])
def process_zoom_meeting_attach_resource(payload, context):
    workflow = MeetingWorkflow.objects.get(id=context.get("w"))
    meeting = workflow.meeting
    user = workflow.user
    slack_access_token = user.organization.slack_integration.access_token

    meeting_resource = context.get("resource")
    selected_action = context.get("action")

    # get state - state contains the values based on the block_id
    state = payload["view"]["state"]["values"]
    if selected_action == "SEARCH":
        # the key is the action id which is a query string so we just use values instead
        workflow.resource_id = list(state["select_existing"].values())[0]["selected_option"][
            "value"
        ]
        workflow.resource_type = meeting_resource
        workflow.save()

    ts, channel = workflow.slack_interaction.split("|")
    # clear old forms
    workflow.forms.all().delete()
    workflow.add_form(
        meeting_resource, slack_const.FORM_TYPE_MEETING_REVIEW,
    )
    res = slack_requests.update_channel_message(
        channel,
        ts,
        slack_access_token,
        block_set=get_block_set("initial_meeting_interaction", {"w": context.get("w")}),
    ).json()

    workflow.slack_interaction = f"{res['ts']}|{res['channel']}"
    workflow.save()
    return {"response_action": "clear"}


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
    object_fields = meeting.zoom_account.user.salesforce_account.object_fields

    if participant.get("integration_id", None):
        ContactAdapter.update_contact(
            data,
            access_token,
            instance_url,
            integration_id,
            object_fields.get("Contact", {}).get("fields", {}),
        )
    else:
        data["external_owner"] = meeting.zoom_account.user.salesforce_account.salesforce_id
        # if the meeting type is account add the contact account manually
        if meeting.meeting_resource == slack_const.FORM_RESOURCE_ACCOUNT:
            data["external_account"] = meeting.linked_account.integration_id
        res = ContactAdapter.create_new_contact(
            data, access_token, instance_url, object_fields.get("Contact", {}).get("fields", {}),
        )
        participant["integration_id"] = res["id"]
        participant["integration_source"] = "SALESFORCE"

        # if the meeting type is not an account we need to add a contact role
        if meeting.meeting_resource == slack_const.FORM_RESOURCE_OPPORTUNITY:
            meeting.opportunity.add_contact_role(
                access_token, instance_url, participant["integration_id"],
            )
    meeting.participants[index] = {**meeting.participants[index], "secondary_data": data}
    meeting.save()
    return


def handle_view_submission(payload):
    """
    This takes place when a modal's Submit button is clicked.
    """
    switcher = {
        slack_const.ZOOM_MEETING__SELECTED_RESOURCE: process_zoom_meeting_attach_resource,
        slack_const.ZOOM_MEETING__PROCESS_MEETING_SENTIMENT: process_zoom_meeting_data,
        slack_const.ZOOM_MEETING__EDIT_CONTACT: process_update_meeting_contact,
        slack_const.ZOOM_MEETING__PROCESS_NEXT_PAGE: process_next_page,
        slack_const.ZOOM_MEETING__SEARCH_OR_CREATE_NEXT_PAGE: process_search_or_create_next_page,
    }
    callback_id = payload["view"]["callback_id"]
    view_context = json.loads(payload["view"]["private_metadata"])
    return switcher.get(callback_id, NO_OP)(payload, view_context)
