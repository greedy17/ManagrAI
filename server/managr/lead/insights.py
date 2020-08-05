from django.db.models import Sum, Avg

from .models import Lead, LeadActivityLog
from . import constants as lead_constants


class LeadInsights:
    """Compute insights for Leads from a LeadActivityLog queryset.

    Attributes:
        lead_queryset (QuerySet<Lead>):             QuerySet of Leads to use for gathering insights.
                                                      Some are computed directly from the leads, others
                                                      from related activity logs.
        loq_queryset (QuerySet<LeadActivityLog>):   QuerySet of LeadActivityLog objects to use
                                                      as a basis for filtering events. Defaults
                                                      to ALL.

    TODO: This is currently just counting the 'created' events for each major related
            model. This is fine as long as users cannot update and delete items, but
            once the log has 'updated' and 'deleted' events, these calculations should
            be updated to reflect that.
    """

    def __init__(
        self,
        lead_queryset=Lead.objects.all(),
        log_queryset=LeadActivityLog.objects.all(),
        filter_params={},
    ):
        # Start with a base queryset, for example, already filtered by lead or
        # activity logs that a user is allowed to see.
        self._lead_queryset = lead_queryset
        self._log_queryset = log_queryset
        self._filter_params = filter_params

    @property
    def lead_queryset(self):
        if self._filter_params['empty']:
            return self._lead_queryset.none()
        return self._lead_queryset

    @property
    def log_queryset(self):
        """Filter the log queryset by leads, if applicable."""
        if self._filter_params['empty']:
            return self._log_queryset.none()

        lead_ids = self._lead_queryset.values_list("id", flat=True)
        if len(lead_ids) > 0:
            return self._log_queryset.filter(lead__id__in=lead_ids)

        # Since no leads selected, then there should be no logs to calculate from.
        # This is because the client-side UX does not include seeing account-wide
        # or organization-wide log statistics, but rather the aggregate statistics
        # of leads that meet claimed_by and date-range filters.
        return self._log_queryset.none()

    @property
    def call_count(self):
        return self.log_queryset.filter(
            activity=lead_constants.CALL_NOTE_CREATED
        ).count()

    @property
    def call_latest(self):
        """Get timestamp of the latest call action."""
        latest_call = self.log_queryset.filter(
            activity=lead_constants.CALL_NOTE_CREATED
        ).first()
        if latest_call is not None:
            return latest_call.action_timestamp

    @property
    def note_count(self):
        return self.log_queryset.filter(activity=lead_constants.NOTE_CREATED).count()

    @property
    def note_latest(self):
        latest_note = self.log_queryset.filter(
            activity=lead_constants.NOTE_CREATED
        ).first()
        if latest_note is not None:
            return latest_note.action_timestamp

    @property
    def action_count(self):
        return self.log_queryset.filter(activity=lead_constants.ACTION_CREATED).count()

    @property
    def action_latest(self):
        latest_action = self.log_queryset.filter(
            activity=lead_constants.ACTION_CREATED
        ).first()
        if latest_action is not None:
            return latest_action.action_timestamp

    @property
    def reminder_count(self):
        return self.log_queryset.filter(activity=lead_constants.REMINDER_CREATED).count()

    @property
    def reminder_latest(self):
        latest_reminder = self.log_queryset.filter(
            activity=lead_constants.REMINDER_CREATED
        ).first()
        if latest_reminder is not None:
            return latest_reminder.action_timestamp

    @property
    def email_count(self):
        return self.log_queryset.filter(activity=lead_constants.EMAIL_SENT).count()

    @property
    def email_latest(self):
        latest_action = self.log_queryset.filter(
            activity=lead_constants.EMAIL_SENT
        ).first()
        if latest_action is not None:
            return latest_action.action_timestamp

    @property
    def message_count(self):
        return self.log_queryset.filter(activity=lead_constants.MESSAGE_SENT).count()

    @property
    def message_latest(self):
        latest_action = self.log_queryset.filter(
            activity=lead_constants.MESSAGE_SENT
        ).first()
        if latest_action is not None:
            return latest_action.action_timestamp

    @property
    def open_leads(self):
        return self.lead_queryset.open_leads()

    @property
    def closed_leads(self):
        return self.lead_queryset.closed_leads(
                                    date_range_from=self._filter_params['date_range_from'],
                                    date_range_to=self._filter_params['date_range_to']
                                )

    @property
    def open_leads_count(self):
        return self.open_leads.count()

    @property
    def closed_leads_count(self):
        return self.closed_leads.count()

    @property
    def closed_leads_value(self):
        return self.closed_leads.aggregate(sum=Sum("closing_amount"))["sum"] or 0

    @property
    def open_leads_value(self):
        return self.open_leads.aggregate(sum=Sum("amount"))["sum"] or 0

    @property
    def as_dict(self):
        return {
            "calls": {"count": self.call_count, "latest": self.call_latest, },
            "notes": {"count": self.note_count, "latest": self.note_latest, },
            "reminders": {"count": self.reminder_count, "latest": self.reminder_latest, },
            "actions": {"count": self.action_count, "latest": self.action_latest, },
            "emails": {"count": self.email_count, "latest": self.email_latest, },
            "messages": {"count": self.message_count, "latest": self.message_latest, },
            "closed_leads": {
                "count": self.closed_leads_count,
                "total_value": self.closed_leads_value,
            },
            "open_leads": {
                "count": self.open_leads_count,
                "total_value": self.open_leads_value,
            },
        }
