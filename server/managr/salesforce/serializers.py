from rest_framework import serializers
from rest_framework.exceptions import ValidationError, PermissionDenied

from managr.zoom.serializers import ZoomMeetingSerializer
from managr.slack.models import OrgCustomSlackFormInstance
from managr.meetings.serializers import MeetingSerializer
from .models import (
    MeetingWorkflow,
    SalesforceAuthAccount,
    SObjectPicklist,
    SObjectField,
    SObjectValidation,
)


class SalesforceAuthSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesforceAuthAccount
        fields = (
            "id",
            "user",
            "access_token",
            "refresh_token",
            "signature",
            "scope",
            "id_token",
            "instance_url",
            "salesforce_id",
            "salesforce_account",
            "login_link",
            "user",
            "sobjects",
            "exclude_fields",
            "is_busy",
            "last_sync_time",
            "extra_pipeline_fields",
        )


class SObjectFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = SObjectField
        fields = (
            "id",
            "salesforce_account",
            "salesforce_object",
            "api_name",
            "custom",
            "createable",
            "updateable",
            "unique",
            "required",
            "data_type",
            "display_value",
            "value",
            "label",
            "length",
            "reference",
            "reference_to_infos",
            "relationship_name",
            "options",
            "reference_display_label",
            "integration_source",
            "integration_id",
            "is_public",
            "imported_by",
            "filterable",
        )


class SObjectValidationSerializer(serializers.ModelSerializer):
    class Meta:
        model = SObjectValidation
        fields = (
            "id",
            "message",
            "description",
            "salesforce_object",
            "salesforce_account",
            "integration_id",
            "integration_source",
            "imported_by",
        )

    def to_internal_value(self, data):
        if data.get("message", None) in ["", None]:
            data.update({"message": "No Message Provided"})

        if data.get("description", None) in ["", None]:
            data.update({"description": "No Description Provided"})

        return super().to_internal_value(data)


class SObjectPicklistSerializer(serializers.ModelSerializer):
    class Meta:
        model = SObjectPicklist
        fields = (
            "id",
            "values",
            "field",
            "salesforce_account",
            "picklist_for",
            "imported_by",
            "salesforce_object",
        )

    def to_internal_value(self, data):

        if data.get("picklist_for") not in ["", None]:
            data["field"] = (
                SObjectField.objects.filter(
                    imported_by__id=data.get("imported_by"),
                    api_name=data.get("picklist_for"),
                    salesforce_object=data.get("salesforce_object"),
                )
                .values_list("id", flat=True)
                .first()
            )
        return super().to_internal_value(data)


class MeetingWorkflowSerializer(serializers.ModelSerializer):
    meeting_ref = MeetingSerializer(many=False, source="meeting", read_only=True)
    is_completed = serializers.SerializerMethodField("get_completed_status")

    class Meta:
        model = MeetingWorkflow
        fields = ("id", "meeting", "meeting_ref", "resource_id", "resource_type", "is_completed")

    def get_completed_status(self, instance):
        form = instance.forms.filter(template__form_type="UPDATE").first()
        if form:
            if form.saved_data:
                return True
        return False
