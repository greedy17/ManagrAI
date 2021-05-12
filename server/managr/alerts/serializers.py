from rest_framework import serializers
from rest_framework.exceptions import ValidationError, PermissionDenied

from . import models as alert_models

# REF SERIALIZERS
##  SHORTENED SERIALIZERS FOR REF OBJECTS


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
            "operand_value",
            "operand_order",
            "data_type",
        )


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

    class Meta:
        model = alert_models.AlertConfig
        fields = (
            "id",
            "recurrence_frequency",
            "recurrence_day",
            "recipients",
            "template",
            "template_ref",
        )


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
        )


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


class AlertConfigWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = alert_models.AlertConfig
        fields = (
            "id",
            "recurrence_frequency",
            "recurrence_day",
            "recipients",
            "template",
        )


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

            _new_configs = AlertConfigWriteSerializer(data=new_configs, many=True)
            _new_configs.is_valid(raise_exception=True)
            _new_configs.save()
        return data

