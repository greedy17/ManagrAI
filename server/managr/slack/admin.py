from django.contrib import admin
from .models import OrganizationSlackIntegration, UserSlackIntegration

admin.site.register(OrganizationSlackIntegration)
admin.site.register(UserSlackIntegration)
