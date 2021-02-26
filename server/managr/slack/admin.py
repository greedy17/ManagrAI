from django.contrib import admin
from . import models as slack_models


class CustomOrgSlackForms(admin.ModelAdmin):
    model = slack_models.OrgCustomSlackForm
    list_filter = ("organization",)


admin.site.register(slack_models.OrgCustomSlackForm, CustomOrgSlackForms)
admin.site.register(slack_models.OrganizationSlackIntegration)
admin.site.register(slack_models.UserSlackIntegration)
