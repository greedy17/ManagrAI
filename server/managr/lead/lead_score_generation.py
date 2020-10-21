import logging
from django.utils import timezone, dateparse

from managr.lead import constants as lead_const
from managr.organization import constants as org_const
from managr.lead.models import Lead, LeadScore, LeadActivityLog
from managr.organization.models import Stage

logger = logging.getLogger("managr")


def generate_lead_scores():
    # the score regards the last 30 days of lead activity
    date_range_end = timezone.now()
    date_range_start = date_range_end - timezone.timedelta(days=30)
    # all open (not-closed) leads should be targeted for score-generation
    open_leads = Lead.objects.exclude(status__title=lead_const.LEAD_STATUS_CLOSED)
    for lead in open_leads:
        generate_score(lead, date_range_end, date_range_start)


def generate_score(lead, date_range_end, date_range_start):
    try:
        # (1) put lead through score-generator
        data = LeadScoreGenerator(
                        lead,
                        date_range_end,
                        date_range_start,
                    )
        # (2) create the LeadScore
        LeadScore.objects.create(
            lead=lead,
            previous_score=lead.scores.first(),
            date_range_end=date_range_end,
            date_range_start=date_range_start,
            # scores
            actions_score=data.actions_score,
            recent_action_score=data.recent_action_score,
            incoming_messages_score=data.incoming_messages_score,
            days_in_stage_score=data.days_in_stage_score,
            forecast_table_score=data.forecast_table_score,
            expected_close_date_score=data.expected_close_date_score,
            # insights
            actions_insight=data.actions_insight,
            recent_action_insight=data.recent_action_insight,
            incoming_messages_insight=data.incoming_messages_insight,
            days_in_stage_insight=data.days_in_stage_insight,
            forecast_table_insight=data.forecast_table_insight,
            expected_close_date_insight=data.expected_close_date_insight,
        )
    except Exception as e:
        logger.warning(
            f"Could not generate LeadScore for Lead {lead.id}. ERROR: {e}"
        )


class LeadScoreGenerator:
    def __init__(self, lead, upper_bound, lower_bound):
        self.lead = lead
        self.upper_bound = upper_bound
        self.lower_bound = lower_bound
        # cache:
        self.__cached__logs = None
        self.__cached__actions_score = None
        self.__cached__recent_action_score = None
        self.__cached__incoming_messages_score = None
        self.__cached__days_in_stage_score = None
        self.__cached__forecast_table_score = None
        self.__cached__expected_close_date_score = None

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
        if self.__cached__actions_score is None:
            maximum = 25
            points_per = 5
            count = self.lead.actions.filter(
                                datetime_created__gte=self.lower_bound,
                                datetime_created__lte=self.upper_bound
                            ).count()
            self.__cached__actions_score = min(count * points_per, maximum)
        return self.__cached__actions_score

    @property
    def actions_insight(self):
        score = self.actions_score
        if score is 25:
            return "Interaction is very high."
        if score is 20:
            return "Interaction is high."
        if score is 15:
            return "Interaction is moderate."
        if score is 10:
            return "Interaction is ok."
        if score is 5:
            return "Interaction is low."
        return "No Interactions."

    @property
    def recent_action_score(self):
        # Any of the 5 actions taken within past day is +5 points
        if self.__cached__recent_action_score is None:
            lower_bound = self.upper_bound - timezone.timedelta(days=1)
            recent_action = self.lead.actions.filter(
                                datetime_created__gte=lower_bound,
                                datetime_created__lte=self.upper_bound
                            ).first()
            self.__cached__recent_action_score = 5 if recent_action else 0
        return self.__cached__recent_action_score

    @property
    def recent_action_insight(self):
        score = self.recent_action_score
        if score:
            return "Opportunity was worked yesterday."

    @property
    def incoming_messages_score(self):
        # Count of Incoming Messages ( up to 20 pts) - 5 pts per inbound text or email
        if self.__cached__incoming_messages_score is None:
            maximum = 20
            points_per = 5
            count = self._logs.filter(
                                activity__in=[
                                    lead_const.EMAIL_RECEIVED,
                                    lead_const.MESSAGE_RECEIVED,
                                ],
                            ).count()
            self.__cached__incoming_messages_score = min(count * points_per, maximum)
        return self.__cached__incoming_messages_score

    @property
    def incoming_messages_insight(self):
        score = self.incoming_messages_score
        if score is 20:
            return "Engagement is very high."
        if score is 15:
            return "Engagement is high."
        if score is 10:
            return "Engagement is moderate."
        if score is 5:
            return "Engagement is low."
        return "No Engagement."

    @property
    def days_in_stage_score(self):
        if self.__cached__days_in_stage_score is None:
            self.__cached__days_in_stage_score = self._generate_days_in_stage_score()
        return self.__cached__days_in_stage_score

    def _generate_days_in_stage_score(self):
        # Days in Stage (up to 20 pts)
        # under 30 days = 5 pts
        # under 20 days = 10 pts
        # under 10 days = 15 pts
        # under 5 days = 20 pts
        # Exclude: Ready, Lost, Reset
        ready = Stage.objects.get(
                title=lead_const.LEAD_STATUS_READY,
                type=org_const.STAGE_TYPE_PUBLIC,
            )
        lost = Stage.objects.get(
                title=lead_const.LEAD_STATUS_LOST,
                type=org_const.STAGE_TYPE_PUBLIC,
            )
        latest_stage_change = self._logs.filter(
                activity__in=[
                    lead_const.LEAD_UPDATED,
                    lead_const.LEAD_RESET,
                ],
                meta__extra__status_update=True,
            ).exclude(
                meta__extra__new_status__in=[
                    str(ready.id),
                    str(lost.id),
                ],
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

    @property
    def days_in_stage_insight(self):
        score = self.days_in_stage_score
        if score is 20:
            # 5 days
            return "Very recently moved to a new Stage."
        if score is 15 or score is 10:
            # 20/10 days
            return "Recently moved to a new Stage."
        if score is 5:
            # 30 days
            return "Getting stuck in a Stage."

    def _get_forecast_score(self, previous_forecast=None, new_forecast=None):
        # Unforecasted OR Future to 50/50 - 5 pts
        # Unforecasted OR Future OR 50/50 to Strong - 10 pts
        # Unforecasted OR Future OR 50/50 or Strong to Verbal - 20 pts
        if previous_forecast is None or new_forecast is None:
            raise ValueError(
                    'args.previous_forecast & args.new_forecast are required'
                )
        map_dict = {}
        map_dict[lead_const.FORECAST_VERBAL] = 20
        map_dict[lead_const.FORECAST_STRONG] = 10
        map_dict[lead_const.FORECAST_FIFTY_FIFTY] = 5
        if previous_forecast not in lead_const.FORECAST_TABLE:
            return map_dict.get(new_forecast, 0)
        # FORECAST_TABLE is in order, most-weight first
        if lead_const.FORECAST_TABLE.index(previous_forecast) < lead_const.FORECAST_TABLE.index(new_forecast):
            # the new forecast weighs less than the old forecast
            return 0
        # the new forecast weighs more than the old forecast
        return map_dict[new_forecast]

    @property
    def forecast_table_score(self):
        if self.__cached__forecast_table_score is None:
            self.__cached__forecast_table_score = self._generate_forecast_table_score()
        return self.__cached__forecast_table_score

    def _generate_forecast_table_score(self):
        # Moved Into into a stronger FC state (up to 20 pts)
        forecast_logs = self._logs.filter(
                activity__in=[
                    lead_const.LEAD_UPDATED,
                    lead_const.LEAD_RESET,
                ],
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
                            new_forecast=newest_forecast,
                        )
        # if there are multiple logs, compare the total change in forecast
        # (oldest and newest, ignoring any middle-stages)
        oldest_log_data = forecast_logs.last().meta.get('extra')
        oldest_forecast = oldest_log_data.get('previous_forecast')
        score = 0
        try:
            score = self._get_forecast_score(
                            previous_forecast=oldest_forecast,
                            new_forecast=newest_forecast,
                        )
        except ValueError:
            pass
        return score

    @property
    def forecast_table_insight(self):
        score = self.forecast_table_score
        if score is 20:
            return "Forecast momentum is significantly increasing."
        if score is 10:
            return "Forecast momentum is increasing."
        if score is 5:
            return "On the Forecast Table."

    @property
    def expected_close_date_score(self):
        if self.__cached__expected_close_date_score is None:
            self.__cached__expected_close_date_score = self._generate_expected_close_date_score()
        return self.__cached__expected_close_date_score

    def _generate_expected_close_date_score(self):
        # Expected Close date change (15 pts)
        # (1) --  Exp close date moved up to current month (15 pts)
        # (2) --  Exp close date moved up to current quarter (10 pts)
        # (3) --  (a) Exp close date moved up by any days,
        #         (b) OR added exp close date (5 pt)
        # (4) --  Exp close date moved back 30 or more days (-10 pts)
        # (5) --  (a) Exp close date moved back 90 or more,
        #         (b) OR removed expected close date (-15 pts)
        # (6) --  Expected closed date moved back any days (-5 pt)
        latest_log = self._logs.filter(
                activity__in=[
                    lead_const.LEAD_UPDATED,
                    lead_const.LEAD_RESET,
                ],
                meta__extra__expected_close_date_update=True,
            ).first()
        if not latest_log:
            return 0
        current_datetime = self.upper_bound
        current_month = current_datetime.month
        current_quarter = ((current_month - 1) // 3) + 1
        # NOTE: 'previous' regards the previous value of expected_close_date
        # so previous_month regards the month of the previous value of expected_close_date
        previous_from_meta = latest_log.meta.get(
                                    'extra'
                                ).get(
                                    'previous_expected_close_date'
                                )
        if previous_from_meta:
            previous_datetime = dateparse.parse_datetime(previous_from_meta)
            previous_month = previous_datetime.month
            previous_quarter = ((previous_month - 1) // 3) + 1
        # NOTE: 'new' regards the newest / most-recent value of expected_close_date
        # so new_month regards the month of the current value of expected_close_date
        new_from_meta = latest_log.meta.get(
                                    'extra'
                                ).get(
                                    'new_expected_close_date'
                                )
        if new_from_meta:
            new_datetime = dateparse.parse_datetime(new_from_meta)
            new_month = new_datetime.month
            new_quarter = ((new_month - 1) // 3) + 1
        # NOTE: they both cannot be null b/c there is a log so there is a change
        if not previous_from_meta and new_from_meta:
            set_to_current_month = new_month is current_month
            if set_to_current_month:
                # scenario (1) -- Exp close date moved up to current month (15 pts)
                return 15
            set_to_current_quarter = new_quarter is current_quarter
            if set_to_current_quarter:
                # scenario (2) -- Exp close date moved up to current quarter (10 pts)
                return 10
            # scenario (3b) -- Added exp close date (5 pts)
            return 5
        if previous_from_meta and not new_from_meta:
            # scenario (5b) -- Removed expected close date (-15 pts)
            return -15
        # NOTE: from this point forward, can assume both values are truthy
        # scenario (1) -- Exp close date moved up to current month (15 pts)
        hurried_to_current_month = (previous_month is not current_month) and (new_month is current_month)
        if hurried_to_current_month:
            return 15
        hurried_to_current_quarter = (previous_quarter is not current_quarter) and (new_quarter is current_quarter)
        if hurried_to_current_quarter:
            # scenario (2) -- Exp close date moved up to current quarter (10 pts)
            return 10
        hurried_at_all = previous_datetime > new_datetime
        if hurried_at_all:
            # scenario (3a) -- Expected closed date moved up by any days (5 pt)
            return 5
        delayed_at_all = new_datetime > previous_datetime
        delayed_30_or_more_days = new_datetime >= (previous_datetime + timezone.timedelta(days=30))
        delayed_90_or_more_days = new_datetime >= (previous_datetime + timezone.timedelta(days=30))
        if delayed_at_all and (not delayed_30_or_more_days) and (not delayed_90_or_more_days):
            # scenario (6) -- Expected closed date moved back any days (-5 pt)
            return -5
        if delayed_30_or_more_days and (not delayed_90_or_more_days):
            # scenario (4) -- Exp close date moved back 30 or more days (-10 pts)
            return -10
        if delayed_90_or_more_days:
            # scenario (5a) -- Exp close date moved back 90 or more (-15 pts)
            return -15
        # NOTE: should never reach this line!
        return -1

    @property
    def expected_close_date_insight(self):
        score = self.expected_close_date_score
        if score > 0:
            return "Timeline was moved up."
        if score < 0:
            return "Timeline was pushed back."
        if score is 0:
            return "No timeline to close."
