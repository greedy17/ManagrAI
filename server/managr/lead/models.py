from django.db import models
from managr.core.models import UserManager, TimeStampModel
from managr.core.models import STATE_ACTIVE

LEAD_RATING_CHOCIES = [(i, i) for i in range(1, 6)]
# Create your models here.
FILE_TYPE_OTHER = 'OTHER'
FILE_TYPE_CONTRACT = 'CONTRACT'
FILE_TYPE_CHOICES = (
    (FILE_TYPE_OTHER, 'Other'),
    (FILE_TYPE_CONTRACT, 'Contract')
)
LEAD_STATE_CLAIMED = 'CLAIMED'
LEAD_STATE_UNCLAIMED = 'UNCLAIMED'
LEAD_STATE_CHOICES = ((LEAD_STATE_CLAIMED, 'Claimed'),
                      (LEAD_STATE_UNCLAIMED, 'Unclaimed'),)

LEAD_STATUS_READY = 'READY'
LEAD_STATUS_TRIAL = 'TRIAL'
LEAD_STATUS_DEMO = 'DEMO'
LEAD_STATUS_WAITING = 'WAITING'
LEAD_STATUS_CLOSED = 'CLOSED'
LEAD_STATUS_LOST = 'LOST'
LEAD_STATUS_CHOICES = (
    (LEAD_STATUS_READY, 'Ready'), (LEAD_STATUS_TRIAL, 'Trial'), (LEAD_STATUS_DEMO,
                                                                 'Demo'), (LEAD_STATUS_WAITING, 'Waiting'), (LEAD_STATUS_CLOSED, 'Closed'), (LEAD_STATUS_LOST, 'Lost'),
)
FORECAST_FIFTY_FIFTY = '50/50'
FORECAST_NA = 'NA'
FORCAST_STRONG = 'STRONG'
FORECAST_FUTURE = 'FUTURE'
FORECAST_VERBAL = 'VERBAL'
FORECAST_CHOICES = (
    (FORECAST_FIFTY_FIFTY, '50/50'), (FORECAST_NA, 'NA'), (FORCAST_STRONG,
                                                           'Strong'), (FORECAST_FUTURE, 'Future'), (FORECAST_VERBAL, 'Verbal'),
)
ACTIVITY_NOTE_ADDED = 'NOTE_ADDED'
ACTIVITY_NOTE_DELETED = 'NOTE_DELETED'
ACTIVITY_NOTE_UPDATED = 'NOTE_UPDATED'
ACTIVITY_LEAD_CREATED = "LEAD_CREATED"
ACTIVITY_LEAD_UPDATED = "LEAD_UPDATED"
ACTIVITY_LEAD_CLAIMED = "LEAD_CLAIMED"
ACTIVITY_LEAD_UNCLAIMED = "LEAD_UNCLAIMED"
# THERE WILL BE MANY MORE OF THESE, MAY MOVE THEM TO SEPARATE PY FILE
ACTIVITY_CHOICES = (
    (ACTIVITY_NOTE_ADDED, 'Note Added'), (ACTIVITY_NOTE_DELETED,
                                          'Note Deleted'), (ACTIVITY_NOTE_UPDATED, 'Note Updated')
)
# WILL RESULT IN A SNOOZE FOR A CERTAIN TIME BEFORE IT REMINDS AGAIN
REMINDER_ACTION_SNOOZE = 'SNOOZE'
REMINDER_ACTION_VIEWED = 'VIEWED'  # MARK AS VIEWED
REMINDER_ACTION_CHOICES = (
    (REMINDER_ACTION_SNOOZE, 'Snooze'), (REMINDER_ACTION_VIEWED, 'Viewed')
)


class LeadQuerySet(models.QuerySet):

    def for_user(self, user):
        if user.is_superuser:
            return self.all()
        elif user.organization and user.state == STATE_ACTIVE:
            return self.filter(account__organization=user.organization_id)
        else:
            return None


class Lead(TimeStampModel):
    """
        Leads are collections of Accounts with forecasting, status and Notes attached
        Currently we are setting on_delete to null and allowing null values.
        However we may choose to use PROTECT and require that leads are transferred before
        delete

    """
    title = models.CharField(max_length=255, blank=True, null=False)
    amount = models.PositiveIntegerField(
        help_text="This field is editable", default=0)
    closing_amount = models.PositiveIntegerField(
        help_text="This field is set at close and non-editable", default=0)
    primary_description = models.CharField(max_length=150)
    secondary_description = models.CharField(max_length=150, blank=True)
    rating = models.IntegerField(choices=LEAD_RATING_CHOCIES, default=1)
    account = models.ForeignKey('api.Account', related_name="leads",
                                on_delete=models.CASCADE, blank=False, null=True)
    created_by = models.ForeignKey(
        "core.User", related_name="created_leads", null=True, on_delete=models.SET_NULL)
    linked_contacts = models.ManyToManyField(
        'api.Contact', related_name='leads', blank=True)
    # last_updated will also be updated when an action is taken
    last_updated_at = models.DateTimeField(auto_now=True)
    contract = models.CharField(
        max_length=500, blank=True, help_text="This field will be populated from either an upload of a document or selecting an existing document")
    status = models.CharField(
        max_length=255, choices=LEAD_STATUS_CHOICES, help_text="Status in the sale process", null=True)
    claimed_by = models.ForeignKey(
        "core.User", related_name="claimed_leads", null=True, on_delete=models.SET_NULL)
    last_updated_by = models.ForeignKey(
        "core.User", related_name="updated_leads", null=True, on_delete=models.SET_NULL)
    # will also need actions_allowed
    objects = LeadQuerySet.as_manager()

    class Meta:
        ordering = ['-datetime_created']

    @property
    def is_claimed(self):
        """ property to define if lead is claimed or not """
        if self.claimed_by:
            return True
        return False


class ListQuerySet(models.QuerySet):

    def for_user(self, user):

        if user.is_superuser:
            return self.all()
        elif user.organization and user.state == STATE_ACTIVE:
            return self.filter(created_by__organization=user.organization_id)
        else:
            return None


class List(TimeStampModel):
    title = models.CharField(max_length=255, blank=False, null=False)
    created_by = models.ForeignKey(
        "core.User", null=True, on_delete=models.SET_NULL)
    last_updated_at = models.DateTimeField(auto_now=True)
    leads = models.ManyToManyField('Lead', blank=True)
    organization = models.ForeignKey(
        'api.Organization', blank=False, null=True, on_delete=models.SET_NULL, related_name="lists")

    objects = ListQuerySet.as_manager()

    class Meta:
        ordering = ['-datetime_created']


class File(TimeStampModel):
    name = models.CharField(max_length=255, blank=False, null=False)
    link = models.CharField(max_length=500, blank=False, null=False)
    last_update_at = models.DateTimeField(auto_now=True)
    type = models.CharField(
        max_length=255, choices=FILE_TYPE_CHOICES, default=FILE_TYPE_OTHER)
    uploaded_by = models.ForeignKey(
        "core.User", null=True, on_delete=models.SET_NULL, related_name="files_uploaded")
    uploaded_to = models.ForeignKey(
        'Lead', null=True, on_delete=models.SET_NULL, related_name="files")

    class Meta:
        ordering = ['-datetime_created']


class NoteQuerySet(models.QuerySet):

    def for_user(self, user):
        if user.is_superuser:
            return self.all()
        elif user.organization and user.state == STATE_ACTIVE:
            return self.filter(created_by__organization=user.organization_id)
        else:
            return None


class Note(TimeStampModel):
    title = models.CharField(max_length=255, blank=False, null=False)
    content = models.CharField(max_length=255, blank=False, null=False)
    last_updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        "core.User", null=True, on_delete=models.SET_NULL, related_name="created_notes")
    updated_by = models.ForeignKey(
        "core.User", null=True, related_name="updated_notes", on_delete=models.SET_NULL)
    created_for = models.ForeignKey(
        'Lead', related_name='notes', null=True, on_delete=models.SET_NULL)

    objects = NoteQuerySet.as_manager()

    class Meta:
        ordering = ['-datetime_created']


class ForecastQuerySet(models.QuerySet):

    def for_user(self, user):

        if user.is_superuser:
            return self.all()
        elif user.organization and user.state == STATE_ACTIVE:
            return self.filter(lead__account__organization=user.organization_id)
        else:
            return None


class Forecast(TimeStampModel):
    """ only one forecast per lead is allowed """
    last_updated_at = models.DateTimeField(auto_now=True)
    lead = models.OneToOneField('Lead', null=True, on_delete=models.CASCADE)
    forecast = models.CharField(
        choices=FORECAST_CHOICES, default=FORECAST_NA, max_length=255, null=True)

    objects = ForecastQuerySet.as_manager()
    # created by and updated by not used here since they can be taken from logs

    class Meta:
        ordering = ['-datetime_created']


class ActivityLog(TimeStampModel):
    """
        This contains a log of all activity taken on a LEAD and is created when an activity occurs
    """
    activity = models.CharField(
        max_length=255, choices=ACTIVITY_CHOICES, help_text="records any actions taken on a lead")
    last_updated_at = models.DateTimeField(auto_now=True)
    action_taken_by = models.ForeignKey(
        "core.User", null=True, on_delete=models.SET_NULL)
    lead = models.ForeignKey(
        'Lead', null=True, on_delete=models.SET_NULL)
    meta = models.CharField(
        max_length=255, help_text="Extra details about activity", blank=True)

    class Meta:
        ordering = ['-datetime_created']


class Reminder(TimeStampModel):
    """ 
        Reminders are like notes they are created with a date time, a title and content 
        Reminders are not auto set to notify, in order to notify they will need to be attached to a notification

    """
    title = models.CharField(max_length=255, blank=True, null=False)
    content = models.CharField(max_length=255, blank=True, null=False)
    datetime_for = models.DateTimeField()
    datetime_reminded = models.DateTimeField()
    action_taken = models.CharField(
        max_length=255, blank=False, null=True, choices=REMINDER_ACTION_CHOICES)
    action_taken_at = models.DateTimeField(null=True)

    class Meta:
        ordering = ['-datetime_created']


class ActionChoiceQuerySet(models.QuerySet):
    def for_user(self, user):
        if user.is_superuser:
            return self.all()
        elif user.organization and user.state == STATE_ACTIVE:
            return self.filter(organization=user.organization_id)
        else:
            return None


class ActionChoice(TimeStampModel):
    title = models.CharField(max_length=255, blank=True, null=False)
    description = models.CharField(max_length=255, blank=True, null=False)
    organization = models.ForeignKey(
        'api.Organization', on_delete=models.CASCADE, related_name="action_choices")

    objects = ActionChoiceQuerySet.as_manager()

    class Meta:
        ordering = ['title']


class ActionQuerySet(models.QuerySet):
    def for_user(self, user):

        if user.is_superuser:
            return self.all()
        elif user.organization and user.state == STATE_ACTIVE:
            return self.filter(action_type__organization=user.organization_id)
        else:
            return None


class Action(TimeStampModel):
    action_type = models.ForeignKey(
        'ActionChoice', on_delete=models.PROTECT, null=True, blank=False)
    action_detail = models.CharField(max_length=255, blank=True, null=False)
    lead = models.ForeignKey(
        'Lead', on_delete=models.CASCADE, null=True, blank=False, related_name="actions")
    last_updated_at = models.DateTimeField(auto_now=True)
    objects = ActionQuerySet.as_manager()

    class Meta:
        ordering = ['-datetime_created']
