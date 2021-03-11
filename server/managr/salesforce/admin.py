from django.contrib import admin
from django import forms

from managr.slack.models import OrgCustomSlackFormInstance
from . import models as models


class SyncOperationForm(forms.ModelForm):
    class Meta:
        model = models.SFSyncOperation
        fields = (
            "user",
            "operations",
            "completed_operations",
            "failed_operations",
        )


class CustomSyncOperationAdmin(admin.ModelAdmin):
    form = SyncOperationForm
    list_filter = ("user",)


class CustomFormInstanceInline(admin.StackedInline):
    model = OrgCustomSlackFormInstance


class CustomMeetingWorkflow(admin.ModelAdmin):
    model = models.MeetingWorkflow
    inlines = (CustomFormInstanceInline,)


# Register your models here.
admin.site.register(models.SalesforceAuthAccount)
admin.site.register(models.SObjectField)
admin.site.register(models.SObjectValidation)
admin.site.register(models.SObjectPicklist)
admin.site.register(models.SFSyncOperation, CustomSyncOperationAdmin)
admin.site.register(models.MeetingWorkflow, CustomMeetingWorkflow)
