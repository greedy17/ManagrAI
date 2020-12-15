from django.utils import timezone
from django.shortcuts import render

import logging
import requests
import json
from faker import Faker
from urllib.parse import urlencode
from datetime import datetime

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


from managr.lead.models import Lead, LeadActivityLog, Notification

# Create your views here.


@api_view(["post"])
@permission_classes([permissions.IsAuthenticated])
def clear_activity_log(request):
    ## clear all notification for a user to avoid the check that a notif doesnt exist already
    Notification.objects.for_user(request.user).delete()
    data = request.data
    lead = Lead.objects.get(id=data["lead"])
    ## get one log to change if it exists
    log = Lead.objects.first()
    ## delete the rest
    lead.activity_logs.all().delete()
    ## make its time within the 100 days
    time_occured = timezone.now() - timezone.timedelta(days=100)
    if log:
        log.action_timestamp = time_occured
        log.save()
    else:
        LeadActivityLog.objects.create(
            lead=lead,
            action_timestamp=time_occured,
            activity="Note.CREATED",
            action_taken_by=request.user,
        )

    return Response(data={"success": True})


@api_view(["post"])
@permission_classes([permissions.IsAuthenticated])
def stalled_in_stage(request):
    ## clear all notification for a user to avoid the check that a notif doesnt exist already
    Notification.objects.for_user(request.user).delete()
    data = request.data
    lead = Lead.objects.get(id=data["lead"])
    stalled_date = timezone.now() - timezone.timedelta(days=65)
    lead.status_last_update = stalled_date
    lead.save()

    return Response(data={"success": True})


@api_view(["post"])
@permission_classes([permissions.IsAuthenticated])
def past_expected_close_date(request):
    ## clear all notification for a user to avoid the check that a notif doesnt exist already
    Notification.objects.for_user(request.user).delete()
    data = request.data
    lead = Lead.objects.get(id=data["lead"])
    days = int(data["days"]) + 1
    expected_close_date = timezone.now() - timezone.timedelta(days=days)
    lead.expected_close_date = expected_close_date
    lead.save()

    return Response(data={"success": True})
