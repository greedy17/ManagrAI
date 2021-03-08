import json

from managr.zoom.models import ZoomMeeting
from managr.slack import constants as slack_const
from managr.slack.helpers import requests as slack_requests
from managr.slack.helpers.utils import action_with_params, NO_OP, processor
from managr.slack.helpers.block_sets import get_block_set


@processor()
def process_close_edit_meeting_contact(payload, context):
    # private_meta = json.loads(context.get("private_metadata"))
    return  # get_block_set("show_meeting_contacts", {"m": private_meta.get("m")})


def handle_view_closed(payload):

    switcher = {
        slack_const.ZOOM_MEETING__EDIT_CONTACT: process_close_edit_meeting_contact,
    }
    view = payload["view"]
    callback_id = payload["view"]["callback_id"]
    return switcher.get(callback_id, NO_OP)(payload, view)
