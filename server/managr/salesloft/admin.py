from django.contrib import admin
from . import models as models

# Register your models here.


class CustomSalesloftAuthAccount(admin.ModelAdmin):
    model = models.SalesloftAuthAccount
    list_display = ("datetime_created", "admin")
    list_filter = ("organization",)
    ordering = ("-datetime_created",)


class CustomSalesloftAccount(admin.ModelAdmin):
    model = models.SalesloftAccount
    list_display = ("datetime_created", "user")
    ordering = ("-datetime_created",)


class CustomSLAccount(admin.ModelAdmin):
    model = models.SLAccount
    list_display = ("datetime_created", "name", "owner")
    list_filter = ("owner", "owner__auth_account__organization")
    ordering = ("-datetime_created",)


class CustomCadence(admin.ModelAdmin):
    model = models.Cadence
    list_display = ("datetime_created", "name", "owner")
    list_filter = ("owner", "owner__auth_account__organization")
    ordering = ("-datetime_created",)


class CustomPeople(admin.ModelAdmin):
    model = models.People
    list_display = ("datetime_created", "full_name", "owner")
    list_filter = ("owner", "account")
    ordering = ("-datetime_created",)


admin.site.register(models.SalesloftAuthAccount, CustomSalesloftAuthAccount)
admin.site.register(models.SalesloftAccount, CustomSalesloftAccount)
admin.site.register(models.Cadence, CustomCadence)
admin.site.register(models.SLAccount, CustomSLAccount)
admin.site.register(models.People, CustomPeople)
