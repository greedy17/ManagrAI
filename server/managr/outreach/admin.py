from django.contrib import admin
from . import models as models

# Register your models here.


class CustomOutreachAccount(admin.ModelAdmin):
    model = models.OutreachAccount
    list_display = ("datetime_created", "user")
    ordering = ("-datetime_created",)


class CustomAccount(admin.ModelAdmin):
    model = models.Account
    list_display = ("datetime_created", "name", "owner")
    ordering = ("-datetime_created",)


class CustomSequence(admin.ModelAdmin):
    model = models.Sequence
    list_display = ("datetime_created", "name", "owner")
    ordering = ("-datetime_created",)


class CustomProspect(admin.ModelAdmin):
    model = models.Prospect
    list_display = ("datetime_created", "full_name", "owner")
    ordering = ("-datetime_created",)


admin.site.register(models.OutreachAccount, CustomOutreachAccount)
admin.site.register(models.Sequence, CustomSequence)
admin.site.register(models.Account, CustomAccount)
admin.site.register(models.Prospect, CustomProspect)
