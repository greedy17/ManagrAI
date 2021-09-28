from rest_framework import serializers
from rest_framework.exceptions import ValidationError, PermissionDenied

from .models import GongAuthAccount, GongAccount


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
