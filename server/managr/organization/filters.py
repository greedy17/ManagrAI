import django_filters
import json

from django.core.exceptions import ValidationError as DjangoValidationError
from django_filters.rest_framework import FilterSet
from django_filters import OrderingFilter
from itertools import chain
from django.db.models import F, Q, Count, Max, Min, DateTimeField, Value, Case, When
from django.db.models.functions import Lower
from django_filters import OrderingFilter

from managr.lead.models import Lead
from .models import Contact, Account


class ContactFilterSet(FilterSet):
    by_lead = django_filters.CharFilter(field_name='leads')

    class Meta:
        model = Contact
        fields = ('account',)


class AccountFilterSet(FilterSet):
    by_params = django_filters.CharFilter(method='filter_by_params')

    class Meta:
        model = Account
        fields = []

    def filter_by_params(self, queryset, name, value):
        """
        This custom filter receives JSON with a number of params and acts accordingly.
        This is done instead of multiple custom filters because:
            - There is a need for AND conditions within queryset.filter() for the has_many
              relationship of leads (account has many leads).
        This is done instead of a custom POST endpoint because:
            - There is a need to incorporate pagination and generally to use the CollectionManager
              interface from the client-side.
        """
        params = json.loads(value)
        only_unclaimed = params.get('only_unclaimed', False)
        representatives = params.get('representatives', [])
        search_term = params.get('search_term', '')

        # if search term and unclaimed
        if search_term and only_unclaimed:
            leads = Lead.objects.filter(title__icontains=search_term, claimed_by__isnull=True)
            accounts = {l.account.id for l in leads}
            return queryset.filter(pk__in=accounts)

        # if search term and representatives
        if search_term and len(representatives):
            leads = Lead.objects.filter(title__icontains=search_term, claimed_by__in=representatives)
            accounts = {l.account.id for l in leads}
            return queryset.filter(pk__in=accounts)

        # if search only
        if search_term:
            return queryset.filter(leads__title__icontains=search_term).distinct()

        # if unclaimed
        if only_unclaimed:
            return queryset.filter(leads__claimed_by__isnull=False).distinct()

        # if representatives
        if len(representatives):
            return queryset.filter(leads__claimed_by__in=representatives).distinct()

        return queryset
