from django.shortcuts import render
from django.core.management import call_command


from rest_framework.decorators import (
    api_view,
    permission_classes,
    authentication_classes,
)
from rest_framework.response import Response
from rest_framework import (
    permissions,
    status,
)

from managr.salesforce.cron import (
    queue_stale_sf_data_for_delete,
    queue_users_sf_resource,
    queue_users_sf_fields,
)
from managr.alerts.cron import init_alert_check

# Create your views here.


@api_view(["post"])
# @authentication_classes((slack_auth.SlackWebhookAuthentication,))
@permission_classes([permissions.AllowAny])
def init_clear_stale_data(request):
    queue_stale_sf_data_for_delete(1440)
    return Response()


@api_view(["post"])
# @authentication_classes((slack_auth.SlackWebhookAuthentication,))
@permission_classes([permissions.AllowAny])
def init_resource_sync(request):
    queue_users_sf_resource()
    return Response()


@api_view(["post"])
# @authentication_classes((slack_auth.SlackWebhookAuthentication,))
@permission_classes([permissions.AllowAny])
def init_object_field_sync(request):
    queue_users_sf_fields()
    return Response()


@api_view(["post"])
# @authentication_classes((slack_auth.SlackWebhookAuthentication,))
@permission_classes([permissions.AllowAny])
def init_trigger_alerts(request):
    init_alert_check()
    return Response()
