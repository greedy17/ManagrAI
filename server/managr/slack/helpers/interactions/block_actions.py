import json
import pdb
import logging
from urllib.parse import urlencode
from django.db.models import Q
from managr.organization.models import Organization, Stage
from managr.opportunity.models import Opportunity
from managr.zoom.models import ZoomMeeting
from managr.slack import constants as slack_const
from managr.opportunity import constants as opp_consts
from managr.slack.helpers import requests as slack_requests
from managr.slack.helpers.utils import process_action_id, NO_OP, processor, block_finder
from managr.slack.helpers.block_sets import get_block_set
from managr.slack.helpers import block_builders
from managr.slack.models import OrgCustomSlackFormInstance
from managr.salesforce.models import MeetingWorkflow
from managr.core.models import User
from managr.slack.helpers.exceptions import (
    UnHandeledBlocksException,
    InvalidBlocksFormatException,
    InvalidBlocksException,
    InvalidAccessToken,
)
from managr.api.decorators import slack_api_exceptions


logger = logging.getLogger("managr")


@processor()
def process_meeting_review(payload, context):
    url = slack_const.SLACK_API_ROOT + slack_const.VIEWS_OPEN
    trigger_id = payload["trigger_id"]
    workflow_id = payload["actions"][0]["value"]
    workflow = MeetingWorkflow.objects.get(id=workflow_id)
    meeting = workflow.meeting
    organization = meeting.zoom_account.user.organization
    access_token = organization.slack_integration.access_token
    private_metadata = {
        "original_message_channel": payload["channel"]["id"],
        "original_message_timestamp": payload["message"]["ts"],
    }
    context = {
        "w": workflow_id,
        "f": str(workflow.forms.filter(template__form_type="MEETING_REVIEW").first().id),
    }

    private_metadata.update(context)
    data = {
        "trigger_id": trigger_id,
        "view": {
            "type": "modal",
            "callback_id": slack_const.ZOOM_MEETING__PROCESS_MEETING_SENTIMENT,
            "title": {"type": "plain_text", "text": "Log Meeting"},
            "blocks": get_block_set("meeting_review_modal", context=context),
            "submit": {"type": "plain_text", "text": "Submit"},
            "private_metadata": json.dumps(private_metadata),
            "external_id": "meeting_review_modal",
        },
    }
    try:
        res = slack_requests.generic_request(url, data, access_token=access_token)
    except InvalidBlocksException as e:
        return logger.exception(
            f"Failed To Generate Slack Workflow Interaction for user with workflow {str(workflow.id)} email {workflow.user.email} {e}"
        )
    except InvalidBlocksFormatException as e:
        return logger.exception(
            f"Failed To Generate Slack Workflow Interaction for user with workflow {str(workflow.id)} email {workflow.user.email} {e}"
        )
    except UnHandeledBlocksException as e:
        return logger.exception(
            f"Failed To Generate Slack Workflow Interaction for user with workflow {str(workflow.id)} email {workflow.user.email} {e}"
        )
    except InvalidAccessToken as e:
        return logger.exception(
            f"Failed To Generate Slack Workflow Interaction for user with workflow {str(workflow.user.id)} email {workflow.user.email} {e}"
        )
    view_id = res["view"]["id"]
    workflow.slack_view = view_id
    workflow.save()


@processor(required_context=["w"], action=slack_const.VIEWS_OPEN)
def process_show_meeting_contacts(payload, context, action=slack_const.VIEWS_OPEN):
    url = slack_const.SLACK_API_ROOT + action
    trigger_id = payload["trigger_id"]
    # view_id = payload["view"]["id"]
    workflow = MeetingWorkflow.objects.get(id=context.get("w"))
    org = workflow.user.organization

    access_token = org.slack_integration.access_token
    blocks = get_block_set(
        "show_meeting_contacts",
        context,
    )

    data = {
        "trigger_id": trigger_id,
        # "view_id": view_id,
        "view": {
            "type": "modal",
            "title": {"type": "plain_text", "text": "Contacts"},
            "blocks": blocks,
            "private_metadata": json.dumps(context),
        },
    }
    if action == slack_const.VIEWS_UPDATE:
        data["view_id"] = payload["view"]["id"]

    # private_metadata.update(context)
    try:
        res = slack_requests.generic_request(url, data, access_token=access_token)
    except InvalidBlocksException as e:
        return logger.exception(
            f"Failed To Generate Slack Workflow Interaction for user with workflow {str(workflow.id)} email {workflow.user.email} {e}"
        )
    except InvalidBlocksFormatException as e:
        return logger.exception(
            f"Failed To Generate Slack Workflow Interaction for user with workflow {str(workflow.id)} email {workflow.user.email} {e}"
        )
    except UnHandeledBlocksException as e:
        return logger.exception(
            f"Failed To Generate Slack Workflow Interaction for user with workflow {str(workflow.id)} email {workflow.user.email} {e}"
        )
    except InvalidAccessToken as e:
        return logger.exception(
            f"Failed To Generate Slack Workflow Interaction for user with workflow {str(workflow.id)} email {workflow.user.email} {e}"
        )
    workflow.slack_view = res.get("view").get("id")
    workflow.save()


@processor(required_context=["w", "tracking_id"])
def process_edit_meeting_contact(payload, context):
    url = slack_const.SLACK_API_ROOT + slack_const.VIEWS_UPDATE
    trigger_id = payload["trigger_id"]
    workflow = MeetingWorkflow.objects.get(id=context.get("w"))
    meeting = workflow.meeting

    org = meeting.zoom_account.user.organization

    access_token = org.slack_integration.access_token

    salesforce_account = meeting.zoom_account.user.salesforce_account

    view = payload["view"]
    # retrieve original blocks, view will use the same blocks but change the submit action
    blocks = view["blocks"]
    view_id = view["id"]
    title = view["title"]
    actions = payload["actions"]
    callback_id = None
    submit_button_text = None
    selected_action_block = actions[0] if len(actions) else None
    if selected_action_block:
        action = process_action_id(selected_action_block["action_id"])
        block_id = selected_action_block["block_id"]
        index, selected_block = block_finder(block_id, blocks)
        if (
            action["true_id"] == slack_const.ZOOM_MEETING__EDIT_CONTACT
            and selected_block["elements"][0]["value"] == slack_const.ZOOM_MEETING__EDIT_CONTACT
        ):
            selected_block["elements"][0]["text"]["text"] = "Cancel Edit Contact"
            selected_block["elements"][0]["value"] = slack_const.ZOOM_MEETING__CANCEL_EDIT_CONTACT
            blocks[index] = selected_block
            callback_id = slack_const.ZOOM_MEETING__EDIT_CONTACT
            submit_button_text = "Edit Contact"
            # change the block to show it is selected
        elif (
            action["true_id"] == slack_const.ZOOM_MEETING__EDIT_CONTACT
            and selected_block["elements"][0]["value"]
            == slack_const.ZOOM_MEETING__CANCEL_EDIT_CONTACT
        ):
            selected_block["elements"][0]["text"]["text"] = "Click To Select For Editing"
            selected_block["elements"][0]["value"] = slack_const.ZOOM_MEETING__EDIT_CONTACT
            blocks[index] = selected_block
            callback_id = None
            submit_button_text = None
            # change the block to show it is selected

    data = {
        "trigger_id": trigger_id,
        "view_id": view_id,
        "view": {
            "close": {"type": "plain_text", "text": "Close", "emoji": True},
            "type": "modal",
            "title": title,
            "blocks": blocks,
            "private_metadata": json.dumps(
                {
                    "w": context.get("w"),
                    "tracking_id": context.get("tracking_id"),
                }
            ),
        },
    }
    if callback_id:
        data["view"]["callback_id"] = callback_id

    if submit_button_text:
        data["view"]["submit"] = {"type": "plain_text", "text": submit_button_text, "emoji": True}
    try:
        res = slack_requests.generic_request(url, data, access_token=access_token)
    except InvalidBlocksException as e:
        return logger.exception(
            f"Failed To Generate Slack Workflow Interaction for user  with workflow {str(workflow.id)} email {workflow.user.email} {e}"
        )
    except InvalidBlocksFormatException as e:
        return logger.exception(
            f"Failed To Generate Slack Workflow Interaction for user  with workflow {str(workflow.id)} email {workflow.user.email} {e}"
        )
    except UnHandeledBlocksException as e:
        return logger.exception(
            f"Failed To Generate Slack Workflow Interaction for user  with workflow {str(workflow.id)} email {workflow.user.email} {e}"
        )
    except InvalidAccessToken as e:
        return logger.exception(
            f"Failed To Generate Slack Workflow Interaction for user  with workflow {str(workflow.id)} email {workflow.user.email} {e}"
        )
    workflow.slack_view = res["view"]["id"]
    workflow.save()


@processor(required_context=[])
def process_stage_selected(payload, context):
    url = slack_const.SLACK_API_ROOT + slack_const.VIEWS_UPDATE
    workflow = MeetingWorkflow.objects.filter(id=context.get("w")).first()
    user = workflow.user
    org = user.organization
    access_token = org.slack_integration.access_token
    trigger_id = payload["trigger_id"]
    view_id = payload["view"]["id"]
    private_metadata = json.loads(payload["view"]["private_metadata"])

    if len(payload["actions"]):
        action = payload["actions"][0]
        blocks = payload["view"]["blocks"]
        selected_value = action["selected_option"]["value"]

        # delete all existing stage forms
        workflow.forms.filter(template__form_type=slack_const.FORM_TYPE_STAGE_GATING).delete()
        stage_form = org.custom_slack_forms.filter(
            form_type=slack_const.FORM_TYPE_STAGE_GATING, stage=selected_value
        ).first()

        if stage_form:
            workflow.add_form(
                slack_const.FORM_RESOURCE_OPPORTUNITY,
                slack_const.FORM_TYPE_STAGE_GATING,
                stage=selected_value,
            )
        # gather and attach all forms

    if not stage_form:
        submit_text = "Submit"
        if payload["view"]["external_id"] == "create_modal_block_set":
            callback_id = slack_const.COMMAND_FORMS__SUBMIT_FORM
        else:
            callback_id = slack_const.ZOOM_MEETING__PROCESS_MEETING_SENTIMENT
    else:
        submit_text = "Next"
        callback_id = slack_const.ZOOM_MEETING__PROCESS_STAGE_NEXT_PAGE
        if payload["view"]["callback_id"] == slack_const.ZOOM_MEETING__PROCESS_MEETING_SENTIMENT:
            context = {
                **context,
                "form_type": slack_const.FORM_TYPE_MEETING_REVIEW,
                "callback_id": slack_const.ZOOM_MEETING__PROCESS_MEETING_SENTIMENT,
            }
        else:
            context = {
                **context,
                "form_type": slack_const.FORM_TYPE_CREATE,
                "callback_id": slack_const.COMMAND_FORMS__SUBMIT_FORM,
            }
    private_metadata.update(context)
    data = {
        "trigger_id": trigger_id,
        "view_id": view_id,
        "view": {
            "type": "modal",
            "callback_id": callback_id,
            "title": {"type": "plain_text", "text": payload["view"]["title"]["text"]},
            "blocks": blocks,
            "submit": {"type": "plain_text", "text": submit_text},
            "private_metadata": json.dumps(private_metadata),
        },
    }
    try:
        res = slack_requests.generic_request(url, data, access_token=access_token)
    except InvalidBlocksException as e:
        return logger.exception(
            f"Failed To Generate Slack Workflow Interaction for user  with workflow {str(workflow.id)} email {workflow.user.email} {e}"
        )
    except InvalidBlocksFormatException as e:
        return logger.exception(
            f"Failed To Generate Slack Workflow Interaction for user  with workflow {str(workflow.id)} email {workflow.user.email} {e}"
        )
    except UnHandeledBlocksException as e:
        return logger.exception(
            f"Failed To Generate Slack Workflow Interaction for user  with workflow {str(workflow.id)} email {workflow.user.email} {e}"
        )
    except InvalidAccessToken as e:
        return logger.exception(
            f"Failed To Generate Slack Workflow Interaction for user  with workflow {str(workflow.id)} email {workflow.user.email} {e}"
        )
    workflow.slack_view = res.get("view").get("id")
    workflow.save()


@processor(required_context=["u", "f"])
def process_stage_selected_command_form(payload, context):
    url = slack_const.SLACK_API_ROOT + slack_const.VIEWS_UPDATE
    current_form_ids = context.get("f").split(",")
    user = User.objects.get(id=context.get("u"))
    org = user.organization
    access_token = org.slack_integration.access_token
    trigger_id = payload["trigger_id"]
    view_id = payload["view"]["id"]
    private_metadata = json.loads(payload["view"]["private_metadata"])
    # get the forms associated with this slack

    current_forms = user.custom_slack_form_instances.filter(id__in=current_form_ids)
    # delete any existing stage forms
    current_forms.exclude(template__form_type__in=["UPDATE", "CREATE"]).delete()
    main_form = current_forms.first()
    added_form_ids = []
    if len(payload["actions"]):
        action = payload["actions"][0]
        blocks = payload["view"]["blocks"]
        selected_value = action["selected_option"]["value"]
        # blockfinder returns a tuple of its index in the block and the object
        index, action_block = block_finder(action["block_id"], blocks)

        # find all stages previous to it
        stage_form = org.custom_slack_forms.filter(
            form_type=slack_const.FORM_TYPE_STAGE_GATING, stage=selected_value
        ).first()

        if stage_form:
            new_form = OrgCustomSlackFormInstance.objects.create(
                user=user, template=stage_form, resource_id=main_form.resource_id
            )
            added_form_ids.append(str(new_form.id))

        # gather and attach all forms
    context = {**context, "f": ",".join([str(main_form.id), *added_form_ids])}
    private_metadata.update(context)
    submit_button_message = "Next" if len(added_form_ids) else "Submit"
    callback_id = (
        slack_const.COMMAND_FORMS__PROCESS_NEXT_PAGE
        if len(added_form_ids)
        else slack_const.COMMAND_FORMS__SUBMIT_FORM
    )
    data = {
        "trigger_id": trigger_id,
        "view_id": view_id,
        "view": {
            "type": "modal",
            "callback_id": callback_id,
            "title": {"type": "plain_text", "text": "Update"},
            "blocks": blocks,
            "submit": {"type": "plain_text", "text": submit_button_message},
            "private_metadata": json.dumps(private_metadata),
        },
    }
    try:
        res = slack_requests.generic_request(url, data, access_token=access_token)
    except InvalidBlocksException as e:
        return logger.exception(f"Failed To Generate Slack {e}")
    except InvalidBlocksFormatException as e:
        return logger.exception(f"Failed To Generate Slack  {e}")
    except UnHandeledBlocksException as e:
        return logger.exception(f"Failed To Generate Slack  {e}")
    except InvalidAccessToken as e:
        return logger.exception(f"Failed To Generate Slack Workflow Interaction for user {e}")


@processor(required_context=["w", "tracking_id"])
def process_remove_contact_from_meeting(payload, context):
    workflow = MeetingWorkflow.objects.get(id=context.get("w"))
    meeting = workflow.meeting

    for i, part in enumerate(meeting.participants):
        if part["_tracking_id"] == context.get("tracking_id"):
            # remove its form if it exists
            if part["_form"] not in [None, ""]:
                workflow.forms.filter(id=part["_form"]).delete()
            del meeting.participants[i]
            break
    meeting.save()

    return process_show_meeting_contacts(payload, context, action=slack_const.VIEWS_UPDATE)


@processor(required_context=["w"])
def process_meeting_selected_resource(payload, context):
    """opens a modal with the options to search or create"""
    url = slack_const.SLACK_API_ROOT + slack_const.VIEWS_OPEN
    trigger_id = payload["trigger_id"]

    workflow = MeetingWorkflow.objects.get(id=context.get("w"))
    select = payload["actions"][0]["selected_option"]
    selected_option = select["value"]
    organization = workflow.user.organization
    access_token = organization.slack_integration.access_token
    private_metadata = {
        "original_message_channel": payload["channel"]["id"],
        "original_message_timestamp": payload["message"]["ts"],
    }

    context = {
        "w": context.get("w"),
        "resource": str(selected_option),
    }

    private_metadata.update(context)
    data = {
        "trigger_id": trigger_id,
        "view": {
            "type": "modal",
            "callback_id": slack_const.ZOOM_MEETING__SELECTED_RESOURCE,
            "title": {"type": "plain_text", "text": f"{selected_option}"},
            "blocks": get_block_set("create_or_search_modal", context=context),
            "private_metadata": json.dumps(private_metadata),
        },
    }
    try:
        res = slack_requests.generic_request(url, data, access_token=access_token)
    except InvalidBlocksException as e:
        return logger.exception(
            f"Failed To Generate Slack Workflow Interaction for user  with workflow {str(workflow.id)} email {workflow.user.email} {e}"
        )
    except InvalidBlocksFormatException as e:
        return logger.exception(
            f"Failed To Generate Slack Workflow Interaction for user  with workflow {str(workflow.id)} email {workflow.user.email} {e}"
        )
    except UnHandeledBlocksException as e:
        return logger.exception(
            f"Failed To Generate Slack Workflow Interaction for user  with workflow {str(workflow.id)} email {workflow.user.email} {e}"
        )
    except InvalidAccessToken as e:
        return logger.exception(
            f"Failed To Generate Slack Workflow Interaction for user  with workflow {str(workflow.id)} email {workflow.user.email} {e}"
        )
    workflow.slack_view = res.get("view").get("id")
    workflow.save()


@processor(required_context=[])
def process_meeting_selected_resource_option(payload, context):
    """depending on the selection on the meeting review form (create new) this will open a create form or an empty block set"""
    url = slack_const.SLACK_API_ROOT + slack_const.VIEWS_UPDATE
    trigger_id = payload["trigger_id"]
    workflow_id = json.loads(payload["view"]["private_metadata"])["w"]
    workflow = MeetingWorkflow.objects.get(id=workflow_id)
    select = payload["actions"][0]["selected_option"]["value"]
    resource_type = context.get("resource")
    action = None
    external_id = ""

    try:
        action, resource_type = select.split(".")
    except ValueError:

        pass
    context = {
        "w": workflow_id,
        "resource": resource_type,
    }
    if not action:
        blocks = [block_finder("select_existing", payload["view"]["blocks"])[1]]
        context["action"] = "EXISTING"
    else:
        context["action"] = "CREATE_NEW"
        blocks = [
            block_finder("select_existing", payload["view"]["blocks"])[1],
            *get_block_set(
                "create_modal_block_set",
                context,
            ),
        ]
        external_id = "create_modal_block_set"

    organization = workflow.user.organization
    access_token = organization.slack_integration.access_token
    # change variables based on selection
    private_metadata = json.loads(payload["view"]["private_metadata"])
    private_metadata.update({**context})
    if action == "CREATE_NEW":
        callback_id = slack_const.COMMAND_FORMS__SUBMIT_FORM
        private_metadata = json.loads(payload["view"]["private_metadata"])
        private_metadata = {
            **private_metadata,
            "u": str(workflow.user.id),
            "f": str(
                workflow.forms.filter(
                    template__form_type="CREATE", template__resource=resource_type
                )
                .first()
                .id
            ),
        }

    else:
        callback_id = slack_const.ZOOM_MEETING__SELECTED_RESOURCE

    data = {
        "view_id": payload["view"]["id"],
        "view": {
            "type": "modal",
            "callback_id": callback_id,
            "title": {"type": "plain_text", "text": f"{resource_type}"},
            "blocks": blocks,
            "private_metadata": json.dumps(private_metadata),
            "submit": {
                "type": "plain_text",
                "text": "Submit",
            },
            "external_id": external_id,
        },
    }
    try:
        res = slack_requests.generic_request(url, data, access_token=access_token)
    except InvalidBlocksException as e:
        return logger.exception(
            f"Failed To Generate Slack Workflow Interaction for user  with workflow {str(workflow.id)} email {workflow.user.email} {e}"
        )
    except InvalidBlocksFormatException as e:
        return logger.exception(
            f"Failed To Generate Slack Workflow Interaction for user  with workflow {str(workflow.id)} email {workflow.user.email} {e}"
        )
    except UnHandeledBlocksException as e:
        return logger.exception(
            f"Failed To Generate Slack Workflow Interaction for user  with workflow {str(workflow.id)} email {workflow.user.email} {e}"
        )
    except InvalidAccessToken as e:
        return logger.exception(
            f"Failed To Generate Slack Workflow Interaction for user  with workflow {str(workflow.id)} email {workflow.user.email} {e}"
        )
    workflow.slack_view = res.get("view").get("id")
    workflow.save()


@processor()
def process_create_or_search_selected(payload, context):
    """attaches a drop down to the message block for selecting a resource type"""
    workflow_id = payload["actions"][0]["value"]
    workflow = MeetingWorkflow.objects.get(id=workflow_id)
    meeting = workflow.meeting

    organization = workflow.user.organization
    access_token = organization.slack_integration.access_token
    # get current blocks
    previous_blocks = payload["message"]["blocks"]
    # check if the dropdown option has been added already
    select_block = block_finder(slack_const.ZOOM_MEETING__ATTACH_RESOURCE_SECTION, previous_blocks)
    block_sets = []
    if not select_block:
        # create new block including the resource type
        block_sets = get_block_set("attach_resource_interaction", {"w": workflow_id})
    try:
        res = slack_requests.update_channel_message(
            payload["channel"]["id"],
            payload["message"]["ts"],
            access_token,
            block_set=[*previous_blocks, *block_sets],
        )
    except InvalidBlocksException as e:
        return logger.exception(
            f"Failed To Generate Slack Workflow Interaction for user  with workflow {str(workflow.id)} email {workflow.user.email} {e}"
        )
    except InvalidBlocksFormatException as e:
        return logger.exception(
            f"Failed To Generate Slack Workflow Interaction for user  with workflow {str(workflow.id)} email {workflow.user.email} {e}"
        )
    except UnHandeledBlocksException as e:
        return logger.exception(
            f"Failed To Generate Slack Workflow Interaction for user  with workflow {str(workflow.id)} email {workflow.user.email} {e}"
        )
    except InvalidAccessToken as e:
        return logger.exception(
            f"Failed To Generate Slack Workflow Interaction for user  with workflow {str(workflow.id)} email {workflow.user.email} {e}"
        )

    workflow.slack_interaction = f"{res['ts']}|{res['channel']}"
    workflow.meeting.save()


@processor()
def process_restart_flow(payload, context):
    workflow_id = payload["actions"][0]["value"]
    workflow = MeetingWorkflow.objects.get(id=workflow_id)
    organization = workflow.user.organization
    access_token = organization.slack_integration.access_token
    ts, channel = workflow.slack_interaction.split("|")
    try:
        res = slack_requests.update_channel_message(
            channel,
            ts,
            access_token,
            block_set=get_block_set("initial_meeting_interaction", context={"w": workflow_id}),
        )
    except InvalidBlocksException as e:
        return logger.exception(
            f"Failed To Generate Slack Workflow Interaction for user  with workflow {str(workflow.id)} email {workflow.user.email} {e}"
        )
    except InvalidBlocksFormatException as e:
        return logger.exception(
            f"Failed To Generate Slack Workflow Interaction for user  with workflow {str(workflow.id)} email {workflow.user.email} {e}"
        )
    except UnHandeledBlocksException as e:
        return logger.exception(
            f"Failed To Generate Slack Workflow Interaction for user  with workflow {str(workflow.id)} email {workflow.user.email} {e}"
        )
    except InvalidAccessToken as e:
        return logger.exception(
            f"Failed To Generate Slack Workflow Interaction for user  with workflow {str(workflow.id)} email {workflow.user.email} {e}"
        )

    workflow.slack_interaction = f"{res['ts']}|{res['channel']}"
    workflow.save()


@slack_api_exceptions(rethrow=True)
@processor(required_context=["resource", "u"])
def process_show_update_resource_form(payload, context):
    from managr.slack.models import OrgCustomSlackForm, OrgCustomSlackFormInstance

    url = slack_const.SLACK_API_ROOT + slack_const.VIEWS_UPDATE
    select = payload["actions"][0]["selected_option"]
    selected_option = select["value"]
    resource_id = selected_option
    resource_type = context.get("resource")
    user = User.objects.get(id=context.get("u"))
    access_token = user.organization.slack_integration.access_token

    # HACK forms are generated with a helper fn currently stagename takes a special action id to update forms
    # we need to manually change this action_id
    if resource_id:
        template = (
            OrgCustomSlackForm.objects.for_user(user)
            .filter(Q(resource=resource_type, form_type="UPDATE"))
            .first()
        )
        slack_form = OrgCustomSlackFormInstance.objects.create(
            template=template,
            resource_id=resource_id,
            user=user,
        )
        if slack_form:
            context.update({"f": str(slack_form.id)})

    blocks = get_block_set(
        "update_modal_block_set",
        context={**context, "resource_type": resource_type, "resource_id": resource_id},
    )
    if slack_form:
        try:
            index, block = block_finder("StageName", blocks)
        except ValueError:
            # did not find the block
            block = None
            pass

        if block:
            block = {
                **block,
                "accessory": {
                    **block["accessory"],
                    "action_id": f"{slack_const.COMMAND_FORMS__STAGE_SELECTED}?u={str(user.id)}&f={str(slack_form.id)}",
                },
            }
            blocks = [*blocks[:index], block, *blocks[index + 1 :]]

    private_metadata = {
        "channel_id": payload.get("container").get("channel_id"),
    }

    private_metadata.update(context)
    data = {
        "trigger_id": payload["trigger_id"],
        "view_id": payload["view"]["id"],
        "view": {
            "type": "modal",
            "callback_id": slack_const.COMMAND_FORMS__SUBMIT_FORM,
            "title": {"type": "plain_text", "text": f"Update {resource_type}"},
            "blocks": blocks,
            "submit": {"type": "plain_text", "text": "Update", "emoji": True},
            "private_metadata": json.dumps(private_metadata),
            "external_id": "update_modal_block_set",
        },
    }

    slack_requests.generic_request(url, data, access_token=access_token)


@processor()
def process_disregard_meeting_review(payload, context):
    workflow_id = payload["actions"][0]["value"]
    workflow = MeetingWorkflow.objects.get(id=workflow_id)
    organization = workflow.user.organization
    access_token = organization.slack_integration.access_token
    try:
        res = slack_requests.update_channel_message(
            payload["channel"]["id"],
            payload["message"]["ts"],
            access_token,
            block_set=get_block_set("disregard_meeting_review", context={"w": workflow_id}),
        )
    except InvalidBlocksException as e:
        return logger.exception(
            f"Failed To Generate Slack Workflow Interaction for user  with workflow {str(workflow.id)} email {workflow.user.email} {e}"
        )
    except InvalidBlocksFormatException as e:
        return logger.exception(
            f"Failed To Generate Slack Workflow Interaction for user  with workflow {str(workflow.id)} email {workflow.user.email} {e}"
        )
    except UnHandeledBlocksException as e:
        return logger.exception(
            f"Failed To Generate Slack Workflow Interaction for user  with workflow {str(workflow.id)} email {workflow.user.email} {e}"
        )
    except InvalidAccessToken as e:
        return logger.exception(
            f"Failed To Generate Slack Workflow Interaction for user  with workflow {str(workflow.id)} email {workflow.user.email} {e}"
        )
    workflow.slack_interaction = f"{res['ts']}|{res['channel']}"
    workflow.save()


@processor(requried_context="u")
def process_coming_soon(payload, context):
    url = slack_const.SLACK_API_ROOT + slack_const.VIEWS_OPEN
    trigger_id = payload["trigger_id"]
    u = User.objects.get(id=context.get("u"))
    org = u.organization

    data = {
        "trigger_id": trigger_id,
        "view": {
            "type": "modal",
            "callback_id": "NEXT",
            "title": {"type": "plain_text", "text": f"Coming Soon"},
            "blocks": get_block_set("coming_soon_modal", {}),
        },
    }
    try:
        slack_requests.generic_request(url, data, access_token=org.slack_integration.access_token)

    except InvalidBlocksException as e:
        return logger.exception(f"Failed To Generate Blocks {e}")
    except InvalidBlocksFormatException as e:
        return logger.exception(f"Failed To Generate Blocks {e}")
    except UnHandeledBlocksException as e:
        return logger.exception(f"Failed To Generate Blocks {e}")
    except InvalidAccessToken as e:
        return logger.exception(f"Failed To send slack {e}")


@processor(required_context="u")
def process_create_task(payload, context):
    url = slack_const.SLACK_API_ROOT + slack_const.VIEWS_OPEN
    trigger_id = payload["trigger_id"]
    u = User.objects.get(id=context.get("u"))
    org = u.organization

    data = {
        "trigger_id": trigger_id,
        "view": {
            "type": "modal",
            "callback_id": slack_const.COMMAND_CREATE_TASK,
            "title": {"type": "plain_text", "text": f"Create a Task"},
            "blocks": get_block_set(
                "create_task_modal",
                context={
                    "u": context.get("u"),
                    "resource_type": context.get("resource_type"),
                    "resource_id": context.get("resource_id"),
                },
            ),
            "submit": {"type": "plain_text", "text": "Submit", "emoji": True},
            "private_metadata": json.dumps(context),
        },
    }

    try:
        slack_requests.generic_request(url, data, access_token=org.slack_integration.access_token)
    except InvalidBlocksException as e:
        return logger.exception(
            f"Failed To Generate Slack Workflow Interaction for user {u.full_name} email {u.email} {e}"
        )
    except InvalidBlocksFormatException as e:
        return logger.exception(
            f"Failed To Generate Slack Workflow Interaction for user {u.full_name} email {u.email} {e}"
        )
    except UnHandeledBlocksException as e:
        return logger.exception(
            f"Failed To Generate Slack Workflow Interaction for user {u.full_name} email {u.email} {e}"
        )
    except InvalidAccessToken as e:
        return logger.exception(
            f"Failed To Generate Slack Workflow Interaction for user {u.full_name} email {u.email} {e}"
        )


@processor()
def process_request_invite_from_home_tab(payload, context):
    """
    According to slack anyone can see the home tab if a user triggers the home event
    And is not a user we show a button to request access, this will ask the is_admin user to invite them
    """
    # get the org team
    team_id = payload["user"]["team_id"]
    new_user_slack_id = payload["actions"][0]["value"]
    # get the is_admin user
    o = Organization.objects.filter(slack_integration__team_id=team_id).first()
    u = o.users.filter(is_admin=True).first()
    # send a message to invite the user
    slack_requests.send_ephemeral_message(
        u.slack_integration.channel,
        o.slack_integration.access_token,
        u.slack_integration.slack_id,
        text="User requested an invite",
        block_set=[
            block_builders.simple_section(
                f"<@{new_user_slack_id}> has requested an invite to Managr", "mrkdwn"
            )
        ],
    )
    old_view = payload["view"]
    blocks = old_view["blocks"]
    # remove the request button
    index, block = block_finder("INVITE_BUTTON", blocks)
    new_blocks = [
        *blocks[0:index],
        block_builders.simple_section("Invite Sent"),
        *blocks[index + 1 :],
    ]
    view = {"type": "home", "blocks": new_blocks}
    slack_requests.publish_view(new_user_slack_id, o.slack_integration.access_token, view)
    # update the home tab of the user with message that it was sent


@processor(required_context="u")
def process_resource_selected_for_task(payload, context):

    url = slack_const.SLACK_API_ROOT + slack_const.VIEWS_UPDATE
    trigger_id = payload["trigger_id"]
    u = User.objects.get(id=context.get("u"))
    org = u.organization
    selected_value = None
    if len(payload["actions"]):
        action = payload["actions"][0]
        blocks = payload["view"]["blocks"]
        selected_value = action["selected_option"]["value"]
    data = {
        "trigger_id": trigger_id,
        "view_id": payload.get("view").get("id"),
        "view": {
            "type": "modal",
            "callback_id": slack_const.COMMAND_CREATE_TASK,
            "title": {"type": "plain_text", "text": f"Create a Task"},
            "blocks": get_block_set(
                payload["view"]["external_id"], {**context, "resource_type": selected_value}
            ),
            "submit": payload["view"]["submit"],
            "private_metadata": json.dumps(context),
            "external_id": payload["view"]["external_id"],
        },
    }
    try:
        slack_requests.generic_request(url, data, access_token=org.slack_integration.access_token)
    except InvalidBlocksException as e:
        return logger.exception(
            f"Failed To Generate Slack Workflow Interaction for user {u.full_name} email {u.email} {e}"
        )
    except InvalidBlocksFormatException as e:
        return logger.exception(
            f"Failed To Generate Slack Workflow Interaction for user {u.full_name} email {u.email} {e}"
        )
    except UnHandeledBlocksException as e:
        return logger.exception(
            f"Failed To Generate Slack Workflow Interaction for user {u.full_name} email {u.email} {e}"
        )
    except InvalidAccessToken as e:
        return logger.exception(
            f"Failed To Generate Slack Workflow Interaction for user {u.full_name} email {u.email} {e}"
        )


def handle_block_actions(payload):
    """
    This takes place when user completes a general interaction,
    such as clicking a button.
    """
    switcher = {
        slack_const.ZOOM_MEETING__VIEW_MEETING_CONTACTS: process_show_meeting_contacts,
        slack_const.ZOOM_MEETING__EDIT_CONTACT: process_edit_meeting_contact,
        slack_const.ZOOM_MEETING__REMOVE_CONTACT: process_remove_contact_from_meeting,
        slack_const.ZOOM_MEETING__CREATE_OR_SEARCH: process_create_or_search_selected,
        slack_const.ZOOM_MEETING__SELECTED_RESOURCE: process_meeting_selected_resource,
        slack_const.ZOOM_MEETING__SELECTED_RESOURCE_OPTION: process_meeting_selected_resource_option,
        slack_const.ZOOM_MEETING__DISREGARD_REVIEW: process_disregard_meeting_review,
        slack_const.ZOOM_MEETING__RESTART_MEETING_FLOW: process_restart_flow,
        slack_const.ZOOM_MEETING__INIT_REVIEW: process_meeting_review,
        slack_const.ZOOM_MEETING__STAGE_SELECTED: process_stage_selected,
        slack_const.ZOOM_MEETING__CREATE_TASK: process_create_task,
        slack_const.ZOOM_MEETING__CONVERT_LEAD: process_coming_soon,
        slack_const.COMMAND_FORMS__GET_LOCAL_RESOURCE_OPTIONS: process_show_update_resource_form,
        slack_const.COMMAND_FORMS__STAGE_SELECTED: process_stage_selected_command_form,
        slack_const.UPDATE_TASK_SELECTED_RESOURCE: process_resource_selected_for_task,
        slack_const.HOME_REQUEST_SLACK_INVITE: process_request_invite_from_home_tab,
    }
    action_query_string = payload["actions"][0]["action_id"]
    processed_string = process_action_id(action_query_string)
    action_id = processed_string.get("true_id")
    action_params = processed_string.get("params")
    # added special key __block_action to allow us to override the defaults since the action_id is used for both the suggestions and the actions
    if action_params.get("__block_action", None):
        action_id = action_params.get("__block_action")

    return switcher.get(action_id, NO_OP)(payload, action_params)
