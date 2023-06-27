from django.contrib import admin
from managr.api.models import ManagrToken


class ManagrTokenntegrationInline(admin.ModelAdmin):
    model = ManagrToken
