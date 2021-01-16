import requests
import json
import os
import pdb
from urllib.parse import urlencode

from django.conf import settings
from managr.slack import constants as slack_const
from managr.slack.helpers import auth as slack_auth
from managr.slack.helpers.block_sets import get_block_set


def request_access_token(code, redirect_uri):
    url = slack_const.SLACK_API_ROOT + slack_const.OAUTH_V2_ACCESS
    data = {
        "code": code,
        "redirect_uri": redirect_uri,  # TODO: redirect_URI also ENV
        "client_id": settings.SLACK_CLIENT_ID,
        "client_secret": settings.SLACK_SECRET,
    }
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
    }
    return requests.post(url, data=data, headers=headers,)


def revoke_access_token(token):
    query = urlencode({"token": token})
    url = slack_const.SLACK_API_ROOT + "auth.revoke?" + query
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
    }

    return requests.post(url, headers=headers,)


def request_user_dm_channel(slack_id, access_token):
    """
    Request the Slack Channel ID for a 1:1 conversation
    between the user and the Managr app
    """
    url = slack_const.SLACK_API_ROOT + slack_const.CONVERSATIONS_OPEN
    data = {"users": slack_id}
    return requests.post(url, data=json.dumps(data), headers=slack_auth.auth_headers(access_token),)


def send_channel_message(channel, access_token, text=None, block_set=None):
    """
    Posts a message to a public channel, private channel, or DM channel.
    Initial context for block_set goes here!
    """
    url = slack_const.SLACK_API_ROOT + slack_const.POST_MESSAGE
    data = {}
    data["channel"] = channel
    if text:
        data["text"] = text
    if block_set:
        data["blocks"] = block_set
    return requests.post(url, data=json.dumps(data), headers=slack_auth.auth_headers(access_token),)


def update_channel_message(channel, message_timestamp, access_token, text=None, block_set=None):
    """
    Updates a message.
    """
    url = slack_const.SLACK_API_ROOT + slack_const.CHAT_UPDATE
    data = {}
    data["channel"] = channel
    data["ts"] = message_timestamp
    if text:
        data["text"] = text
    if block_set:
        data["blocks"] = block_set
    return requests.post(url, data=json.dumps(data), headers=slack_auth.auth_headers(access_token),)


def generic_request(url, data, access_token=None):
    return requests.post(
        url,
        data=json.dumps(data),
        headers=slack_auth.auth_headers(access_token)
        if access_token
        else slack_auth.json_headers(),
    )
