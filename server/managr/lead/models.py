from django.db import models
from managr.core.models import UserManager, TimeStampModel

LEAD_RANK_CHOCIES = [(i, i) for i in range(5)]
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
# THERE WILL BE MANY MORE OF THESE, MAY MOVE THEM TO SEPARATE PY FILE
ACTIVITY_CHOICES = (
    (ACTIVITY_NOTE_ADDED, 'Note Added'), (ACTIVITY_NOTE_DELETED,
                                          'Note Deleted'), (ACTIVITY_NOTE_UPDATED, 'Note Updated')
)


class Lead(TimeStampModel):
    """ 
        Leads are collections of Accounts with forecasting, status and Notes attached
        Currently we are setting on_delete to null and allowing null values.
        However we may choose to use PROTECT and require that leads are transferred before
        delete

    """

    amount = models.IntegerField()
    primary_description = models.CharField(max_length=150)
    secondary_description = models.CharField(max_length=150, blank=True)
    rank = models.IntegerField(choices=LEAD_RANK_CHOCIES)
    account = models.ForeignKey('api.Account', related_name="leads",
                                on_delete=models.CASCADE, blank=False, null=True)
    organization = models.ForeignKey('api.Organization', related_name="leads",
                                     on_delete=models.CASCADE, blank=False, null=True)
    created_by = models.ForeignKey(
        "core.User", null=True, on_delete=models.SET_NULL)

    linked_contacts = models.ManyToManyField(
        'api.Contact', related_name='leads', blank=True)
    # last_updated will also be updated when an action is taken
    last_updated_at = models.DateTimeField(auto_now=True)
    contract = models.CharField(
        max_length=500, blank=True, help_text="This field will be populated from either an upload of a document or selecting an existing document")

    # will also need actions_history
    # will also need actions_allowed

    class Meta:
        ordering = ['-datetime_created']


class List(TimeStampModel):
    title = models.CharField(max_length=255, blank=False, null=False)
    created_by = models.ForeignKey(
        "core.User", null=True, on_delete=models.SET_NULL)
    last_updated_at = models.DateTimeField(auto_now=True)
    leads = models.ManyToManyField('api.Account', blank=True)
    organization = models.ForeignKey(
        'api.Organization', blank=False, null=True, on_delete=models.SET_NULL)


class File(TimeStampModel):
    name = models.CharField(max_length=255, blank=False, null=False)
    link = models.CharField(max_length=500, blank=False, null=False)
    last_update_at = models.DateTimeField(auto_now=True)
    type = models.CharField(
        max_length=255, choices=FILE_TYPE_CHOICES, default=FILE_TYPE_OTHER)
    uploaded_by = models.ForeignKey(
        "core.User", null=True, on_delete=models.SET_NULL)
    uploaded_to = models.ForeignKey(
        'Lead', null=True, on_delete=models.SET_NULL)


class Note(TimeStampModel):
    title = models.CharField(max_length=255, blank=False, null=False)
    content = models.CharField(max_length=255, blank=False, null=False)
    last_updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        "core.User", null=True, on_delete=models.SET_NULL)
    created_for = models.ManyToManyField(
        'Lead')


class Forecast(TimeStampModel):
    """ only one forecast per lead is allowed """
    last_updated_at = models.DateTimeField(auto_now=True)
    lead = models.OneToOneField('Lead', null=True, on_delete=models.CASCADE)
    forecast = models.CharField(
        choices=FORECAST_CHOICES, default=FORECAST_NA, max_length=255, null=True)


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
