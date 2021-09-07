from rest_framework import serializers
from rest_framework.exceptions import ValidationError, PermissionDenied

from .models import SalesloftAuthAccount, SalesloftAccount


class SalesloftAuthSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesloftAuthAccount
        fields = (
            "id",
            "organization",
            "access_token",
            "refresh_token",
            "admin",
        )


class SalesloftAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesloftAccount
        fields = (
            "id",
            "auth_account",
            "user",
            "salesloft_id",
            "guid",
            "is_active",
            "email",
            "team_id",
        )
