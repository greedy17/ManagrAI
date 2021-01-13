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

from managr.opportunity.models import Opportunity, LeadActivityLog, Notification
from managr.opportunity import constants as opp_consts
from managr.organization import constants as org_consts
from managr.organization.models import Stage
from managr.opportunity.background import emit_event
from managr.zoom.models import ZoomMeeting
from managr.slack.helpers import requests as slack_requests
from managr.slack.helpers.block_sets import get_block_set

# Create your views here.


def _create_notification(
    title, content, notification_type, opportunity, user, notification_class="ALERT"
):
    Notification.objects.create(
        notify_at=timezone.now(),
        title=title,
        notification_type=notification_type,
        resource_id=str(opportunity.id),
        notification_class=notification_class,
        user=user,
        meta={
            "id": str(opportunity.id),
            "title": title,
            "content": content,
            "leads": [{"id": str(opportunity.id), "title": opportunity.title}],
        },
    )


def _convert_to_user_friendly_date(date):
    return date.strftime("%m/%d/%Y")


@api_view(["post"])
@permission_classes([permissions.IsAuthenticated])
def clear_activity_log(request):
    data = request.data
    ## clear all notification for a user to avoid the check that a notif doesnt exist already
    Notification.objects.for_user(request.user).filter(
        resource_id=data["opportunity"],
        notification_class="SLACK",
        notification_type=opp_consts.NOTIFICATION_TYPE_OPPORTUNITY_INACTIVE,
    ).delete()

    opportunity = Opportunity.objects.get(id=data["opportunity"])
    ## get one log to change if it exists
    log = opportunity.activity_logs.first()
    ## delete the rest
    opportunity.activity_logs.all().delete()
    ## make its time within the 100 days
    time_occured = timezone.now() - timezone.timedelta(days=100)
    if log:
        log.activity = opp_consts.EMAIL_RECEIVED
        log.action_timestamp = time_occured
        log.save()
    else:
        LeadActivityLog.objects.create(
            opportunity=opportunity,
            action_timestamp=time_occured,
            activity=opp_consts.EMAIL_RECEIVED,
            action_taken_by=request.user,
        )

    latest_activity_str = _convert_to_user_friendly_date(time_occured)
    user = opportunity.claimed_by
    if hasattr(user, "slack_integration"):
        ## check if alert already exists
        title = f"No New Activity on opportunity {opportunity.title} since {latest_activity_str}"
        slack_message = f"The opportunity *{opportunity.title}* has not shown any activity since *{latest_activity_str}*"

        user_slack_channel = user.slack_integration.channel
        slack_org_access_token = user.organization.slack_integration.access_token
        block_set = get_block_set(
            "opp_inactive_block_set",
            {
                "l": str(opportunity.id),
                "m": slack_message,
                "u": str(user.id),
                "t": title,
            },
        )
        slack_requests.send_channel_message(
            user_slack_channel, slack_org_access_token, block_set=block_set,
        )

        _create_notification(
            title,
            slack_message,
            opp_consts.NOTIFICATION_TYPE_OPPORTUNITY_INACTIVE,
            opportunity,
            user,
            core_consts.NOTIFICATION_TYPE_SLACK,
        )

    return Response(data={"success": True})


@api_view(["post"])
@permission_classes([permissions.IsAuthenticated])
def stalled_in_stage(request):
    data = request.data
    ## clear all notification for a user to avoid the check that a notif doesnt exist already
    Notification.objects.for_user(request.user).filter(
        resource_id=data["opportunity"],
        notification_class="SLACK",
        notification_type=opp_consts.NOTIFICATION_TYPE_OPPORTUNITY_STALLED_IN_STAGE,
    ).delete()

    opportunity = Opportunity.objects.get(id=data["opportunity"])
    stalled_date = timezone.now() - timezone.timedelta(days=65)
    opportunity.status_last_update = stalled_date
    opportunity.save()
    status_last_updated_str = _convert_to_user_friendly_date(
        opportunity.status_last_update.date()
    )
    user = opportunity.claimed_by
    title = "Opportunity stalled in stage for over 60 days"
    content = f"*{opportunity.title}* has been in the same stage since *{status_last_updated_str}*"

    if hasattr(user, "slack_integration"):
        ## check if alert already exists
        user_slack_channel = user.slack_integration.channel
        slack_org_access_token = user.organization.slack_integration.access_token
        block_set = get_block_set(
            "opp_inactive_block_set",
            {"l": str(opportunity.id), "m": content, "u": str(user.id), "t": title,},
        )
        slack_requests.send_channel_message(
            user_slack_channel, slack_org_access_token, block_set=block_set,
        )

        _create_notification(
            title,
            content,
            opp_consts.NOTIFICATION_TYPE_OPPORTUNITY_STALLED_IN_STAGE,
            opportunity,
            user,
            core_consts.NOTIFICATION_TYPE_SLACK,
        )

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
        resource_id=data["opportunity"],
        notification_class="SLACK",
        notification_type=notification_type_str,
    ).delete()

    opportunity = Opportunity.objects.get(id=data["opportunity"])

    expected_close_date = timezone.now() - timezone.timedelta(days=days)
    opportunity.expected_close_date = expected_close_date
    opportunity.save()
    user = opportunity.claimed_by
    expected_close_date_str = _convert_to_user_friendly_date(
        opportunity.expected_close_date
    )
    title = f"Opportunity {opportunity.title} expected to close {days} day(s) ago"
    content = f"This *{opportunity.title}* opportunity was expected to close on *{expected_close_date_str}*, you are now *{days}* day(s) over"

    user_slack_channel = user.slack_integration.channel
    slack_org_access_token = user.organization.slack_integration.access_token
    block_set = get_block_set(
        "opp_inactive_block_set",
        {"l": str(opportunity.id), "m": content, "u": str(user.id), "t": title,},
    )
    slack_requests.send_channel_message(
        user_slack_channel, slack_org_access_token, block_set=block_set,
    )

    _create_notification(
        title,
        content,
        notification_type_str,
        opportunity,
        user,
        core_consts.NOTIFICATION_TYPE_SLACK,
    )

    return Response(data={"success": True})


@api_view(["post"])
@permission_classes([permissions.IsAuthenticated])
def close_lead(request):
    # TODO - add CanEditResourceOrReadOnly to ensure person closing is person claiming 05/02/20
    """ special endpoint to close a opportunity, requires a contract and a closing amount
            file must already exist and is expected to be identified by an ID
        """
    data = request.data
    opportunity = Opportunity.objects.get(id=data["opportunity"])
    opportunity.status = Stage.objects.get(
        title=opp_consts.LEAD_STATUS_CLOSED, type=org_consts.STAGE_TYPE_PUBLIC
    )
    closing_amount = data["closing_amount"]
    opportunity.closing_amount = closing_amount
    opportunity.expected_close_date = timezone.now()
    if opportunity.forecast:
        opportunity.forecast.forecast = opp_consts.FORECAST_CLOSED
        opportunity.forecast.save()
    else:
        Forecast.objects.create(
            opportunity=opportunity, forecast=opp_consts.FORECAST_CLOSED,
        )
    opportunity.save()
    emit_event(opp_consts.LEAD_CLOSED, request.user, opportunity)

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
