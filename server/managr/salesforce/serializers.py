from rest_framework import serializers
from rest_framework.exceptions import ValidationError, PermissionDenied
from managr.zoom.serializers import ZoomMeetingSerializer
from managr.slack.models import OrgCustomSlackFormInstance
from managr.meetings.serializers import MeetingFrontendSerializer
from .models import (
    MeetingWorkflow,
    SalesforceAuthAccount,
    SObjectPicklist,
    SObjectField,
    SObjectValidation,
)
from managr.core.models import User


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
    field_ref = SObjectFieldSerializer(source="field", required=False)

    class Meta:
        model = SObjectPicklist
        fields = (
            "id",
            "values",
            "field",
            "field_ref",
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


class MeetingUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "first_name", "last_name", "email")


class MeetingWorkflowSerializer(serializers.ModelSerializer):
    org_ref = serializers.SerializerMethodField("get_org_ref")
    meeting_ref = MeetingFrontendSerializer(many=False, source="meeting", read_only=True)
    resource_ref = serializers.SerializerMethodField("get_resource_ref")
    is_completed = serializers.SerializerMethodField("get_completed_status")
    user_ref = MeetingUserSerializer(source="user")

    class Meta:
        model = MeetingWorkflow
        fields = (
            "id",
            "meeting",
            "meeting_ref",
            "resource_id",
            "resource_type",
            "resource_ref",
            "user",
            "user_ref",
            "org_ref",
            "is_completed",
        )

    def get_org_ref(self, instance):
        from managr.core.serializers import OrganizationSerializer

        return OrganizationSerializer(instance=instance.user.organization).data

    def get_completed_status(self, instance):
        form = instance.forms.filter(template__form_type="UPDATE").first()
        if form:
            if form.saved_data:
                return True
        return False

    def get_resource_ref(self, instance):
        from managr.salesforce.routes import routes

        if instance.resource_type:
            resource_type = instance.resource_type
            serializer = routes[resource_type]["serializer"]
            resource = routes[resource_type]["model"].objects.filter(id=instance.resource_id)
            if len(resource):
                return serializer(instance=resource.first()).data
            else:
                return None
        else:
            return None

