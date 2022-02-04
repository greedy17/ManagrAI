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
from django.utils import timezone

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
from managr.core.models import User

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

    def get_serializer_class(self, *args, **kwargs):
        if self.request.method == "POST":
            return alert_serializers.AlertTemplateWriteSerializer

        return self.serializer_class

    def create(self, request, *args, **kwargs):
        data = request.data
        serializer = alert_serializers.AlertTemplateWriteSerializer(data=data, context=request)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        readSerializer = self.serializer_class(instance=serializer.instance)
        return Response(data=readSerializer.data)

    @action(
        methods=["post"],
        permission_classes=[permissions.IsAuthenticated],
        detail=True,
        url_path="test",
    )
    def test_alert(self, request, *args, **kwargs):
        # obj = self.get_object()
        # obj.test_alert()
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
            template.invocation = template.invocation + 1
            template.last_invocation_datetime = timezone.now()
            template.save()
            users = config.target_users
            for user in users:
                run_time = datetime.now(pytz.utc)
                _process_check_alert(
                    str(config.id),
                    str(user.id),
                    template.invocation,
                    run_time.strftime("%Y-%m-%dT%H:%M%z"),
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


class RealTimeAlertConfigViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = (permissions.IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        data = request.data
        print(data)
        return Response(data)


class AlertConfigViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = alert_serializers.AlertConfigRefSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return alert_models.AlertConfig.objects.for_user(self.request.user)

    def get_serializer_class(self, *args, **kwargs):
        if self.request.method == "POST":
            return alert_serializers.AlertConfigWriteSerializer

        return self.serializer_class

    def create(self, request, *args, **kwargs):
        data = request.data
        serializer = alert_serializers.AlertConfigWriteSerializer(data=data, context=request)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        readSerializer = self.serializer_class(instance=serializer.instance)
        return Response(data=readSerializer.data)


class AlertGroupViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = alert_serializers.AlertGroupSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return alert_models.AlertGroup.objects.for_user(self.request.user)

    def get_serializer_class(self, *args, **kwargs):
        if self.request.method == "POST":
            return alert_serializers.AlertGroupWriteSerializer

        return self.serializer_class

    def create(self, request, *args, **kwargs):
        data = request.data
        serializer = alert_serializers.AlertGroupWriteSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        readSerializer = alert_serializers.AlertGroupSerializer(instance=serializer.instance)
        return Response(data=readSerializer.data)


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

    def get_serializer_class(self, *args, **kwargs):
        if self.request.method == "POST":
            return alert_serializers.AlertOperandWriteSerializer

        return self.serializer_class


class RealTimeAlertViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = (permissions.IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        from managr.salesforce.models import SObjectField

        data = request.data
        print(data)
        manager = User.objects.get(id=data.get("user"))
        api_name = data.get("api_name", None)
        if api_name:
            field = SObjectField.objects.filter(salesforce_object=data.get("resource")).filter(
                api_name=api_name
            )
            current_config = data.get("config")
            pipelines = data.get("pipelines")
            current_config["recipients"] = {str(manager.id): data.get("recipients")}
            current_config["api_name"] = api_name
            users = User.objects.filter(id__in=pipelines)
            for user in users:
                configs = user.slack_integration.realtime_alert_configs
                if str(field.id) in configs:
                    if api_name in configs[str(field.id)].keys():
                        if (
                            str(manager.id)
                            not in configs[str(field.id)][api_name]["recipients"].keys()
                        ):
                            configs[str(field.id)][api_name]["recipients"][
                                str(manager.id)
                            ] = data.get("recipients")
                else:
                    new_config = {current_config["title"]: current_config}
                    configs[str(field.id)] = new_config
                user.slack_integration.save()
        return Response({"status": "success"})
