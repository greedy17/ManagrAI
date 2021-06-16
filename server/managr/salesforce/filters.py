import django_filters
from django_filters.rest_framework import FilterSet
from django_filters import OrderingFilter
from django.db.models import IntegerField, F
from django.db.models.functions import Cast
from . import models as sf_models


class SObjectFieldFilterSet(FilterSet):

    for_alerts = django_filters.CharFilter(method="by_alerts")

    class Meta:
        model = sf_models.SObjectField
        fields = (
            "salesforce_object",
            "createable",
            "updateable",
            "filterable",
        )

    def by_alerts(self, qs, name, value):
        """returns qs with field types that we support for alerts as list"""

        if value:
            return qs.filter(
                data_type__in=[
                    "Currency",
                    "String",
                    "Float",
                    "Date",
                    "DateTime",
                    "Int",
                    "Double",
                    "Long",
                    "Boolean",
                    "Picklist",
                    "Email",
                ]
            )
        return qs
