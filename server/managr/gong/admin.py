from django.contrib import admin
from . import models as models

admin.site.register(models.GongAuthAccount)
admin.site.register(models.GongAccount)
admin.site.register(models.GongCall)


class CustomGongCall(admin.ModelAdmin):
    model = models.GongCall
    list_display = ("datetime_created", "auth_account", "crm_id")
    list_filter = ("auth_account",)
    ordering = ("-datetime_created",)
