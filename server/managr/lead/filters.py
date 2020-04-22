import django_filters
from django_filters.rest_framework import FilterSet
from django_filters import OrderingFilter
from itertools import chain
from django.db.models import F, Q, Count, Max, Min, DateTimeField, Value, Case, When
from django.db.models.functions import Lower
from .models import Lead


class LeadFilterSet(FilterSet):
    class Meta:
        model = Lead
        fields = ['rating', ]
