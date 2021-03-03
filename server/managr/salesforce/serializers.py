from rest_framework import serializers
from rest_framework.exceptions import ValidationError, PermissionDenied

from .models import SalesforceAuthAccount


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
