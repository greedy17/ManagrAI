import json
from rest_framework import serializers, status, filters, permissions
from rest_framework.exceptions import ValidationError, PermissionDenied
from rest_framework.response import Response

from managr.opportunity.models import ActionChoice
from managr.slack.serializers import OrganizationSlackIntegrationSerializer
from managr.utils.numbers import validate_phone_number

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
    class Meta:
        model = Stage
        fields = "__all__"


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
        )
        read_only_fields = ()


class ContactSerializer(serializers.ModelSerializer):
    def validate_phone_number_1(self, value):
        if value:
            try:
                validate_phone_number(value)
            except ValueError:
                raise ValidationError()
        return value

    def validate_phone_number_2(self, value):
        if value:
            try:
                validate_phone_number(value)
            except ValueError:
                raise ValidationError()
        return value

    class Meta:
        model = Contact
        fields = (
            "id",
            "title",
            "full_name",
            "first_name",
            "last_name",
            "email",
            "phone_number_1",
            "phone_number_2",
            "account",
        )
        extra_kwargs = {
            "email": {"required": True},
            "account": {"required": True},
        }
