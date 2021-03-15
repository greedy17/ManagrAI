from django.contrib import admin
from django import forms

# Register your models here.

from .models import Opportunity, Lead

# Register your models here.


class OpportunityForm(forms.ModelForm):
    class Meta:
        model = Opportunity
        fields = (
            "integration_id",
            "integration_source",
            "name",
            "amount",
            "close_date",
            "forecast_category",
            "account",
            "stage",
            "owner",
            "last_stage_update",
            "last_activity_date",
            "external_account",
            "external_owner",
            "imported_by",
            "contacts",
            "secondary_data",
            "is_stale",
        )


class CustomOpportunityAdmin(admin.ModelAdmin):
    form = OpportunityForm
    list_filter = ("owner",)


admin.site.register(Opportunity, CustomOpportunityAdmin)
admin.site.register(Lead)
