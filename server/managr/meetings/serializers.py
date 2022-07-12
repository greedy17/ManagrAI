from rest_framework import serializers
import json
from datetime import datetime
import pytz
from managr.meetings.models import Meeting


class MeetingZoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meeting
        fields = (
            "id",
            "user",
            "meeting_id",
            "topic",
            "start_time",
            "end_time",
            "provider",
            "meta_data",
        )

    def to_internal_value(self, data):
        user = data.pop("user")
        model_data = {
            "user": user,
            "meeting_id": data["meeting_uuid"],
            "topic": data["topic"],
            "start_time": data["start_time"],
            "end_time": data["end_time"],
            "provider": data["source"],
            "meta_data": dict(data),
        }
        return super().to_internal_value(model_data)


class MeetingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meeting
        fields = (
            "id",
            "user",
            "meeting_id",
            "topic",
            "start_time",
            "end_time",
            "provider",
            "meta_data",
        )

    def to_internal_value(self, data):
        user = data.pop("user")
        utc_start = datetime.utcfromtimestamp(data["when"]["start_time"])
        utc_end = datetime.utcfromtimestamp(data["when"]["end_time"])
        tz = pytz.timezone(user.timezone)
        conferencing = data.get("conferencing", None)
        provider = conferencing["provider"] if conferencing else "None"
        local_start = utc_start.astimezone(tz)
        local_end = utc_end.astimezone(tz)
        model_data = {
            "user": user.id,
            "meeting_id": data.pop("id"),
            "topic": data["title"],
            "start_time": local_start,
            "end_time": local_end,
            "provider": provider,
            "meta_data": json.dumps(data),
        }
        return super().to_internal_value(model_data)


class MeetingFrontendSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meeting
        fields = (
            "id",
            "user",
            "meeting_id",
            "topic",
            "start_time",
            "end_time",
            "participants",
            "provider",
            "meta_data",
        )


class MeetingConverterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meeting
        fields = (
            "id",
            "user",
            "meeting_id",
            "topic",
            "start_time",
            "end_time",
            "provider",
            "meta_data",
        )

    def to_internal_value(self, data):
        user = data.pop("user")
        model_data = {
            "user": user,
            "meeting_id": "None",
            "topic": data["title"],
            "start_time": data.pop("start_time"),
            "end_time": data.pop("end_time"),
            "provider": data["provider"],
            "meta_data": data,
        }
        return super().to_internal_value(model_data)
