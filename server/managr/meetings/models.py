from django.db import models
from managr.core.models import TimeStampModel
from django.contrib.postgres.fields import JSONField, ArrayField
from managr.zoom.models import ZoomAuthAccount, ZoomMeeting
from managr.zoom.zoom_helper.models import ZoomMtg
from managr.core.models import NylasAuthAccount


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
    def recreate_from_zoom_meeting_model(cls, zoom_meeting_id):
        zoom_meeting = ZoomMeeting.objects.get(id=zoom_meeting_id)
        meeting_data = vars(zoom_meeting)
        zoom_account_id = meeting_data.get("zoom_account_id")
        zoom_account = ZoomAuthAccount.objects.get(id=zoom_account_id)
        participants = meeting_data.get("participants")
        workflow_ref = str(ZoomMeeting.workflow.id)
        print(zoom_account)
        print(participants)
        print(workflow_ref)
        return

