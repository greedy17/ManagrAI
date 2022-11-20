import logging
import json
from django.conf import settings
from django.forms import ValidationError
import pytz
from django.core import serializers
from django.db.models import Q
from datetime import datetime
from django_filters.rest_framework import DjangoFilterBackend
from copy import copy
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
from managr.salesforce.routes import routes as model_routes

from managr.salesforce.adapter.exceptions import TokenExpired, SFQueryOffsetError

from rest_framework.response import Response

from .background import _process_check_alert

from . import models as alert_models
from . import serializers as alert_serializers
from .filters import AlertInstanceFilterSet, AlertTemplateFilterSet
from managr.core.models import User

logger = logging.getLogger("managr")


def create_configs_for_target(target, template_user, config):
    from managr.core.models import User

    if target in ["MANAGERS", "REPS", "SDR"]:
        if target == "MANAGERS":
            target = "MANAGER"
        elif target == "REPS":
            target = "REP"
        users = User.objects.filter(
            Q(organization=template_user.organization, user_level=target, is_active=True)
        )
    elif target == "SELF":
        config["recipient_type"] = "SLACK_CHANNEL"
        if "default" in config["recipients"] and template_user.has_slack_integration:
            config["recipients"] = [
                template_user.slack_integration.recap_channel
                if template_user.slack_integration.recap_channel
                else template_user.slack_integration.channel
            ]
        else:
            config["recipients"] = ["default"]
        return [config]
    elif target == "ALL":
        users = User.objects.filter(organization=template_user.organization, is_active=True)
    elif target == "TEAM":
        users = User.objects.filter(team=template_user.team, is_active=True).exclude(
            email=template_user.email
        )
    else:
        users = User.objects.filter(id=target)
    new_configs = []
    for user in users:
        if user.has_salesforce_integration:
            config_copy = copy(config)
            config_copy["alert_targets"] = [str(user.id)]
            if user.has_slack_integration:
                config_copy["recipients"] = [
                    user.slack_integration.recap_channel
                    if user.slack_integration.recap_channel
                    else user.slack_integration.channel
                ]
                config_copy["recipient_type"] = "SLACK_CHANNEL"
            else:
                config_copy["recipients"] = ["default"]
                config_copy["recipient_type"] = "default"
            new_configs.append(config_copy)
    return new_configs


def remove_duplicate_alert_configs(configs):
    recipients_in_configs = set()
    sorted_configs = []
    for config in configs:
        if config["alert_targets"][0] not in recipients_in_configs:
            sorted_configs.append(config)
            recipients_in_configs.add(config["alert_targets"][0])

    return sorted_configs


def alert_config_creator(data, user):
    new_configs = data.pop("new_configs", [])
    direct_to_users = data.pop("direct_to_users", False)
    if len(new_configs):
        if direct_to_users:
            all_configs = list()
            for target in new_configs[0]["alert_targets"]:
                created_configs = create_configs_for_target(target, user, new_configs[0])
                if len(created_configs):
                    all_configs = [*all_configs, *created_configs]
            if len(all_configs) > 1:
                all_configs = remove_duplicate_alert_configs(all_configs)
            new_configs = all_configs if len(all_configs) else None
        if user.slack_integration.recap_channel is None:
            if "SELF" in new_configs[0]["alert_targets"]:
                user.slack_integration.change_recap_channel(new_configs[0]["recipients"][0])
    else:
        return None
    return new_configs


# Create your views here.


class AlertTemplateViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    filter_backends = (
        DjangoFilterBackend,
        filters.SearchFilter,
    )
    serializer_class = alert_serializers.AlertTemplateSerializer
    permission_classes = (permissions.IsAuthenticated,)
    filter_class = AlertTemplateFilterSet

    def get_queryset(self):
        if self.request.data.get("from_workflow", False):
            return alert_models.AlertTemplate.objects.filter(
                user__organization=self.request.user.organization
            )
        return alert_models.AlertTemplate.objects.for_user(self.request.user)

    def get_serializer_class(self, *args, **kwargs):
        if self.request.method == "POST":
            return alert_serializers.AlertTemplateWriteSerializer
        if self.request.GET.get("for_pipeline", None):
            return alert_serializers.AlertTemplateRunNowSerializer
        return self.serializer_class

    def create(self, request, *args, **kwargs):
        data = request.data
        alert_target_ref = data["new_configs"][0]["alert_targets"]
        configs = alert_config_creator(data, request.user)
        if configs is None:
            serializer = alert_serializers.AlertTemplateWriteSerializer(data=None, context=request)
            serializer.is_valid(raise_exception=True)
        else:
            data["new_configs"] = configs
            data["target_reference"] = alert_target_ref
            serializer = alert_serializers.AlertTemplateWriteSerializer(data=data, context=request)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            readSerializer = self.serializer_class(instance=serializer.instance)
            return Response(data=readSerializer.data)
        return Response(data=data)

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
        data = self.request.data
        from_workflow = data.get("from_workflow", False)
        if isinstance(from_workflow, dict):
            config = obj.configs.all().first()
            template = config.template
            attempts = 1
            while True:
                sf = self.request.user.salesforce_account
                try:
                    if template.user != self.request.user:
                        if hasattr(self.request.user, "salesforce_account"):
                            res = sf.adapter_class.execute_alert_query(
                                template.url_str(self.request.user, config.id),
                                template.resource_type,
                            )
                            res_data = [item.integration_id for item in res]
                            break
                    users = []
                    for config in obj.configs.all():
                        config.target_users
                        users = [*users, *config.target_users]
                    res_data = []
                    for user in users:
                        if hasattr(user, "salesforce_account"):
                            res = sf.adapter_class.execute_alert_query(
                                template.url_str(user, config.id), template.resource_type
                            )
                            res_data.extend([item.integration_id for item in res])

                    break
                except TokenExpired:
                    if attempts >= 5:
                        res_data = {"error": "Could not refresh token"}
                        logger.exception(
                            f"Failed to retrieve alerts for {template.resource} data for user {str(user.id)} after {attempts} tries"
                        )
                        break
                    else:
                        sf.regenerate_token()
                        attempts += 1
                except SFQueryOffsetError:
                    return logger.warning(
                        f"Failed to sync some data for resource {template.resource} for user {str(user.id)} because of SF LIMIT"
                    )
                except Exception as e:
                    return logger.warning(
                        f"Failed retreive data for {template.title} for user {str(user.id)} because of {e}"
                    )
            model = model_routes[template.resource_type]["model"]
            queryset = model.objects.filter(integration_id__in=res_data)
            serialized = model_routes[template.resource_type]["serializer"](queryset, many=True)
            return Response({"results": serialized.data})
        elif isinstance(from_workflow, bool) and from_workflow is True:
            config = (
                obj.configs.all().filter(alert_targets__contains=[self.request.user.id]).first()
            )
            template = config.template
            template.invocation = template.invocation + 1
            template.last_invocation_datetime = timezone.now()
            template.save()
            users = config.target_users
            user = str(template.user.id) if len(users) > 1 else str(users.first().id)
            run_time = datetime.now(pytz.utc)
            _process_check_alert(
                str(config.id),
                str(request.user.id),
                template.invocation,
                run_time.strftime("%Y-%m-%dT%H:%M%z"),
            )
        else:
            for config in obj.configs.all():
                template = config.template
                template.invocation = template.invocation + 1
                template.last_invocation_datetime = timezone.now()
                template.save()
                users = config.target_users
                user = str(template.user.id) if len(users) > 1 else str(users.first().id)
                run_time = datetime.now(pytz.utc)
                _process_check_alert(
                    str(config.id),
                    user,
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

    @action(
        methods=["get"],
        permission_classes=[permissions.IsAuthenticated],
        detail=False,
        url_path="current-instances",
    )
    def get_current_instances(self, request, *args, **kwargs):
        user = User.objects.get(id=request.user.id)
        config_id = self.request.GET.get("config_id")
        last_instance = alert_models.AlertInstance.objects.filter(
            user=user, config=config_id
        ).first()
        if last_instance and last_instance.datetime_created.date() == datetime.today().date():
            template = alert_models.AlertTemplate.objects.filter(
                id=last_instance.template.id
            ).values()[0]
            instances = alert_models.AlertInstance.objects.filter(
                user=user, config__id=config_id, invocation=last_instance.invocation,
            )
            return Response(data={"instances": instances.values(), "template": template})

        return Response(data=[])


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


class AlertInstanceViewSet(
    mixins.ListModelMixin, viewsets.GenericViewSet,
):
    filter_backends = (
        DjangoFilterBackend,
        filters.SearchFilter,
    )
    serializer_class = alert_serializers.AlertInstanceSerializer
    filter_class = AlertInstanceFilterSet
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return alert_models.AlertInstance.objects.for_user(self.request.user)


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
        manager = User.objects.get(id=data.get("user"))
        api_name = data.get("api_name", None)
        if api_name:
            field = (
                SObjectField.objects.filter(salesforce_object=data.get("resource_type"))
                .filter(api_name=api_name)
                .first()
            )
            current_config = data.get("config")
            pipelines = data.get("pipelines")
            title = current_config["title"]
            current_config["recipients"] = {str(manager.id): data.get("recipients")}
            current_config["api_name"] = api_name
            users = User.objects.filter(id__in=pipelines)
            for user in users:
                if hasattr(user, "slack_integration"):
                    configs = user.slack_integration.realtime_alert_configs
                    if str(field.id) in configs.keys():
                        configs[str(field.id)][title] = current_config
                    else:
                        new_config = {current_config["title"]: current_config}
                        configs[str(field.id)] = new_config
                    user.slack_integration.save()
                else:
                    continue
        return Response({"status": "success"})
