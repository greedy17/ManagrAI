import django_filters
from django_filters.rest_framework import FilterSet
from django_filters import OrderingFilter
from django.db.models import IntegerField, F
from django.db.models.functions import Cast
from . import models as sf_models

sobject_comparison = {
    "EQUALS": "%s",
    "GREATER_THAN": "%s__gt",
    "GREATER_THAN_EQUALS": "%s__gte",
    "LESS_THAN": "%s__lt",
    "LESS_THAN_EQUALS": "%s__lte",
    "CONTAINS": "%s__icontains",
    "RANGE": "%s__range",
    "NOT_EQUALS": "%s",
}


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


class SalesforceSObjectFilterSet(FilterSet):

    for_filter = django_filters.CharFilter(method="for_filter")

    def for_filter(qs, filters):
        for filter in filters:
            filter_field = f"secondary_data__{sobject_comparison[filter[0]]}"
            new_query = filter_field % filter[1]
            if filter[0] == "NOT_EQUALS":
                qs = qs.exclude(**{new_query: filter[2]})
            else:
                qs = qs.filter(**{new_query: filter[2]})
        return qs
