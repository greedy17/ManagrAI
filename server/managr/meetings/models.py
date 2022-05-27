import json
import pytz
from datetime import datetime
from django.db import models
from managr.core.models import TimeStampModel
from django.contrib.postgres.fields import JSONField, ArrayField
from managr.zoom.models import ZoomAuthAccount, ZoomMeeting
from managr.salesforce.models import MeetingWorkflow
from managr.zoom.zoom_helper.models import ZoomMtg


class Meeting(TimeStampModel):
    user = models.ForeignKey("core.User", on_delete=models.CASCADE, related_name="meetings")
    meeting_id = models.CharField(max_length=255, help_text="Aka meeting number")
    topic = models.CharField(max_length=255, null=True, blank=True)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    provider = models.CharField(max_length=255, null=True, blank=True)
    is_owner = models.BooleanField(default=True)
    participants = ArrayField(
        JSONField(max_length=128, default=dict),
        default=list,
        blank=True,
        null=True,
        help_text="Json object of participants",
    )
    meta_data = JSONField(
        default=dict, blank=True, null=True, help_text="Json object of extra meeting data"
    )

    @property
    def as_dict(self):
        return vars(self)

    @property
    def meeting_account(self):
        if self.provider == "Zoom" and self.is_owner:
            return self.user.zoom_account
        else:
            return self.user.nylas

    @property
    def zoom_adapter_class(self):
        return ZoomMtg(**(self.meta_data))

    def get_past_meeting_participants(self, access_token):
        if self.provider == "Zoom" and self.is_owner:
            self.participants = self.zoom_adapter_class.get_past_meeting_participants(access_token)
        self.save()
        return self

    @classmethod
    def recreate_from_zoom_meeting_model(cls, zoom_meeting_id, workflow_id):
        from managr.meetings.serializers import MeetingZoomSerializer

        zoom_meeting = ZoomMeeting.objects.filter(id=zoom_meeting_id).values()[0]
        zoom_account_id = zoom_meeting.pop("zoom_account_id")
        zoom_account = ZoomAuthAccount.objects.get(id=zoom_account_id)
        participants = zoom_meeting.pop("participants")
        zoom_meeting["workflow_ref"] = str(workflow_id)
        zoom_meeting["user"] = str(zoom_account.user.id)
        zoom_meeting["source"] = "Zoom"
        zoom_meeting.pop("id")
        zoom_meeting = json.loads(json.dumps(zoom_meeting, default=str))
        serializer = MeetingZoomSerializer(data=zoom_meeting)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        meeting = Meeting.objects.get(id=serializer.data.get("id"))
        meeting.participants = participants
        meeting.save()
        return

    @classmethod
    def recreate_from_non_zoom(cls, meeting_id, workflow_id):
        from managr.core.models import MeetingPrepInstance
        from managr.meetings.serializers import MeetingSerializer

        meeting = MeetingPrepInstance.objects.get(id=meeting_id)
        event_data = meeting.event_data
        event_data["workflow_ref"] = workflow_id
        meeting_data = {}
        start_time = datetime.utcfromtimestamp(int(event_data["times"]["start_time"]))
        end_time = datetime.utcfromtimestamp(int(event_data["times"]["end_time"]))
        formatted_start = start_time.astimezone(pytz.timezone(meeting.user.timezone))
        formatted_end = end_time.astimezone(pytz.timezone(meeting.user.timezone))
        meeting_data["start_time"] = formatted_start
        meeting_data["end_time"] = formatted_end
        meeting_data["title"] = event_data["title"]
        meeting_data["provider"] = (
            "Zoom" if event_data["provider"] == "Zoom Meeting" else "Google Meet"
        )
        meeting_data["user"] = meeting.user.id
        meeting_data["meeting_uuid"] = "None"
        meeting_data["meta_data"] = event_data
        serializer = MeetingSerializer(data=meeting_data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        new_meeting = Meeting.objects.get(id=serializer.data.get("id"))
        new_meeting.participants = meeting.participants
        new_meeting.is_owner = True if meeting.user.email in event_data["owner"] else False
        new_meeting.save()
        return
