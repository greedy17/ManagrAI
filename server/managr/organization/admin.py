from django.contrib import admin

from managr.slack.models import OrganizationSlackIntegration

from .models import Organization, Account, Contact, Stage, ActionChoice


class OrganizationSlackIntegrationInline(admin.StackedInline):
    model = OrganizationSlackIntegration


class CustomOrganization(admin.ModelAdmin):
    model = Organization
    inlines = (OrganizationSlackIntegrationInline,)
    list_display = ("name",)


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
                    "name",
                    "title",
                    "email",
                    "phone_number",
                    "mobile_phone",
                    "account",
                    "external_owner",
                    "external_account",
                    "user",
                ),
            },
        ),
    )


admin.site.register(Organization, CustomOrganization)
admin.site.register(Account, CustomAccount)

admin.site.register(Contact)
admin.site.register(ActionChoice)
admin.site.register(Stage)
