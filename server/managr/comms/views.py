import json
from datetime import datetime
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import (
    mixins,
    viewsets,
)
from managr.api.models import ExpiringTokenAuthentication
from django.db.models import Q
from rest_framework.response import Response

from rest_framework.views import APIView
from rest_framework import (
    filters,
    permissions,
    generics,
    mixins,
    status,
    viewsets,
)
from rest_framework.decorators import (
    api_view,
    permission_classes,
)
from . import constants as comms_consts
from managr.utils.client import Client, Variable_Client


@api_view(["GET"])
@permission_classes(
    [permissions.IsAuthenticated,]
)
def get_new_summary(request):
    company = request.data.get("company_name")

    data = {}
    return Response(data=data)
