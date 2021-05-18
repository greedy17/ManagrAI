from django.db.models import Sum, Avg, Q
from django.utils import timezone

from datetime import datetime, timedelta
from calendar import monthrange

from managr.core.models import User
from managr.organization import constants as org_consts
from .models import Opportunity
from . import constants as opportunity_constants


class ForecastKPIs:
    def __init__(
        self,
        date_range_from,
        date_range_to,
        representatives=[],
    ):
        self._representatives = representatives
        self._date_range_from = date_range_from
        self._date_range_to = date_range_to

    def _add_representatives_filter_to_user_queryset(self, user_queryset):
        return user_queryset.filter(pk__in=self._representatives)

    def _add_representatives_filter_to_lead_queryset(self, lead_queryset):
        return lead_queryset.filter(claimed_by__in=self._representatives)

    def _add_date_range_filter_to_lead_queryset(self, lead_queryset):
        # date_range_from and date_range_to can be missing, because:
        # - TODAY_ONWARD means there is no date_range_to
        # - ALL_TIME means both are missing
        if not self._date_range_from and not self._date_range_to:
            return lead_queryset
        if not self._date_range_to:
            return lead_queryset.filter(expected_close_date__gte=self._date_range_from)
        return lead_queryset.filter(
            expected_close_date__gte=self._date_range_from,
            expected_close_date__lte=self._date_range_to,
        )

    @property
    def sold(self):
        """
        Formerly known as Total Closed Value.
        """
        # filter for leads whose status is CLOSED
        qs_1 = Opportunity.objects.filter(
            status__title=opportunity_constants.LEAD_STATUS_CLOSED,
            status__type=org_consts.STAGE_TYPE_PUBLIC,
        )
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
        qs_1 = Opportunity.objects.filter(
            status__title=opportunity_constants.LEAD_STATUS_CLOSED,
            status__type=org_consts.STAGE_TYPE_PUBLIC,
        )
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
        # Weighted forecast: 50% of '50/50' values, 75% 'Strong' values, 90% 'Verbal' values.

        # filter for leads whose forecast is 50/50
        temp_1 = Opportunity.objects.filter(
            forecast__forecast=opportunity_constants.FORECAST_FIFTY_FIFTY
        )
        # filter for leads that are claimed by given representatives
        temp_2 = self._add_representatives_filter_to_lead_queryset(temp_1)
        # filter for leads closed within the given date range
        fifty_fifty_queryset = self._add_date_range_filter_to_lead_queryset(temp_2)

        # filter for leads whose forecast is STRONG
        temp_1 = Opportunity.objects.filter(
            forecast__forecast=opportunity_constants.FORECAST_STRONG
        )
        # filter for leads that are claimed by given representatives
        temp_2 = self._add_representatives_filter_to_lead_queryset(temp_1)
        # filter for leads closed within the given date range
        strong_queryset = self._add_date_range_filter_to_lead_queryset(temp_2)

        # filter for leads whose forecast is VERBAL
        temp_1 = Opportunity.objects.filter(
            forecast__forecast=opportunity_constants.FORECAST_VERBAL
        )
        # filter for leads that are claimed by given representatives
        temp_2 = self._add_representatives_filter_to_lead_queryset(temp_1)
        # filter for leads closed within the given date range
        verbal_queryset = self._add_date_range_filter_to_lead_queryset(temp_2)

        fifty_fifty_sum = fifty_fifty_queryset.aggregate(sum=Sum("amount"))["sum"] or 0
        strong_sum = strong_queryset.aggregate(sum=Sum("amount"))["sum"] or 0
        verbal_sum = verbal_queryset.aggregate(sum=Sum("amount"))["sum"] or 0
        return (float(fifty_fifty_sum) * 0.5) + (float(strong_sum) * 0.75) + (float(verbal_sum) * 0.9)
        """
        return float("0.5")

    @property
    def quota(self):
        """
        Sum Quotas of all selected representatives.
        """
        # temp = User.objects.all()
        # user_queryset = self._add_representatives_filter_to_user_queryset(temp)
        # return user_queryset.aggregate(sum=Sum("quota"))["sum"] or 0
        return 0

    @property
    def commit(self):
        """
        Sum Commits of all selected representatives.
        """
        # temp = User.objects.all()
        # user_queryset = self._add_representatives_filter_to_user_queryset(temp)
        # return user_queryset.aggregate(sum=Sum("commit"))["sum"] or 0
        return 0

    @property
    def upside(self):
        """
        Sum Upsides of all selected representatives.
        """
        # temp = User.objects.all()
        # user_queryset = self._add_representatives_filter_to_user_queryset(temp)
        # return user_queryset.aggregate(sum=Sum("upside"))["sum"] or 0
        return 0

    @property
    def as_dict(self):
        return {
            "sold": self.sold,
            "quota": self.quota,
            "average_contract_value": self.average_contract_value,
            "forecast": self.forecast,
            "commit": self.commit,
            "upside": self.upside,
        }
