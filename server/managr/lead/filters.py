import django_filters
from django_filters.rest_framework import FilterSet
from django_filters import OrderingFilter
from itertools import chain
from django.db.models import F, Q, Count, Max, Min, DateTimeField, Value, Case, When
from django.db.models.functions import Lower
from .models import Lead, Forecast


class LeadFilterSet(FilterSet):
    """
        this filters for rating 1-5
        on_list is a filter set to only show leads currently on a list or leads that are currently not on a list
        is_claimed will return a list of claimed or unclaimed leads

    """
    on_list = django_filters.BooleanFilter(method="list_count")
    is_claimed = django_filters.BooleanFilter(method="claim_status")
    by_list = django_filters.CharFilter(method="retrieve_leads_in_list")

    class Meta:
        model = Lead
        fields = ['rating', 'on_list', 'is_claimed', 'by_list']

    def list_count(self, queryset, name, value):
        """ filter leads by list count """
        if value:
            # if true on_list=True return leads with a list count of greater than 0 (non inclusive)
            return queryset.annotate(len_lists=Count('lists')).filter(len_lists__gt=0)
        else:
            # if false on_list=False return leads with a list count of less than 1 (non inclusive)
            return queryset.annotate(len_lists=Count('lists')).filter(len_lists__lt=1)

    def claim_status(self, queryset, name, value):
        """ checks if the claimed_by field is null """
        if value:
            return queryset.filter(claimed_by__isnull=False)
        return queryset.filter(claimed_by__isnull=True)

    def retrieve_leads_in_list(self, queryset, name, value):
        """ Lists will not return leads by default, this filter
            retrieves leads in a list (to provide pagination)
        """

        if value:
            return queryset.filter(lists=value)
        else:
            return queryset.all()


class ForecastFilterSet(FilterSet):
    by_user = django_filters.CharFilter(method="forecasts_by_user")

    class Meta:
        model = Forecast
        fields = ['by_user', 'forecast']

    def forecasts_by_user(self, queryset, name, value):
        """ provide a user or a list of users """
        # TODO:- check to see if user exists
        if value:
            value = value.strip()
            user_list = value.split(',')
            if self.request.user.organization.users.filter(id__in=user_list).exists():
                return queryset.filter(lead__claimed_by__in=user_list).order_by('forecast')
