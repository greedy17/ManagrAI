import pdb
import pytz
import uuid
import json

from datetime import datetime

from django.db.models import Q

from managr.utils.sites import get_site_url
from managr.core.models import User, Notification
from managr.opportunity.models import Opportunity
from managr.zoom.models import ZoomMeeting
from managr.salesforce.models import MeetingWorkflow
from managr.salesforce import constants as sf_consts
from managr.slack import constants as slack_const
from managr.slack.helpers.utils import action_with_params, block_set, map_fields_to_type
from managr.slack.helpers import block_builders
from managr.utils.misc import snake_to_space
from managr.salesforce.routes import routes as form_routes
from managr.slack.models import OrgCustomSlackForm, OrgCustomSlackFormInstance


@block_set()
def loading_block_set(context):
    message = context.get("message", "Saving Data")
    return block_builders.section_with_accessory_block(
        f"*{message}*",
        block_builders.simple_image_block(
            "https://upload.wikimedia.org/wikipedia/commons/b/b1/Loading_icon.gif", "Loading..."
        ),
    )


@block_set()
def success_modal_block_set(context):
    message = context.get("message", ":clap: Success!")
    show_image = context.get("show_image", True)
    blocks = [block_builders.simple_section(message, "mrkdwn")]
    return blocks


@block_set()
def error_modal_block_set(context):
    message = context.get("message", ":no_entry: Ugh-Ohhhh.. We've hit a snag!")
    show_image = context.get("show_image", True)
    blocks = [block_builders.simple_section(message, "mrkdwn")]
    return blocks


@block_set()
def coming_soon_modal_block_set(context):
    blocks = [
        block_builders.simple_section(
            ":clock1: *This feature is in the works* :exclamation:", "mrkdwn"
        )
    ]
    return blocks


@block_set()
def error_message_block_set(context):
    message = context.get("message", ":no_entry: Ugh-Ohhhh.. We've hit a snag!")
    return [block_builders.simple_section(message, "mrkdwn")]

