from rest_framework import serializers
from rest_framework.exceptions import ValidationError, PermissionDenied
from managr.salesforce.serializers import SObjectFieldSerializer
from managr.core.serializers import UserSerializer
from managr.core.models import User
from . import constants as alert_consts
from . import models as alert_models
from copy import copy

# REF SERIALIZERS
##  SHORTENED SERIALIZERS FOR REF OBJECTS
def create_configs_for_target(target, template_user, config):
    if target in ["MANAGERS", "REPS", "SDR"]:
        if target == "MANAGERS":
            target = "MANAGER"
        elif target == "REPS":
            target = "REP"
        users = User.objects.filter(
            organization=template_user.organization, user_level=target, is_active=True,
        )
    elif target == "SELF":
        config["recipient_type"] = "SLACK_CHANNEL"
        return [config]
    elif target == "ALL":
        users = User.objects.filter(organization=template_user.organization, is_active=True)
    else:
        users = User.objects.filter(id=target)
    new_configs = []
    for user in users:
        if user.has_slack_integration:
            config_copy = copy(config)
            config_copy["recipients"] = [
                user.slack_integration.zoom_channel
                if user.slack_integration.zoom_channel
                else user.slack_integration.channel
            ]
            config_copy["alert_targets"] = [str(user.id)]
            config_copy["recipient_type"] = "SLACK_CHANNEL"
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


class AlertTemplateRefSerializer(serializers.ModelSerializer):
    class Meta:
        model = alert_models.AlertTemplate
        fields = (
            "id",
            "title",
            "user",
            "is_active",
            "resource_type",
            "alert_level",
            "invocation",
            "last_invocation_datetime",
        )


class AlertGroupRefSerializer(serializers.ModelSerializer):
    template_ref = AlertTemplateRefSerializer(source="template")

    class Meta:
        model = alert_models.AlertGroup
        fields = (
            "id",
            "group_condition",
            "template",
            "template_ref",
            "operands",
            "group_order",
        )


class AlertOperandRefSerializer(serializers.ModelSerializer):
    group_ref = AlertGroupRefSerializer(source="group")
    operand_identifier_ref = serializers.SerializerMethodField("get_field_ref")

    class Meta:
        model = alert_models.AlertOperand
        fields = (
            "id",
            "group",
            "group_ref",
            "operand_condition",
            "operand_type",
            "operand_identifier",
            "operand_operator",
            "operand_identifier_ref",
            "operand_value",
            "operand_order",
            "data_type",
        )

    def get_field_ref(self, instance):
        return SObjectFieldSerializer(instance.operand_identifier_ref).data


class AlertMessageTemplateRefSerializer(serializers.ModelSerializer):
    template_ref = AlertTemplateRefSerializer(source="template")

    class Meta:
        model = alert_models.AlertMessageTemplate
        fields = (
            "id",
            "template",
            "template_ref",
            "bindings",
            "notification_text",
            "body",
        )


class AlertConfigRefSerializer(serializers.ModelSerializer):
    template_ref = AlertTemplateRefSerializer(source="template")
    alert_targets_ref = serializers.SerializerMethodField("get_alert_targets_ref")
    recipients_ref = serializers.SerializerMethodField("get_recipients_ref")

    class Meta:
        model = alert_models.AlertConfig
        fields = (
            "id",
            "recurrence_frequency",
            "recurrence_day",
            "recurrence_days",
            "recipients",
            "recipient_type",
            "recipients_ref",
            "template",
            "template_ref",
            "alert_targets",
            "alert_targets_ref",
            "recipients_ref",
        )

    def get_alert_targets_ref(self, instance):
        target_groups = list(
            filter(
                lambda group: group in ["SELF", "MANAGERS", "REPS", "ALL", "SDR"],
                instance.alert_targets,
            )
        )
        target_users = list(
            filter(
                lambda group: group not in ["SELF", "MANAGERS", "REPS", "ALL", "SDR"],
                instance.alert_targets,
            )
        )
        return [
            *list(
                filter(
                    lambda opt: opt.get("value") in target_groups, alert_consts.ALERT_TARGET_GROUPS
                )
            ),
            *list(
                map(
                    lambda u: dict(key=u.full_name, value=u.id),
                    instance.template.user.organization.users.filter(
                        id__in=target_users, is_active=True
                    ),
                )
            ),
        ]

    def get_recipients_ref(self, instance):
        if instance.recipient_type == "USER_LEVEL":
            target_groups = list(
                filter(
                    lambda group: group in ["SELF", "MANAGERS", "REPS", "ALL", "SDR", "OWNER"],
                    instance.recipients,
                )
            )
            target_users = list(
                filter(
                    lambda group: group not in ["SELF", "MANAGERS", "REPS", "ALL", "SDR", "OWNER"],
                    instance.recipients,
                )
            )
            return [
                *list(
                    filter(
                        lambda opt: opt.get("value") in target_groups,
                        alert_consts.ALERT_RECIPIENT_GROUPS,
                    )
                ),
                *list(
                    map(
                        lambda u: dict(key=u.full_name, value=u.id),
                        instance.template.user.organization.users.filter(
                            id__in=target_users, is_active=True
                        ),
                    )
                ),
            ]
        else:
            return list(map(lambda channel: dict(key=channel, value=channel), instance.recipients))


class AlertInstanceRefSerializer(serializers.ModelSerializer):
    template_ref = AlertTemplateRefSerializer(source="template")

    class Meta:
        model = alert_models.AlertInstance
        fields = (
            "id",
            "template",
            "template_ref",
            "user",
            "rendered_text",
            "resource_id",
            "sent_at",
            "channel",
            "config",
            "invocation",
        )


class AlertInstanceSerializer(serializers.ModelSerializer):
    template_ref = AlertTemplateRefSerializer(source="template")
    resource_ref = serializers.SerializerMethodField("get_resource_ref")
    form_instance_ref = serializers.SerializerMethodField("get_form_ref")

    class Meta:
        model = alert_models.AlertInstance
        fields = (
            "id",
            "template",
            "template_ref",
            "user",
            "rendered_text",
            "resource_id",
            "resource_ref",
            "sent_at",
            "channel",
            "config",
            "invocation",
            "form_instance_ref",
        )

    def get_resource_ref(self, instance):
        from managr.salesforce.routes import routes

        resource = instance.template.resource_type
        serializer = routes[resource]["serializer"]
        resource_id = routes[resource]["model"].objects.get(id=instance.resource_id)
        return serializer(instance=resource_id).data

    def get_form_ref(self, instance):
        forms = instance.form_instance.all().values_list("is_submitted", flat=True)
        if len(forms):
            return forms[0]
        return False


# READ SERIALIZERS


class AlertGroupSerializer(serializers.ModelSerializer):
    operands_ref = AlertOperandRefSerializer(source="operands", many=True)
    template_ref = AlertTemplateRefSerializer(source="template")

    class Meta:
        model = alert_models.AlertGroup
        fields = (
            "id",
            "group_condition",
            "template",
            "template_ref",
            "operands",
            "operands_ref",
            "group_order",
        )


class AlertTemplateSerializer(serializers.ModelSerializer):
    groups_ref = AlertGroupSerializer(source="groups", many=True)
    message_template_ref = AlertMessageTemplateRefSerializer(source="message_template")
    configs_ref = AlertConfigRefSerializer(source="configs", many=True)
    instances_ref = AlertInstanceRefSerializer(source="instances", many=True)

    class Meta:
        model = alert_models.AlertTemplate
        fields = (
            "id",
            "title",
            "user",
            "is_active",
            "resource_type",
            "groups",
            "groups_ref",
            "message_template",
            "message_template_ref",
            "configs",
            "configs_ref",
            "instances",
            "instances_ref",
            "alert_level",
        )


## WRITE SERIALIZERS


class AlertMessageTemplateWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = alert_models.AlertMessageTemplate
        fields = (
            "id",
            "template",
            "bindings",
            "notification_text",
            "body",
        )


class AlertOperandWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = alert_models.AlertOperand
        fields = (
            "id",
            "group",
            "operand_condition",
            "operand_type",
            "operand_identifier",
            "operand_operator",
            "operand_value",
            "operand_order",
            "data_type",
        )


class AlertGroupWriteSerializer(serializers.ModelSerializer):
    new_operands = serializers.ListField(required=False)

    class Meta:
        model = alert_models.AlertGroup
        fields = (
            "id",
            "group_condition",
            "template",
            "new_operands",
            "group_order",
        )

    def create(self, validated_data, *args, **kwargs):
        new_operands = validated_data.pop("new_operands", [])
        data = super().create(validated_data, *args, **kwargs)

        if len(new_operands):
            new_operands = list(map(lambda x: {**x, "group": data.id}, new_operands))

            _new_operands = AlertOperandWriteSerializer(data=new_operands, many=True)
            _new_operands.is_valid(raise_exception=True)
            _new_operands.save()
        return data


# class RealTimeAlertConfigWriteSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = alert_models.Config
#         fields = (
#             "title",
#             "is_active",
#             "recipients",
#         )


class AlertConfigWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = alert_models.AlertConfig
        fields = (
            "id",
            "recurrence_frequency",
            "recurrence_day",
            "recurrence_days",
            "recipients",
            "recipient_type",
            "template",
            "alert_targets",
        )

    def validate_recurrence_day(self, value):
        return value

    def validate_alert_targets(self, value):
        if not self.context.user.user_level == "MANAGER":
            value = list(
                filter(lambda opt: opt == "SELF" or opt == str(self.context.user.id), value)
            )

        return value

    def to_internal_value(self, data):
        print(self.context.user)
        if (
            not self.context.user.user_level == "MANAGER"
            and not data.get("recipient_type") == "SLACK_CHANNEL"
        ):
            value = list(
                filter(
                    lambda opt: opt == "SELF" or opt == str(self.context.user.id),
                    data.get("recipients", []),
                )
            )
            if not len(value):
                value = ["SELF"]

            data.update({"recipients": value})
        internal_data = super().to_internal_value(data)
        return internal_data


class AlertTemplateWriteSerializer(serializers.ModelSerializer):
    new_groups = serializers.ListField(required=False)
    message_template = serializers.DictField(required=False)
    new_configs = serializers.ListField(required=False)

    class Meta:
        model = alert_models.AlertTemplate
        fields = (
            "id",
            "title",
            "user",
            "is_active",
            "resource_type",
            "new_groups",
            "message_template",
            "new_configs",
            "alert_level",
        )

    def create(self, validated_data, *args, **kwargs):
        new_groups = validated_data.pop("new_groups", [])
        message_template = validated_data.pop("message_template")
        new_configs = validated_data.pop("new_configs", [])
        data = super().create(validated_data, *args, **kwargs)
        message_template = AlertMessageTemplateWriteSerializer(
            data={**message_template, "template": data.id}
        )
        message_template.is_valid(raise_exception=True)
        message_template.save()
        if len(new_groups):
            new_groups = list(map(lambda x: {**x, "template": data.id}, new_groups))

            _new_groups = AlertGroupWriteSerializer(data=new_groups, many=True)
            _new_groups.is_valid(raise_exception=True)
            _new_groups.save()
        if len(new_configs):
            new_configs = list(map(lambda x: {**x, "template": data.id}, new_configs))
            _new_configs = AlertConfigWriteSerializer(
                data=new_configs, many=True, context=self.context,
            )
            try:
                _new_configs.is_valid(raise_exception=True)
                _new_configs.save()
            except Exception as e:
                print(f"ERROR {e}")
        return data
