import django_filters
from django.core.exceptions import ValidationError as DjangoValidationError
from django_filters.rest_framework import FilterSet
from django_filters import OrderingFilter
from itertools import chain
from django.db.models import F, Q, Count, Max, Min, DateTimeField, Value, Case, When
from django.db.models.functions import Lower
from .models import Lead, Forecast, List, Note, File, CallNote
from django_filters import OrderingFilter


class LeadRatingOrderFiltering(OrderingFilter):
    def filter_queryset(self, request, queryset, view):
        ordering = request.query_params.get('order_by', None)
        if ordering is not None:
            if ordering.startswith('-'):
                ordering.strip('-')
                queryset = queryset.order_by(ordering)
            else:
                queryset = queryset.order_by(ordering)

        return queryset


class LeadFilterSet(FilterSet):
    """
        this filters for rating 1-5
        on_list is a filter set to only show leads currently on a list or leads that are currently not on a list
        is_claimed will return a list of claimed or unclaimed leads

    """
    on_list = django_filters.BooleanFilter(method="list_count")
    is_claimed = django_filters.BooleanFilter(method="claim_status")
    by_list = django_filters.CharFilter(method="retrieve_leads_in_list")
    by_status = django_filters.CharFilter(method="leads_by_status")
    forecast = django_filters.CharFilter(method="by_forecast")
    by_user = django_filters.CharFilter(method="leads_by_user")
    by_account = django_filters.CharFilter(method="list_leads_by_account")
    by_rating = django_filters.CharFilter(method="leads_by_rating")

    class Meta:
        model = Lead
        fields = ['rating', 'on_list', 'is_claimed',
                  'by_list', 'by_user', 'by_account']

    def leads_by_user(self, queryset, name, value):
        u = self.request.user
        if value:
            value = value.strip()
            user_list = value.split(',')
            users_in_org = u.organization.users.filter(
                id__in=user_list).values_list('id', flat=True)
            return queryset.filter(claimed_by__in=users_in_org)
        return queryset

    def leads_by_status(self, qs, name, value):
        """ allows list of statuses"""
        if value:

            v = value.strip('')
            v = value.upper()
            v = v.split(',')

            return qs.filter(status__in=v)
        return qs

    def leads_by_rating(self, qs, name, value):
        if value:
            v = value.strip('')
            v = v.split(',')
            return qs.filter(rating__in=v)
        return qs

    def by_forecast(self, qs, name, value):
        """ allows list of forecasts """

        if value:
            v = value.strip('')
            v = v.split(',')

            return qs.filter(forecast__forecast__in=v)
        return qs

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

    def list_leads_by_account(self, queryset, name, value):
        u = self.request.user
        if value:
            value = value.strip()
            account_list = value.split(',')
            for acc in account_list:
                # check if account is in org
                if u.organization.accounts.filter(id=acc).exists():
                    pass
                else:
                    account_list.remove(acc)

            return queryset.filter(account__in=account_list).order_by('account')
        return queryset


class ForecastFilterSet(FilterSet):
    by_user = django_filters.CharFilter(method="forecasts_by_user")

    class Meta:
        model = Forecast
        fields = ['by_user', 'forecast']

    def forecasts_by_user(self, queryset, name, value):
        """ provide a user or a list of users """
        if value:
            value = value.strip()
            user_list = value.split(',')
            try:
                if self.request.user.organization.users.filter(id__in=user_list).exists():
                    return queryset.filter(lead__claimed_by__in=user_list).order_by('forecast')
                else:
                    # if there is a user that does not exist or a problem with the query silently fail
                    # return None
                    return queryset.none()
            except DjangoValidationError:
                # if a malformed User Id is sent fail silently and return None
                return queryset.none()


class ListFilterSet(FilterSet):
    by_user = django_filters.CharFilter(method="lists_by_user")
    by_lead = django_filters.CharFilter(field_name="leads")

    class Meta:
        model = List
        fields = ['by_user']

    def lists_by_user(self, queryset, name, value):
        u = self.request.user
        if value:
            value = value.strip()
            user_list = value.split(',')
            users_in_org = u.organization.users.filter(
                id__in=user_list).values_list('id', flat=True)
            return queryset.filter(created_by_id__in=users_in_org)
        return queryset


class NoteFilterSet(FilterSet):
    by_lead = django_filters.CharFilter(field_name="created_for")

    class Meta:
        model = Note
        fields = ['by_lead']


class CallNoteFilterSet(FilterSet):
    by_lead = django_filters.CharFilter(field_name="created_for")

    class Meta:
        model = CallNote
        fields = ['by_lead']


class FileFilterSet(FilterSet):
    by_lead = django_filters.CharFilter(method="files_by_lead")

    class Meta:
        model = File
        fields = ['by_lead', 'lead']

    def files_by_lead(self, queryset, name, value):
        if value:
            return queryset.filter(lead=value)
