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

from . import constants as gong_consts
from .models import (
    GongAuthAccount,
    GongAuthAdapter,
    GongAccount,
    GongAccountAdapter,
)
from .serializers import GongAuthSerializer, GongAccountSerializer

# Create your views here.
logger = logging.getLogger("managr")


@api_view(["GET"])
def get_gong_auth_link(request):
    link = GongAuthAdapter.get_authorization()
    return Response({"link": link})


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def get_gong_authentication(request):
    code = request.data.get("code", None)
    context = request.data.get("context", None)
    scope = request.data.get("scope", None)
    if not code:
        raise ValidationError()
    res = GongAuthAdapter.create_auth_account(code, context, scope, request.user.id)
    existing = GongAuthAccount.objects.filter(admin=request.user).first()
    if existing:
        serializer = GongAuthSerializer(data=res.as_dict, instance=existing)
    else:
        serializer = GongAuthSerializer(data=res.as_dict)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    admin_account = GongAuthAccount.objects.filter(admin=request.user).first()
    if admin_account:
        users = admin_account.helper_class.get_users()
        user_data = users.get("data")
        for user in user_data:
            user_res = GongAccountAdapter.create_account(user, admin_account.id)
            if user_res is None:
                logger.error(f"Could not create gong account for {user['email']}")
                continue
            else:
                user_existing = GongAccount.objects.filter(email=user.get("email")).first()
                if user_existing:
                    user_serializer = GongAccountSerializer(
                        data=user_res.as_dict, instance=user_existing
                    )
                else:
                    user_serializer = GongAccountSerializer(data=user_res.as_dict)
                user_serializer.is_valid(raise_exception=True)
                user_serializer.save()
    return Response(data={"success": True})


@api_view(["delete"])
@permission_classes([permissions.IsAuthenticated])
def revoke_gong_access_token(request):
    if hasattr(request.user, "gong_account"):
        gong = request.user.gong_account
        try:
            gong.helper_class.revoke()
        except Exception:
            # revoke token will fail if ether token is expired
            pass
        # if gong.refresh_token_task:
        #     task = Task.objects.filter(id=gong.refresh_token_task).first()
        #     if task:
        #         task.delete()
        # gong.delete()

    return Response()


def redirect_from_gong(request):
    code = request.GET.get("code", None)
    context = request.GET.get("context", None)
    scope = request.GET.get("scope", None)
    q = urlencode({"code": code, "scope": scope, "context": context, "state": "SALESLOFT"})
    if not code:
        err = {"error": "there was an error"}
        err = urlencode(err)
        return redirect(f"{gong_consts.SALESLOFT_FRONTEND_REDIRECT}?{err}")
    return redirect(f"{gong_consts.SALESLOFT_FRONTEND_REDIRECT}?{q}")

