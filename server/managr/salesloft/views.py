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

from . import constants as salesloft_consts
from .models import (
    SalesloftAuthAccount,
    SalesloftAuthAdapter,
)
from .helpers.class_functions import process_account
from .serializers import SalesloftAuthSerializer
from .cron import queue_account_sl_syncs

# Create your views here.
logger = logging.getLogger("managr")


@api_view(["GET"])
def get_salesloft_auth_link(request):
    link = SalesloftAuthAdapter.get_authorization()
    return Response({"link": link})


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def get_salesloft_authentication(request):
    code = request.data.get("code", None)
    context = request.data.get("context", None)
    scope = request.data.get("scope", None)
    if not code:
        raise ValidationError()
    res = SalesloftAuthAdapter.create_auth_account(code, context, scope, request.user.id)
    existing = SalesloftAuthAccount.objects.filter(admin=request.user).first()
    if existing:
        serializer = SalesloftAuthSerializer(data=res.as_dict, instance=existing)
    else:
        serializer = SalesloftAuthSerializer(data=res.as_dict)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    admin_account = SalesloftAuthAccount.objects.filter(admin=request.user).first()
    me_info = admin_account.helper_class.get_me()
    process_account(me_info["data"], str(admin_account.id))
    queue_account_sl_syncs(str(admin_account.id))
    return Response(data={"success": True})


@api_view(["delete"])
@permission_classes([permissions.IsAuthenticated])
def revoke_salesloft_access_token(request):
    if hasattr(request.user, "salesloft_account"):
        salesloft = request.user.salesloft_account
        try:
            salesloft.helper_class.revoke()
        except Exception:
            pass
    return Response()


def redirect_from_salesloft(request):
    code = request.GET.get("code", None)
    context = request.GET.get("context", None)
    scope = request.GET.get("scope", None)
    q = urlencode({"code": code, "scope": scope, "context": context, "state": "SALESLOFT"})
    if not code:
        err = {"error": "there was an error"}
        err = urlencode(err)
        return redirect(f"{salesloft_consts.SALESLOFT_FRONTEND_REDIRECT}?{err}")
    return redirect(f"{salesloft_consts.SALESLOFT_FRONTEND_REDIRECT}?{q}")

