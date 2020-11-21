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
from managr.core.serializers import UserSerializer
from .models import OrganizationSlackIntegration, UserSlackIntegration


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
        data = response.json()
        # NOTE:
        # Only AddToWorkspace yields tokenType == 'bot'.
        # Both AddToWorkspace and UserSignIn yield data.authedUser, and in both cases
        # the user needs to integrate slack.
        # Therefore user slack integration can and should take place regardless.
        if data.get("token_type") == slack_const.TOKEN_TYPE_BOT:
            scope = data.get("scope")
            team_name = data.get("team").get("name")
            team_id = data.get("team").get("id")
            bot_user_id = data.get("bot_user_id")
            access_token = data.get("access_token")
            incoming_webhook = data.get("incoming_webhook")
            enterprise = data.get("enterprise")
            integration = OrganizationSlackIntegration.objects.create(
                organization=request.user.organization,
                scope=scope,
                team_name=team_name,
                team_id=team_id,
                bot_user_id=bot_user_id,
                access_token=access_token,
                incoming_webhook=incoming_webhook,
                enterprise=enterprise,
            )
        else:
            team_id = data.get("team").get("id")
            if team_id != request.user.organization.slack_integration.team_id:
                raise ValidationError(
                    "You signed into the wrong Slack workspace, please try again."
                )
        slack_id = data.get("authed_user").get("id")
        UserSlackIntegration.objects.create(user=request.user, slack_id=slack_id)
        # return serialized user because client-side needs updated slackRef(s)
        return Response(
            data=UserSerializer(request.user).data, status=status.HTTP_200_OK
        )

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
