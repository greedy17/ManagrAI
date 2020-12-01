from managr.slack import constants as slack_const
from managr.slack.helpers import requests as slack_requests
from managr.slack.helpers.blocks import get_block_set
from managr.slack.models import UserSlackIntegration
import pdb


def wip(payload):
    # TODO: somehow need to keep track of what lead etc (i.e. STATE across interactions)
    # such as with values (i.e. button value)
    # submit next UI
    url = payload["response_url"]
    data = {
        "blocks": get_block_set("test"),
    }
    res = slack_requests.generic_request(url, data)
    print("-=-=-=-=--=-")
    print(res.status_code)
    print(res.json())
    return res


def handle_block_actions(payload):
    switcher = {
        slack_const.ZOOM_MEETING__GREAT: wip,
        slack_const.ZOOM_MEETING__NOT_WELL: wip,
    }
    action_id = payload["actions"][0]["action_id"]

    return switcher.get(action_id)(payload)


def handle_interaction(payload):
    switcher = {
        slack_const.BLOCK_ACTIONS: handle_block_actions,
    }
    return switcher.get(payload["type"])(payload)
