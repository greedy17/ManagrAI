import requests
import json

from rest_framework import (
    authentication,
    filters,
    permissions,
    generics,
    mixins,
    status,
    views,
    viewsets,
)
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError, APIException
from rest_framework.response import Response

from managr.slack import constants as slack_const
from managr.slack import helpers as slack_helpers
import pdb

# TODO add action: get access token


class SlackViewSet(
    viewsets.GenericViewSet,
):
    @action(
        methods=["post"],
        permission_classes=[permissions.IsAuthenticated],
        detail=False,
        url_path="get-oauth-link",
    )
    def get_oauth_link(self, request, *args, **kwargs):
        redirect_uri = request.data.get("redirect_uri", None)
        link_type = request.data.get("link_type", None)
        if redirect_uri is None:
            raise ValidationError("Missing data.redirect_uri")
        if link_type is None:
            raise ValidationError("Missing data.link_type")
        if link_type not in slack_const.OAUTH_LINK_TYPES:
            raise ValidationError("Invalid link type")
        t = slack_helpers.OAuthLinkBuilder(request.user, redirect_uri)
        data = {
            "link": slack_helpers.OAuthLinkBuilder(
                request.user, redirect_uri
            ).link_for_type(link_type)
        }
        return Response(data=data, status=status.HTTP_200_OK)

    @action(
        methods=["post"],
        permission_classes=[permissions.IsAuthenticated],
        detail=False,
        url_path="generate-access-token",
    )
    def generate_access_token(self, request, *args, **kwargs):
        code = request.data.get("code", None)
        redirect_uri = request.data.get("redirect_uri", None)
        if code is None:
            raise ValidationError("Missing data.code")
        if redirect_uri is None:
            raise ValidationError("Missing data.redirect_uri")
        response = slack_helpers.request_access_token(code, redirect_uri)
        # here depending on token_type (bot or user) generate slack_integration
        pdb.set_trace()

        # return serialized user because client-side needs updated slackRef(s)
        return Response(data=data, status=status.HTTP_200_OK)

    @action(
        methods=["get"],
        permission_classes=[permissions.IsAuthenticated],
        detail=False,
        url_path="test-channel",
    )
    def test_channel(self, request, *args, **kwargs):
        """
        Interact with the SlackAPI to trigger a test message in the Organization's
        default Slack Channel for the Managr app
        """

        organization_slack = request.user.organization.slack_integration
        url = organization_slack.incoming_webhook.get("url")
        data = {"text": "Testing, testing... 1, 2. Hello, World!"}

        requests.post(
            url,
            data=json.dumps(data),
            headers={
                "Content-Type": "application/json; charset=utf-8",
                "Accept": "application/json",
            },
        )
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=["get"],
        permission_classes=[permissions.IsAuthenticated],
        detail=False,
        url_path="test-dm",
    )
    def test_DM(self, request, *args, **kwargs):
        """
        Interact with the SlackAPI to trigger a test direct message for the
        requesting user
        """
        user = request.user
        user_slack = user.slack_integration
        access_token = user.organization.slack_integration.access_token

        if not user_slack.channel:
            # request the Slack Channel ID to DM this user
            response = slack_helpers.request_user_dm_channel(
                user_slack.slack_id, access_token
            )
            # save Slack Channel ID
            channel = response.json().get("channel").get("id")
            user_slack.channel = channel
            user_slack.save()

        # DM user
        text = "Testing, testing... 1, 2. Hello, Friend!"
        slack_helpers.dm_user(user_slack.channel, text, access_token)
        return Response(status=status.HTTP_204_NO_CONTENT)
