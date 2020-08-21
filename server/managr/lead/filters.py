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
from dateutil.parser import parse
from django.utils import timezone

from managr.lead import constants as lead_constants
from .models import (
    Lead,
    Forecast,
    List,
    Note,
    File,
    CallNote,
    Reminder,
    Notification,
    LeadMessage,
    LeadActivityLog,
)


class LeadRatingOrderFiltering(OrderingFilter):
    def filter_queryset(self, request, queryset, view):
        ordering = request.query_params.get("order_by", None)
        if ordering is not None:
            if ordering.startswith("-"):
                ordering.strip("-")
                queryset = queryset.order_by(ordering)
            else:
                queryset = queryset.order_by(ordering)

        return queryset


class LeadActivityLogFilterSet(FilterSet):
    leads = django_filters.CharFilter(method="by_leads")
    min_date = django_filters.CharFilter(method="by_min_date")
    max_date = django_filters.CharFilter(method="by_max_date")

    class Meta:
        model = LeadActivityLog
        fields = ["lead", "leads"]

    def by_leads(self, queryset, name, value):
        q = Q()
        if value:
            l = value.split(",")
            for lead in l:
                q |= Q(id=lead)
            leads = Lead.objects.for_user(self.request.user).filter(q)

            return queryset.filter(lead__in=leads)
        return queryset

    def by_min_date(self, queryset, name, value):
        if value:

            # min = timezone.datetime.strptime(value, '%Y-%m-%d %H:%M:%S.%f%Z')
            min = parse(value)
            return queryset.filter(action_timestamp__gte=min)

    def by_max_date(self, queryset, name, value):
        if value:

            # min = timezone.datetime.strptime(value, '%Y-%m-%d %H:%M:%S.%f%Z')
            min = parse(value)
            return queryset.filter(action_timestamp__lte=min)


class ReminderOrderingFilter(OrderingFilter):
    def filter_queryset(self, request, queryset, view):
        ordering = request.query_params.get("order_by", None)
        if ordering is not None:
            if ordering.startswith("-"):
                ordering.strip("-")
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
        fields = ["rating", "on_list", "is_claimed", "by_list", "by_user", "by_account"]

    def leads_by_user(self, queryset, name, value):
        u = self.request.user
        if value:
            value = value.strip()
            user_list = value.split(",")
            users_in_org = u.organization.users.filter(id__in=user_list).values_list(
                "id", flat=True
            )
            return queryset.filter(claimed_by__in=users_in_org)
        return queryset

    def leads_by_status(self, qs, name, value):
        """ allows list of statuses"""
        if value:

            v = value.strip("")
            v = v.split(",")

            return qs.filter(status__in=v)
        return qs

    def leads_by_rating(self, qs, name, value):
        if value:
            v = value.strip("")
            v = v.split(",")
            return qs.filter(rating__in=v)
        return qs

    def by_forecast(self, qs, name, value):
        """ allows list of forecasts """

        if value:
            v = value.strip("")
            v = v.split(",")

            return qs.filter(forecast__forecast__in=v)
        return qs

    def list_count(self, queryset, name, value):
        """ filter leads by list count """
        if value:
            # if true on_list=True return leads with a list count of greater than 0 (non inclusive)
            return (
                queryset.annotate(len_lists=Count("lists"))
                .filter(len_lists__gt=0)
                .order_by("title")
            )
        else:
            # if false on_list=False return leads with a list count of less than 1 (non inclusive)
            return (
                queryset.annotate(len_lists=Count("lists"))
                .filter(len_lists__lt=1)
                .order_by("title")
            )

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
            account_list = value.split(",")
            for acc in account_list:
                # check if account is in org
                if u.organization.accounts.filter(id=acc).exists():
                    pass
                else:
                    account_list.remove(acc)

            return queryset.filter(account__in=account_list).order_by(
                "account", "title"
            )
        return queryset


class ForecastFilterSet(FilterSet):
    by_user = django_filters.CharFilter(method="forecasts_by_user")
    date_range_from = django_filters.CharFilter(method="filter_by_date_range_from")
    date_range_to = django_filters.IsoDateTimeFilter(
        field_name="lead__expected_close_date", lookup_expr="lte"
    )

    class Meta:
        model = Forecast
        fields = ["by_user", "forecast"]

    def forecasts_by_user(self, queryset, name, value):
        """ provide a user or a list of users """
        if value:
            value = value.strip()
            user_list = value.split(",")
            try:
                # exclude unclaimed leads
                # order by expected_close_date, nulls last
                # then order by lead title
                if self.request.user.organization.users.filter(
                    id__in=user_list
                ).exists():
                    return (
                        queryset.exclude(lead__claimed_by__isnull=True)
                        .filter(lead__claimed_by__in=user_list)
                        .order_by(
                            F("lead__expected_close_date").asc(nulls_last=True),
                            "lead__title",
                        )
                    )
                else:
                    # if there is a user that does not exist or a problem with the query silently fail
                    # return None
                    return queryset.none()
            except DjangoValidationError:
                # if a malformed User Id is sent fail silently and return None
                return queryset.none()

    def filter_by_date_range_from(self, queryset, name, value):
        # if the request does not include date_range_to param,
        # then also include leads without an expected_close_date
        if not self.request.query_params.get("date_range_to"):
            return queryset.filter(
                Q(lead__expected_close_date__gte=value)
                | Q(lead__expected_close_date__isnull=True)
            )
        else:
            return queryset.filter(lead__expected_close_date__gte=value)


class ListFilterSet(FilterSet):
    by_user = django_filters.CharFilter(method="lists_by_user")
    by_lead = django_filters.CharFilter(field_name="leads")

    class Meta:
        model = List
        fields = ["by_user"]

    def lists_by_user(self, queryset, name, value):
        u = self.request.user
        if value:
            value = value.strip()
            user_list = value.split(",")
            users_in_org = u.organization.users.filter(id__in=user_list).values_list(
                "id", flat=True
            )
            return queryset.filter(created_by_id__in=users_in_org)
        return queryset


class LeadMessageFilterSet(FilterSet):
    by_lead = django_filters.CharFilter(field_name="lead")

    class Meta:
        model = LeadMessage
        fields = ["by_lead"]


class NoteFilterSet(FilterSet):
    by_lead = django_filters.CharFilter(field_name="created_for")

    class Meta:
        model = Note
        fields = ["by_lead"]


class CallNoteFilterSet(FilterSet):
    by_lead = django_filters.CharFilter(field_name="created_for")

    class Meta:
        model = CallNote
        fields = ["by_lead"]


class FileFilterSet(FilterSet):
    by_lead = django_filters.CharFilter(method="files_by_lead")

    class Meta:
        model = File
        fields = ["by_lead", "lead"]

    def files_by_lead(self, queryset, name, value):
        if value:
            return queryset.filter(lead=value)


class ReminderFilterSet(FilterSet):
    """ filter for reminders that are in the future (+5 minutes) to display to user"""

    # also filtering out has_notifications technically this should not occur
    by_remind_on = django_filters.CharFilter(method="from_date")

    class Meta:
        model = Reminder
        fields = ["by_remind_on"]

    def from_date(self, qs, name, value):
        if value:
            min = parse(value)
            min = min + timezone.timedelta(minutes=5)
            ns = Notification.objects.filter(notification_type="REMINDER").values_list(
                "resource_id", flat=True
            )
        query = Q()
        for n in ns:
            query |= Q(id=n)
        return qs.filter(datetime_for__gte=min).exclude(query).order_by("datetime_for")
