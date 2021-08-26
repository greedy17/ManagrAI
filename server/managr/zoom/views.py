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
from managr.slack.helpers.exceptions import (
    UnHandeledBlocksException,
    InvalidBlocksFormatException,
    InvalidBlocksException,
    InvalidAccessToken,
)
from managr.slack.helpers.block_sets import get_block_set
from managr.zoom.zoom_helper import constants as zoom_model_consts
from managr.zoom.zoom_helper.models import ZoomAcct, ZoomMtg
from managr.zoom.zoom_helper.exceptions import InvalidRequest
from managr.slack.models import UserSlackIntegration
from managr.salesforce.models import MeetingWorkflow
from managr.core.models import User
from .models import ZoomAuthAccount, ZoomMeeting
from .serializers import (
    ZoomAuthRefSerializer,
    ZoomAuthSerializer,
    ZoomMeetingWebhookSerializer,
    ZoomMeetingSerializer,
)
from . import constants as zoom_consts
from .background import (
    _get_past_zoom_meeting_details,
    _kick_off_slack_interaction,
    _process_confirm_compliance,
)

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
    existing = ZoomAuthAccount.objects.filter(user=request.user).first()
    if existing:
        serializer = ZoomAuthSerializer(data=res.as_dict, instance=existing)
    else:
        serializer = ZoomAuthSerializer(data=res.as_dict)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(data={"success": True})


@api_view(["delete"])
@permission_classes([permissions.IsAuthenticated])
def revoke_zoom_access_token(request):
    if hasattr(request.user, "zoom_account"):
        zoom = request.user.zoom_account
        try:
            zoom.helper_class.revoke()
        except Exception:
            # revoke token will fail if ether token is expired
            pass
        if zoom.refresh_token_task:
            task = Task.objects.filter(id=zoom.refresh_token_task).first()
            if task:
                task.delete()
        zoom.delete()

    return Response()


@api_view(["post"])
@permission_classes([permissions.AllowAny])
@authentication_classes((zoom_auth.ZoomWebhookAuthentication,))
def zoom_deauth_webhook(request):
    """
    When a user uninstalls the zoom app directly from their apps we will be notified here
    We must complete the steps provided in this document
    https://marketplace.zoom.us/docs/guides/publishing/data-compliance
    """
    event = request.data.get("event", None)
    obj = request.data.get("payload", None)
    if event == "app_deauthorized":
        # get user if exists
        zoom = ZoomAuthAccount.objects.filter(zoom_id=obj.get("user_id", None)).first()
        if not zoom:
            logger.warning(f"Did not find user in our system to deauthorize {json.dumps(obj)}")
            # emit delete event

        elif obj.get("user_data_retention", False):
            # user has authorized us to save their data
            try:
                zoom.helper_class.revoke()
            except Exception:
                # revoke token will fail if ether token is expired
                pass
            zoom.is_revoked = True
            zoom.access_token = ""
            zoom.refresh_token = ""

            if zoom.refresh_token_task:
                task = Task.objects.filter(id=zoom.refresh_token_task).first()
                if task:
                    task.delete()
            zoom.save()
        else:
            zoom.delete()

        try:
            _process_confirm_compliance.now(json.dumps(obj))
        except InvalidRequest:
            logger.exception(
                f'There was a problem informing zoom of compliance you may try this manually - {json.dumps({"event":event,"payload":obj})}, if this is in dev you may ignore this message'
            )
        return Response()

    # check for host_id


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
    logger.info({f"--ZOOM_MEETING_FROM_ZOOM event {event} payload{obj}"})
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
    allowed_commands = ["opp", "acc", "lead"]
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
        logger.exception(f"{command_params[0]}")
        if command_params[0] not in allowed_commands:
            return Response(
                data={
                    "response_type": "ephemeral",
                    "text": "Sorry I don't know that : {},only allowed{}".format(
                        command_params[0], allowed_commands
                    ),
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
        workflow = _get_past_zoom_meeting_details.now(
            str(zoom_account.user.id), meeting_uuid, original_duration, send_slack=False
        )
        if not workflow:
            return Response(data={"response_type": "ephemeral", "text": "An error occured",})
        # get meeting
        workflow.begin_communication(now=True)
        workflow = MeetingWorkflow.objects.filter(meeting__meeting_uuid=meeting_uuid).first()
        if meeting_resource and meeting_resource.lower() == "acc":
            acc = user.accounts.first()
            workflow.resource_id = str(acc.id)
            workflow.resource_type = "Account"
            workflow.save()
        elif not meeting_resource:
            workflow.resource_id = None
            workflow.resource_type = ""
            workflow.save()
        elif meeting_resource == "lead":
            l = user.owned_leads.first()
            workflow.resource_id = str(l.id)
            workflow.resource_type = "Lead"
            workflow.save()

        access_token = user.organization.slack_integration.access_token

        ts, channel = workflow.slack_interaction.split("|")
        try:
            res = slack_requests.update_channel_message(
                channel,
                ts,
                access_token,
                block_set=get_block_set(
                    "initial_meeting_interaction", context={"w": str(workflow.id)},
                ),
            )
        except InvalidBlocksException as e:
            return logger.exception(
                f"Failed To Generate Slack Workflow Interaction for user with workflow {str(workflow.id)} email {workflow.user.email} {e}"
            )
        except InvalidBlocksFormatException as e:
            return logger.exception(
                f"Failed To Generate Slack Workflow Interaction for user with workflow {str(workflow.id)} email {workflow.user.email} {e}"
            )
        except UnHandeledBlocksException as e:
            return logger.exception(
                f"Failed To Generate Slack Workflow Interaction for user with workflow {str(workflow.id)} email {workflow.user.email} {e}"
            )
        except InvalidAccessToken as e:
            return logger.exception(
                f"Failed To Generate Slack Workflow Interaction for user with workflow {str(workflow.id)} email {workflow.user.email} {e}"
            )
        workflow.slack_interaction = f"{res['ts']}|{res['channel']}"
        workflow.save()

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


@api_view(["post"])
@permission_classes([permissions.AllowAny])
@authentication_classes((zoom_auth.ZoomWebhookAuthentication,))
def zoom_recordings_webhook(request):
    event = request.data.get("event", None)
    main_payload = request.data.get("payload")
    obj = main_payload.get("object", None)
    topic = main_payload.get("topic", None)
    user = User.objects.get(zoom_account__account_id=obj["account_id"])
    if event == zoom_consts.ZOOM_RECORDING_COMPLETED:
        download_object = list(
            filter(lambda file: file["file_type"] == "MP4", obj["recording_files"])
        )[0]
        download_url = download_object["download_url"]
        try:
            res = slack_requests.send_channel_message(
                user.slack_integration.channel,
                user.organization.slack_integration.access_token,
                text="Your meeting recording is ready!",
                block_set=get_block_set(
                    "zoom_recording_blockset",
                    {"u": str(user.id), "url": download_url, "topic": topic},
                ),
            )
        except Exception as e:
            logger.warning(f"Zoom recording error: {e}")
        return Response()


@api_view(["post"])
@permission_classes([permissions.AllowAny])
@authentication_classes((slack_auth.SlackWebhookAuthentication,))
def fake_recording(request):
    slack_id = request.data.get("user_id")
    user = User.objects.get(slack_integration__slack_id=slack_id)
    topic = "test"
    download_url = "https://us06web.zoom.us/rec/webhook_download/_XTU8KwMgoJV3NkXbv3ZDdORNSBzPqneTyb-i2MO8qIVKPOtCaNwwlk5K2izyotkXE3iY2Lyz1aMINkJ.2wtE9i4dx27tqIWT/98tyKvXsqGFFYoPDz3jVW_YEA9zPaKnWu1xZ5o5tyHTwgkw-G9lDE_ggxCtBAJQ"
    try:
        res = slack_requests.send_channel_message(
            user.slack_integration.channel,
            user.organization.slack_integration.access_token,
            text="Your meeting recording is ready!",
            block_set=get_block_set(
                "zoom_recording_blockset", {"u": str(user.id), "url": download_url, "topic": topic},
            ),
        )
    except Exception as e:
        logger.warning(f"Zoom recording error: {e}")
    return Response()
