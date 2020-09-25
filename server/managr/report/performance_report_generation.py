import logging
import json
import inspect
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from django.core import serializers
from django.db.models import Q, Sum

from managr.core.models import EmailAuthAccount
from managr.lead.models import LeadActivityLog

from managr.lead import constants as lead_constants
from managr.lead.serializers import LeadRefSerializer
from managr.core.nylas.emails import send_new_email_legacy
from managr.utils.sites import get_site_url

from .models import PerformanceReport
from .story_report_generation import LeadDataGenerator

logger = logging.getLogger("managr")

# NOTE: remove import:
from pdb import set_trace


def generate_performance_report_data(performance_report_id, generated_by_id):
    """
    Given a PerformanceReport UUID, generate the report's
    data and update the instance with the generated data.
    Finally, trigger email regarding report availability to
    user that triggered this performance_report to be generated.
    """
    performance_report = PerformanceReport.objects.get(pk=performance_report_id)

    # NOTE: here need to figure out if org-wide or rep-specific, use classes accordingly

    try:
        # generate report's data
        performance_report.data["focus"] = RepDataForSelectedDateRange(performance_report).as_dict
        # performance_report.data["representative"] = RepresentativeDataGenerator(lead).as_dict
        # performance_report.data["organization"] = OrganizationDataGenerator(lead).as_dict
        performance_report.datetime_generated = timezone.now()
        performance_report.save()
        # send email to user that generated report
        # send_email(performance_report)
    except Exception as e:
        # TODO (Bruno 09-22-2020):
        # Send an email to user that generated report notifying of failure?
        logger.exception(
            f"failed to generate performance report with UUID {performance_report_id}, error: {e}"
        )


def send_email(report):
    recipient = report.generated_by

    ea = EmailAuthAccount.objects.filter(user__is_serviceaccount=True).first()
    if ea:
        token = ea.access_token
        sender = {"email": ea.email_address, "name": "Managr"}
        recipient = [{"email": recipient.email, "name": recipient.full_name}]
        message = {
            "subject": f"Story Report Generated for {report.lead.title}",
            "body": f"The report is available at {report.client_side_url}.",
        }
        try:
            send_new_email_legacy(token, sender, recipient, message)
        except Exception as e:
            """ this error is most likely going to be an error on our set
            up rather than the user_token """
            pass


# NOTE: the following classes regard representative-specific
# (as opposed to organization-wide) performance report data generation

class BaseGenerator:
    def __init__(self, report):
        self._report = report
        self._organization = report.generated_by.organization
        self._representative = report.representative

    def failure_logger(self, e):
        method_name = inspect.stack()[1][3]
        class_name = RepThisDateRange.__name__
        logger.exception(
            f"Unable to create report UUID {self._report.id} failed at method {method_name} of class {class_name}, with error {e}"
        )
        raise (e)


class RepDataForSelectedDateRange(BaseGenerator):
    """
    Generates rep-level metrics for PerformanceReport.
    These metrics regard the specific date-range of the report.
    Final output is the self.as_dict method.
    """

    # private properties:

    @property
    def _logs_for_closing_events(self):
        return self.activity_logs.filter(
            activity=lead_constants.LEAD_CLOSED,
        )

    @property
    def _closed_leads(self):
        return {log.lead for log in self._logs_for_closing_events.prefetch_related("lead")}

    @property
    def _closed_leads_data(self):
        return [LeadDataGenerator(lead).as_dict for lead in self._closed_leads]

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
            lead.id = log.lead.id
            forecast_amount = log.meta["extra"]["forecast_amount"]
            if lead_amounts.get(lead.id, None) is None:
                lead_amounts[lead.id] = forecast_amount
            else:
                lead_amounts[lead.id] = max(lead_amounts[lead.id], forecast_amount)
        return sum(lead_amounts.values())

    @property
    def deals_closed_count(self):
        return self._logs_for_closing_events.count()

    @property
    def amount_closed(self):
        return self._logs_for_closing_events.prefetch_related(
            "lead"
        ).aggregate(
            sum=Sum("lead__closing_amount")
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
            "CLOSED": None,
            "VERBAL": None,
            "STRONG": None,
            "50/50": None,
        }
        closed_leads = [
            log.lead for log in self._logs_for_closing_events.prefetch_related("lead").order_by('lead__closing_amount')[:total_needed_count]
        ]
        output[lead_constants.LEAD_STATUS_CLOSED] = [data["fields"] for data in json.loads(
                                                        serializers.serialize(
                                                            "json",
                                                            closed_leads,
                                                            fields=("pk", "title", "closing_amount", "amount")
                                                        ))
                                                    ]

        if len(closed_leads) == total_needed_count:
            # There is no need to look through logs regarding entrance into FORECAST_TABLE
            pass
        else:
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

            still_needed_count = total_needed_count - len(closed_leads)
            logs = self.activity_logs.filter(
                    activity=lead_constants.LEAD_UPDATED,
                    meta__extra__forecast_update=True,
                ).exclude(
                    lead__status__title=lead_constants.LEAD_CLOSED,
                    lead__expected_close_date__gte=self._report.date_range_from,
                    lead__expected_close_date__lte=self._report.date_range_to,
                ).prefetch_related("lead")
            for forecast in lead_constants.FORECAST_TABLE:
                if total_needed_count == still_needed_count:
                    break
                leads_logged = {}
                target_leads = []
                for log in logs:
                    if log.meta["extra"].get("new_forecast") == forecast and not leads_logged.get(log.lead_id):
                        target_leads.append(log.lead)
                    if len(target_leads) == still_needed_count:
                        break
                    leads_logged[log.lead_id] = True
                output[forecast] = [data["fields"] for data in json.loads(
                                                        serializers.serialize(
                                                            "json",
                                                            target_leads,
                                                            fields=("pk", "title", "closing_amount", "amount")
                                                        ))
                                                    ]
                still_needed_count -= len(target_leads)
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
        return round(aggregate / count)

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
            "average": round(aggregate / count),
            "most_performed": max(actions_map),
        }

    @property
    def ACV(self):
        aggregate = self.amount_closed
        count = self.deals_closed_count
        if count is 0:
            return None
        return round(aggregate / count, 2)


    @property
    def deal_analysis(self):
        # (value => count) for each lead-custom-field:
        # -- company_size (char-field-choices)
        # -- industry (char-field-choices)
        # -- type (char-field-choices)
        # -- competitor (Bool)
        # -- geography_address_components (???)

        company_size_map = {}
        industry_map = {}
        type_map = {}
        competitor_map = {}
        geography_map = {}

        # run through CLOSED LEADS DATA
        for cld in self._closed_leads:
            # company_size:
            if company_size_map.get(cld.company_size, None) is None:
                company_size_map[cld.company_size] = 1
            else:
                company_size_map[cld.company_size] += 1
            # industry:
            if industry_map.get(cld.industry, None) is None:
                industry_map[cld.industry] = 1
            else:
                industry_map[cld.industry] += 1
            # type:
            if type_map.get(cld.type, None) is None:
                type_map[cld.type] = 1
            else:
                type_map[cld.type] += 1
            # competitor:
            if competitor_map.get(cld.competitor, None) is None:
                competitor_map[cld.competitor] = 1
            else:
                competitor_map[cld.competitor] += 1
            # geography:
            # if company_size_map.get(cld.company_size, None) is None:
            #     company_size_map[cld.company_size] = 1
            # else:
            #     company_size_map[cld.company_size] += 1

        # TODO: figure top per field, figure out geography
        return {
            "company_size": company_size_map,
            "industry": industry_map,
            "type": type_map,
            "competitor": competitor_map,
            "geograpy": None,
        }

    # -------------------------------------

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
            # For next few boxes:
            "forecast_table_additions": self.forecast_table_additions,
            "top_opportunities": self.top_opportunities,
            "sales_cycle": self.sales_cycle,
            "actions_to_close_opportunity": self.actions_to_close_opportunity,
            "ACV": self.ACV,
            # For Deal-Analysis Box:
            "deal_analysis": self.deal_analysis,
        }


class RepDataAverageForSelectedDateRange(BaseGenerator):
    """
    Generates rep-level metrics for PerformanceReport.
    These metrics regard the rep's averages across time for a given date-range.
    Final output is the self.as_dict method.
    """
    pass
