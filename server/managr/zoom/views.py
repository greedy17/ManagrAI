import logging
import requests
import json
from faker import Faker
from urllib.parse import urlencode
from datetime import datetime

from django.core.management import call_command
from django.shortcuts import render, redirect
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt, csrf_protect

from rest_framework.views import APIView
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
    api_view,
    permission_classes,
    authentication_classes,
)


from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, PermissionDenied

from background_task.models import Task
from managr.core.permissions import (
    IsOrganizationManager,
    IsSuperUser,
    IsSalesPerson,
    CanEditResourceOrReadOnly,
)

from managr.zoom.zoom_helper import auth as zoom_auth
from managr.slack.helpers import auth as slack_auth
from managr.slack.helpers import requests as slack_requests
from managr.slack.helpers.block_sets import get_block_set
from managr.zoom.zoom_helper import constants as zoom_model_consts
from managr.zoom.zoom_helper.models import ZoomAcct, ZoomMtg
from managr.slack.models import UserSlackIntegration
from .models import ZoomAuthAccount, ZoomMeeting
from .serializers import (
    ZoomAuthRefSerializer,
    ZoomAuthSerializer,
    ZoomMeetingWebhookSerializer,
    ZoomMeetingSerializer,
)
from . import constants as zoom_consts
from .background import _get_past_zoom_meeting_details, _kick_off_slack_interaction

# Create your views here.
logger = logging.getLogger("managr")


@api_view(["get"])
@permission_classes([permissions.IsAuthenticated])
def get_zoom_auth_link(request):
    link = ZoomAcct.get_authorization()
    return Response({"link": link})


@api_view(["post"])
@permission_classes([permissions.IsAuthenticated])
def get_zoom_authentication(request):
    code = request.data.get("code", None)
    if not code:
        raise ValidationError()
    res = ZoomAcct.create_account(code, request.user.id)
    if hasattr(request.user, "zoom_account"):
        zoom = request.user.zoom_account
        zoom.access_token = res.access_token
        zoom.refresh_token = res.refresh_token
        zoom.is_revoked = False
        zoom.save()
        return Response(data={"success": True})

    serializer = ZoomAuthSerializer(data=res.as_dict)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(data={"success": True})


@api_view(["delete"])
@permission_classes([permissions.IsAuthenticated])
def revoke_zoom_access_token(request):
    if hasattr(request.user, "zoom_account"):
        zoom = request.user.zoom_account
        zoom.is_revoked = True
        zoom.access_token = ""
        zoom.refresh_token = ""
        if zoom.refresh_token_task:
            task = Task.objects.filter(id=zoom.refresh_token_task).first()
            if task:
                task.delete()
        zoom.save()

    return Response(data={"message": "success"}, status=status.HTTP_204_NO_CONTENT)


def redirect_from_zoom(request):
    ## this is only for dev, since the redirect url to localhost will not work
    if settings.IN_DEV:
        code = request.GET.get("code", None)
        q = urlencode({"code": code, "state": "ZOOM"})
        if not code:
            err = {"error": "there was an error"}
            err = urlencode(err)
            return redirect(f"{zoom_model_consts.ZOOM_FRONTEND_REDIRECT}")
        return redirect(f"{zoom_model_consts.ZOOM_FRONTEND_REDIRECT}?{q}")
    else:
        return redirect(f"{zoom_model_consts.ZOOM_FRONTEND_REDIRECT}")


@api_view(["post"])
@permission_classes([permissions.AllowAny])
@authentication_classes((zoom_auth.ZoomWebhookAuthentication,))
def zoom_meetings_webhook(request):
    event = request.data.get("event", None)
    obj = request.data.get("payload", None)
    # only tracking meeting.ended
    if event == zoom_consts.MEETING_EVENT_ENDED:
        extra_obj = obj.pop("object", {})
        obj = {**obj, **extra_obj}
        host_id = obj.get("host_id", None)
        meeting_uuid = obj.get("uuid", None)
        original_duration = obj.get("duration", None)
        if not original_duration or original_duration < 0:
            original_duration = 0
        zoom_account = ZoomAuthAccount.objects.filter(zoom_id=host_id).first()
        if zoom_account and not zoom_account.is_revoked:
            # emit the process
            _get_past_zoom_meeting_details(
                str(zoom_account.user.id), meeting_uuid, original_duration
            )

    return Response()


@api_view(["post"])
@authentication_classes((slack_auth.SlackWebhookAuthentication,))
@permission_classes([permissions.AllowAny])
def init_fake_meeting(request):
    # list of accepted commands for this fake endpoint
    allowed_commands = ["opportunity", "account"]
    slack_id = request.data.get("user_id", None)
    if slack_id:
        slack = (
            UserSlackIntegration.objects.filter(slack_id=slack_id).select_related("user").first()
        )
        if not slack:
            return Response(
                data={
                    "response_type": "ephemeral",
                    "text": "Sorry I cant find your managr account",
                }
            )
    user = slack.user
    if not user.has_zoom_integration:
        return Response(
            data={"response_type": "ephemeral", "text": "Sorry I cant find your zoom account",}
        )
    host_id = user.zoom_account.zoom_id
    text = request.data.get("text", "")
    if len(text):
        command_params = text.split(" ")
    else:
        command_params = []
    meeting_resource = None
    if len(command_params):
        if command_params[0] not in allowed_commands:
            return Response(
                data={
                    "response_type": "ephemeral",
                    "text": "Sorry I don't know that option: {}".format(command_params[0]),
                }
            )
        meeting_resource = command_params[0]

    meeting_uuid = settings.ZOOM_FAKE_MEETING_UUID
    if not meeting_uuid:
        return Response(
            data={"response_type": "ephemeral", "text": "Sorry I cant find your zoom meeting",}
        )
    host_id = host_id
    meeting = ZoomMeeting.objects.filter(meeting_uuid=meeting_uuid).first()
    if meeting:
        meeting.delete()
    original_duration = None

    if not original_duration or original_duration < 0:
        original_duration = 0
    ### move all this to a background task, zoom requires response in 60s
    zoom_account = user.zoom_account

    if zoom_account and not zoom_account.is_revoked:
        # emit the process
        meeting = _get_past_zoom_meeting_details.now(
            str(zoom_account.user.id), meeting_uuid, original_duration, send_slack=False
        )
        # get meeting
        _kick_off_slack_interaction.now(str(user.id), str(meeting.id))
        meeting = ZoomMeeting.objects.filter(meeting_uuid=meeting_uuid).first()
        if meeting_resource and meeting_resource.lower() == "account":

            meeting.opportunity = None
            acc = user.accounts.first()
            meeting.linked_account_id = acc.id
            meeting.save()
        elif not meeting_resource:

            meeting.opportunity = None
            meeting.linked_account = None
            meeting.save()
        if not meeting_resource or not meeting_resource.lower() == "opportunity":
            access_token = user.organization.slack_integration.access_token
            attempts = 0
            while True:

                if not len(meeting.slack_interaction):

                    meeting = ZoomMeeting.objects.filter(meeting_uuid=meeting_uuid).first()
                    attempts += 1

                else:
                    break
            ts, channel = meeting.slack_interaction.split("|")
            res = slack_requests.update_channel_message(
                channel,
                ts,
                access_token,
                block_set=get_block_set(
                    "initial_meeting_interaction", context={"m": str(meeting.id)},
                ),
            ).json()
            meeting.slack_interaction = f"{res['ts']}|{res['channel']}"
            meeting.save()

        # if commands has a type update meeting to that type

    return Response(data="Done")


@api_view(["post"])
@authentication_classes((slack_auth.SlackWebhookAuthentication,))
@permission_classes([permissions.AllowAny])
def score_meetings(request):
    slack_id = request.data.get("user_id", None)
    if slack_id:
        slack = (
            UserSlackIntegration.objects.filter(slack_id=slack_id).select_related("user").first()
        )
        if not slack:
            return Response(
                data={
                    "response_type": "ephemeral",
                    "text": "Sorry I cant find your managr account",
                }
            )
    call_command("generatemeetingscores")

    return Response(data="Scoring Meeting...")

