import logging
from faker import Faker
from urllib.parse import urlencode

from django.shortcuts import redirect

from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework import permissions
from rest_framework.decorators import (
    api_view,
    permission_classes,
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
    try:
        serializer.is_valid(raise_exception=True)
        serializer.save()
    except Exception as e:
        logger.exception(f"HUBSPOT ACCOUNT CREATION ERROR: {e}")
    request.user.crm = "HUBSPOT"
    request.user.save()
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
        hubspot.delete()
        request.user.crm = None
        request.user.save()
    return Response()


def redirect_from_hubspot(request):
    code = request.GET.get("code", None)
    q = urlencode({"code": code, "state": "HUBSPOT"})
    if not code:
        err = {"error": "there was an error"}
        err = urlencode(err)
        return redirect(f"{hubspot_consts.HUBSPOT_FRONTEND_REDIRECT}?{err}")
    return redirect(f"{hubspot_consts.HUBSPOT_FRONTEND_REDIRECT}?{q}")

