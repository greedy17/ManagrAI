from rest_framework import serializers
from datetime import datetime
from managr.organization.models import Organization
from managr.crm.models import BaseContact, BaseAccount, BaseOpportunity, ObjectField
from managr.meetings.serializers import MeetingFrontendSerializer
from managr.salesforce.exceptions import ResourceAlreadyImported
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
    field_ref = SObjectFieldSerializer(source="object_field", required=False)

    class Meta:
        model = SObjectPicklist
        fields = (
            "id",
            "values",
            "object_field",
            "field_ref",
            "salesforce_account",
            "picklist_for",
            "imported_by",
            "salesforce_object",
        )

    def to_internal_value(self, data):

        if data.get("picklist_for") not in ["", None]:
            data["object_field"] = (
                ObjectField.objects.filter(
                    imported_by__id=data.get("imported_by"),
                    api_name=data.get("picklist_for"),
                    crm_object=data.get("salesforce_object"),
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
        from managr.salesforce.routes import routes as sf_routes
        from managr.hubspot.routes import routes as hs_routes

        if instance.resource_type:
            routes = sf_routes if instance.user.crm == "SALESFORCE" else hs_routes
            resource_type = instance.resource_type
            serializer = routes[resource_type]["serializer"]
            resource = routes[resource_type]["model"].objects.filter(id=instance.resource_id)
            if len(resource):
                return serializer(instance=resource.first()).data
            else:
                return None
        else:
            return None


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
            "external_owner",
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
            acct = BaseAccount.objects.filter(
                integration_id=account, organization__users__id=imported_by
            ).first()
            acct = acct.id if acct else acct
            data.update({"account": acct})

        # remove contacts from validation
        internal_data = super().to_internal_value(data)
        return internal_data

class UserRefSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "full_name",
            "first_name",
            "last_name",
            "profile_photo",
        )

    def get_full_name(self, instance):
        return f"{instance.first_name} {instance.last_name}"


class OpportunitySerializer(serializers.ModelSerializer):
    owner_ref = UserRefSerializer(source="owner", required=False)
    account_ref = AccountSerializer(source="account", required=False)

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
            "account_ref",
            "stage",
            "owner",
            "owner_ref",
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
            acct = BaseAccount.objects.filter(
                integration_id=account, organization__users__id=imported_by
            ).first()
            acct = acct.id if acct else acct
            data.update({"account": acct})
        # if data.get("last_activity_date"):
        #     data["last_activity_date"] = self._format_date_time_from_api(data["last_activity_date"])
        # remove contacts from validation

        contacts = data.pop("contacts", [])
        contacts = BaseContact.objects.filter(integration_id__in=contacts).values_list(
            "id", flat=True
        )
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

