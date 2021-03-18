import json
import pdb
import pytz
from datetime import datetime
import logging


from rest_framework.response import Response
from django.http import JsonResponse

from managr.api.decorators import log_all_exceptions
from managr.salesforce.adapter.exceptions import FieldValidationError, RequiredFieldError
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
from managr.zoom import constants as zoom_consts
from managr.zoom.background import _save_meeting_review_data
from managr.salesforce.routes import routes as model_routes
from managr.salesforce.adapter.routes import routes as adapter_routes
from managr.salesforce.background import _process_create_new_resource
from managr.slack.helpers.exceptions import (
    UnHandeledBlocksException,
    InvalidBlocksFormatException,
    InvalidBlocksException,
)

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
@processor(required_context=["w", "form_type"])
def process_stage_next_page(payload, context):
    # get context
    block_set_context = {"w": context["w"]}
    workflow = MeetingWorkflow.objects.get(id=context.get("w"))
    view = payload["view"]
    # if there are additional stage gating forms aggregate them and push them in 1 view
    # save current data to its form we will close all views at the end
    state = view["state"]["values"]

    review_form = workflow.forms.filter(template__form_type=context.get("form_type")).first()
    review_form.save_form(state)
    forms = workflow.forms.filter(template__form_type=slack_const.FORM_TYPE_STAGE_GATING).all()
    if len(forms):
        next_blocks = []
        for form in forms:
            next_blocks.extend(form.generate_form())

        return {
            "response_action": "push",
            "view": {
                "type": "modal",
                "title": {"type": "plain_text", "text": "Stage Related Fields"},
                "submit": {"type": "plain_text", "text": "Submit"},
                "blocks": next_blocks,
                "private_metadata": view["private_metadata"],
                "callback_id": context.get("callback_id"),
            },
        }
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
    # if we had a next page the form data for the review was already saved
    forms = workflow.forms.filter(template__form_type=slack_const.FORM_TYPE_STAGE_GATING)
    if len(forms):
        for form in forms:
            form.save_form(state)
    # otherwise we save the meeting review form
    else:
        form = workflow.forms.filter(
            template__form_type=slack_const.FORM_TYPE_MEETING_REVIEW
        ).first()
        form.save_form(state)

    contact_forms = workflow.forms.filter(template__resource=slack_const.FORM_RESOURCE_CONTACT)
    logger.info(f"{contact_forms.values_list('id', 'template__form_type')}")
    ops = [
        # update
        f"{sf_consts.MEETING_REVIEW__UPDATE_RESOURCE}.{str(workflow.id)}",
        # create call log
        f"{sf_consts.MEETING_REVIEW__SAVE_CALL_LOG}.{str(workflow.id)}",
        # save meeting data
    ]
    for form in contact_forms:
        if form.template.form_type == slack_const.FORM_TYPE_CREATE:
            ops.append(
                f"{sf_consts.MEETING_REVIEW__CREATE_CONTACTS}.{str(workflow.id)},{str(form.id)}"
            )
        else:
            ops.append(
                f"{sf_consts.MEETING_REVIEW__UPDATE_CONTACTS}.{str(workflow.id)},{str(form.id)}"
            )

    # emit all events
    if len(workflow.operations_list):
        workflow.operations_list = [*workflow.operations_list, *ops]
    else:
        workflow.operations_list = ops

    ts, channel = workflow.slack_interaction.split("|")
    block_set = [
        get_block_set("loading", {"message": ":rocket: We are saving your data to salesforce..."}),
        get_block_set("create_meeting_task", {"w": str(workflow.id)}),
    ]
    try:
        res = slack_requests.update_channel_message(
            channel, ts, slack_access_token, block_set=block_set
        )
    except InvalidBlocksException as e:
        return logger.exception(
            f"Failed To Generate Slack Workflow Interaction for user {str(workflow.id)} email {workflow.user.email} {e}"
        )
    except InvalidBlocksFormatException as e:
        return logger.exception(
            f"Failed To Generate Slack Workflow Interaction for user {str(workflow.id)} email {workflow.user.email} {e}"
        )
    except UnHandeledBlocksException as e:
        return logger.exception(
            f"Failed To Generate Slack Workflow Interaction for user {str(workflow.id)} email {workflow.user.email} {e}"
        )

    workflow.slack_interaction = f"{res['ts']}|{res['channel']}"
    workflow.save()
    workflow.begin_tasks()

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
        # update the forms to the correct type

        workflow.save()

    elif selected_action == "CREATE":
        create_forms = workflow.forms.filter(
            template__form_type__in=[
                slack_const.FORM_TYPE_CREATE,
                slack_const.FORM_TYPE_STAGE_GATING,
            ]
        ).exclude(template__resource=slack_const.FORM_RESOURCE_CONTACT)
        for form in create_forms:
            form.save_form(state)
        try:
            resource = _process_create_new_resource.now(context.get("w"), meeting_resource)

        except FieldValidationError as e:

            return {
                "response_action": "push",
                "view": {
                    "type": "modal",
                    "title": {"type": "plain_text", "text": "An Error Occured"},
                    "blocks": get_block_set(
                        "error_modal",
                        {
                            "message": f":no_entry: Uh-Ohhh it looks like we found an error, this error is based on Validations set up by your org for {meeting_resource} objects\n *Error* : _{e}_"
                        },
                    ),
                },
            }
        except RequiredFieldError as e:

            return {
                "response_action": "push",
                "view": {
                    "type": "modal",
                    "title": {"type": "plain_text", "text": "An Error Occurred"},
                    "blocks": get_block_set(
                        "error_modal",
                        {
                            "message": f":no_entry: Uh-Ohhh it looks like we found an error, this error is based on Required fields from Salesforce for {meeting_resource} objects\n *Error* : _{e}_"
                        },
                    ),
                },
            }
        workflow.resource_id = str(resource.id)
        workflow.resource_type = meeting_resource

    workflow.save()

    ts, channel = workflow.slack_interaction.split("|")
    # clear old forms (except contact forms)

    workflow.forms.exclude(template__resource=slack_const.FORM_RESOURCE_CONTACT).delete()

    workflow.add_form(
        meeting_resource, slack_const.FORM_TYPE_MEETING_REVIEW,
    )
    try:
        res = slack_requests.update_channel_message(
            channel,
            ts,
            slack_access_token,
            block_set=get_block_set("initial_meeting_interaction", {"w": context.get("w")}),
        )
    except InvalidBlocksException as e:
        return logger.exception(
            f"Failed To Generate Slack Workflow Interaction for user {str(workflow.id)} email {workflow.user.email} {e}"
        )
    except InvalidBlocksFormatException as e:
        return logger.exception(
            f"Failed To Generate Slack Workflow Interaction for user {str(workflow.id)} email {workflow.user.email} {e}"
        )
    except UnHandeledBlocksException as e:
        return logger.exception(
            f"Failed To Generate Slack Workflow Interaction for user {str(workflow.id)} email {workflow.user.email} {e}"
        )

    workflow.slack_interaction = f"{res['ts']}|{res['channel']}"
    workflow.save()
    return {"response_action": "clear"}


@processor()
def process_update_meeting_contact(payload, context):
    state = payload["view"]["state"]["values"]
    workflow = MeetingWorkflow.objects.get(id=context.get("w"))
    contact = dict(
        *filter(
            lambda contact: contact["_tracking_id"] == context.get("tracking_id"),
            workflow.meeting.participants,
        )
    )

    form = workflow.forms.get(id=contact["_form"])
    form.save_form(state)
    # reconstruct the current data with the updated data
    adapter = ContactAdapter.from_api(
        {**contact.get("secondary_data", {}), **form.saved_data}, str(workflow.user_id)
    )
    new_contact = {
        **contact,
        **adapter.as_dict,
        "id": contact.get("id", None),
        "__has_changes": True,
    }
    # replace the contact in the participants list
    part_index = None
    for index, participant in enumerate(workflow.meeting.participants):
        if participant["_tracking_id"] == new_contact["_tracking_id"]:
            part_index = index
            break
    workflow.meeting.participants = [
        *workflow.meeting.participants[:part_index],
        new_contact,
        *workflow.meeting.participants[part_index + 1 :],
    ]
    workflow.meeting.save()
    action = slack_const.VIEWS_UPDATE
    url = slack_const.SLACK_API_ROOT + action
    trigger_id = payload["trigger_id"]
    view_id = payload["view"]["id"]
    workflow = MeetingWorkflow.objects.get(id=context.get("w"))

    org = workflow.user.organization

    access_token = org.slack_integration.access_token
    blocks = get_block_set("show_meeting_contacts", {"w": context.get("w")},)

    data = {
        "trigger_id": trigger_id,
        "view_id": view_id,
        "view": {
            "type": "modal",
            "callback_id": slack_const.ZOOM_MEETING__VIEW_MEETING_CONTACTS,
            "title": {"type": "plain_text", "text": "Contacts"},
            "submit": {"type": "plain_text", "text": "Submit"},
            "blocks": blocks,
        },
    }
    try:
        res = slack_requests.generic_request(url, data, access_token=access_token)
    except InvalidBlocksException as e:
        return logger.exception(
            f"Failed To Generate Slack Workflow Interaction for user {str(workflow.id)} email {workflow.user.email} {e}"
        )
    except InvalidBlocksFormatException as e:
        return logger.exception(
            f"Failed To Generate Slack Workflow Interaction for user {str(workflow.id)} email {workflow.user.email} {e}"
        )
    except UnHandeledBlocksException as e:
        return logger.exception(
            f"Failed To Generate Slack Workflow Interaction for user {str(workflow.id)} email {workflow.user.email} {e}"
        )
    return


@processor()
def process_edit_meeting_contact(payload, context):
    """ This Submission returns the update form stacked on top of the view contacts form """
    action = slack_const.VIEWS_UPDATE
    url = slack_const.SLACK_API_ROOT + action
    trigger_id = payload["trigger_id"]
    view_id = payload["view"]["id"]
    workflow = MeetingWorkflow.objects.get(id=context.get("w"))
    meeting = workflow.meeting
    org = workflow.user.organization

    access_token = org.slack_integration.access_token
    # blocks = get_block_set("show_meeting_contacts", {"w": context.get("w")},)

    # res = slack_requests.generic_request(url, data, access_token=access_token)

    return {
        "response_action": "push",
        "view": {
            "type": "modal",
            "title": {"type": "plain_text", "text": "Updated view"},
            "submit": {"type": "plain_text", "text": "Submit"},
            "blocks": get_block_set("edit_meeting_contacts", context,),
            "callback_id": slack_const.ZOOM_MEETING__UPDATE_PARTICIPANT_DATA,
            "private_metadata": json.dumps(context),
        },
    }


@processor()
def process_save_contact_data(payload, context):
    workflow = MeetingWorkflow.objects.get(id=context.get("w"))
    # update the old view to change edit contact to submit again

    state = payload["view"]["state"]["values"]
    ## save the checked contacts to the operations list
    create = []
    update = []
    for val in state.values():
        if val.get("CREATE") and len(val["CREATE"]["selected_options"]):
            create.append(val["CREATE"]["selected_options"][0]["value"])
        elif val.get("UPDATE") and len(val["UPDATE"]["selected_options"]):
            update.append(val["UPDATE"]["selected_options"][0]["value"])

    if not len(workflow.operations_list):
        workflow.operations_list = []
    if len(create):

        workflow.operations_list = [
            *workflow.operations_list,
            *[
                f"{sf_consts.MEETING_REVIEW__CREATE_CONTACTS}.{str(workflow.id)},{form}"
                for form in create
            ],
        ]

    if len(update):
        workflow.operations_list = [
            *workflow.operations_list,
            *[
                f"{sf_consts.MEETING_REVIEW__UPDATE_CONTACTS}.{str(workflow.id)},{form}"
                for form in update
            ],
        ]

    workflow.save()

    return


def handle_view_submission(payload):
    """
    This takes place when a modal's Submit button is clicked.
    """
    switcher = {
        slack_const.ZOOM_MEETING__SELECTED_RESOURCE: process_zoom_meeting_attach_resource,
        slack_const.ZOOM_MEETING__PROCESS_MEETING_SENTIMENT: process_zoom_meeting_data,
        slack_const.ZOOM_MEETING__EDIT_CONTACT: process_edit_meeting_contact,
        slack_const.ZOOM_MEETING__PROCESS_STAGE_NEXT_PAGE: process_stage_next_page,
        slack_const.ZOOM_MEETING__SEARCH_OR_CREATE_NEXT_PAGE: process_search_or_create_next_page,
        slack_const.ZOOM_MEETING__UPDATE_PARTICIPANT_DATA: process_update_meeting_contact,
        slack_const.ZOOM_MEETING__SAVE_CONTACTS: process_save_contact_data,
    }
    callback_id = payload["view"]["callback_id"]
    view_context = json.loads(payload["view"]["private_metadata"])
    return switcher.get(callback_id, NO_OP)(payload, view_context)
