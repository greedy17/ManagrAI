from rest_framework import serializers
from rest_framework.exceptions import ValidationError, PermissionDenied

from . import models as alert_models


class AlertTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = alert_models.AlertTemplate
        fields = (
            "id",
            "title",
            "user",
            "is_active",
            "resource_type",
            "groups",
            "message_template",
            "configurations",
            "instances",
        )


class AlertOperandWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = alert_models.AlertOperand
        fields = (
            "id",
            "group",
            "operand_conidtion",
            "operand_type",
            "operand_identifier",
            "operand_operator",
            "operand_value",
        )


class AlertGroupWriteSerializer(serializers.ModelSerializer):
    new_operands = AlertOperandWriteSerializer(many=True, write_only=True)
    model = alert_models.AlertGroup
    fields = (
        "id",
        "group_condition",
        "template",
        "new_operands",
    )


class AlertTemplateWriteSerializer(serializers.ModelSerializer):
    new_groups = AlertGroupWriteSerializer(many=True, write_only=True)

    class Meta:
        model = alert_models.AlertTemplate
        fields = (
            "id",
            "title",
            "user",
            "is_active",
            "resource_type",
            "new_groups",
            # "new_configurations",
            # "new_message_template",
        )


class AlertGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = alert_models.AlertGroup
        fields = (
            "id",
            "group_condition",
            "template",
            "operands",
        )


class AlertOperandSerializer(serializers.ModelSerializer):
    class Meta:
        model = alert_models.AlertOperand
        fields = (
            "id",
            "group",
            "operand_conidtion",
            "operand_type",
            "operand_identifier",
            "operand_operator",
            "operand_value",
        )


class AlertMessageTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = alert_models.AlertMessageTemplate
        fields = (
            "id",
            "template",
            "bindings",
            "notification_text",
            "body",
        )


class AlertConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = alert_models.AlertConfig
        fields = (
            "id",
            "recurrence_frequency",
            "recurrence_day",
            "recipients",
            "template",
        )


class AlertInstanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = alert_models.AlertInstance
        fields = (
            "id",
            "template",
            "user",
            "rendered_text",
            "resource_id",
            "sent_at",
        )

