from django.contrib import admin
from . import models
from django.forms import ModelForm, Textarea

# Register your models here.


class CustomZoomMeetingForm(ModelForm):
    class Meta:
        model = models.ZoomMeeting
        fields = (
            "zoom_account",
            "account_id",
            "operator",
            "meeting_id",
            "meeting_uuid",
            "host_id",
            "topic",
            "type",
            "start_time",
            "end_time",
            "duration",
            "participants",
            "participants_count",
            "total_minutes",
            "original_duration",
        )


class CustomZoomMeeting(admin.ModelAdmin):
    form = CustomZoomMeetingForm
    list_filter = ("zoom_account__user",)


admin.site.register(models.ZoomAuthAccount)
admin.site.register(models.ZoomMeeting, CustomZoomMeeting)
