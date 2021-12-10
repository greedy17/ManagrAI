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
    list_display = ("name",)
    list_filter = ("owner",)
    list_display = (
        "name",
        "last_edited",
    )


class CustomContact(admin.ModelAdmin):
    model = Contact
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "email",
                    "account",
                    "external_owner",
                    "external_account",
                    "owner",
                    "imported_by",
                    "secondary_data",
                ),
            },
        ),
    )
    list_filter = ("owner",)
    list_display = (
        "email",
        "imported_by",
        "last_edited",
    )
    readonly_fields = ["secondary_data", "imported_by", "account"]


admin.site.register(Organization, CustomOrganization)
admin.site.register(Account, CustomAccount)

admin.site.register(Contact, CustomContact)
admin.site.register(ActionChoice)
admin.site.register(Stage)
