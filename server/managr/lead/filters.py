import django_filters
from django_filters.rest_framework import FilterSet
from django_filters import OrderingFilter
from itertools import chain
from django.db.models import F, Q, Count, Max, Min, DateTimeField, Value, Case, When
from django.db.models.functions import Lower
from .models import Lead


class LeadFilterSet(FilterSet):
    """
        this filters for rating 1-5
        on_list is a filter set to only show leads currently on a list or leads that are currently not on a list
        is_claimed will return a list of claimed or unclaimed leads

    """
    on_list = django_filters.BooleanFilter(method="list_count")
    is_claimed = django_filters.BooleanFilter(method="claim_status")
    by_list = django_filters.CharFilter(method="retrieve_users_in_list")

    class Meta:
        model = Lead
        fields = ['rating', 'on_list', 'is_claimed', 'by_list']

    def list_count(self, queryset, name, value):
        """ filter leads by list count """
        if value:
            return queryset.annotate(len_lists=Count('lists')).filter(len_lists__gt=0)
        else:
            return queryset.annotate(len_lists=Count('lists')).filter(len_lists__lt=1)

    def claim_status(self, queryset, name, value):
        """ checks if the claimed_by field is null """
        if value:
            return queryset.filter(claimed_by__isnull=False)
        return queryset.filter(claimed_by__isnull=True)

    def retrieve_users_in_list(self, queryset, name, value):
        """ Lists will not return leads by default """

        if value:
            return queryset.filter(lists=value)
        else:
            return queryset.all()
