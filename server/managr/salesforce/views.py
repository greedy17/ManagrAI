import logging
import requests
import json
from faker import Faker
from urllib.parse import urlencode
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

from .adapter.models import SalesforceAuthAccountAdapter


@api_view(["get"])
@permission_classes([permissions.AllowAny])
def auth_link_test(request):
    return render(request, "test/test-auth-flow.html")


@api_view(["post"])
@permission_classes([permissions.AllowAny])
def authenticate(request):
    code = request.data.get("code", None)


@api_view(["get"])
@permission_classes([permissions.AllowAny])
def salesforce_auth_link(request):
    link = SalesforceAuthAccountAdapter.generate_auth_link()
    return Response({"url": link})

