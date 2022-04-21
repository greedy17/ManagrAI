import django_filters
from datetime import datetime
from django_filters.rest_framework import FilterSet
from .models import AlertInstance, AlertTemplate


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


class AlertTemplateFilterSet(FilterSet):
    for_pipeline = django_filters.BooleanFilter(method="by_pipeline")

    def by_pipeline(self, qs, name, value):
        user = qs[0].user
        if value and user.user_level == "REP":
            user_targeted = AlertTemplate.objects.filter(
                configs__alert_targets__contains=[str(user.id)]
            ).exclude(user=user)

            return qs | user_targeted
        else:
            return qs
