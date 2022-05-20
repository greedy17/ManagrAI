from django.db import models
from managr.core.models import TimeStampModel
from django.contrib.postgres.fields import JSONField, ArrayField


class Meeting(TimeStampModel):
    user = models.OneToOneField("core.User", on_delete=models.CASCADE, related_name="meetings")
    meeting_id = models.CharField(max_length=255, help_text="Aka meeting number")
    topic = models.CharField(max_length=255, null=True, blank=True)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
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

