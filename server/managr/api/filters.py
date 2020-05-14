import django_filters
from django.core.exceptions import ValidationError as DjangoValidationError
from django_filters.rest_framework import FilterSet
from django_filters import OrderingFilter
from itertools import chain
from django.db.models import F, Q, Count, Max, Min, DateTimeField, Value, Case, When
from django.db.models.functions import Lower
from django_filters import OrderingFilter

from .models import Contact


class ContactFilterSet(FilterSet):
    by_lead = django_filters.CharFilter(field_name='leads')

    class Meta:
        model = Contact
        fields = ('account',)
