from rest_framework import serializers

from managr.salesforce.serializers import SObjectFieldSerializer
from .models import (
    OrgCustomSlackFormInstance,
    OrganizationSlackIntegration,
    OrgCustomSlackForm,
    UserSlackIntegration,
    FormField,
)


class CustomFormFieldSerializer(serializers.ModelSerializer):
    field_ref = SObjectFieldSerializer(source="field", read_only=True)

    class Meta:
        model = FormField
        fields = ("datetime_created", "order", "field", "form", "field_ref", "include_in_recap")


class OrganizationSlackIntegrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganizationSlackIntegration
        fields = (
            "datetime_created",
            "team_name",
            "team_id",
        )


class OrgSlackIntegrationWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganizationSlackIntegration
        fields = (
            "organization",
            "scope",
            "team_name",
            "team_id",
            "bot_user_id",
            "access_token",
            "incoming_webhook",
            "enterprise",
        )


class UserSlackIntegrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSlackIntegration
        fields = (
            "slack_id",
            "datetime_created",
        )


class OrgCustomSlackFormSerializer(serializers.ModelSerializer):
    fields_ref = serializers.SerializerMethodField()

    class Meta:
        model = OrgCustomSlackForm
        fields = (
            "id",
            "organization",
            "config",
            "form_type",
            "resource",
            "stage",
            "fields",
            "fields_ref",
        )

        read_only_fields = (
            "fields",
            "fields_ref",
        )

    def get_fields_ref(self, obj):
        fields = obj.formfield_set.all().order_by("order")
        fields_ref = []
        for field in fields:
            fields_ref.append(CustomFormFieldSerializer(field).data)
        return fields_ref


class OrgCustomSlackFormInstanceSerializer(serializers.ModelSerializer):
    template_ref = OrgCustomSlackFormSerializer(source="template")

    class Meta:
        model = OrgCustomSlackFormInstance
        fields = (
            "id",
            "workflow",
            "resource_id",
            "resource",
            "is_submitted",
            "submission_date",
            "update_source",
            "user",
            "template",
            "template_ref",
            "saved_data",
            "previous_data",
        )


class UserFrontEndSlackIntegrationSerializer(serializers.ModelSerializer):
    recap_receivers_ref = serializers.SerializerMethodField("get_recap_receivers")

    class Meta:
        model = UserSlackIntegration
        fields = (
            "slack_id",
            "datetime_created",
            "channel",
            "zoom_channel",
            "recap_channel",
            "recap_receivers",
            "recap_receivers_ref",
            "realtime_alert_configs",
        )

    def get_recap_receivers(self, instance):
        return list(instance.recap_receivers)
