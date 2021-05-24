from django.contrib import admin
from django import forms

from managr.slack.models import OrgCustomSlackFormInstance
from . import models as models


class SyncResourceForm(forms.ModelForm):
    class Meta:
        model = models.SFResourceSync
        fields = (
            "user",
            "operations",
            "completed_operations",
            "failed_operations",
            "operation_type",
        )


class CustomSyncOperationAdmin(admin.ModelAdmin):
    form = SyncResourceForm
    list_filter = ("user",)
    ordering = ("-datetime_created",)


class CustomFormInstanceInline(admin.StackedInline):
    model = OrgCustomSlackFormInstance


class CustomMeetingWorkflow(admin.ModelAdmin):
    model = models.MeetingWorkflow
    inlines = (CustomFormInstanceInline,)
    list_filter = ("user__email",)
    list_display = (
        "datetime_created",
        "meeting",
        "progress",
    )
    ordering = ("-datetime_created",)


class CustomSObjectField(admin.ModelAdmin):
    model = models.SObjectField
    list_filter = (
        "salesforce_account__user",
        "salesforce_object",
    )
    list_display = (
        "label",
        "salesforce_object",
        "last_edited",
        "salesforce_account",
    )
    ordering = ("-last_edited",)


class CustomPicklistValue(admin.ModelAdmin):
    model = models.SObjectPicklist
    list_filter = (
        "salesforce_account__user",
        "salesforce_object",
    )


# Register your models here.
admin.site.register(models.SalesforceAuthAccount)
admin.site.register(models.SObjectField, CustomSObjectField)
admin.site.register(models.SObjectValidation)
admin.site.register(models.SObjectPicklist, CustomPicklistValue)
admin.site.register(models.SFObjectFieldsOperation)
admin.site.register(models.SFResourceSync, CustomSyncOperationAdmin)
admin.site.register(models.MeetingWorkflow, CustomMeetingWorkflow)
