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

from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
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

from . import constants as outreach_consts
from .cron import queue_outreach_sync
from .models import (
    OutreachAccount,
    OutreachAccountAdapter,
)
from .serializers import OutreachAccountSerializer

# Create your views here.
logger = logging.getLogger("managr")


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def get_outreach_auth_link(request):
    link = OutreachAccountAdapter.get_authorization()
    return Response({"link": link})


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def get_outreach_authentication(request):
    code = request.data.get("code", None)
    if not code:
        raise ValidationError()
    res = OutreachAccountAdapter.create_account(code, request.user.id)
    existing = OutreachAccount.objects.filter(user=request.user).first()
    if existing:
        serializer = OutreachAccountSerializer(data=res.as_dict, instance=existing)
    else:
        serializer = OutreachAccountSerializer(data=res.as_dict)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    outreach_acc = OutreachAccount.objects.filter(user=request.user).first()
    queue_outreach_sync(outreach_acc.id)
    return Response(data={"success": True})


@api_view(["delete"])
@permission_classes([permissions.IsAuthenticated])
def revoke_outreach_access_token(request):
    if hasattr(request.user, "outreach_account"):
        outreach = request.user.outreach_account
        try:
            outreach.helper_class.revoke()
        except Exception:
            # revoke token will fail if ether token is expired
            pass
        # if outreach.refresh_token_task:
        #     task = Task.objects.filter(id=outreach.refresh_token_task).first()
        #     if task:
        #         task.delete()
        # outreach.delete()

    return Response()


def redirect_from_outreach(request):
    code = request.GET.get("code", None)
    q = urlencode({"code": code, "state": "OUTREACH"})
    if not code:
        err = {"error": "there was an error"}
        err = urlencode(err)
        return redirect(f"{outreach_consts.OUTREACH_FRONTEND_REDIRECT}?{err}")
    return redirect(f"{outreach_consts.OUTREACH_FRONTEND_REDIRECT}?{q}")

