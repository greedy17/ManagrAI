from . import constants as lead_constants


class LeadInsights:
    """Compute insights from a queryset.

    TODO: This is currently just counting the 'created' events for each major related
            model. This is fine as long as users cannot update and delete items, but
            once the log has 'updated' and 'deleted' events, these calculations should
            be updated to reflect that.
    """

    def __init__(self, queryset):
        # Start with a base queryset, for example, already filtered by lead or
        # activity logs that a user is allowed to see.
        self.queryset = queryset

    @property
    def call_count(self):
        return self.queryset.filter(activity=lead_constants.CALL_NOTE_CREATED).count()

    @property
    def call_latest(self):
        """Get timestamp of the latest call action."""
        latest_call = self.queryset.filter(
            activity=lead_constants.CALL_NOTE_CREATED
        ).first()
        if latest_call is not None:
            return latest_call.action_timestamp

    @property
    def note_count(self):
        return self.queryset.filter(activity=lead_constants.NOTE_CREATED).count()

    @property
    def note_latest(self):
        latest_note = self.queryset.filter(activity=lead_constants.NOTE_CREATED).first()
        if latest_note is not None:
            return latest_note.action_timestamp

    @property
    def action_count(self):
        return self.queryset.filter(activity=lead_constants.ACTION_CREATED).count()

    @property
    def action_latest(self):
        latest_action = self.queryset.filter(
            activity=lead_constants.ACTION_CREATED
        ).first()
        if latest_action is not None:
            return latest_action.action_timestamp

    @property
    def as_dict(self):
        return {
            "calls": {"count": self.call_count, "latest": self.call_latest,},
            "notes": {"count": self.note_count, "latest": self.note_latest,},
            "actions": {"count": self.action_count, "latest": self.action_latest,},
        }
