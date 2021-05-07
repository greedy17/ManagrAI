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

from . import models as alert_models
from . import serializers as alert_serializers

# Create your views here.


class AlertViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    generics.GenericAPIView,
):
    serializer_class = alert_serializers.AlertTemplateSerializer

    def get_queryset(self):
        return alert_models.AlertTemplate.objects.for_user(self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = alert_serializers.AlertTemplateWriteSerializer()
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return super().create(request, *args, **kwargs)

