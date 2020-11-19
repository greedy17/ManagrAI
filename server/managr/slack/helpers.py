import requests
import json
from managr.slack import constants as slack_const


def get_headers(access_token):
    return {
        "Authorization": "Bearer " + access_token,
        "Content-Type": "application/json; charset=utf-8",
        "Accept": "application/json",
    }


def request_user_dm_channel(slack_id, access_token):
    """
    Request the Slack Channel ID for a 1:1 conversation
    between the user and the Managr app
    """
    url = slack_const.SLACK_API_ROOT + slack_const.CONVERSATIONS_OPEN
    data = {"users": slack_id}
    return requests.post(
        url,
        data=json.dumps(data),
        headers=get_headers(access_token),
    )


def dm_user(channel, text, access_token):
    url = slack_const.SLACK_API_ROOT + slack_const.POST_MESSAGE
    data = {
        "channel": channel,
        "text": text,
    }
    return requests.post(
        url,
        data=json.dumps(data),
        headers=get_headers(access_token),
    )
