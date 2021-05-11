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


class AlertTemplateViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = alert_serializers.AlertTemplateSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return alert_models.AlertTemplate.objects.for_user(self.request.user)

    def create(self, request, *args, **kwargs):
        data = request.data
        data.update({"user": request.user.id})
        serializer = alert_serializers.AlertTemplateWriteSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        response_serializer = self.serializer_class(serializer.instance)
        return Response(data=response_serializer.data)


class AlertMessageTemplateViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = alert_serializers.AlertMessageTemplateRefSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return alert_models.AlertMessageTemplate.objects.for_user(self.request.user)

