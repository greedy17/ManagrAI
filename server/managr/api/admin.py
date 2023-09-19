from django.contrib import admin
from managr.api.models import ManagrToken


class ManagrTokenntegrationInline(admin.ModelAdmin):
    model = ManagrToken

    list_display = ("user",)


admin.site.register(ManagrToken, ManagrTokenntegrationInline)
