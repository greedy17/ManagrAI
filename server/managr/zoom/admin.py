from django.contrib import admin
from . import models
from django.forms import ModelForm, Textarea

# Register your models here.


class MeetinReviewInline(admin.StackedInline):
    model = models.MeetingReview


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
            "duration",
            "participants",
            "participants_count",
            "total_minutes",
            "meeting_score_components",
            "original_duration",
        )


class CustomZoomMeeting(admin.ModelAdmin):
    form = CustomZoomMeetingForm
    inlines = (MeetinReviewInline,)
    list_filter = ("zoom_account__user",)


admin.site.register(models.ZoomAuthAccount)
admin.site.register(models.MeetingReview)
admin.site.register(models.ZoomMeeting, CustomZoomMeeting)
