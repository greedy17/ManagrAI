from django.contrib import admin
from managr.meetings.models import Meeting
from . import models as models

# Register your models here.


class CustomMeeting(admin.ModelAdmin):
    list_display = (
        "datetime_created",
        "topic",
        "provider",
        "user",
    )
    ordering = ("-datetime_created",)


admin.site.register(Meeting, CustomMeeting)
