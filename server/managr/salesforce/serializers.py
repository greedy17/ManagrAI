from rest_framework import serializers
from rest_framework.exceptions import ValidationError, PermissionDenied

from .models import SalesforceAuthAccount, SObjectPicklist, SObjectField, SObjectValidation


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
            "object_fields",
            "is_busy",
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
            "options",
            "reference_display_label",
            "integration_source",
            "integration_id",
            "is_public",
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
        )


class SObjectPicklisterializer(serializers.ModelSerializer):
    class Meta:
        model = SObjectPicklist
        fields = (
            "id",
            "label",
            "attributes",
            "valid_for",
            "value",
            "field",
            "salesforce_object",
            "salesforce_account",
        )
