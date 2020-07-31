from django.db.models import Sum, Avg, Q
from django.utils import timezone

from datetime import datetime, timedelta
from calendar import monthrange

from managr.core.models import User
from .models import Lead
from . import constants as lead_constants


class ForecastKPIs:

    def __init__(
        self,
        representatives=[],
        date_range_preset=lead_constants.TODAY_ONWARD
    ):
        self._representatives = representatives
        self._date_range_preset = date_range_preset

    def _add_representatives_filter_to_user_queryset(self, user_queryset):
        return user_queryset.filter(pk__in=self._representatives)

    def _add_representatives_filter_to_lead_queryset(self, lead_queryset):
        return lead_queryset.filter(claimed_by__in=self._representatives)

    def _add_date_range_filter_to_lead_queryset(self, lead_queryset):
        """
        Using a switcher, apply a .filter() to given lead_queryset
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
        return switcher.get(self._date_range_preset)(lead_queryset)

    def _filter_by_TODAY_ONWARD(self, lead_queryset):
        """
        Today to all of Future, plus Undated (Lead.expected_close_date is null).
        """
        today = timezone.now().date()
        return lead_queryset.filter(Q(expected_close_date__gte=today) | Q(expected_close_date__isnull=True))

    def _filter_by_TODAY(self, lead_queryset):
        # while this is exact to the date, GTE & LTE are used because
        # the DB uses datetime field, not just date field, and we want
        # this range to encompass the whole day
        today = timezone.now().date()
        return lead_queryset.filter(
                expected_close_date__gte=today,
                expected_close_date__lte=today,
            )

    def _filter_by_YESTERDAY(self, lead_queryset):
        # while this is exact to the date, GTE & LTE are used because
        # the DB uses datetime field, not just date field, and we want
        # this range to encompass the whole day
        yesterday = timezone.now().date() - timedelta(days=1)
        return lead_queryset.filter(
                expected_close_date__gte=yesterday,
                expected_close_date__lte=yesterday,
            )

    def _filter_by_THIS_WEEK(self, lead_queryset):
        # A week is defined as Monday 12AM - Sunday 11:59PM
        today = timezone.now().date()
        # Monday is 0, Sunday is 6
        weekday_integer = today.weekday()
        start_of_week = today - timedelta(days=weekday_integer)
        end_of_week = today + timedelta(days=6 - weekday_integer)
        return lead_queryset.filter(
                expected_close_date__gte=start_of_week,
                expected_close_date__lte=end_of_week,
            )

    def _filter_by_LAST_WEEK(self, lead_queryset):
        # A week is defined as Monday 12AM - Sunday 11:59PM
        a_week_ago = timezone.now().date() - timedelta(weeks=1)
        # Monday is 0, Sunday is 6
        weekday_integer = a_week_ago.weekday()
        start_of_week = a_week_ago - timedelta(days=weekday_integer)
        end_of_week = a_week_ago + timedelta(days=6 - weekday_integer)
        return lead_queryset.filter(
                expected_close_date__gte=start_of_week,
                expected_close_date__lte=end_of_week,
            )

    def _filter_by_THIS_MONTH(self, lead_queryset):
        today = timezone.now().date()
        # monthrange() returns a tuple as such: (month_integer, last_day_of_month),
        # e.g. For January it would be (1, 31)
        last_day_of_month = monthrange(today.year, today.month)[1]
        start_of_month = datetime(today.year, today.month, 1).date()
        end_of_month = datetime(today.year, today.month, last_day_of_month).date()
        return lead_queryset.filter(
                expected_close_date__gte=start_of_month,
                expected_close_date__lte=end_of_month,
            )

    def _filter_by_LAST_MONTH(self, lead_queryset):
        today = timezone.now().date()
        a_month_ago = today - timedelta(weeks=4)
        # monthrange() returns a tuple as such: (month_integer, last_day_of_month),
        # e.g. For January it would be (1, 31)
        last_day_of_month = monthrange(a_month_ago.year, a_month_ago.month)[1]
        start_of_month = datetime(a_month_ago.year, a_month_ago.month, 1).date()
        end_of_month = datetime(a_month_ago.year, a_month_ago.month, last_day_of_month).date()
        return lead_queryset.filter(
                expected_close_date__gte=start_of_month,
                expected_close_date__lte=end_of_month,
            )

    def _filter_by_THIS_QUARTER(self, lead_queryset):
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
        return lead_queryset.filter(
                expected_close_date__gte=start_of_quarter,
                expected_close_date__lte=end_of_quarter,
            )

    def _filter_by_LAST_QUARTER(self, lead_queryset):
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
        return lead_queryset.filter(
                expected_close_date__gte=start_of_quarter,
                expected_close_date__lte=end_of_quarter,
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

    def _filter_by_THIS_YEAR(self, lead_queryset):
        today = timezone.now().date()
        start_of_year = datetime(today.year, 1, 1).date()
        return lead_queryset.filter(
                expected_close_date__gte=start_of_year,
            )

    def _filter_by_LAST_YEAR(self, lead_queryset):
        a_year_ago = timezone.now().date() - timedelta(days=365)
        start_of_year = datetime(a_year_ago.year, 1, 1).date()
        end_of_year = datetime(a_year_ago.year, 12, 31).date()
        return lead_queryset.filter(
                expected_close_date__gte=start_of_year,
                expected_close_date__lte=end_of_year,
            )

    def _filter_by_ALL_TIME(self, lead_queryset):
        return lead_queryset

    @property
    def sold(self):
        """
        Formerly known as Total Closed Value.
        """
        # filter for leads whose status is CLOSED
        qs_1 = Lead.objects.filter(status=lead_constants.LEAD_STATUS_CLOSED)
        # filter for leads that are claimed by given representatives
        qs_2 = self._add_representatives_filter_to_lead_queryset(qs_1)
        # filter for leads closed within the given date range
        final_qs = self._add_date_range_filter_to_lead_queryset(qs_2)
        return final_qs.aggregate(sum=Sum("closing_amount"))["sum"] or 0

    @property
    def average_contract_value(self):
        """
        Formerly known as Total Closed Value.
        """
        # filter for leads whose status is CLOSED
        qs_1 = Lead.objects.filter(status=lead_constants.LEAD_STATUS_CLOSED)
        # filter for leads that are claimed by given representatives
        qs_2 = self._add_representatives_filter_to_lead_queryset(qs_1)
        # filter for leads closed within the given date range
        final_qs = self._add_date_range_filter_to_lead_queryset(qs_2)

        count = final_qs.count()
        average = 0
        if count > 0:
            average = self.sold / count
        return average

    @property
    def forecast(self):
        """
        Weighted forecast: 50% of '50/50' values, 75% 'Strong' values, 100% 'Verbal' values.
        """
        # filter for leads whose forecast is 50/50
        temp_1 = Lead.objects.filter(forecast__forecast=lead_constants.FORECAST_FIFTY_FIFTY)
        # filter for leads that are claimed by given representatives
        temp_2 = self._add_representatives_filter_to_lead_queryset(temp_1)
        # filter for leads closed within the given date range
        fifty_fifty_queryset = self._add_date_range_filter_to_lead_queryset(temp_2)

        # filter for leads whose forecast is STRONG
        temp_1 = Lead.objects.filter(forecast__forecast=lead_constants.FORECAST_STRONG)
        # filter for leads that are claimed by given representatives
        temp_2 = self._add_representatives_filter_to_lead_queryset(temp_1)
        # filter for leads closed within the given date range
        strong_queryset = self._add_date_range_filter_to_lead_queryset(temp_2)

        # filter for leads whose forecast is VERBAL
        temp_1 = Lead.objects.filter(forecast__forecast=lead_constants.FORECAST_VERBAL)
        # filter for leads that are claimed by given representatives
        temp_2 = self._add_representatives_filter_to_lead_queryset(temp_1)
        # filter for leads closed within the given date range
        verbal_queryset = self._add_date_range_filter_to_lead_queryset(temp_2)

        fifty_fifty_sum = fifty_fifty_queryset.aggregate(sum=Sum("amount"))["sum"] or 0
        strong_sum = strong_queryset.aggregate(sum=Sum("amount"))["sum"] or 0
        verbal_sum = verbal_queryset.aggregate(sum=Sum("amount"))["sum"] or 0

        return (fifty_fifty_sum * 0.5) + (strong_sum * 0.75) + verbal_sum

    @property
    def quota(self):
        """
        Sum Quotas of all selected representatives.
        """
        temp = User.objects.all()
        user_queryset = self._add_representatives_filter_to_user_queryset(temp)
        return user_queryset.aggregate(sum=Sum("quota"))["sum"] or 0

    @property
    def commit(self):
        """
        Sum Commits of all selected representatives.
        """
        temp = User.objects.all()
        user_queryset = self._add_representatives_filter_to_user_queryset(temp)
        return user_queryset.aggregate(sum=Sum("commit"))["sum"] or 0

    @property
    def upside(self):
        """
        Sum Upsides of all selected representatives.
        """
        temp = User.objects.all()
        user_queryset = self._add_representatives_filter_to_user_queryset(temp)
        return user_queryset.aggregate(sum=Sum("upside"))["sum"] or 0

    @property
    def as_dict(self):
        return {
            'sold': self.sold,
            'quota': self.quota,
            'average_contract_value': self.average_contract_value,
            'forecast': self.forecast,
            'commit': self.commit,
            'upside': self.upside
        }
