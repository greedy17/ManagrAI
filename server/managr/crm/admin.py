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


class CustomBaseOpportunity(admin.ModelAdmin):
    model = crm_models.BaseOpportunity
    list_display = ("name", "owner", "object_type")


# Register your models here.
admin.site.register(crm_models.BaseAccount)
admin.site.register(crm_models.BaseOpportunity, CustomBaseOpportunity)
admin.site.register(crm_models.BaseContact)
admin.site.register(crm_models.ObjectField, CustomObjectField)
