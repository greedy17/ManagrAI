import django_filters
from datetime import datetime
from django_filters.rest_framework import FilterSet
from .models import AlertInstance


class AlertInstanceFilterSet(FilterSet):
    by_config = django_filters.CharFilter(method="for_config")

    class Meta:
        model = AlertInstance
        fields = ["config_id"]

    def for_config(self, qs, name, value):
        by_config = qs.filter(config__id=value)
        last = by_config.first()
        if last and last.datetime_created.date() == datetime.today().date():
            instances = qs.filter(config__id=value, invocation=last.invocation,)
            return instances
        return AlertInstance.objects.none()
