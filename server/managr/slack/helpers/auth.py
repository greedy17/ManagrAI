import os

from django.conf import settings

from managr.slack import constants as slack_const


def auth_headers(access_token):
    return {
        "Authorization": "Bearer " + access_token,
        "Content-Type": "application/json; charset=utf-8",
        "Accept": "application/json",
    }


def json_headers():
    return {
        "Content-Type": "application/json; charset=utf-8",
        "Accept": "application/json",
    }


class OAuthLinkBuilder:
    def __init__(self, user, redirect_uri):
        self.user = user
        self.redirect_uri = redirect_uri

    @property
    def workspace_scopes_param(self):
        return "scope=" + ",".join(slack_const.WORKSPACE_SCOPES)

    @property
    def user_scopes_param(self):
        return "user_scope=" + ",".join(slack_const.USER_SCOPES)

    @property
    def client_id_param(self):
        return "client_id=" + settings.SLACK_CLIENT_ID

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
        return slack_const.SLACK_OAUTH_AUTHORIZE_ROOT + "?" + "&".join(params)

    @property
    def user_sign_in_link(self):
        params = [
            self.client_id_param,
            self.state_param,
            self.redirect_uri_param,
            self.user_scopes_param,
            self.team_id_param,
        ]
        return slack_const.SLACK_OAUTH_AUTHORIZE_ROOT + "?" + "&".join(params)

    def link_for_type(self, link_type):
        if link_type == slack_const.WORKSPACE:
            return self.add_to_workspace_link
        return self.user_sign_in_link
