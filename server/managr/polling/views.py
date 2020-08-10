from django_filters.rest_framework import DjangoFilterBackend
from dateutil.parser import parse
from rest_framework.authtoken.models import Token
from rest_framework import viewsets, mixins, generics, status, filters, permissions
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError, PermissionDenied
from rest_framework.response import Response
from django.db.models import Q
from django.shortcuts import render
from django.utils import timezone
from django.contrib.auth import authenticate, login
from django.db.models.functions import Lower
from django.db import transaction, IntegrityError
from django.template.exceptions import TemplateDoesNotExist
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
)


from managr.utils.numbers import validate_phone_number, format_phone_number
from managr.core.permissions import (
    IsOrganizationManager,
    IsSuperUser,
    IsSalesPerson,
    CanEditResourceOrReadOnly,
)
from managr.lead.models import Notification, LeadActivityLog

POLLING_ITEM_NOTIFICATION = Notification
POLLING_ITEM_LEAD_ACTIVITY_LOG = LeadActivityLog
POLLING_ITEM_NOTFICIATION_COUNT = "NOTIFICATIONCOUNT"
POLLING_ITEMS = (POLLING_ITEM_NOTIFICATION,)

# Create your views here.


def _list_polling_counts_lead_activity_log(user, last_checked, lead_id=None):
    """ helper method for updating lead activity log """
    return (
        POLLING_ITEM_LEAD_ACTIVITY_LOG.objects.for_user(user)
        .filter(lead__id=lead_id, last_edited__gte=last_checked)
        .count()
    )


@api_view(["post"])
@permission_classes(
    [permissions.IsAuthenticated,]
)
def list_polling_counts(request):
    """ will return a list of counts for items from the endpoint """
    items_to_return = request.data.get("items", None)
    last_checked_at = request.data.get("last_checked_at", None)
    last_checked_at = (
        parse(last_checked_at) - timezone.timedelta(minutes=1)
        if last_checked_at
        else None
    )

    now = timezone.now()
    items = dict()
    args = None
    if not items_to_return:
        return Response()

    for item in items_to_return:
        # certain items have extra attrs like lead_activity so try and split the item
        try:
            item, args = item.split(":")
        except ValueError as e:
            # item is not splittable so ignore it
            pass
        if item.lower() == POLLING_ITEM_NOTIFICATION.__name__.lower():
            data = (
                POLLING_ITEM_NOTIFICATION.objects.for_user(request.user)
                .filter(last_edited__gte=last_checked_at)
                .count()
            )
            items[item] = {"count": data, "last_check": now}
        if item.lower() == POLLING_ITEM_LEAD_ACTIVITY_LOG.__name__.lower():
            data = _list_polling_counts_lead_activity_log(
                request.user, last_checked_at, args
            )
            items[item] = {"count": data, "last_check": now}
        if item.lower() == POLLING_ITEM_NOTFICIATION_COUNT.lower():
            data = {
                "count": request.user.unviewed_notifications_count,
                "last_check": now,
            }
            items[item] = {"count": data, "last_check": now}

    return Response({"items": items, "last_check": now})

