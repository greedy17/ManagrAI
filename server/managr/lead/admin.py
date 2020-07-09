from django.contrib import admin
from .models import ActionChoice, Lead, List, LeadActivityLog
# Register your models here.


class CustomActionChoice(admin.ModelAdmin):

    model = ActionChoice


class CustomLead(admin.ModelAdmin):
    model = Lead


class CustomList(admin.ModelAdmin):
    model = List


admin.site.register(Lead, CustomLead)
admin.site.register(ActionChoice, CustomActionChoice)
admin.site.register(List, CustomList)
admin.site.register(LeadActivityLog)
