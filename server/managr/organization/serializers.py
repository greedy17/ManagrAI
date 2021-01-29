import json
from rest_framework import serializers, status, filters, permissions
from rest_framework.exceptions import ValidationError, PermissionDenied
from rest_framework.response import Response

from managr.organization.models import ActionChoice
from managr.slack.serializers import OrganizationSlackIntegrationSerializer
from managr.utils.numbers import validate_phone_number
from managr.opportunity import constants as opp_consts

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
            "url",
            "type",
            "organization",
            "logo",
            "parent_integration_id",
            "integration_id",
            "integration_source",
        )
        read_only_fields = ()


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = (
            "id",
            "title",
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "mobile_phone",
            "account",
            "external_owner",
            "external_account",
            "user",
            "integration_source",
            "integration_id",
        )
        extra_kwargs = {}
