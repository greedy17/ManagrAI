from django.contrib import admin
from managr.crm import models as crm_models


class CustomObjectField(admin.ModelAdmin):
    model = crm_models.ObjectField
    list_display = (
        "user",
        "label",
        "crm_object",
        "data_type",
    )
    search_fields = ("label",)
    list_filter = ("crm_object", "user__organization")


class CustomBaseOpportunity(admin.ModelAdmin):
    model = crm_models.BaseOpportunity
    list_display = ("name", "owner")
    list_filter = ("owner__organization", "owner")


class CustomBaseAccount(admin.ModelAdmin):
    model = crm_models.BaseAccount
    list_display = ("name", "owner")
    list_filter = ("owner__organization", "owner")


class CustomBaseContact(admin.ModelAdmin):
    model = crm_models.BaseContact
    list_display = ("email", "owner")
    list_filter = ("owner__organization", "owner")


# Register your models here.
admin.site.register(crm_models.BaseAccount, CustomBaseAccount)
admin.site.register(crm_models.BaseOpportunity, CustomBaseOpportunity)
admin.site.register(crm_models.BaseContact, CustomBaseContact)
admin.site.register(crm_models.ObjectField, CustomObjectField)
