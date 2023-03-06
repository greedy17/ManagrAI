import logging
from urllib.parse import urlencode
from django.shortcuts import redirect
from django.utils import timezone
from django.conf import settings
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework import permissions
from rest_framework.decorators import (
    api_view,
    permission_classes,
)
from managr.hubspot.tasks import emit_generate_hs_form_template

from . import constants as hubspot_consts
from managr.core.background import _process_change_team_lead

# from .cron import queue_hubspot_sync
from .models import HubspotAuthAccount
from .adapter.models import HubspotAuthAccountAdapter
from .tasks import emit_gen_next_hubspot_sync, emit_gen_next_hubspot_field_sync
from .serializers import HubspotAuthAccountSerializer
from managr.hubspot.tasks import emit_generate_team_form_templates

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
    user = request.user
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
        logger.exception(f"HUBSPOT ACCOUNT CREATION ERROR: {e}\n RES: {res}")
        return Response(data={"success": False})
    if serializer.instance:
        user.crm = "HUBSPOT"
        user.save()
        operations = [
            *serializer.instance.field_sync_opts,
        ]
        scheduled_time = timezone.now()
        formatted_time = scheduled_time.strftime("%Y-%m-%dT%H:%M%Z")
        emit_gen_next_hubspot_field_sync(str(user.id), operations, formatted_time)
        # generate forms
        if serializer.instance.user.is_admin:
            form_check = user.team.team_forms.all()
            schedule = (
                (timezone.now() + timezone.timedelta(minutes=5))
                if len(form_check) > 0
                else timezone.now()
            )
            if settings.IN_DEV:
                schedule = timezone.now() + timezone.timedelta(minutes=2)
            emit_generate_hs_form_template(str(res.user), schedule=schedule)
        if (
            not serializer.instance.user.organization.is_paid
            and not serializer.instance.user.is_admin
        ):
            emit_generate_team_form_templates(
                str(serializer.instance.user.id),
                schedule=(timezone.now() + timezone.timedelta(minutes=2)),
            )
        if user.make_team_lead:
            _process_change_team_lead(
                str(user.id), schedule=(timezone.now() + timezone.timedelta(minutes=2))
            )
        sync_operations = [*user.hubspot_account.resource_sync_opts]
        sync_time = (timezone.now() + timezone.timedelta(minutes=5)).strftime("%Y-%m-%dT%H:%M%Z")
        emit_gen_next_hubspot_sync(str(user.id), sync_operations, sync_time)
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

