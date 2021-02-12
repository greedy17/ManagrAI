from django.contrib import admin
from . import models as slack_models

admin.site.register(slack_models.OrganizationSlackIntegration)
admin.site.register(slack_models.OrgCustomSlackForm)
admin.site.register(slack_models.UserSlackIntegration)
