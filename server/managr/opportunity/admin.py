from django.contrib import admin
from django import forms

# Register your models here.

from .models import Opportunity

# Register your models here.


class OpportunityForm(forms.ModelForm):
    class Meta:
        model = Opportunity
        fields = (
            "integration_id",
            "integration_source",
            "title",
            "amount",
            "close_date",
            "forecast_category",
        )


class CustomOpportunityAdmin(admin.ModelAdmin):
    form = OpportunityForm
    list_filter = ("owner",)


admin.site.register(Opportunity, CustomOpportunityAdmin)
