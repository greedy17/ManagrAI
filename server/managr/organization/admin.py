from django.contrib import admin

from managr.slack.models import OrganizationSlackIntegration

from .models import Organization, Account, Contact, Stage


class OrganizationSlackIntegrationInline(admin.StackedInline):
    model = OrganizationSlackIntegration


class CustomOrganization(admin.ModelAdmin):
    model = Organization
    inlines = (OrganizationSlackIntegrationInline,)
    list_display = (
        "name",
        "message_auth_count",
    )


class CustomAccount(admin.ModelAdmin):
    model = Account
    list_display = (
        "name",
        "url",
    )


class CustomContact(admin.ModelAdmin):
    model = Contact
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "email",
                    "phone_number_1",
                    "phone_number_2",
                    "account",
                ),
            },
        ),
    )


admin.site.register(Organization, CustomOrganization)
admin.site.register(Account, CustomAccount)

admin.site.register(Contact)
admin.site.register(Stage)
