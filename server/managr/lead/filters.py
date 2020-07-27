import time
import pytz
from itertools import chain
from dateutil.parser import parse
from datetime import datetime, timedelta
from calendar import monthrange

import django_filters
from django.core.exceptions import ValidationError as DjangoValidationError
from django_filters.rest_framework import FilterSet
from django_filters import OrderingFilter
from django.db.models import F, Q, Count, Max, Min, DateTimeField, Value, Case, When
from django.db.models.functions import Lower
from django.utils import timezone

from managr.lead import constants as lead_constants
from .models import Lead, Forecast, List, Note, File, CallNote, Reminder, Notification


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
        on_list is a filter set to only show leads currently on a
         list or leads that are currently not on a list
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
            users_in_org = u.organization.users.filter(id__in=user_list).values_list(
                'id', flat=True
            )
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
            return queryset.annotate(len_lists=Count('lists')).filter(len_lists__gt=0).order_by('title')
        else:
            # if false on_list=False return leads with a list count of less than 1 (non inclusive)
            return queryset.annotate(len_lists=Count('lists')).filter(len_lists__lt=1).order_by('title')

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

            return queryset.filter(account__in=account_list).order_by('account', 'title')
        return queryset


class ForecastFilterSet(FilterSet):
    by_user = django_filters.CharFilter(method="forecasts_by_user")
    date_range = django_filters.CharFilter(method="forecasts_by_date_range")

    class Meta:
        model = Forecast
        fields = ['by_user', 'forecast', 'date_range']

    def forecasts_by_user(self, queryset, name, value):
        """ provide a user or a list of users """
        if value:
            value = value.strip()
            user_list = value.split(',')
            try:
                # exclude unclaimed leads
                # order by expected_close_date, nulls last
                # then order by lead title
                if self.request.user.organization.users.filter(id__in=user_list).exists():
                    return queryset.exclude(lead__claimed_by__isnull=True) \
                                   .filter(lead__claimed_by__in=user_list) \
                                   .order_by(
                                       F('lead__expected_close_date').desc(nulls_last=True),
                                       'lead__title'
                                   )
                else:
                    # if there is a user that does not exist or a problem with the query silently fail
                    # return None
                    return queryset.none()
            except DjangoValidationError:
                # if a malformed User Id is sent fail silently and return None
                return queryset.none()    

    def forecasts_by_date_range(self, queryset, name, value):
        """
        Given a date_range_preset, apply proper date-range filtering.
        """
        if value in lead_constants.DATE_RANGE_PRESETS:
            return self._add_date_range_filter_to_queryset(queryset, value)
        return queryset

    def _add_date_range_filter_to_queryset(self, queryset, date_range_preset):
        """
        Using a switcher, apply a .filter() to given queryset
        that limits results to a date range, derived from a preset const.
        """
        switcher = {}
        switcher[lead_constants.TODAY_ONWARD] = self._filter_by_TODAY_ONWARD
        switcher[lead_constants.TODAY] = self._filter_by_TODAY
        switcher[lead_constants.YESTERDAY] = self._filter_by_YESTERDAY
        switcher[lead_constants.THIS_WEEK] = self._filter_by_THIS_WEEK
        switcher[lead_constants.LAST_WEEK] = self._filter_by_LAST_WEEK
        switcher[lead_constants.THIS_MONTH] = self._filter_by_THIS_MONTH
        switcher[lead_constants.LAST_MONTH] = self._filter_by_LAST_MONTH
        switcher[lead_constants.THIS_QUARTER] = self._filter_by_THIS_QUARTER
        switcher[lead_constants.LAST_QUARTER] = self._filter_by_LAST_QUARTER
        switcher[lead_constants.THIS_YEAR] = self._filter_by_THIS_YEAR
        switcher[lead_constants.LAST_YEAR] = self._filter_by_LAST_YEAR
        switcher[lead_constants.ALL_TIME] = self._filter_by_ALL_TIME
        return switcher.get(date_range_preset)(queryset)

    def _filter_by_TODAY_ONWARD(self, queryset):
        """
        Today to all of Future, plus Undated (Lead.expected_close_date is null).
        """
        today = timezone.now().date()
        return queryset.filter(Q(lead__expected_close_date__gte=today) | Q(lead__expected_close_date__isnull=True))

    def _filter_by_TODAY(self, queryset):
        # while this is exact to the date, GTE & LTE are used because
        # the DB uses datetime field, not just date field, and we want
        # this range to encompass the whole day
        today = timezone.now().date()
        return queryset.filter(
                lead__expected_close_date__gte=today,
                lead__expected_close_date__lte=today,
            )

    def _filter_by_YESTERDAY(self, queryset):
        # while this is exact to the date, GTE & LTE are used because
        # the DB uses datetime field, not just date field, and we want
        # this range to encompass the whole day
        yesterday = timezone.now().date() - timedelta(days=1)
        return queryset.filter(
                lead__expected_close_date__gte=yesterday,
                lead__expected_close_date__lte=yesterday,
            )

    def _filter_by_THIS_WEEK(self, queryset):
        # A week is defined as Monday 12AM - Sunday 11:59PM
        today = timezone.now().date()
        # Monday is 0, Sunday is 6
        weekday_integer = today.weekday()
        start_of_week = today - timedelta(days=weekday_integer)
        end_of_week = today + timedelta(days=6 - weekday_integer)
        return queryset.filter(
                lead__expected_close_date__gte=start_of_week,
                lead__expected_close_date__lte=end_of_week,
            )

    def _filter_by_LAST_WEEK(self, queryset):
        # A week is defined as Monday 12AM - Sunday 11:59PM
        a_week_ago = timezone.now().date() - timedelta(weeks=1)
        # Monday is 0, Sunday is 6
        weekday_integer = a_week_ago.weekday()
        start_of_week = a_week_ago - timedelta(days=weekday_integer)
        end_of_week = a_week_ago + timedelta(days=6 - weekday_integer)
        return queryset.filter(
                lead__expected_close_date__gte=start_of_week,
                lead__expected_close_date__lte=end_of_week,
            )

    def _filter_by_THIS_MONTH(self, queryset):
        today = timezone.now().date()
        # monthrange() returns a tuple as such: (month_integer, last_day_of_month),
        # e.g. For January it would be (1, 31)
        last_day_of_month = monthrange(today.year, today.month)[1]
        start_of_month = datetime(today.year, today.month, 1).date()
        end_of_month = datetime(today.year, today.month, last_day_of_month).date()
        return queryset.filter(
                lead__expected_close_date__gte=start_of_month,
                lead__expected_close_date__lte=end_of_month,
            )

    def _filter_by_LAST_MONTH(self, queryset):
        today = timezone.now().date()
        a_month_ago = today - timedelta(weeks=4)
        # monthrange() returns a tuple as such: (month_integer, last_day_of_month),
        # e.g. For January it would be (1, 31)
        last_day_of_month = monthrange(a_month_ago.year, a_month_ago.month)[1]
        start_of_month = datetime(a_month_ago.year, a_month_ago.month, 1).date()
        end_of_month = datetime(a_month_ago.year, a_month_ago.month, last_day_of_month).date()
        return queryset.filter(
                lead__expected_close_date__gte=start_of_month,
                lead__expected_close_date__lte=end_of_month,
            )

    def _filter_by_THIS_QUARTER(self, queryset):
        # Quarters are:
        # January 1 - March 31
        # April 1 - June 30
        # July 1 - September 30
        # October 1 - December 31
        today = timezone.now().date()
        current_quarter = self._derive_quarter(today)
        if current_quarter == 1:
            start_of_quarter = datetime(today.year, 1, 1).date()
            end_of_quarter = datetime(today.year, 3, 31).date()
        if current_quarter == 2:
            start_of_quarter = datetime(today.year, 4, 1).date()
            end_of_quarter = datetime(today.year, 6, 30).date()
        if current_quarter == 3:
            start_of_quarter = datetime(today.year, 7, 1).date()
            end_of_quarter = datetime(today.year, 9, 30).date()
        if current_quarter == 4:
            start_of_quarter = datetime(today.year, 8, 1).date()
            end_of_quarter = datetime(today.year, 12, 31).date()
        return queryset.filter(
                lead__expected_close_date__gte=start_of_quarter,
                lead__expected_close_date__lte=end_of_quarter,
            )

    def _filter_by_LAST_QUARTER(self, queryset):
        # Quarters are:
        # January 1 - March 31
        # April 1 - June 30
        # July 1 - September 30
        # October 1 - December 31
        today = timezone.now().date()
        current_quarter = self._derive_quarter(today)
        if current_quarter == 1:
            a_year_ago = today - timedelta(years=1)
            start_of_quarter = datetime(a_year_ago.year, 8, 1).date()
            end_of_quarter = datetime(a_year_ago.year, 12, 31).date()
        if current_quarter == 2:
            start_of_quarter = datetime(today.year, 1, 1).date()
            end_of_quarter = datetime(today.year, 3, 31).date()
        if current_quarter == 3:
            start_of_quarter = datetime(today.year, 4, 1).date()
            end_of_quarter = datetime(today.year, 6, 30).date()
        if current_quarter == 4:
            start_of_quarter = datetime(today.year, 7, 1).date()
            end_of_quarter = datetime(today.year, 9, 30).date()
        return queryset.filter(
                lead__expected_close_date__gte=start_of_quarter,
                lead__expected_close_date__lte=end_of_quarter,
            )

    def _derive_quarter(self, date):
        if date.month <= 3:
            return 1
        elif date.month <= 6:
            return 2
        elif date.month <= 9:
            return 3
        else:
            return 4

    def _filter_by_THIS_YEAR(self, queryset):
        today = timezone.now().date()
        start_of_year = datetime(today.year, 1, 1).date()
        return queryset.filter(
                lead__expected_close_date__gte=start_of_year,
            )

    def _filter_by_LAST_YEAR(self, queryset):
        a_year_ago = timezone.now().date() - timedelta(days=365)
        start_of_year = datetime(a_year_ago.year, 1, 1).date()
        end_of_year = datetime(a_year_ago.year, 12, 31).date()
        return queryset.filter(
                lead__expected_close_date__gte=start_of_year,
                lead__expected_close_date__lte=end_of_year,
            )

    def _filter_by_ALL_TIME(self, queryset):
        return queryset


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
            users_in_org = u.organization.users.filter(id__in=user_list).values_list(
                'id', flat=True
            )
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


class ReminderFilterSet(FilterSet):
    """ filter for reminders that are in the future (+5 minutes) to display to user"""
    # also filtering out has_notifications technically this should not occur
    by_remind_on = django_filters.CharFilter(method="from_date")

    class Meta:
        model = Reminder
        fields = ['by_remind_on']

    def from_date(self, qs, name, value):
        if value:
            min = parse(value)
            min = min + timezone.timedelta(minutes=5)
            ns = Notification.objects.filter(
                notification_type="REMINDER").values_list('resource_id', flat=True)
        query = Q()
        for n in ns:
            query |= Q(id=n)
        return qs.filter(datetime_for__gte=min).exclude(query)
