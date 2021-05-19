import os
import math
import hmac
import hashlib
from datetime import datetime
from django.conf import settings
from django.utils import timezone

from rest_framework import authentication
from rest_framework import exceptions

from managr.core.models import WebhookAuthUser
from managr.slack import constants as slack_const


class SlackWebhookAuthentication(authentication.BaseAuthentication):
    def _check_time_stamp(self, rqst):
        time_stamp = rqst.headers.get("X-Slack-Request-Timestamp", None)
        if not time_stamp:
            raise exceptions.AuthenticationFailed("Invalid token header")
        is_expired = int(time_stamp) <= math.floor(
            datetime.timestamp(timezone.now() - timezone.timedelta(minutes=5))
        )
        if is_expired:
            raise exceptions.AuthenticationFailed("Expired Request")

        return time_stamp

    def authenticate(self, request):
        time_stamp = self._check_time_stamp(request)
        slack_signature = request.headers.get("X-Slack-Signature", None)
        if not slack_signature:
            raise exceptions.AuthenticationFailed("Invalid or Missing Token")
        data = request.body.decode("utf-8")
        sig_basedstring = (f"{slack_const.SLACK_APP_VERSION}:{time_stamp}:{data}").encode("utf-8")
        my_sig = (
            slack_const.SLACK_APP_VERSION
            + "="
            + hmac.new(
                slack_const.SLACK_SIGNING_SECRET.encode("utf-8"), sig_basedstring, hashlib.sha256,
            ).hexdigest()
        )
        if hmac.compare_digest(my_sig, slack_signature):
            user = WebhookAuthUser()
            return user, None

        raise exceptions.AuthenticationFailed("Invalid Token")


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
        return "state=SLACK"

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
