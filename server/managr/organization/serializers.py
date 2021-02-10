import json
from rest_framework import serializers, status, filters, permissions
from rest_framework.exceptions import ValidationError, PermissionDenied
from rest_framework.response import Response

from managr.organization.models import ActionChoice
from managr.slack.serializers import OrganizationSlackIntegrationSerializer
from managr.utils.numbers import validate_phone_number
from managr.opportunity import constants as opp_consts
from managr.salesforce.models import SalesforceAuthAccount
from .models import Organization, Account, Contact, Stage


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = (
            "name",
            "photo",
            "state",
            "is_trial",
            "slack_integration",
        )


class ActionChoiceRefSerializer(serializers.ModelSerializer):
    """
    Read Only Ref Serializer for ActionChoices Tied to an Organization
    """

    class Meta:
        model = ActionChoice
        fields = (
            "title",
            "description",
        )


class StageSerializer(serializers.ModelSerializer):
    def to_internal_value(self, data):
        forecast_category = data.get("forecast_category", None)
        if forecast_category:
            formatted_category = None
            for category in opp_consts.FORECAST_CHOICES:
                if category[1] == forecast_category:
                    formatted_category = category[0]
            if formatted_category:
                data.update({"forecast_category": formatted_category})
        return super().to_internal_value(data)

    class Meta:
        model = Stage
        fields = (
            "id",
            "integration_id",
            "integration_source",
            "label",
            "description",
            "color",
            "value",
            "organization",
            "order",
            "is_closed",
            "is_won",
            "is_active",
            "forecast_category",
            "imported_by",
        )


class AccountSerializer(serializers.ModelSerializer):
    """
    Serializer for Accounts tied to organization
    Only Organization Managers can add, update, delete accounts
    Other users can list
    """

    class Meta:
        model = Account
        fields = (
            "id",
            "name",
            "organization",
            "parent_integration_id",
            "integration_id",
            "integration_source",
            "imported_by",
            "owner",
            "secondary_data",
        )

    def to_internal_value(self, data):
        imported_by = data.get("imported_by")
        owner = data.get("external_owner", None)
        parent = data.get("parent_integration_id", None)

        if not data.get("parent_integration_id", None):
            data.update({"parent_integration_id": ""})
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
        if parent:
            acct = Account.objects.filter(
                integration_id=parent, organization__users__id=imported_by
            ).first()
            acct = acct.id if acct else acct
            data.update({"parent": acct})
        org = Organization.objects.get(users__id=imported_by)
        data.update({"organization": org.id})
        # remove contacts from validation
        internal_data = super().to_internal_value(data)
        return internal_data


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
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
