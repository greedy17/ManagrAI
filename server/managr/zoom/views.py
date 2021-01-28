import logging
import requests
import json
from faker import Faker
from urllib.parse import urlencode
from datetime import datetime

from django.core.management import call_command
from django.shortcuts import render, redirect
from django.conf import settings
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

from managr.core.permissions import (
    IsOrganizationManager,
    IsSuperUser,
    IsSalesPerson,
    CanEditResourceOrReadOnly,
)

from managr.zoom.zoom_helper import auth as zoom_auth
from managr.zoom.zoom_helper import constants as zoom_model_consts
from managr.zoom.zoom_helper.models import ZoomAcct, ZoomMtg
from .models import ZoomAuthAccount, ZoomMeeting
from .serializers import (
    ZoomAuthRefSerializer,
    ZoomAuthSerializer,
    ZoomMeetingWebhookSerializer,
    ZoomMeetingSerializer,
)
from . import constants as zoom_consts
from .background import _get_past_zoom_meeting_details

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
    # for v1 only tracking meeting.ended
    if event == zoom_consts.MEETING_EVENT_ENDED:
        extra_obj = obj.pop("object", {})
        obj = {**obj, **extra_obj}
        host_id = obj.get("host_id", None)
        meeting_uuid = obj.get("uuid", None)
        original_duration = obj.get("duration", None)
        print(meeting_uuid)
        if not original_duration or original_duration < 0:
            original_duration = 0
        ### move all this to a background task, zoom requires response in 60s
        zoom_account = ZoomAuthAccount.objects.filter(zoom_id=host_id).first()

        if zoom_account and not zoom_account.is_revoked:
            # emit the process
            _get_past_zoom_meeting_details(
                str(zoom_account.user.id), meeting_uuid, original_duration
            )

    return Response()
