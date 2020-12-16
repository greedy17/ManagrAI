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
            "password",
            "start_url",
            "join_url",
            "participants",
            "lead",
            "notification_attempts",
            "scoring_in_progress",
            "current_interaction",
            "is_closed",
            "interaction_status",
            "participants_count",
            "total_minutes",
            "meeting_score",
            "meeting_score_components",
            "original_duration",
        )


class CustomZoomMeeting(admin.ModelAdmin):
    form = CustomZoomMeetingForm
    inlines = (MeetinReviewInline,)


admin.site.register(models.ZoomAuthAccount)
admin.site.register(models.ZoomMeeting, CustomZoomMeeting)
