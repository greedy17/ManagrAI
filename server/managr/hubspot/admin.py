from django.contrib import admin

# Register your models here.

from .models import HubspotAuthAccount

# Register your models here.


class CustomHubspotAuthAccountAdmin(admin.ModelAdmin):
    model = HubspotAuthAccount
    list_filter = ("user",)
    list_display = ["user", "datetime_created"]


admin.site.register(HubspotAuthAccount, CustomHubspotAuthAccountAdmin)
