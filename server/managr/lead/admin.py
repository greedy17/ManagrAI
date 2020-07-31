from django.contrib import admin

# Register your models here.
from .models import ActionChoice, Lead, List, Reminder, Notification, Forecast, LeadActivityLog


class CustomActionChoice(admin.ModelAdmin):

    model = ActionChoice


class ForecastInline(admin.StackedInline):
    model = Forecast


class CustomLead(admin.ModelAdmin):
    model = Lead
    inlines = (ForecastInline,)


class CustomList(admin.ModelAdmin):
    model = List


admin.site.register(Lead, CustomLead)
admin.site.register(ActionChoice, CustomActionChoice)
admin.site.register(List, CustomList)
admin.site.register(LeadActivityLog)
admin.site.register(Reminder)
admin.site.register(Notification)
