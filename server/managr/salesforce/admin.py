from django.contrib import admin
from . import models as models
from django import forms


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


# Register your models here.
admin.site.register(models.SalesforceAuthAccount)
admin.site.register(models.SObjectField)
admin.site.register(models.SObjectValidation)
admin.site.register(models.SObjectPicklist)
admin.site.register(models.SFSyncOperation, CustomSyncOperationAdmin)
admin.site.register(models.MeetingWorkflow)
