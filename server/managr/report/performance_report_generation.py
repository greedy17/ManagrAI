import logging
import json
import inspect
from django.utils import timezone
from dateutil.parser import parse

from rest_framework.exceptions import ValidationError
from django.core import serializers
from django.db.models import Q, Sum

from managr.core.models import EmailAuthAccount
from managr.lead.models import Lead, LeadActivityLog

from managr.lead import constants as lead_constants
from managr.lead.serializers import LeadRefSerializer, UserRefSerializer
from managr.core.nylas.emails import send_new_email_legacy
from managr.utils.sites import get_site_url

from managr.report import constants as report_constants
from .models import PerformanceReport
from .story_report_generation import LeadDataGenerator

logger = logging.getLogger("managr")


def generate_performance_report_data(performance_report_id):
    """
    Given a PerformanceReport UUID, generate the report's
    data and update the instance with the generated data.
    Finally, trigger email regarding report availability to
    user that triggered this performance_report to be generated.
    """
    report = PerformanceReport.objects.get(pk=performance_report_id)

    try:
        # generate report's data
        # there are two types of performance reports:
        # (1) representative-specific, and
        # (2) organization-wide
        if report.is_representative_report:
            data = {
                "representative": {
                    "focus": RepFocusData(report).as_dict,
                    "typical": RepTypicalData(report).as_dict,
                },
                "organization": {
                    "focus": OrgFocusData(report).as_dict_for_representative_report,
                    "typical": OrgTypicalData(report).as_dict_for_representative_report,
                }
            }
        else:
            data = {
                "focus": OrgFocusData(report).as_dict_for_organization_report,
                "typical": OrgTypicalData(report).as_dict_for_organization_report,
            }
        report.data = data
        report.datetime_generated = timezone.now()
        report.save()
        # send email to user that generated report
        send_email(report)
    except Exception as e:
        # TODO (Bruno 09-22-2020):
        # Send an email to user that generated report notifying of failure?
        logger.exception(
            f"failed to generate performance report with UUID {performance_report_id}, error: {e}"
        )


def send_email(report):
    if report.is_representative_report:
        report_type = "Representative"
        report_focus = report.representative.full_name or report.representative.email
    else:
        report_type = "Organization"
        report_focus = report.generated_by.organization
    report_date_range = get_report_focus_from_preset(report.date_range_preset)

    recipient = report.generated_by
    subject = f"{report_type} Performance Report ({report_date_range}) generated for {report_focus}"

    ea = EmailAuthAccount.objects.filter(user__is_serviceaccount=True).first()
    if ea:
        token = ea.access_token
        sender = {"email": ea.email_address, "name": "Managr"}
        recipient = [{"email": recipient.email, "name": recipient.full_name}]
        message = {
            "subject": subject,
            "body": f"The report is available at {report.client_side_url}.",
        }
        try:
            send_new_email_legacy(token, sender, recipient, message)
        except Exception as e:
            """ this error is most likely going to be an error on our set
            up rather than the user_token """
            pass


def get_report_focus_from_preset(preset):
    # Get user-friendly text for constant
    for preset_set in report_constants.DATE_RANGES:
        if preset_set[0] == preset:
            return preset_set[1]
    raise ValidationError({"performance_report": "invalid date_range_preset"})


class BaseGenerator:
    def __init__(self, report):
        self._report = report
        self._organization = report.generated_by.organization
        self._representative = report.representative

    def failure_logger(self, e):
        method_name = inspect.stack()[1][3]
        class_name = self.__name__
        logger.exception(
            f"Unable to create report UUID {self._report.id} failed at method {method_name} of class {class_name}, with error {e}"
        )
        raise (e)


class RepFocusData(BaseGenerator):
    """
    Generates rep-level metrics for PerformanceReport.
    These metrics regard the specific date-range of the report.
    Final output is the self.as_dict method.
    """
    def __init__(self, report):
        self.__cached__closed_leads = None
        self.__cached__closed_leads_data = None
        super().__init__(report)

    @property
    def __name__(self):
        return "RepFocusData"

    # private properties:

    @property
    def _closed_leads(self):
        if self.__cached__closed_leads is None:
            leads = Lead.objects.filter(
                status__title=lead_constants.LEAD_STATUS_CLOSED,
                claimed_by=self._representative,
                expected_close_date__gte=self._report.date_range_from,
                expected_close_date__lte=self._report.date_range_to,
            )
            self.__cached__closed_leads = leads
        return self.__cached__closed_leads

    @property
    def _closed_leads_data(self):
        if self.__cached__closed_leads_data is None:
            self.__cached__closed_leads_data = [LeadDataGenerator(lead).as_dict for lead in self._closed_leads]
        return self.__cached__closed_leads_data

    # public properties:

    @property
    def activity_logs(self):
        """
        Only include the logs that were performed by the report's targeted representative,
        and that fall within the report's date range.
        """
        try:
            return LeadActivityLog.objects.filter(
                action_timestamp__gte=self._report.date_range_from,
                action_timestamp__lte=self._report.date_range_to,
                action_taken_by=self._representative,
            )
        except Exception as e:
            self.failure_logger(e)

    @property
    def activities_count(self):
        """
        Generate count of activities.
        Includes regular (reminder, note), communication (call/text/email), and custom (org-level) actions
        """
        return self.activity_logs.exclude(
                activity__in=lead_constants.ACTIVITIES_TO_EXCLUDE_FROM_HISTORY
            ).count()

    @property
    def actions_count(self):
        """
        Generate count of custom (org-level) actions.
        """
        org_level_actions = self._organization.action_choices
        count = 0
        for action_choice in org_level_actions.all():
            count += action_choice.action_set.filter(
                created_by=self._representative,
                datetime_created__gte=self._report.date_range_from,
                datetime_created__lte=self._report.date_range_to,
            ).count()
        return count

    @property
    def incoming_messages_count(self):
        return self.activity_logs.filter(
            activity=lead_constants.EMAIL_RECEIVED
        ).count()

    @property
    def forecast_amount(self):
        # Exclude logs whose lead closed during the date-range
        # If lead went through many forecast changes during date-range,
        # then take the most recent forecast-update-log for that lead.
        lead_amounts = {}
        for log in self.activity_logs.filter(
            activity=lead_constants.LEAD_UPDATED,
            meta__extra__forecast_table_addition=True,
        ).exclude(
            lead__status__title=lead_constants.LEAD_CLOSED,
            lead__expected_close_date__gte=self._report.date_range_from,
            lead__expected_close_date__lte=self._report.date_range_to,
        ).prefetch_related("lead"):
            # If lead not in dict, add this log's forecast_amount
            # If in dict then keep max of the two:
            # this log's forecast_amount and whatever current value
            lead = log.lead
            # All logs that include meta__extra__forecast_table_addition=True
            # should include meta__extra__forecast_amount.
            forecast_amount = log.meta["extra"]["forecast_amount"]
            if lead_amounts.get(lead.id, None) is None:
                lead_amounts[lead.id] = forecast_amount
            else:
                lead_amounts[lead.id] = max(lead_amounts[lead.id], forecast_amount)
        if not bool(lead_amounts):
            return 0
        return sum(lead_amounts.values())

    @property
    def deals_closed_count(self):
        return len(self._closed_leads)

    @property
    def amount_closed(self):
        return self._closed_leads.aggregate(
            sum=Sum("closing_amount")
        )["sum"] or 0

    @property
    def forecast_table_additions(self):
        return self.activity_logs.filter(
            activity=lead_constants.LEAD_UPDATED,
            meta__extra__forecast_table_addition=True,
        ).distinct('lead__id').order_by('lead_id').count()

    @property
    def top_opportunities(self):
        total_needed_count = 3
        output = {
            "CLOSED": [],
            "VERBAL": [],
            "STRONG": [],
            "50/50": [],
        }
        closed_leads = self._closed_leads.order_by('-closing_amount')[:total_needed_count]

        output[lead_constants.FORECAST_CLOSED] = [
                                                        data["fields"] for data in json.loads(
                                                            serializers.serialize(
                                                                "json",
                                                                closed_leads,
                                                                fields=("title", "closing_amount", "amount")
                                                            ))
                                                    ]

        total_needed_count = total_needed_count - len(closed_leads)
        if total_needed_count:
            # Since still need leads, go through FORECAST_TABLE:
            # (1) largest VERBAL, then
            # (2) largest STRONG, then
            # (3) largest 50/50
            # --- else blank

            # These leads must have ended the report's date_range with this the respective forecast
            # Example: need to find leads that went into VERBAL and stayed in VERBAL as regards the report's date_range

            # Therefore:
            # (1) Look through each forecast within FORECAST_TABLE (this list is already ordered).
            # (2) Look through all logs with meta__extra__forecast_update=True, in newest-first order.
            # (3) Keep track of leads as iterating:
            #       If this log's meta__extra__new_forecast == current forecast,
            #       and is first time seeing this log's lead,
            #       => this is the forecast with which this lead ended the report's date_range, so keep it!
            # (4) Stop once total_count_needed is fulfilled

            logs = self.activity_logs.filter(
                    activity=lead_constants.LEAD_UPDATED,
                    meta__extra__forecast_update=True,
                ).exclude(
                    lead__status__title=lead_constants.LEAD_CLOSED,
                    lead__expected_close_date__gte=self._report.date_range_from,
                    lead__expected_close_date__lte=self._report.date_range_to,
                ).prefetch_related("lead")

            for forecast in lead_constants.FORECAST_TABLE:
                if not total_needed_count:
                    break

                # Get unique leads
                # NOTE: Tried adding .distinct("lead")[:total_needed_count] to queryset, but error on distinct.
                # See: https://docs.djangoproject.com/en/dev/ref/models/querysets/#distinct
                # Therefore, going at it manually
                logs_for_forecast = logs.filter(meta__extra__new_forecast=forecast)
                leads_for_forecast = []
                for index, log in enumerate(logs_for_forecast):
                    if not total_needed_count:
                        break
                    lead = log.lead
                    if lead not in leads_for_forecast:
                        leads_for_forecast.append(lead)
                        total_needed_count -= 1
                output[forecast] = [
                                        data["fields"] for data in json.loads(
                                                        serializers.serialize(
                                                            "json",
                                                            leads_for_forecast,
                                                            fields=("title", "closing_amount", "amount")
                                                        ))
                                    ]
        return output

    @property
    def sales_cycle(self):
        # average: for leads closed, what is total time to close, as per story-report protocol
        count = len(self._closed_leads_data)
        aggregate = 0
        for cld in self._closed_leads_data:
            aggregate += cld["days_to_closed"]
        if count is 0:
            return None
        return aggregate / count

    @property
    def actions_to_close_opportunity(self):
        actions_map = {}
        # need to populate actions_map to produce 'most performed action'
        for cld in self._closed_leads_data:
            actions_dict = cld["custom_action_counts"]
            for key in actions_dict:
                if actions_map.get(key, None) is None:
                    actions_map[key] = actions_dict[key]
                else:
                    actions_map[key] += actions_dict[key]

        aggregate = sum(actions_map.values())
        count = len(self._closed_leads_data)

        return {
            "average": aggregate / count if count else None,
            "most_performed": max(actions_map) if bool(actions_map) else None,
        }

    @property
    def ACV(self):
        aggregate = self.amount_closed
        count = self.deals_closed_count
        if count is 0:
            return None
        return aggregate / count

    @property
    def deal_analysis(self):
        # (value => count) for each lead-custom-field:
        # -- company_size (char-field-choices)
        # -- industry (char-field-choices)
        # -- type (char-field-choices)
        # -- competitor (Bool)
        # -- geography (String, based on administrative_area_level_1)

        company_size_map = {}
        industry_map = {}
        type_map = {}
        competitor_map = {}
        geography_map = {}

        # run through CLOSED LEADS, populating the count-maps accordingly
        for lead in self._closed_leads:
            # company_size:
            if company_size_map.get(lead.company_size, None) is None:
                company_size_map[lead.company_size] = 1
            else:
                company_size_map[lead.company_size] += 1
            # industry:
            if industry_map.get(lead.industry, None) is None:
                industry_map[lead.industry] = 1
            else:
                industry_map[lead.industry] += 1
            # type:
            if type_map.get(lead.type, None) is None:
                type_map[lead.type] = 1
            else:
                type_map[lead.type] += 1
            # competitor:
            if competitor_map.get(lead.competitor, None) is None:
                competitor_map[lead.competitor] = 1
            else:
                competitor_map[lead.competitor] += 1
            # geography:
            geography_component = lead.geography_address_components.get("administrative_area_level_1", None)
            if geography_component is not None:
                key = geography_component["long_name"]
                if geography_map.get(key, None) is None:
                    geography_map[key] = 1
                else:
                    geography_map[key] += 1
            else:
                if geography_map.get(None, None) is None:
                    geography_map[None] = 1
                else:
                    geography_map[None] = 1

        def get_field_values(field_map):
            # need to filter out None
            num_null = field_map.get(None, 0)
            if num_null:
                del field_map[None]
            if bool(field_map):
                max_key = max(field_map)
                proportion = field_map[max_key] / (sum(field_map.values()) + num_null)
                percentage = round(proportion * 100)
                return {
                    "value": max_key,
                    "percentage": percentage,
                }
            else:
                return {
                    "value": None,
                    "percentage": None,
                }

        return {
            "company_size": get_field_values(company_size_map),
            "industry": get_field_values(industry_map),
            "type": get_field_values(type_map),
            "competitor": get_field_values(competitor_map),
            "geography": get_field_values(geography_map),
        }

    @property
    def as_dict(self):
        return {
            # For Summary Box:
            "activities_count": self.activities_count,
            "actions_count": self.actions_count,
            "incoming_messages_count": self.incoming_messages_count,
            "forecast_amount": self.forecast_amount,
            "deals_closed_count": self.deals_closed_count,
            "amount_closed": self.amount_closed,
            # Other:
            "forecast_table_additions": self.forecast_table_additions,
            "top_opportunities": self.top_opportunities,
            "sales_cycle": self.sales_cycle,
            "actions_to_close_opportunity": self.actions_to_close_opportunity,
            "ACV": self.ACV,
            "deal_analysis": self.deal_analysis,
        }


class RepTypicalData(BaseGenerator):
    """
    Generates average rep-level metrics for PerformanceReport.
    These metrics regard the rep's averages across time for a given date-range.
    Final output is the self.as_dict method.
    """
    def __init__(self, report):
        self.__cached__time_slices = None
        self.__cached__data_for_time_slices = None
        super().__init__(report)

    @property
    def __name__(self):
        return "RepTypicalData"

    # private properties:

    @property
    def _representative_join_date(self):
        return parse(self._representative.datetime_created) if isinstance(self._representative.datetime_created, str) else self._representative.datetime_created

    @property
    def _report_upper_bound(self):
        return parse(self._report.date_range_to) if isinstance(self._report.date_range_to, str) else self._report.date_range_to

    @property
    def _report_lower_bound(self):
        return parse(self._report.date_range_from) if isinstance(self._report.date_range_from, str) else self._report.date_range_from

    @property
    def _slice_length_in_days(self):
        return (self._report_upper_bound - self._report_lower_bound).days

    @property
    def _time_delta(self):
        return timezone.timedelta(days=self._slice_length_in_days)

    def _get_next_time_slice(self, current_slice):
        # Given current_slice, returns time-slice to its chronological-left
        return {
            "to": current_slice["to"] - self._time_delta,
            "from": current_slice["from"] - self._time_delta,
        }

    def _next_slice_would_be_invalid(self, current_slice):
        next_slice_lower_bound = self._get_next_time_slice(current_slice)["from"]
        return next_slice_lower_bound < self._representative_join_date

    @property
    def _time_slices(self):
        if self.__cached__time_slices is None:
            # reverse-chronological
            # "this [date-range]" is excluded
            # ignore remainder
            initial_slice = {
                "to": self._report_lower_bound,
                "from": self._report_lower_bound - self._time_delta,
            }
            slices_list = [initial_slice]
            latest_slice = initial_slice
            while not self._next_slice_would_be_invalid(latest_slice):
                # Build next slice
                new_slice = self._get_next_time_slice(latest_slice)
                # Insert at beginning of slices_list
                slices_list.insert(0, new_slice)
                # Set as latest_slice
                latest_slice = new_slice
            self.__cached__time_slices = slices_list
        return self.__cached__time_slices

    @property
    def _data_for_time_slices(self):
        if self.__cached__data_for_time_slices is None:
            data_list = []
            for ts in self._time_slices:
                non_db_report = PerformanceReport(
                    date_range_from=ts["from"],
                    date_range_to=ts["to"],
                    date_range_preset=self._report.date_range_preset,
                    representative=self._representative,
                    generated_by=self._report.generated_by,
                )
                data_item = RepFocusData(non_db_report).as_dict
                data_list.append(data_item)
            self.__cached__data_for_time_slices = data_list
        return self.__cached__data_for_time_slices

    # public properties:

    def average_for_field(self, field, sub_field=None, could_be_null=False, force_floats=False):
        if sub_field:
            target_data = [data_item[field][sub_field] for data_item in self._data_for_time_slices]
        else:
            target_data = [data_item[field] for data_item in self._data_for_time_slices]
        if could_be_null:
            no_nulls_target_data = list(filter(lambda x: x is not None, target_data))
            if force_floats:
                no_nulls_target_data = [float(item) for item in no_nulls_target_data]
            numerator = sum(no_nulls_target_data)
            denominator = len(no_nulls_target_data)
        else:
            if force_floats:
                target_data = [float(item) for item in target_data]
            numerator = sum(target_data)
            denominator = len(target_data)
        if denominator is 0:
            return None
        return numerator / denominator

    @property
    def as_dict(self):
        return {
            # For Summary Box:
            "activities_count": self.average_for_field("activities_count"),
            "actions_count": self.average_for_field("actions_count"),
            "incoming_messages_count": self.average_for_field("incoming_messages_count"),
            "forecast_amount": self.average_for_field("forecast_amount"),
            "deals_closed_count": self.average_for_field("deals_closed_count"),
            "amount_closed": self.average_for_field("amount_closed", force_floats=True),
            # Other:
            "forecast_table_additions": self.average_for_field("forecast_table_additions"),
            "sales_cycle": self.average_for_field("sales_cycle", could_be_null=True),
            "actions_to_close_opportunity": self.average_for_field(
                                                    "actions_to_close_opportunity",
                                                    sub_field="average",
                                                    could_be_null=True,
                                                ),
            "ACV": self.average_for_field("ACV", could_be_null=True, force_floats=True),
        }


class OrgFocusData(BaseGenerator):
    """
    Generates org-level metrics for PerformanceReport.
    These metrics regard the specific date-range of the report.
    Final outputs are two methods:
    (1) self.as_dict_for_organization_report
    (2) self.as_dict_for_representative_report
    """
    def __init__(self, report, representative=None):
        self.__cached__non_db_representative_reports = None
        self.__cached__representatives_data = None
        self.__cached__active_organization_reps = None
        self.__cached__active_rep_logs = None
        self.__cached__closed_leads = None
        self.__cached__closed_leads_data = None

        super().__init__(report)

    @property
    def __name__(self):
        return "OrgFocusData"

    # private properties:

    @property
    def _active_organization_reps(self):
        if self.__cached__active_organization_reps is None:
            reps = self._organization.users.filter(is_active=True)
            self.__cached__active_organization_reps = reps
        return self.__cached__active_organization_reps

    @property
    def _active_rep_logs(self):
        if self.__cached__active_rep_logs is None:
            logs = LeadActivityLog.objects.filter(
                        action_timestamp__gte=self._report.date_range_from,
                        action_timestamp__lte=self._report.date_range_to,
                        action_taken_by__in=self._active_organization_reps,
                    )
            self.__cached__active_rep_logs = logs
        return self.__cached__active_rep_logs

    @property
    def _closed_leads(self):
        if self.__cached__closed_leads is None:
            leads = Lead.objects.filter(
                status__title=lead_constants.LEAD_STATUS_CLOSED,
                claimed_by__in=self._active_organization_reps,
                expected_close_date__gte=self._report.date_range_from,
                expected_close_date__lte=self._report.date_range_to,
            )
            self.__cached__closed_leads = leads
        return self.__cached__closed_leads

    @property
    def _closed_leads_data(self):
        if self.__cached__closed_leads_data is None:
            data = [LeadDataGenerator(lead).as_dict for lead in self._closed_leads]
            self.__cached__closed_leads_data = data
        return self.__cached__closed_leads_data

    @property
    def _non_db_representative_reports(self):
        if self.__cached__non_db_representative_reports is None:
            self.__cached__non_db_representative_reports = [
                                                        PerformanceReport(
                                                            date_range_from=self._report.date_range_from,
                                                            date_range_to=self._report.date_range_to,
                                                            date_range_preset=self._report.date_range_preset,
                                                            generated_by=self._report.generated_by,
                                                            representative=representative,
                                                        ) for representative in self._active_organization_reps
                                                ]
        return self.__cached__non_db_representative_reports

    @property
    def _representatives_data(self):
        if self.__cached__representatives_data is None:
            data = [
                    {
                        "data": RepFocusData(report).as_dict,
                        "representative": report.representative,
                    } for report in self._non_db_representative_reports
                ]
            self.__cached__representatives_data = data
        return self.__cached__representatives_data

    def _generate_top_performers_sorter(self, by_metric, sub_field=False, highest_value_best=True):
        def sorter(rep_data):
            if sub_field and rep_data["data"][by_metric][sub_field] is None:
                return -float("inf") if highest_value_best else float("inf")
            if rep_data["data"][by_metric] is None:
                return -float("inf") if highest_value_best else float("inf")
            if sub_field:
                return rep_data["data"][by_metric][sub_field]
            return rep_data["data"][by_metric]
        return sorter

    def _deal_analysis_get_field_values(self, field_map):
        # need to filter out None
        num_null = field_map.get(None, 0)
        if num_null:
            del field_map[None]
        if bool(field_map):
            max_key = max(field_map)
            proportion = field_map[max_key] / (sum(field_map.values()) + num_null)
            percentage = round(proportion * 100)
            return {
                "value": max_key,
                "percentage": percentage,
            }
        else:
            return {
                "value": None,
                "percentage": None,
            }

    # public:

    def sum_for_field(self, field, sub_field=None, could_be_null=False, force_floats=False):
        if sub_field:
            target_data = [rep_data["data"][field][sub_field] for rep_data in self._representatives_data]
        else:
            target_data = [rep_data["data"][field] for rep_data in self._representatives_data]
        if could_be_null:
            target_data = list(filter(lambda x: x is not None, target_data))
        if force_floats:
            target_data = [float(item) for item in target_data]
        return sum(target_data)

    def average_for_field(self, field, sub_field=None, could_be_null=False, force_floats=False):
        if sub_field:
            target_data = [rep_data["data"][field][sub_field] for rep_data in self._representatives_data]
        else:
            target_data = [rep_data["data"][field] for rep_data in self._representatives_data]
        if could_be_null:
            no_nulls_target_data = list(filter(lambda x: x is not None, target_data))
            if force_floats:
                no_nulls_target_data = [float(item) for item in no_nulls_target_data]
            numerator = sum(no_nulls_target_data)
            denominator = len(no_nulls_target_data)
        else:
            if force_floats:
                target_data = [float(item) for item in target_data]
            numerator = sum(target_data)
            denominator = len(target_data)
        if denominator is 0:
            return None
        return numerator / denominator

    def top_performers(self, num_representatives=None, by_metric=None, highest_value_best=True, sub_field=None):
        if not num_representatives or not by_metric:
            raise ValidationError({"OrgFocusData.top_performers": "missing args.num_representatives or args.by_metric"})

        sorter = self._generate_top_performers_sorter(
                                                by_metric,
                                                sub_field=sub_field,
                                                highest_value_best=highest_value_best,
                                            )
        sorted_data = sorted(
                        self._representatives_data,
                        key=sorter,
                        reverse=highest_value_best,
                    )
        sorted_reps = [rep_data["representative"] for rep_data in sorted_data]
        top_performers = sorted_reps[0:num_representatives]
        serialized_top_performers = [
            UserRefSerializer(rep).data for rep in top_performers
        ]

        for i in range(len(serialized_top_performers)):
            serialized_top_performers[i]["rank"] = i + 1
            serialized_top_performers[i][by_metric] = sorted_data[i]["data"][by_metric]

        # if the report is representative-specific AND the focus-rep is missing
        if self._representative and self._representative not in top_performers:
            serialized_rep = UserRefSerializer(self._representative).data

            sorted_index = sorted_reps.index(self._representative)
            serialized_rep["rank"] = sorted_index + 1
            serialized_rep[by_metric] = sorted_data[sorted_index]["data"][by_metric]
            if len(serialized_top_performers) is num_representatives:
                # if there are three users in the list,
                # swap the last user for self._representative
                serialized_top_performers[num_representatives - 1] = serialized_rep
            else:
                # else append self._representative to the list
                serialized_top_performers.append(serialized_rep)
        return serialized_top_performers

    @property
    def top_opportunities(self):
        total_needed_count = 3
        output = {
            "CLOSED": [],
            "VERBAL": [],
            "STRONG": [],
            "50/50": [],
        }
        closed_leads = self._closed_leads.order_by('closing_amount')[:total_needed_count]

        output[lead_constants.FORECAST_CLOSED] = [
                                                        data["fields"] for data in json.loads(
                                                            serializers.serialize(
                                                                "json",
                                                                closed_leads,
                                                                fields=("title", "closing_amount", "amount")
                                                            ))
                                                    ]

        total_needed_count = total_needed_count - len(closed_leads)
        if total_needed_count:
            # Since still need leads, go through FORECAST_TABLE:
            # (1) largest VERBAL, then
            # (2) largest STRONG, then
            # (3) largest 50/50
            # --- else blank

            # These leads must have ended the report's date_range with this the respective forecast
            # Example: need to find leads that went into VERBAL and stayed in VERBAL as regards the report's date_range

            # Therefore:
            # (1) Look through each forecast within FORECAST_TABLE (this list is already ordered).
            # (2) Look through all logs with meta__extra__forecast_update=True, in newest-first order.
            # (3) Keep track of leads as iterating:
            #       If this log's meta__extra__new_forecast == current forecast,
            #       and is first time seeing this log's lead,
            #       => this is the forecast with which this lead ended the report's date_range, so keep it!
            # (4) Stop once total_count_needed is fulfilled

            logs = self._active_rep_logs.filter(
                    activity=lead_constants.LEAD_UPDATED,
                    meta__extra__forecast_update=True,
                ).exclude(
                    lead__status__title=lead_constants.LEAD_CLOSED,
                    lead__expected_close_date__gte=self._report.date_range_from,
                    lead__expected_close_date__lte=self._report.date_range_to,
                ).prefetch_related("lead")

            for forecast in lead_constants.FORECAST_TABLE:
                if not total_needed_count:
                    break

                # Get unique leads
                # NOTE: Tried adding .distinct("lead")[:total_needed_count] to queryset, but error on distinct.
                # See: https://docs.djangoproject.com/en/dev/ref/models/querysets/#distinct
                # Therefore, going at it manually
                logs_for_forecast = logs.filter(meta__extra__new_forecast=forecast)
                leads_for_forecast = []
                for index, log in enumerate(logs_for_forecast):
                    if not total_needed_count:
                        break
                    lead = log.lead
                    if lead not in leads_for_forecast:
                        leads_for_forecast.append(lead)
                        total_needed_count -= 1
                output[forecast] = [
                                        data["fields"] for data in json.loads(
                                                        serializers.serialize(
                                                            "json",
                                                            leads_for_forecast,
                                                            fields=("title", "closing_amount", "amount")
                                                        ))
                                    ]
        return output

    @property
    def actions_to_close_opportunity_most_performed(self):
        actions_map = {}
        for cld in self._closed_leads_data:
            actions_dict = cld["custom_action_counts"]
            for key in actions_dict:
                if actions_map.get(key, None) is None:
                    actions_map[key] = actions_dict[key]
                else:
                    actions_map[key] += actions_dict[key]
        return max(actions_map) if bool(actions_map) else None

    @property
    def deal_analysis(self):
        # (value => count) for each lead-custom-field:
        # -- company_size (char-field-choices)
        # -- industry (char-field-choices)
        # -- type (char-field-choices)
        # -- competitor (Bool)
        # -- geography (String, based on administrative_area_level_1)

        company_size_map = {}
        industry_map = {}
        type_map = {}
        competitor_map = {}
        geography_map = {}

        # run through CLOSED LEADS, populating the count-maps accordingly
        for lead in self._closed_leads:
            # company_size:
            if company_size_map.get(lead.company_size, None) is None:
                company_size_map[lead.company_size] = 1
            else:
                company_size_map[lead.company_size] += 1
            # industry:
            if industry_map.get(lead.industry, None) is None:
                industry_map[lead.industry] = 1
            else:
                industry_map[lead.industry] += 1
            # type:
            if type_map.get(lead.type, None) is None:
                type_map[lead.type] = 1
            else:
                type_map[lead.type] += 1
            # competitor:
            if competitor_map.get(lead.competitor, None) is None:
                competitor_map[lead.competitor] = 1
            else:
                competitor_map[lead.competitor] += 1
            # geography:
            geography_component = lead.geography_address_components.get("administrative_area_level_1", None)
            if geography_component is not None:
                key = geography_component["long_name"]
                if geography_map.get(key, None) is None:
                    geography_map[key] = 1
                else:
                    geography_map[key] += 1
            else:
                if geography_map.get(None, None) is None:
                    geography_map[None] = 1
                else:
                    geography_map[None] = 1

        return {
            "company_size": self._deal_analysis_get_field_values(company_size_map),
            "industry": self._deal_analysis_get_field_values(industry_map),
            "type": self._deal_analysis_get_field_values(type_map),
            "competitor": self._deal_analysis_get_field_values(competitor_map),
            "geography": self._deal_analysis_get_field_values(geography_map),
        }

    @property
    def as_dict_for_organization_report(self):
        return {
            # For Summary Box:
            "activities_count": self.sum_for_field("activities_count"),
            "actions_count": self.sum_for_field("actions_count"),
            "incoming_messages_count": self.sum_for_field("incoming_messages_count"),
            "forecast_amount": self.sum_for_field("forecast_amount"),
            "deals_closed_count": self.sum_for_field("deals_closed_count"),
            "amount_closed": self.sum_for_field("amount_closed", force_floats=True),
            # For Top Perfomer fields:
            "top_performers_by_A_C_V": self.top_performers(
                                                by_metric="ACV",
                                                num_representatives=5,
                                        ),
            "top_performers_by_actions": self.top_performers(
                                                by_metric="actions_count",
                                                num_representatives=3,
                                        ),
            # Other:
            "forecast_table_additions": {
                "value": self.sum_for_field("forecast_table_additions"),
                "top_performer": self.top_performers(
                                    by_metric="forecast_table_additions",
                                    num_representatives=1,
                                ),
            },
            "top_opportunities": self.top_opportunities,
            "sales_cycle": {
                "average": self.average_for_field("sales_cycle", could_be_null=True),
                "top_performer": self.top_performers(
                                    by_metric="sales_cycle",
                                    highest_value_best=False,
                                    num_representatives=1,
                                ),
            },
            "actions_to_close_opportunity": {
                "average": self.average_for_field(
                            "actions_to_close_opportunity",
                            sub_field="average",
                            could_be_null=True,
                        ),
                "top_performer": self.top_performers(
                                    by_metric="actions_to_close_opportunity",
                                    highest_value_best=False,
                                    sub_field="average",
                                    num_representatives=1,
                                ),
                "most_performed": self.actions_to_close_opportunity_most_performed,
            },
            "ACV": {
                "average": self.average_for_field("ACV", could_be_null=True, force_floats=True),
                "top_performer": self.top_performers(
                                    by_metric="ACV",
                                    num_representatives=1,
                                ),
            },
            # For Deal Analysis:
            "deal_analysis": self.deal_analysis,
        }

    @property
    def as_dict_for_representative_report(self):
        return {
            "top_performers": self.top_performers(
                                                by_metric="ACV",
                                                num_representatives=3
                                ),
        }


class OrgTypicalData(BaseGenerator):
    """
    Generates average org-level metrics for PerformanceReport.
    These metrics regard the org's averages across time for a given date-range.
    Final outputs are two methods:
    (1) self.as_dict_for_organization_report
    (2) self.as_dict_for_representative_report
    """

    def __init__(self, report):
        self.__cached__non_db_representative_reports = None
        self.__cached__averages_per_rep = None
        super().__init__(report)

    @property
    def __name__(self):
        return "OrgTypicalData"

    # private properties:

    @property
    def _non_db_representative_reports(self):
        if self.__cached__non_db_representative_reports is None:
            self.__cached__non_db_representative_reports = [
                                                        PerformanceReport(
                                                            date_range_from=self._report.date_range_from,
                                                            date_range_to=self._report.date_range_to,
                                                            date_range_preset=self._report.date_range_preset,
                                                            generated_by=self._report.generated_by,
                                                            representative=representative,
                                                        ) for representative in self._organization.users.filter(is_active=True)
                                                ]
        return self.__cached__non_db_representative_reports

    @property
    def _averages_per_rep(self):
        if self.__cached__averages_per_rep is None:
            self.__cached__averages_per_rep = [
                        RepTypicalData(report).as_dict
                        for report in self._non_db_representative_reports
                ]
        return self.__cached__averages_per_rep

    # public:

    def average_for_field(self, field, sub_field=None, could_be_null=False, force_floats=False):
        if sub_field:
            target_data = [rep_data[field][sub_field] for rep_data in self._averages_per_rep]
        else:
            target_data = [rep_data[field] for rep_data in self._averages_per_rep]
        if could_be_null:
            no_nulls_target_data = list(filter(lambda x: x is not None, target_data))
            if force_floats:
                no_nulls_target_data = [float(item) for item in no_nulls_target_data]
            numerator = sum(no_nulls_target_data)
            denominator = len(no_nulls_target_data)
        else:
            if force_floats:
                target_data = [float(item) for item in target_data]
            numerator = sum(target_data)
            denominator = len(target_data)
        if denominator is 0:
            return None
        return numerator / denominator

    @property
    def as_dict_for_organization_report(self):
        return {
            # For Summary Box:
            "activities_count": self.average_for_field("activities_count"),
            "actions_count": self.average_for_field("actions_count"),
            "incoming_messages_count": self.average_for_field("incoming_messages_count"),
            "forecast_amount": self.average_for_field("forecast_amount"),
            "deals_closed_count": self.average_for_field("deals_closed_count"),
            "amount_closed": self.average_for_field("amount_closed", force_floats=True),
            # For Forecast Table:
            "forecast_table_additions": self.average_for_field("forecast_table_additions"),
            # For Sales Cycle:
            "sales_cycle": self.average_for_field("sales_cycle", could_be_null=True),
            # For Actions to Close Opportunity:
            "actions_to_close_opportunity": self.average_for_field(
                                                    "actions_to_close_opportunity",
                                                    could_be_null=True,
                                            ),
            # For ACV:
            "ACV": self.average_for_field("ACV", could_be_null=True, force_floats=True),
        }

    @property
    def as_dict_for_representative_report(self):
        return {
            # For Summary Box:
            "activities_count": self.average_for_field("activities_count"),
            "actions_count": self.average_for_field("actions_count"),
            "incoming_messages_count": self.average_for_field("incoming_messages_count"),
            "forecast_amount": self.average_for_field("forecast_amount"),
            "deals_closed_count": self.average_for_field("deals_closed_count"),
            "amount_closed": self.average_for_field("amount_closed", force_floats=True),
        }
