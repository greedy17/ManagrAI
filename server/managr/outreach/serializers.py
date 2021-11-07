from rest_framework import serializers
from rest_framework.exceptions import ValidationError, PermissionDenied

from .models import OutreachAuthAccount, OutreachAccount, Sequence, Account, Prospect


class OutreachAuthSerializer(serializers.ModelSerializer):
    class Meta:
        model = OutreachAuthAccount
        fields = (
            "id",
            "organization",
            "access_token",
            "refresh_token",
            "token_generated_date",
            "admin",
        )


class OutreachAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = OutreachAccount
        fields = (
            "id",
            "auth_account",
            "user",
            "outreach_id",
            "guid",
            "is_active",
            "email",
            "team_id",
        )


class SequenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sequence
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


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ("id", "account_id", "name", "owner", "created_at", "updated_at")


class ProspectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prospect
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
