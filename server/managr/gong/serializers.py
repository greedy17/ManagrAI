from rest_framework import serializers
from rest_framework.exceptions import ValidationError, PermissionDenied

from .models import GongAuthAccount, GongAccount, GongCall


class GongAuthSerializer(serializers.ModelSerializer):
    class Meta:
        model = GongAuthAccount
        fields = (
            "id",
            "organization",
            "access_token",
            "refresh_token",
            "token_generated_date",
            "admin",
        )


class GongAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = GongAccount
        fields = (
            "id",
            "auth_account",
            "user",
            "gong_id",
            "is_active",
            "email",
        )


class GongCallSerializer(serializers.ModelSerializer):
    crm = serializers.CharField(required=False, allow_null=True)
    crm_id = serializers.CharField(required=False, allow_null=True)
    client_id = serializers.CharField(required=False, allow_null=True)
    client_system = serializers.CharField(required=False, allow_null=True)

    class Meta:
        model = GongCall
        fields = ["id", "auth_account", "gong_id", "crm", "crm_id", "client_id", "client_system"]
