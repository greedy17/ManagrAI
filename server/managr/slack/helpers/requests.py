import requests
import json
import logging
import os
import pdb
from urllib.parse import urlencode
from requests.exceptions import HTTPError
from django.conf import settings

from managr.slack import constants as slack_const
from managr.slack.helpers import auth as slack_auth

from managr.slack.helpers.exceptions import CustomAPIException

logger = logging.getLogger("managr")


def _handle_response(response, fn_name=None, blocks=[]):
    if not hasattr(response, "status_code"):
        raise ValueError

    else:
        status_code = response.status_code
        try:
            res_data = response.json()
        except json.decoder.JSONDecodeError:
            # one slack request (see generic requests) does not return json
            return response.text

        if not res_data.get("ok"):
            error_code = response.status_code
            error_param = res_data.get("error")
            if res_data.get("response_metadata", None):
                error_message = res_data.get("response_metadata", {}).get("messages")
            elif res_data.get("error", None):
                error_message = res_data.get("error")
            else:
                error_message = response.text

            kwargs = {
                "status_code": status_code,
                "error_code": error_code,
                "error_param": error_param,
                "error_message": error_message,
            }
            try:
                CustomAPIException(HTTPError(kwargs), fn_name, blocks=blocks)
            except Exception as e:
                if settings.SLACK_ERROR_WEBHOOK:
                    try:
                        generic_request(
                            slack_const.SLACK_ERROR_WEBHOOK, {"text": f"An error occured {e}"}
                        )
                    except Exception as fail_safe_error:
                        logger.exception(
                            f"Failed to send slack error to error channel {fail_safe_error}"
                        )
                        pass
                raise e

        return res_data


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


def send_channel_message(channel, access_token, text="Managr", block_set=[]):
    """
    Posts a message to a DM channel - we do not have chat scope anymore this will only work for dms.
    Initial context for block_set goes here!
    **Channel Id required to send DM's or Channel
    """
    url = slack_const.SLACK_API_ROOT + slack_const.POST_MESSAGE
    data = {}
    data["channel"] = channel
    data["text"] = text
    data["blocks"] = block_set

    res = requests.post(url, data=json.dumps(data), headers=slack_auth.auth_headers(access_token),)
    return _handle_response(res, blocks=block_set)


def publish_view(slack_id, access_token, view):
    """
    Publishes a view to the user's home tab
    slack_id: user slack id
    """
    url = slack_const.SLACK_API_ROOT + slack_const.VIEWS_PUBLISH
    data = {}
    data["user_id"] = slack_id
    data["view"] = view

    res = requests.post(url, data=json.dumps(data), headers=slack_auth.auth_headers(access_token),)
    return _handle_response(res, data)


def send_ephemeral_message(channel, access_token, slack_id, text="Managr", block_set=[]):
    """
    Posts a message to DM channel.
    *Channel and User are required for ephemeral messages
    """
    url = slack_const.SLACK_API_ROOT + slack_const.POST_EPHEMERAL
    data = {}
    data["channel"] = channel
    data["text"] = text
    data["blocks"] = block_set
    data["user"] = slack_id

    res = requests.post(url, data=json.dumps(data), headers=slack_auth.auth_headers(access_token),)
    return _handle_response(res, blocks=block_set)


def update_channel_message(channel, message_timestamp, access_token, text="Managr", block_set=[]):
    """
    Updates a message in DM.
    """
    url = slack_const.SLACK_API_ROOT + slack_const.CHAT_UPDATE
    data = {}
    data["channel"] = channel
    data["ts"] = message_timestamp

    data["text"] = text
    data["blocks"] = block_set
    res = requests.post(url, data=json.dumps(data), headers=slack_auth.auth_headers(access_token),)
    return _handle_response(res, blocks=block_set if block_set else [])


def generic_request(url, data, access_token=None):
    original_data = data
    res = requests.post(
        url,
        data=json.dumps(data),
        headers=slack_auth.auth_headers(access_token)
        if access_token
        else slack_auth.json_headers(),
    )
    blocks = original_data.get("view", {}).get("blocks", []) if data else []
    return _handle_response(res, blocks=blocks)


def list_channels(access_token, limit=25, cursor=None, types=[]):
    q = dict(exclude_archived=True)
    if len(types):
        q["types"] = ",".join(types)
    url = slack_const.SLACK_API_ROOT + slack_const.CONVERSATIONS_LIST
    if limit:
        q["limit"] = limit
    if cursor:
        q["cursor"] = cursor

    url += "?" + urlencode(q)
    return generic_request(url, None, access_token=access_token)


def list_users(access_token, cursor=None):
    url = slack_const.SLACK_API_ROOT + slack_const.USERS_LIST
    if cursor:
        url += "?" + urlencode({"cursor": cursor})
    res = requests.post(url, headers=slack_auth.auth_headers(access_token))
    return _handle_response(res)


def invite_channel(access_token, channel, users):
    q = dict()
    q["channel"] = channel
    q["users"] = users
    url = slack_const.SLACK_API_ROOT + slack_const.CONVERSATIONS_INVITE
    url += "?" + urlencode(q)
    res = requests.post(url, headers=slack_auth.encode_header(access_token))
    return res


def create_channel(access_token, name, team_id, user, is_private=True):
    q = dict()
    q["name"] = name
    q["is_private"] = is_private
    q["team_id"] = team_id
    url = slack_const.SLACK_API_ROOT + slack_const.CONVERSATIONS_CREATE
    url += "?" + urlencode(q)
    try:
        channel_res = requests.post(url, headers=slack_auth.encode_header(access_token)).json()
        if channel_res["ok"] is True:
            user_invite_res = invite_channel(
                access_token, channel_res.get("channel").get("id"), user
            )
            return _handle_response(user_invite_res)
        else:
            return channel_res
    except Exception as e:
        print(e)


def list_user_channels(access_token, user, limit=100, cursor=None, types=[]):
    q = dict(exclude_archived=True)
    q["user"] = user
    if len(types):
        q["types"] = ",".join(types)
    url = slack_const.SLACK_API_ROOT + slack_const.USERS_CONVERSATIONS
    if limit:
        q["limit"] = limit
    if cursor:
        q["cursor"] = cursor

    url += "?" + urlencode(q)
    res = requests.get(url, headers=slack_auth.encode_header(access_token)).json()
    return generic_request(url, None, access_token=access_token)


def get_channel_info(access_token, channel_id):
    q = dict(channel=channel_id)
    url = slack_const.SLACK_API_ROOT + slack_const.CONVERSATIONS_INFO
    url += "?" + urlencode(q)
    res = requests.get(url, headers=slack_auth.encode_header(access_token))
    return _handle_response(res)

