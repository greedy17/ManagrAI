import logging
from urllib.parse import urlencode
from django.shortcuts import redirect
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework import permissions
from rest_framework.decorators import (
    api_view,
    permission_classes,
)
from . import constants as gong_consts
from .models import (
    GongAuthAccount,
    GongAuthAdapter,
)
from .serializers import GongAuthSerializer
from .cron import queue_gong_sync

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
    if not code:
        raise ValidationError()
    res = GongAuthAdapter.create_auth_account(code, request.user.id)
    existing = GongAuthAccount.objects.filter(admin=request.user).first()
    if existing:
        serializer = GongAuthSerializer(data=res.as_dict, instance=existing)
    else:
        serializer = GongAuthSerializer(data=res.as_dict)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    admin_account = GongAuthAccount.objects.filter(admin=request.user).first()
    if admin_account:
        queue_gong_sync(str(admin_account.id))
    return Response(data={"success": True})


@api_view(["delete"])
@permission_classes([permissions.IsAuthenticated])
def revoke_gong_access_token(request):
    if hasattr(request.user, "gong_account"):
        gong = request.user.gong_admin
        try:
            gong.helper_class.revoke()
        except Exception:
            pass
    return Response()


def redirect_from_gong(request):
    ## this is only for dev, since the redirect url to localhost will not work
    code = request.GET.get("code", None)
    q = urlencode({"code": code, "state": "GONG"})
    if not code:
        err = {"error": "there was an error"}
        err = urlencode(err)
        return redirect(f"{gong_consts.GONG_FRONTEND_REDIRECT}?{err}")
    return redirect(f"{gong_consts.GONG_FRONTEND_REDIRECT}?{q}")

