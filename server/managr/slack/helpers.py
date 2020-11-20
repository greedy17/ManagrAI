import requests
import json
import os

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


class OAuthLinkBuilder:
    def __init__(self, user, redirect_uri):
        self.user = user
        self.redirect_uri = redirect_uri

    @property
    def workspace_scopes_param(self):
        return "scope=" + ",".join(slack_const.WORKSPACE_SCOPES)

    @property
    def user_scopes_param(self):
        return "scope=" + ",".join(slack_const.USER_SCOPES)

    @property
    def client_id_param(self):
        return os.environ.get("SLACK_CLIENT_ID")

    # return 'client_id=' + this.clientID

    @property
    def redirect_uri_param(self):
        return "redirect_uri=" + self.redirect_uri

    @property
    def state_param(self):
        return "state=" + str(self.user.id)

    @property
    def team_id_param(self):
        return "team=" + str(self.user.organization.slack_integration.team_id)

    @property
    def add_to_workspace_link(self):
        params = [
            self.client_id_param,
            self.state_param,
            self.redirect_uri_param,
            self.workspace_scopes_param,
        ]
        return slack_const.SLAC_OAUTH_ROOT + "?" + "&".join(params)

    @property
    def user_sign_in_link(self):
        params = [
            self.client_id_param,
            self.state_param,
            self.redirect_uri_param,
            self.user_scopes_param,
            self.team_id_param,
        ]
        return slack_const.SLAC_OAUTH_ROOT + "?" + "&".join(params)

    def link_for_type(self, link_type):
        if link_type is slack_const.WORKSPACE:
            return self.add_to_workspace_link
        return self.user_sign_in_link
