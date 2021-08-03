from django import forms
from django.contrib import admin
from . import models as models


# Register your models here.


class CustomAlertInstance(admin.ModelAdmin):
    model = models.AlertInstance
    list_filter = ("user__email", "user__organization")
    list_display = ("datetime_created", "template", "user", "sent_at")
    ordering = ("-datetime_created",)


admin.site.register(models.AlertConfig)
admin.site.register(models.AlertGroup)
admin.site.register(models.AlertMessageTemplate)
admin.site.register(models.AlertInstance, CustomAlertInstance)
admin.site.register(models.AlertOperand)
admin.site.register(models.AlertTemplate)
