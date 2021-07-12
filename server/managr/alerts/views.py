import logging
import requests
import json
from faker import Faker
import pytz
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
from rest_framework.decorators import action
from rest_framework.decorators import (
    api_view,
    permission_classes,
    authentication_classes,
)


from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, PermissionDenied

from .background import emit_init_alert, _process_check_alert

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

    @action(
        methods=["post"],
        permission_classes=[permissions.IsAuthenticated],
        detail=True,
        url_path="test",
    )
    def test_alert(self, request, *args, **kwargs):
        obj = self.get_object()
        obj.test_alert()
        return Response()

    @action(
        methods=["post"],
        permission_classes=[permissions.IsAuthenticated],
        detail=True,
        url_path="run-now",
    )
    def run_now(self, request, *args, **kwargs):
        obj = self.get_object()
        for config in obj.configs.all():
            template = config.template
            users = template.get_users
            for user in users:
                run_time = datetime.now(pytz.utc)
                _process_check_alert(
                    str(config.id), str(user.id), run_time.strftime("%Y-%m-%dT%H:%M%z")
                )
        return Response()


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


class AlertConfigViewSet(
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
        return alert_models.AlertConfig.objects.for_user(self.request.user)


class AlertGroupViewSet(
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
        return alert_models.AlertGroupTemplate.objects.for_user(self.request.user)


class AlertOperandViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = alert_serializers.AlertOperandRefSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return alert_models.AlertOperand.objects.for_user(self.request.user)
