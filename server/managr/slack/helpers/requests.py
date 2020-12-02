import requests
import json
import os

from managr.slack import constants as slack_const
from managr.slack.helpers import auth as slack_auth
from managr.slack.helpers.blocks import get_block_set
import pdb


def request_access_token(code, redirect_uri):
    url = slack_const.SLACK_API_ROOT + slack_const.OAUTH_V2_ACCESS
    data = {
        "code": code,
        "redirect_uri": redirect_uri,  # TODO: redirect_URI also ENV
        "client_id": os.environ.get("SLACK_CLIENT_ID"),
        "client_secret": os.environ.get("SLACK_SECRET"),
    }
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
    }
    return requests.post(
        url,
        data=data,
        headers=headers,
    )


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
        headers=slack_auth.auth_headers(access_token),
    )


def dm_user(channel, access_token, text=None, block_set=None):
    url = slack_const.SLACK_API_ROOT + slack_const.POST_MESSAGE
    data = {}
    data["channel"] = channel
    if text:
        data["text"] = text
    if block_set:
        data["blocks"] = get_block_set(block_set)
    return requests.post(
        url,
        data=json.dumps(data),
        headers=slack_auth.auth_headers(access_token),
    )


def generic_request(url, data, access_token=None):
    return requests.post(
        url,
        data=json.dumps(data),
        headers=slack_auth.auth_headers(access_token)
        if access_token
        else slack_auth.json_headers(),
    )
