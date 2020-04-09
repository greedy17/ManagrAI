from django.contrib import admin

# Register your models here.

from .models import Organization, Account, Lead, Contact


class CustomOrganization(admin.ModelAdmin):
    model = Organization
    list_display = ('name',)


class CustomAccount(admin.ModelAdmin):
    model = Account
    list_display = ('name', 'url',)


class CustomLead(admin.ModelAdmin):
    model = Account
    list_display = ('account', 'organization',)


admin.site.register(Organization, CustomOrganization)
admin.site.register(Account, CustomAccount)
admin.site.register(Lead, CustomLead)
admin.site.register(Contact)
