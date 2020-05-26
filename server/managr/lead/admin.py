from django.contrib import admin
from .models import ActionChoice, Lead
# Register your models here.


class CustomActionChoice(admin.ModelAdmin):

    model = ActionChoice


class CustomLead(admin.ModelAdmin):
    model = Lead


admin.site.register(Lead, CustomLead)
admin.site.register(ActionChoice, CustomActionChoice)
