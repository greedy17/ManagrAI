from rest_framework import serializers
from rest_framework.exceptions import ValidationError, PermissionDenied

from .models import SalesloftAuthAccount, SalesloftAccount, Cadence, SLAccount, People


class SalesloftAuthSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesloftAuthAccount
        fields = (
            "id",
            "organization",
            "access_token",
            "refresh_token",
            "token_generated_date",
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


class CadenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cadence
        fields = (
            "id",
            "cadence_id",
            "name",
            "owner",
            "is_team_cadence",
            "is_shared",
            "created_at",
            "updated_at",
        )


class SLAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = SLAccount
        fields = ("id", "account_id", "name", "owner", "created_at", "updated_at")


class PeopleSerializer(serializers.ModelSerializer):
    class Meta:
        model = People
        fields = (
            "id",
            "people_id",
            "first_name",
            "last_name",
            "full_name",
            "email",
            "owner",
            "account",
            "created_at",
            "updated_at",
        )
