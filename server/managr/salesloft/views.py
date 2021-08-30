import logging
import requests
import json
from faker import Faker
from urllib.parse import urlencode
from datetime import datetime

from django.core.management import call_command
from django.shortcuts import render, redirect
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt, csrf_protect

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

from . import constants as salesloft_consts

# Create your views here.
logger = logging.getLogger("managr")


@api_view(["GET"])
def get_salesloft_auth_link(request):
    query = urlencode(salesloft_consts.AUTHORIZATION_QUERY_PARAMS)
    return f"{salesloft_consts.AUTHORIZATION_URI}?{query}"
