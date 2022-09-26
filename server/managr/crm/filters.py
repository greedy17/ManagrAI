import django_filters
from django_filters.rest_framework import FilterSet
from managr.crm.models import ObjectField


class ObjectFieldFilterSet(FilterSet):

    for_alerts = django_filters.CharFilter(method="by_alerts")

    class Meta:
        model = ObjectField
        fields = (
            "crm_object",
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
