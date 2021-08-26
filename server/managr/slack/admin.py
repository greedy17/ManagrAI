from django.contrib import admin
from . import models as slack_models


class CustomFormFieldInline(admin.StackedInline):
    model = slack_models.FormField
    fields = (
        "field",
        "order",
    )


class CustomOrgSlackForms(admin.ModelAdmin):
    model = slack_models.OrgCustomSlackForm
    inlines = (CustomFormFieldInline,)
    list_filter = ("organization",)


class CustomOrgSlackFormsInstance(admin.ModelAdmin):
    model = slack_models.OrgCustomSlackFormInstance
    list_filter = ("user", "user__organization", "template__form_type", "update_source")
    list_display = ("template", "user", "submission_date", "update_source")
    ordering = ("-datetime_created",)


admin.site.register(slack_models.OrgCustomSlackForm, CustomOrgSlackForms)
admin.site.register(slack_models.OrgCustomSlackFormInstance, CustomOrgSlackFormsInstance)
admin.site.register(slack_models.OrganizationSlackIntegration)
admin.site.register(slack_models.UserSlackIntegration)
admin.site.register(slack_models.FormField)
