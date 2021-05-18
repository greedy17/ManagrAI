from rest_framework import serializers
from rest_framework.exceptions import ValidationError, PermissionDenied

from .models import ZoomAuthAccount, ZoomMeeting


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
            "email",
            "type",
            "role_name",
            "timezone",
            "account_id",
            "language",
            "status",
            "access_token",
            "refresh_token",
            "token_generated_date",
            "token_scope",
        )


class ZoomMeetingWebhookSerializer(serializers.ModelSerializer):
    """
    special serializer for events coming from the webhook that are different in structure
    to data coming from the django serializer that creates an entry in our db
    """

    class Meta:
        model = ZoomMeeting
        fields = (
            "id",
            "zoom_account",
            "account_id",
            "operator",
            "meeting_id",
            "meeting_uuid",
            "host_id",
            "topic",
            "type",
            "start_time",
            "timezone",
            "duration",
            "occurences",
            "operator_id",
            "operation",
            "original_duration",
        )


class ZoomMeetingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ZoomMeeting
        fields = (
            "id",
            "zoom_account",
            "account_id",
            "operator",
            "meeting_id",
            "meeting_uuid",
            "host_id",
            "topic",
            "type",
            "start_time",
            "duration",
            "operation",
            "timezone",
            "occurences",
            "password",
            "operator_id",
            "status",
            "start_url",
            "join_url",
            "recurrence",
            "participants",
            "end_time",
            "participants_count",
            "total_minutes",
            "original_duration",
        )
