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
from rest_framework.decorators import (
    action,
    api_view,
    permission_classes,
)
from rest_framework.exceptions import ValidationError, APIException
from rest_framework.response import Response

from managr.slack import constants as slack_const


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def slack_test_message(request):
    """_"""
    organization_slack = request.user.organization.slack_integration
    is_user_test = request.data.get("is_user_test", None)

    if is_user_test is None:
        raise ValidationError("missing data.is_user_test")

    if is_user_test:
        # send DM to requesting user
        user_slack = request.user.slack_integration
        if not user_slack.channel:
            url = slack_const.SLACK_API_ROOT + slack_const.CONVERSATIONS_OPEN
            data = {"users": request.user.slack_integration.slack_id}
            response = requests.post(
                url,
                data=json.dumps(data),
                headers={
                    "Authorization": "Bearer " + organization_slack.access_token,
                    "Content-Type": "application/json; charset=utf-8",
                    "Accept": "application/json",
                },
            )
            # save channel id to slack integration
            channel = response.json().get("channel").get("id")
            user_slack.channel = channel
            user_slack.save()

        # DM user
        url = slack_const.SLACK_API_ROOT + slack_const.POST_MESSAGE
        data = {
            "channel": user_slack.channel,
            "text": "Testing, testing... 1, 2. Hello, Friend!",
        }
        response = requests.post(
            url,
            data=json.dumps(data),
            headers={
                "Authorization": "Bearer " + organization_slack.access_token,
                "Content-Type": "application/json; charset=utf-8",
                "Accept": "application/json",
            },
        )
        return Response(status=status.HTTP_204_NO_CONTENT)

    # send message to standard channel
    data = {"text": "Testing, testing... 1, 2. Hello, World!"}
    requests.post(
        organization_slack.incoming_webhook.get("url"),
        data=json.dumps(data),
        headers={
            "Content-Type": "application/json; charset=utf-8",
            "Accept": "application/json",
        },
    )
    return Response(status=status.HTTP_204_NO_CONTENT)
