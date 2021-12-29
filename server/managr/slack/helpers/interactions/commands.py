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

        url = slack_const.SLACK_API_ROOT + slack_const.VIEWS_UPDATE
        data = {
            "view_id": str(context.get("view_id")),
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
        logger.info(f"BLOCKS FROM UPDATE --{data}")
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
                "Pick a resource to create",
                [
                    *map(
                        lambda resource: block_builders.option(resource, resource),
                        slack_const.MEETING_RESOURCE_ATTACHMENT_OPTIONS,
                    )
                ],
                action_id="CREATE",
                block_id=slack_const.ZOOM_MEETING__ATTACH_RESOURCE_SECTION,
            ),
        ]
        access_token = user.organization.slack_integration.access_token
        url = slack_const.SLACK_API_ROOT + slack_const.VIEWS_UPDATE
        data = {
            "view_id": str(context.get("view_id")),
            "view": {
                "type": "modal",
                "callback_id": slack_const.COMMAND_FORMS__SUBMIT_FORM,
                "title": {"type": "plain_text", "text": f"Create Resource"},
                "blocks": blocks,
                "submit": {"type": "plain_text", "text": "Create", "emoji": True},
                "external_id": f"create_modal.{str(uuid.uuid4())}",
            },
        }

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
    url = slack_const.SLACK_API_ROOT + slack_const.VIEWS_UPDATE
    success_blocks = block_builders.simple_section("Successfully got tasks for today")
    data = {
        "view_id": str(context.get("view_id")),
        "view": {
            "type": "modal",
            "title": {"type": "plain_text", "text": "Success"},
            "blocks": [success_blocks],
        },
    }
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
    url = slack_const.SLACK_API_ROOT + slack_const.VIEWS_UPDATE
    user = slack.user
    access_token = user.organization.slack_integration.access_token
    block_context = {
        "u": str(user.id),
        "type": "command",
    }
    blocks = get_block_set("choose_opportunity", context=block_context)
    data = {
        "view_id": str(context.get("view_id")),
        "view": {
            "type": "modal",
            "callback_id": slack_const.GET_NOTES,
            "title": {"type": "plain_text", "text": "Choose opportunity"},
            "blocks": blocks,
            "private_metadata": json.dumps(context),
        },
    }
    return slack_requests.generic_request(url, data, access_token=access_token)


def schedule_meeting(context):
    user = User.objects.get(id=context.get("u"))
    if user.slack_integration:
        slack = UserSlackIntegration.objects.filter(
            slack_id=user.slack_integration.slack_id
        ).first()
        if not slack:
            return
    url = slack_const.SLACK_API_ROOT + slack_const.VIEWS_UPDATE
    access_token = user.organization.slack_integration.access_token
    data = {
        "view_id": str(context.get("view_id")),
        "view": {
            "type": "modal",
            "callback_id": slack_const.ZOOM_MEETING__SCHEDULE_MEETING,
            "title": {"type": "plain_text", "text": "Zoom Meeting Scheduler"},
            "blocks": get_block_set("schedule_meeting_modal", context=context),
            "submit": {"type": "plain_text", "text": "Submit",},
            "private_metadata": json.dumps(context),
        },
    }
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
    blocks = get_block_set(
        "select_account", {"u": str(user.id), "type": "command", "system": "outreach"},
    )
    access_token = user.organization.slack_integration.access_token

    url = slack_const.SLACK_API_ROOT + slack_const.VIEWS_UPDATE
    private_metadata = {
        "resource_type": "Account",
    }

    data = {
        "view_id": str(context.get("view_id")),
        "view": {
            "type": "modal",
            "callback_id": slack_const.ADD_TO_SEQUENCE,
            "title": {"type": "plain_text", "text": "Select Account"},
            "blocks": blocks,
            "private_metadata": json.dumps(private_metadata),
        },
    }
    slack_requests.generic_request(url, data, access_token=access_token)


def add_to_cadence(context):
    user = User.objects.get(id=context.get("u"))
    if user.slack_integration:
        slack = UserSlackIntegration.objects.filter(
            slack_id=user.slack_integration.slack_id
        ).first()
        if not slack:
            return
    blocks = get_block_set(
        "select_account", {"u": str(user.id), "type": "command", "system": "salesloft"},
    )
    access_token = user.organization.slack_integration.access_token

    url = slack_const.SLACK_API_ROOT + slack_const.VIEWS_UPDATE
    private_metadata = {
        "resource_type": "Account",
    }

    data = {
        "view_id": str(context.get("view_id")),
        "view": {
            "type": "modal",
            "callback_id": slack_const.ADD_TO_CADENCE,
            "title": {"type": "plain_text", "text": "Select Account"},
            "blocks": blocks,
            "private_metadata": json.dumps(private_metadata),
        },
    }
    slack_requests.generic_request(url, data, access_token=access_token)


def get_action(action_name, context={}, *args, **kwargs):

    switcher = {
        "UPDATE_RESOURCE": update_resource,
        "CREATE_RESOURCE": create_resource,
        "LIST_TASKS": list_tasks,
        "GET_NOTES": get_notes_command,
        "SCHEDULE_MEETING": schedule_meeting,
        "ADD_SEQUENCE": add_to_sequence,
        "ADD_CADENCE": add_to_cadence,
    }
    return switcher.get(action_name)(context, *args, **kwargs)
