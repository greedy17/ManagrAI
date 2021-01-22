import logging
import requests
import json
from faker import Faker
from urllib.parse import urlencode, unquote
from datetime import datetime

from django.http import HttpResponse
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

from .models import SFSyncOperation
from .serializers import SalesforceAuthSerializer
from .adapter.models import SalesforceAuthAccountAdapter
from .background import emit_sf_sync
from . import constants as sf_consts


@api_view(["post"])
@permission_classes([permissions.IsAuthenticated])
def authenticate(request):
    code = request.data.get("code", None)
    if code:
        data = SalesforceAuthAccountAdapter.create_account(unquote(code), str(request.user.id))
        serializer = SalesforceAuthSerializer(data=data.as_dict)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        # create sf sync object
        operations = [
            sf_consts.RESOURCE_SYNC_ACCOUNT,
            sf_consts.RESOURCE_SYNC_STAGE,
            sf_consts.RESOURCE_SYNC_OPPORTUNITY,
        ]
        # operations[sf_consts.RESOURCE_SYNC_OPPORTUNITY] = []

        if request.user.organization.has_stages_integrated:
            operations.remove(sf_consts.RESOURCE_SYNC_STAGE)

        sync = SFSyncOperation.objects.create(user=request.user, operations_list=operations)
        sync.begin_tasks()

        # initiate process
        return Response(data={"success": True})


@api_view(["get"])
@permission_classes([permissions.IsAuthenticated])
def salesforce_auth_link(request):
    link = SalesforceAuthAccountAdapter.generate_auth_link()
    return Response({"link": link})


@api_view(["post"])
@permission_classes([permissions.IsAuthenticated])
def revoke(request):
    user = request.user
    if hasattr(user, "salesforce_account"):
        sf_acc = user.salesforce_account
        sf_acc.revoke()
    return Response()
