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
    list_display = (
        "datetime_created",
        "user",
        "progress",
    )


class CustomSyncFieldOperationAdmin(admin.ModelAdmin):
    model = models.SFObjectFieldsOperation
    list_display = (
        "datetime_created",
        "user",
        "progress",
    )
    list_filter = ("user",)
    ordering = ("-datetime_created",)


class CustomFormInstanceInline(admin.StackedInline):
    model = OrgCustomSlackFormInstance
    exclude = ["alert_instance_id"]
    readonly_fields = [
        "saved_data",
        "previous_data",
        "user",
        "template",
    ]
    extra = 0


class CustomMeetingWorkflow(admin.ModelAdmin):
    model = models.MeetingWorkflow
    inlines = (CustomFormInstanceInline,)
    list_filter = ("user__email",)
    list_display = (
        "datetime_created",
        "meeting",
        "progress",
    )
    readonly_fields = ["user", "meeting", "non_zoom_meeting"]
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
    list_display = (
        "salesforce_account",
        "salesforce_object",
        "field",
    )


# Register your models here.
admin.site.register(models.SalesforceAuthAccount)
admin.site.register(models.SObjectField, CustomSObjectField)
admin.site.register(models.SObjectValidation)
admin.site.register(models.SObjectPicklist, CustomPicklistValue)
admin.site.register(models.SFObjectFieldsOperation, CustomSyncFieldOperationAdmin)
admin.site.register(models.SFResourceSync, CustomSyncOperationAdmin)
admin.site.register(models.MeetingWorkflow, CustomMeetingWorkflow)
