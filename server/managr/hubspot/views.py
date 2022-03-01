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

from . import constants as hubspot_consts

# from .cron import queue_hubspot_sync
from .models import HubspotAuthAccount
from .adapter.models import HubspotAuthAccountAdapter

from .serializers import HubspotAuthAccountSerializer

# Create your views here.
logger = logging.getLogger("managr")


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def get_hubspot_auth_link(request):
    link = HubspotAuthAccountAdapter.get_authorization()
    print(f"AUTH LINK: {link}")
    return Response({"link": link})


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def get_hubspot_authentication(request):
    code = request.data.get("code", None)
    if not code:
        raise ValidationError()
    res = HubspotAuthAccountAdapter.create_account(code, request.user.id)
    existing = HubspotAuthAccount.objects.filter(user=request.user).first()
    if existing:
        serializer = HubspotAuthAccountSerializer(data=res.as_dict, instance=existing)
    else:
        serializer = HubspotAuthAccountSerializer(data=res.as_dict)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    hubspot_acc = HubspotAuthAccount.objects.filter(user=request.user).first()
    return Response(data={"success": True})


@api_view(["delete"])
@permission_classes([permissions.IsAuthenticated])
def revoke_hubspot_access_token(request):
    if hasattr(request.user, "hubspot_account"):
        hubspot = request.user.hubspot_account
        try:
            hubspot.helper_class.revoke()
        except Exception:
            # revoke token will fail if ether token is expired
            pass
        # if hubspot.refresh_token_task:
        #     task = Task.objects.filter(id=hubspot.refresh_token_task).first()
        #     if task:
        #         task.delete()
        # hubspot.delete()

    return Response()


def redirect_from_hubspot(request):
    code = request.GET.get("code", None)
    q = urlencode({"code": code, "state": "HUBSPOT"})
    if not code:
        err = {"error": "there was an error"}
        err = urlencode(err)
        return redirect(f"{hubspot_consts.HUBSPOT_FRONTEND_REDIRECT}?{err}")
    return redirect(f"{hubspot_consts.HUBSPOT_FRONTEND_REDIRECT}?{q}")

