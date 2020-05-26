from django.contrib import admin

# Register your models here.

from .models import Organization, Account,  Contact


class CustomOrganization(admin.ModelAdmin):
    model = Organization
    list_display = ('name',)


class CustomAccount(admin.ModelAdmin):
    model = Account
    list_display = ('name', 'url',)


class CustomContact(admin.ModelAdmin):
    model = Contact
    fieldsets = (
        (None, {
            "fields": (
                'first_name', 'last_name', 'email', 'phone_number_1', 'phone_number_2', 'account'
            ),
        }),
    )


admin.site.register(Organization, CustomOrganization)
admin.site.register(Account, CustomAccount)

admin.site.register(Contact)
