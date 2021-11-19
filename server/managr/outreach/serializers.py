from rest_framework import serializers
from rest_framework.exceptions import ValidationError, PermissionDenied

from .models import OutreachAccount, Sequence, Account, Prospect


class OutreachAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = OutreachAccount
        fields = (
            "id",
            "user",
            "mailbox",
            "outreach_id",
            "access_token",
            "refresh_token",
            "token_generated_date",
        )


class SequenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sequence
        fields = (
            "id",
            "sequence_id",
            "name",
            "owner",
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
            "prospect_id",
            "full_name",
            "email",
            "owner",
            "contact_id",
            "account",
            "created_at",
            "updated_at",
        )
