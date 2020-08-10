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
from managr.lead.models import Notification

POLLING_ITEM_NOTIFICATION = Notification

POLLING_ITEMS = (POLLING_ITEM_NOTIFICATION,)

# Create your views here.


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
    if not items_to_return:
        return Response()

    for item in items_to_return:
        for model in POLLING_ITEMS:
            if item.lower() == model.__name__.lower():

                data = (
                    model.objects.for_user(request.user)
                    .filter(last_edited__gte=last_checked_at)
                    .count()
                )
                items[item] = {"count": data, "last_check": now}

    return Response({"items": items, "last_check": now})

