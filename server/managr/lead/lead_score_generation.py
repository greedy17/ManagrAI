from django.utils import timezone

from managr.lead import constants as lead_const
from managr.organization import constants as org_const
from managr.lead.models import Lead, LeadScore, LeadActivityLog
from managr.organization.models import Stage


def generate_lead_scores():
    # the score regards the last 30 days of lead activity
    score_upper_bound = timezone.now()
    score_lower_bound = score_upper_bound - timezone.timedelta(days=30)
    # all open (not-closed) leads should be targeted for score-generation
    open_leads = Lead.objects.exclude(status__title=lead_const.LEAD_STATUS_CLOSED)
    for lead in open_leads:
        generate(lead, score_upper_bound, score_lower_bound)


def generate(lead, score_upper_bound, score_lower_bound):
    # given the lead
    # (1) put lead through score-generator.as_dict
    # (2) create the LeadScore with the generated score, along with bounds meta-data
    pass


class LeadScoreGenerator:
    # MVP: get the lead score
    # later can add things like:
    # "Recently Moved to a new Stage" (20/10 days)
    # "Very recently moved to a new stage" (5 days)
    # "Getting stuck in a Stage" (30 days)
    # "On the Forecast "(went to 50/50)
    # Forecast momentum is Increasing (went to Strong)
    # Forecast momentum is Significantly Increasing (went to verbal)
    # Timeline was moved up
    # timeline was pushed to next month/quarter
    # No timeline to close
    # "Opportunity was worked yesterday"
    def __init__(self, lead, upper_bound, lower_bound):
        self.lead = lead
        self.upper_bound = upper_bound
        self.lower_bound = lower_bound
        # cache:
        self.__cached__logs = None

    @property
    def _logs(self):
        # lead's activity logs, time-bound
        if self.__cached__logs is None:
            logs = self.lead.activity_logs.filter(
                    action_timestamp__gte=self.lower_bound,
                    action_timestamp__lte=self.upper_bound,
                )
            self.__cached__logs = logs
        return self.__cached__logs

    @property
    def actions_score(self):
        # Count of Actions (up to 25 pts) - 5 pts per action
        maximum = 25
        points_per = 5
        count = self.lead.actions.filter(
                            datetime_created__gte=self.lower_bound,
                            datetime_created__lte=self.upper_bound
                        ).count()
        return min(count * points_per, maximum)

    @property
    def incoming_messages_score(self):
        # Count of Incoming Messages ( up to 20 pts) - 5 pts per inbound text or email
        maximum = 20
        points_per = 5
        count = self._logs.filter(
                            activity__in=[
                                lead_const.EMAIL_RECEIVED,
                                lead_const.MESSAGE_RECEIVED,
                            ],
                        ).count()
        return min(count * points_per, maximum)

    @property
    def days_in_stage_score(self):
        # Days in Stage (up to 20 pts)
        # under 30 days = 5 pts
        # under 20 days = 10 pts
        # under 10 days = 15 pts
        # under 5 days = 20 pts
        # Exclude: Ready, Lost, Reset
        ready = Stage.objects.get(
                title=lead_constants.LEAD_STATUS_READY,
                type=org_constants.STAGE_TYPE_PUBLIC,
            )
        lost = Stage.objects.get(
                title=lead_constants.LEAD_STATUS_LOST,
                type=org_constants.STAGE_TYPE_PUBLIC,
            )
        latest_stage_change = self._logs.filter(
                activity=lead_constants.LEAD_UPDATED,
                meta__extra__status_update=True,
            ).exclude(
                meta__extra__new_status__in=[ready.id, lost.id],
            ).first()
        if not latest_stage_change:
            return 0
        five_days_ago = self.upper_bound - timezone.timedelta(days=5)
        if latest_stage_change.action_timestamp >= five_days_ago:
            return 20
        ten_days_ago = self.upper_bound - timezone.timedelta(days=10)
        if latest_stage_change.action_timestamp >= ten_days_ago:
            return 15
        twenty_days_ago = self.upper_bound - timezone.timedelta(days=20)
        if latest_stage_change.action_timestamp >= twenty_days_ago:
            return 10
        thirty_days_ago = self.upper_bound - timezone.timedelta(days=30)
        if latest_stage_change.action_timestamp >= thirty_days_ago:
            return 5
        return 0

    def _get_forecast_score(previous_forecast=None, new_forecast=None):
        # Unforecasted OR Future to 50/50 - 5 pts
        # Unforecasted OR Future OR 50/50 to Strong - 10 pts
        # Unforecasted OR Future OR 50/50 or Strong to Verbal - 20 pts
        if previous_forecast is None or new_forecast is None:
            raise ValueError('args.previous_forecast & args.new_forecast are required')
        map_dict = {}
        map_dict[lead_const.FORECAST_VERBAL] = 20
        map_dict[lead_const.FORECAST_STRONG] = 10
        map_dict[lead_const.FORECAST_FIFTY_FIFTY] = 5
        # FORECAST_TABLE is in order, most-weight first
        if previous_forecast not in lead_const.FORECAST_TABLE:
            return map_dict.get(new_forecast, 0)
        if lead_const.FORECAST_TABLE.index(previous_forecast) < lead_const.FORECAST_TABLE.index(new_forecast):
            # the new forecast weighs less than the old forecast
            return 0
        # the new forecast weighs more than the old forecast
        return map_dict[new_forecast]

    @property
    def forecast_table_score(self):
        # Moved Into into a stronger FC state (up to 20 pts)
        forecast_logs = self._logs.filter(
                activity=lead_const.LEAD_UPDATED,
                meta__extra__forecast_update=True,
            )
        log_count = forecast_logs.count()
        if log_count is 0:
            return 0
        newest_log_data = forecast_logs.first().meta.get('extra')
        newest_forecast = newest_log_data.get('new_forecast')
        if log_count is 1:
            # these are forecast.forecast constants
            oldest_forecast = newest_log_data.get('previous_forecast')
            return self._get_forecast_score(
                            previous_forecast=oldest_forecast,
                            new_forecast=newest_forecast
                        )
        # if there are multiple logs, compare the total change in forecast
        # (oldest and newest, ignoring any middle-stages)
        oldest_log_data = forecast_logs.last().meta.get('extra')
        oldest_forecast = oldest_log_data.get('previous_forecast')
        return self._get_forecast_score(
                            previous_forecast=oldest_forecast,
                            new_forecast=newest_forecast
                        )

    @property
    def expected_close_date_score(self):
        # Expected Close date moved up (15 pts)
        # Exp close date moved up to current month (15 pts)
        # Exp close date moved up to current quarter (10 pts)
        # Expected closed date moved up by any days (5 pt)
        # Exp close date moved back beyond this month (-10 pts)
        # Exp close date moved back beyond this quarter or NO expected close date (-15 pts)
        # Expected closed date moved back any days (-5 pt)
        pass

    @property
    def recent_work_score(self):
        # Any of the 5 actions taken within that day is +5 points, cannot exceed cap of 100. 
        pass
