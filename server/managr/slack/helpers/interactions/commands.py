import json
import datetime
import logging
import uuid

from six import text_type
from managr.core.models import User
from managr.slack.models import UserSlackIntegration
from managr.slack import constants as slack_const
from managr.slack.helpers.block_sets import get_block_set
from managr.slack.helpers import requests as slack_requests
from managr.slack.helpers import block_builders
from managr.slack.helpers.utils import action_with_params

logger = logging.getLogger("managr")


def update_resource(context):
    # list of accepted commands for this fake endpoint
    user = User.objects.get(id=context.get("u"))
    if user.slack_integration:
        slack = (
            UserSlackIntegration.objects.filter(slack_id=user.slack_integration.slack_id)
            .select_related("user")
            .first()
        )
        if not slack:
            data = {
                "response_type": "ephemeral",
                "text": "Sorry I cant find your managr account",
            }
        blocks = get_block_set("update_modal_block_set", {"u": str(user.id), "type": "command"},)
        access_token = user.organization.slack_integration.access_token
        view_id = context.get("view_id", None)
        url = (
            slack_const.SLACK_API_ROOT + slack_const.VIEWS_UPDATE
            if view_id
            else slack_const.SLACK_API_ROOT + slack_const.VIEWS_OPEN
        )
        data = {
            "view": {
                "type": "modal",
                "callback_id": slack_const.COMMAND_FORMS__SUBMIT_FORM,
                "title": {"type": "plain_text", "text": "Update Salesforce"},
                "blocks": blocks,
                # "submit": {"type": "plain_text", "text": "Update", "emoji": True},
                "private_metadata": json.dumps(context),
                "external_id": f"update_modal_block_set.{str(uuid.uuid4())}",
            },
        }
        if view_id:
            data["view_id"] = view_id
        else:
            data["trigger_id"] = context.get("trigger_id")
        slack_requests.generic_request(url, data, access_token=access_token)


def create_resource(context):
    # list of accepted commands for this fake endpoint
    user = User.objects.get(id=context.get("u"))
    if user.slack_integration:
        slack = UserSlackIntegration.objects.filter(slack_id=user.slack_integration.id).first()
        if not slack:
            data = {
                "response_type": "ephemeral",
                "text": "Sorry I cant find your managr account",
            }
        blocks = [
            block_builders.static_select(
                "Create a new...",
                [
                    *map(
                        lambda resource: block_builders.option(resource, resource),
                        slack_const.MEETING_RESOURCE_ATTACHMENT_OPTIONS,
                    )
                ],
                action_id=action_with_params(
                    slack_const.COMMAND_FORMS__PROCESS_ADD_CREATE_FORM, [f"u={str(user.id)}"]
                ),
                block_id=slack_const.ZOOM_MEETING__ATTACH_RESOURCE_SECTION,
            ),
        ]
        access_token = user.organization.slack_integration.access_token
        view_id = context.get("view_id", None)
        url = (
            slack_const.SLACK_API_ROOT + slack_const.VIEWS_UPDATE
            if view_id
            else slack_const.SLACK_API_ROOT + slack_const.VIEWS_OPEN
        )
        private_metadata = {
            "type": "command",
            **context,
        }
        data = {
            "view": {
                "type": "modal",
                "title": {"type": "plain_text", "text": "Create New"},
                "blocks": blocks,
                "private_metadata": json.dumps(private_metadata),
                "external_id": f"create_modal.{str(uuid.uuid4())}",
            },
        }
        if view_id:
            data["view_id"] = view_id
        else:
            data["trigger_id"] = context.get("trigger_id")
        slack_requests.generic_request(url, data, access_token=access_token)


def create_task(context):
    # list of accepted commands for this fake endpoint
    user = User.objects.get(id=context.get("u"))
    if user.slack_integration:
        slack = UserSlackIntegration.objects.filter(slack_id=user.slack_integration.id).first()
        if not slack:
            data = {
                "response_type": "ephemeral",
                "text": "Sorry I cant find your managr account",
            }

        access_token = user.organization.slack_integration.access_token
        view_id = context.get("view_id", None)
        url = (
            slack_const.SLACK_API_ROOT + slack_const.VIEWS_UPDATE
            if view_id
            else slack_const.SLACK_API_ROOT + slack_const.VIEWS_OPEN
        )
        data = {
            "view": {
                "type": "modal",
                "callback_id": slack_const.COMMAND_CREATE_TASK,
                "title": {"type": "plain_text", "text": "Create a Task"},
                "blocks": get_block_set("create_task_modal", context={"u": context.get("u"),},),
                "submit": {"type": "plain_text", "text": "Submit", "emoji": True},
                "private_metadata": json.dumps(context),
                "external_id": f"create_task_modal.{str(uuid.uuid4())}",
            },
        }
        if view_id:
            data["view_id"] = view_id
        else:
            data["trigger_id"] = context.get("trigger_id")
        slack_requests.generic_request(url, data, access_token=access_token)


def log_new_activity(context):
    # list of accepted commands for this fake endpoint
    user = User.objects.get(id=context.get("u"))
    if user.slack_integration:
        slack = UserSlackIntegration.objects.filter(slack_id=user.slack_integration.id).first()
        if not slack:
            data = {
                "response_type": "ephemeral",
                "text": "Sorry I cant find your managr account",
            }

        access_token = user.organization.slack_integration.access_token
        view_id = context.get("view_id", None)
        url = (
            slack_const.SLACK_API_ROOT + slack_const.VIEWS_UPDATE
            if view_id
            else slack_const.SLACK_API_ROOT + slack_const.VIEWS_OPEN
        )
        options = [
            block_builders.option("Event", "create_event_modal"),
            block_builders.option("Task", "create_task_modal"),
        ]
        blocks = [
            block_builders.static_select(
                "Type of Activity to log:",
                options,
                slack_const.COMMAND_LOG_NEW_ACTIVITY,
                block_id="selected_activity",
            )
        ]
        data = {
            "view": {
                "type": "modal",
                "title": {"type": "plain_text", "text": "Log Activity"},
                "blocks": blocks,
                "private_metadata": json.dumps(context),
            },
        }
        if view_id:
            data["view_id"] = view_id
        else:
            data["trigger_id"] = context.get("trigger_id")
        slack_requests.generic_request(url, data, access_token=access_token)


def list_tasks(context):
    ## helper to make datetime longform
    def to_date_string(date):
        if not date:
            return "n/a"
        d = datetime.strptime(date, "%Y-%m-%d")
        return d.strftime("%a, %B %d, %Y")

    user = User.objects.get(id=context.get("u"))

    if user.slack_integration:
        slack = UserSlackIntegration.objects.filter(
            slack_id=user.slack_integration.slack_id
        ).first()
        if not slack:
            return

    # Pulls tasks from Salesforce
    blocks = get_block_set("tasks_list", {"u": str(user.id)})
    access_token = user.organization.slack_integration.access_token
    data = {
        "view": {
            "type": "modal",
            "title": {"type": "plain_text", "text": "Success"},
            "blocks": blocks,
        },
    }
    view_id = context.get("view_id", None)
    url = (
        slack_const.SLACK_API_ROOT + slack_const.VIEWS_UPDATE
        if view_id
        else slack_const.SLACK_API_ROOT + slack_const.VIEWS_OPEN
    )
    if view_id:
        data["view_id"] = view_id
    else:
        data["trigger_id"] = context.get("trigger_id")
    try:
        res = slack_requests.generic_request(url, data, access_token=access_token)
        slack_requests.send_ephemeral_message(
            slack.channel, access_token, slack.slack_id, block_set=blocks
        )
        return {"response_action": "clear"}
    except Exception as e:
        logger.exception(f"Actions exception: {e}")


def get_notes_command(context):
    user = User.objects.get(id=context.get("u"))
    if user.slack_integration:
        slack = UserSlackIntegration.objects.filter(
            slack_id=user.slack_integration.slack_id
        ).first()
        if not slack:
            return
    user = slack.user
    access_token = user.organization.slack_integration.access_token
    block_context = {
        "u": str(user.id),
        "type": "command",
    }
    blocks = get_block_set("choose_opportunity", context=block_context)
    view_id = context.get("view_id", None)
    url = (
        slack_const.SLACK_API_ROOT + slack_const.VIEWS_UPDATE
        if view_id
        else slack_const.SLACK_API_ROOT + slack_const.VIEWS_OPEN
    )
    data = {
        "view": {
            "type": "modal",
            "callback_id": slack_const.GET_NOTES,
            "title": {"type": "plain_text", "text": "Choose opportunity"},
            "blocks": blocks,
            "private_metadata": json.dumps(context),
        },
    }
    if view_id:
        data["view_id"] = view_id
    else:
        data["trigger_id"] = context.get("trigger_id")
    return slack_requests.generic_request(url, data, access_token=access_token)


def schedule_meeting(context):
    user = User.objects.get(id=context.get("u"))
    if user.slack_integration:
        slack = UserSlackIntegration.objects.filter(
            slack_id=user.slack_integration.slack_id
        ).first()
        if not slack:
            return
    view_id = context.get("view_id", None)
    url = (
        slack_const.SLACK_API_ROOT + slack_const.VIEWS_UPDATE
        if view_id
        else slack_const.SLACK_API_ROOT + slack_const.VIEWS_OPEN
    )
    access_token = user.organization.slack_integration.access_token
    data = {
        "view": {
            "type": "modal",
            "callback_id": slack_const.ZOOM_MEETING__SCHEDULE_MEETING,
            "title": {"type": "plain_text", "text": "Zoom Meeting Scheduler"},
            "blocks": get_block_set("schedule_meeting_modal", context=context),
            "submit": {"type": "plain_text", "text": "Submit",},
            "private_metadata": json.dumps(context),
        },
    }
    if view_id:
        data["view_id"] = view_id
    else:
        data["trigger_id"] = context.get("trigger_id")
    slack_requests.generic_request(url, data, access_token=access_token)
    return


def add_to_sequence(context):
    user = User.objects.get(id=context.get("u"))
    if user.slack_integration:
        slack = UserSlackIntegration.objects.filter(
            slack_id=user.slack_integration.slack_id
        ).first()
        if not slack:
            return
    options = "%".join(["Contact", "Opportunity", "Account"])
    blocks = get_block_set(
        "pick_resource_modal_block_set",
        {
            "u": str(user.id),
            "options": options,
            "system": "outreach",
            "action_id": slack_const.PROCESS_SHOW_ENGAGEMENT_MODEL,
            "private_metadata": json.dumps(context),
        },
    )
    pm = {"system": "outreach"}
    access_token = user.organization.slack_integration.access_token

    view_id = context.get("view_id", None)
    url = (
        slack_const.SLACK_API_ROOT + slack_const.VIEWS_UPDATE
        if view_id
        else slack_const.SLACK_API_ROOT + slack_const.VIEWS_OPEN
    )

    data = {
        "view": {
            "type": "modal",
            "title": {"type": "plain_text", "text": "Select Object Type"},
            "blocks": blocks,
            "external_id": f"pick_resource_modal_block_set.{str(uuid.uuid4())}",
            "private_metadata": json.dumps(pm),
        },
    }
    if view_id:
        data["view_id"] = view_id
    else:
        data["trigger_id"] = context.get("trigger_id")
    slack_requests.generic_request(url, data, access_token=access_token)


def add_to_cadence(context):
    user = User.objects.get(id=context.get("u"))
    if user.slack_integration:
        slack = UserSlackIntegration.objects.filter(
            slack_id=user.slack_integration.slack_id
        ).first()
        if not slack:
            return
    options = "%".join(["Contact", "Opportunity", "Account"])
    pm = {"system": "salesloft"}
    blocks = get_block_set(
        "pick_resource_modal_block_set",
        {"u": str(user.id), "type": "command", "system": "salesloft"},
    )
    access_token = user.organization.slack_integration.access_token

    view_id = context.get("view_id", None)
    url = (
        slack_const.SLACK_API_ROOT + slack_const.VIEWS_UPDATE
        if view_id
        else slack_const.SLACK_API_ROOT + slack_const.VIEWS_OPEN
    )

    data = {
        "view": {
            "type": "modal",
            "title": {"type": "plain_text", "text": "Select Object Type"},
            "blocks": blocks,
            "external_id": f"pick_resource_modal_block_set.{str(uuid.uuid4())}",
            "private_metadata": json.dumps(pm),
        },
    }
    if view_id:
        data["view_id"] = view_id
    else:
        data["trigger_id"] = context.get("trigger_id")
    slack_requests.generic_request(url, data, access_token=access_token)


def call_recording(context):
    user = User.objects.get(id=context.get("u"))
    if user.slack_integration:
        slack = UserSlackIntegration.objects.filter(
            slack_id=user.slack_integration.slack_id
        ).first()
        if not slack:
            return
    access_token = user.organization.slack_integration.access_token

    view_id = context.get("view_id", None)
    url = (
        slack_const.SLACK_API_ROOT + slack_const.VIEWS_UPDATE
        if view_id
        else slack_const.SLACK_API_ROOT + slack_const.VIEWS_OPEN
    )
    options = "%".join(["Opportunity", "Account"])
    data = {
        "view": {
            "type": "modal",
            "title": {"type": "plain_text", "text": "Call Recording"},
            "blocks": get_block_set(
                "pick_resource_modal_block_set",
                {
                    "u": str(user.id),
                    "options": options,
                    "action_id": slack_const.GONG_CALL_RECORDING,
                },
            ),
            "external_id": f"pick_resource_modal_block_set.{str(uuid.uuid4())}",
        },
    }
    if view_id:
        data["view_id"] = view_id
    else:
        data["trigger_id"] = context.get("trigger_id")
    slack_requests.generic_request(url, data, access_token=access_token)


def get_action(action_name, context={}, *args, **kwargs):

    switcher = {
        "UPDATE_RESOURCE": update_resource,
        "CREATE_RESOURCE": create_resource,
        "LIST_TASKS": list_tasks,
        "LOG_NEW_ACTIVITY": log_new_activity,
        "GET_NOTES": get_notes_command,
        "SCHEDULE_MEETING": schedule_meeting,
        "ADD_SEQUENCE": add_to_sequence,
        "ADD_CADENCE": add_to_cadence,
        "CALL_RECORDING": call_recording,
    }
    return switcher.get(action_name)(context, *args, **kwargs)
