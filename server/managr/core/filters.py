import django_filters
from django_filters.rest_framework import FilterSet
from .models import User


class UserFilterSet(FilterSet):
    for_slack = django_filters.CharFilter(method="for_slack")

    class Meta:
        model = User

    def for_slack(self, qs):
        qs = qs.filter(slack_account__isnull=False)
        return qs
