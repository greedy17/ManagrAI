from rest_framework import serializers
from rest_framework.exceptions import ValidationError, PermissionDenied

from .models import ZoomAuthAccount


class ZoomAuthRefSerializer(serializers.ModelSerializer):
    class Meta:
        model = ZoomAuthAccount
        fields = (
            "id",
            "email",
        )


class ZoomAuthSerializer(serializers.ModelSerializer):
    class Meta:
        model = ZoomAuthAccount
        fields = (
            "id",
            "user",
            "zoom_id",
            "first_name",
            "last_name",
            "email",
            "type",
            "role_name",
            "personal_meeting_url",
            "timezone",
            "verified",
            "dept",
            "pic_url",
            "pmi",
            "use_pmi",
            "host_key",
            "jid",
            "account_id",
            "language",
            "phone_country",
            "phone_number",
            "status",
            "access_token",
            "refresh_token",
            "token_generated_date",
            "token_scope",
        )
