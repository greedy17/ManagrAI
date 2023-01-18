from django.contrib import admin
from django import forms

# Register your models here.

from .models import (
    HubspotAuthAccount,
    HSObjectFieldsOperation,
    HSSyncOperation,
    HObjectField,
    Company,
    Deal,
    HubspotContact,
)

# Register your models here.


class CustomHubspotAuthAccountAdmin(admin.ModelAdmin):
    model = HubspotAuthAccount
    list_filter = ("user",)
    list_display = ["user", "datetime_created"]


class SyncResourceForm(forms.ModelForm):
    class Meta:
        model = HSSyncOperation
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
    model = HSObjectFieldsOperation
    list_display = (
        "datetime_created",
        "user",
        "progress",
    )
    list_filter = ("user",)
    ordering = ("-datetime_created",)


class CustomCompanyAdmin(admin.ModelAdmin):
    model = Company
    list_display = ("datetime_created", "name", "owner")
    list_filter = ("owner",)
    ordering = ("-datetime_created",)


class CustomDealAdmin(admin.ModelAdmin):
    model = Deal
    list_display = ("datetime_created", "name", "owner")
    list_filter = ("owner",)
    ordering = ("-datetime_created",)


class CustomHubspotContactAdmin(admin.ModelAdmin):
    model = HubspotContact
    list_display = ("datetime_created", "email", "owner")
    list_filter = ("owner",)
    ordering = ("-datetime_created",)


class CustomHObjectField(admin.ModelAdmin):
    model = HObjectField
    list_display = ("id", "label")
    list_filter = ("hubspot_object",)


admin.site.register(HubspotAuthAccount, CustomHubspotAuthAccountAdmin)
admin.site.register(HSObjectFieldsOperation, CustomSyncFieldOperationAdmin)
admin.site.register(HSSyncOperation, CustomSyncOperationAdmin)
