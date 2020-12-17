from django.utils import timezone
from django.shortcuts import render

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
from managr.core import constants as core_consts

from managr.lead.models import Lead, LeadActivityLog, Notification, Forecast
from managr.lead import constants as lead_consts
from managr.organization import constants as org_consts
from managr.organization.models import Stage
from managr.lead.background import emit_event
from managr.zoom.models import ZoomMeeting

# Create your views here.


@api_view(["post"])
@permission_classes([permissions.IsAuthenticated])
def clear_activity_log(request):
    data = request.data
    ## clear all notification for a user to avoid the check that a notif doesnt exist already
    Notification.objects.for_user(request.user).filter(
        resource_id=data["lead"],
        notification_class="SLACK",
        notification_type=lead_consts.NOTIFICATION_TYPE_OPPORTUNITY_INACTIVE,
    ).delete()

    lead = Lead.objects.get(id=data["lead"])
    ## get one log to change if it exists
    log = lead.activity_logs.first()
    ## delete the rest
    lead.activity_logs.all().delete()
    ## make its time within the 100 days
    time_occured = timezone.now() - timezone.timedelta(days=100)
    if log:
        log.activity = lead_consts.EMAIL_RECEIVED
        log.action_timestamp = time_occured
        log.save()
    else:
        LeadActivityLog.objects.create(
            lead=lead,
            action_timestamp=time_occured,
            activity=lead_consts.EMAIL_RECEIVED,
            action_taken_by=request.user,
        )
    call_command("createleadnotifications")
    return Response(data={"success": True})


@api_view(["post"])
@permission_classes([permissions.IsAuthenticated])
def stalled_in_stage(request):
    data = request.data
    ## clear all notification for a user to avoid the check that a notif doesnt exist already
    Notification.objects.for_user(request.user).filter(
        resource_id=data["lead"],
        notification_class="SLACK",
        notification_type=lead_consts.NOTIFICATION_TYPE_OPPORTUNITY_STALLED_IN_STAGE,
    ).delete()

    lead = Lead.objects.get(id=data["lead"])
    stalled_date = timezone.now() - timezone.timedelta(days=65)
    lead.status_last_update = stalled_date
    lead.save()
    call_command("createleadnotifications")

    return Response(data={"success": True})


@api_view(["post"])
@permission_classes([permissions.IsAuthenticated])
def past_expected_close_date(request):
    data = request.data
    days = int(data["days"]) + 1
    notification_type_str = "OPPORTUNITY.LAPSED_EXPECTED_CLOSE_DATE_{}".format(
        data["days"]
    )
    ## clear all notification for a user to avoid the check that a notif doesnt exist already
    Notification.objects.for_user(request.user).filter(
        resource_id=data["lead"],
        notification_class="SLACK",
        notification_type=notification_type_str,
    ).delete()

    lead = Lead.objects.get(id=data["lead"])

    expected_close_date = timezone.now() - timezone.timedelta(days=days)
    lead.expected_close_date = expected_close_date
    lead.save()
    call_command("createleadnotifications")

    return Response(data={"success": True})


@api_view(["post"])
@permission_classes([permissions.IsAuthenticated])
def close_lead(request):
    # TODO - add CanEditResourceOrReadOnly to ensure person closing is person claiming 05/02/20
    """ special endpoint to close a lead, requires a contract and a closing amount
            file must already exist and is expected to be identified by an ID
        """
    data = request.data
    lead = Lead.objects.get(id=data["lead"])
    lead.status = Stage.objects.get(
        title=lead_consts.LEAD_STATUS_CLOSED, type=org_consts.STAGE_TYPE_PUBLIC
    )
    closing_amount = data["closing_amount"]
    lead.closing_amount = closing_amount
    lead.expected_close_date = timezone.now()
    if lead.forecast:
        lead.forecast.forecast = lead_consts.FORECAST_CLOSED
        lead.forecast.save()
    else:
        Forecast.objects.create(
            lead=lead, forecast=lead_consts.FORECAST_CLOSED,
        )
    lead.save()
    emit_event(lead_consts.LEAD_CLOSED, request.user, lead)

    return Response()


@api_view(["post"])
@permission_classes([permissions.IsAuthenticated])
def delete_demo_meeting(request):
    meeting_uuid = request.data["payload"]["object"]["uuid"]
    meeting = ZoomMeeting.objects.filter(meeting_uuid=meeting_uuid).first()
    if meeting:
        meeting.delete()

    return Response()


@api_view(["post"])
@permission_classes([permissions.IsAuthenticated])
def demo_generate_meeting_score(request):

    call_command("generatemeetingscores")

    return Response()
