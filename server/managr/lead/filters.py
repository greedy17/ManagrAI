import django_filters
from django_filters.rest_framework import FilterSet
from django_filters import OrderingFilter
from itertools import chain
from django.db.models import F, Q, Count, Max, Min, DateTimeField, Value, Case, When
from django.db.models.functions import Lower
from .models import Lead


class LeadFilterSet(FilterSet):
    on_list = django_filters.CharFilter(method="list_count")

    class Meta:
        model = Lead
        fields = ['rating', 'on_list']

    def list_count(self, queryset, name, value):
        """ filter leads by list count """
        if value.strip().lower() == 'true':
            return queryset.annotate(len_lists=Count('lists')).filter(len_lists__gt=0)
        else:
            return queryset.annotate(len_lists=Count('lists')).filter(len_lists__lt=1)
