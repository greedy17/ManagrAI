from rest_framework import serializers
from datetime import datetime
from managr.zoom.serializers import ZoomMeetingSerializer
from managr.organization.models import Organization
from managr.crm.models import BaseContact, BaseAccount, BaseOpportunity
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
    meeting_ref = serializers.SerializerMethodField("get_meeting_ref")
    is_completed = serializers.SerializerMethodField("get_completed_status")

    class Meta:
        model = MeetingWorkflow
        fields = ("id", "meeting", "meeting_ref", "resource_id", "resource_type", "is_completed")

    def get_meeting_ref(self, instance):
        from managr.core.serializers import MeetingPrepInstanceSerializer

        if instance.non_zoom_meeting is None:
            meeting = ZoomMeetingSerializer(instance=instance.meeting)
        else:
            meeting = MeetingPrepInstanceSerializer(instance=instance.non_zoom_meeting)
        return meeting.data

    def get_completed_status(self, instance):
        form = instance.forms.filter(template__form_type="UPDATE").first()
        if form:
            if form.saved_data:
                return True
        return False


class AccountSerializer(serializers.ModelSerializer):
    """
    Serializer for Accounts tied to organization
    Only Organization Managers can add, update, delete accounts
    Other users can list
    """

    class Meta:
        model = BaseAccount
        fields = (
            "id",
            "name",
            "organization",
            "integration_id",
            "integration_source",
            "imported_by",
            "owner",
            "secondary_data",
        )

    def to_internal_value(self, data):
        imported_by = data.get("imported_by")
        owner = data.get("external_owner", None)
        if not data.get("external_owner", None):
            data.update({"external_owner": ""})

        if owner:
            sf_account = (
                SalesforceAuthAccount.objects.filter(salesforce_id=owner)
                .select_related("user")
                .first()
            )
            user = sf_account.user.id if sf_account else sf_account
            data.update({"owner": user})
        org = Organization.objects.get(users__id=imported_by)
        data.update({"organization": org.id})
        # remove contacts from validation
        internal_data = super().to_internal_value(data)
        return internal_data


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = BaseContact
        fields = (
            "id",
            "email",
            "account",
            "external_owner",
            "external_account",
            "owner",
            "integration_source",
            "integration_id",
            "imported_by",
            "secondary_data",
        )
        extra_kwargs = {}

    def to_internal_value(self, data):
        imported_by = data.get("imported_by")
        owner = data.get("external_owner", None)
        account = data.get("external_account", None)
        if not data.get("external_account", None):
            data.update({"external_account": ""})
        if not data.get("external_owner", None):
            data.update({"external_owner": ""})
        if not data.get("email", None):
            data.update({"email": ""})

        if owner:
            sf_account = (
                SalesforceAuthAccount.objects.filter(salesforce_id=owner)
                .select_related("user")
                .first()
            )
            user = sf_account.user.id if sf_account else sf_account
            data.update({"owner": user})
        if account:
            acct = Account.objects.filter(
                integration_id=account, organization__users__id=imported_by
            ).first()
            acct = acct.id if acct else acct
            data.update({"account": acct})

        # remove contacts from validation
        internal_data = super().to_internal_value(data)
        return internal_data


class OpportunitySerializer(serializers.ModelSerializer):
    class Meta:
        model = BaseOpportunity
        fields = (
            "id",
            "integration_id",
            "integration_source",
            "name",
            "amount",
            "close_date",
            "forecast_category",
            "account",
            "stage",
            "owner",
            "last_stage_update",
            "last_activity_date",
            "external_account",
            "external_owner",
            "imported_by",
            "contacts",
            "is_stale",
            "secondary_data",
        )

    def _format_date_time_from_api(self, d):
        if d and len(d) > 10:
            return datetime.strptime(d, "%Y-%m-%dT%H:%M:%S.%f%z")
        elif d and len(d) <= 10:
            return datetime.strptime(d, "%Y-%m-%d")
        return None

    def to_internal_value(self, data):
        imported_by = data.get("imported_by")
        owner = data.get("external_owner", None)
        account = data.get("external_account", None)
        if not data.get("external_account", None):
            data.update({"external_account": ""})
        if not data.get("external_owner", None):
            data.update({"external_owner": ""})
        if owner:
            sf_account = (
                SalesforceAuthAccount.objects.filter(salesforce_id=owner)
                .select_related("user")
                .first()
            )
            user = sf_account.user.id if sf_account else sf_account
            data.update({"owner": user})
        if account:
            acct = Account.objects.filter(
                integration_id=account, organization__users__id=imported_by
            ).first()
            acct = acct.id if acct else acct
            data.update({"account": acct})
        if data.get("last_activity_date"):
            data["last_activity_date"] = self._format_date_time_from_api(data["last_activity_date"])
        # remove contacts from validation

        contacts = data.pop("contacts", [])
        contacts = Contact.objects.filter(integration_id__in=contacts).values_list("id", flat=True)
        data.update({"contacts": contacts})
        internal_data = super().to_internal_value(data)
        return internal_data

    def create(self, validated_data):
        try:
            return super().create(validated_data)
        except ResourceAlreadyImported:
            pass

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)
