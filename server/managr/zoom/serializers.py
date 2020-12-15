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
            "lead",
            "should_track",
            "end_time",
            "participants_count",
            "total_minutes",
        )
