from django.contrib import admin

# Register your models here.

from .models import HubspotAuthAccount, HSObjectFieldsOperation, HSSyncOperation, HObjectField

# Register your models here.


class CustomHubspotAuthAccountAdmin(admin.ModelAdmin):
    model = HubspotAuthAccount
    list_filter = ("user",)
    list_display = ["user", "datetime_created"]


admin.site.register(HubspotAuthAccount, CustomHubspotAuthAccountAdmin)
admin.site.register(HSObjectFieldsOperation)
admin.site.register(HSSyncOperation)
admin.site.register(HObjectField)

