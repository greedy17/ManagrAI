from django.db import models
from managr.core.models import UserManager, TimeStampModel, STATE_ACTIVE
from managr.lead import constants as lead_constants
from managr.utils.misc import datetime_appended_filepath
from django.contrib.postgres.fields import JSONField
from django.db.models import F, Q, Count
LEAD_RATING_CHOCIES = [(i, i) for i in range(1, 6)]
# Create your models here.


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
LEAD_STATUS_BOOKED = 'BOOKED'
LEAD_STATUS_CHOICES = (
    (LEAD_STATUS_READY, 'Ready'), (LEAD_STATUS_TRIAL, 'Trial'), (LEAD_STATUS_DEMO,
                                                                 'Demo'), (LEAD_STATUS_WAITING, 'Waiting'), (LEAD_STATUS_CLOSED, 'Closed'),
    (LEAD_STATUS_LOST, 'Lost'), (LEAD_STATUS_BOOKED, 'Booked')
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
NOTIFICATION_ACTION_SNOOZE = 'SNOOZE'
NOTIFICATION_ACTION_VIEWED = 'VIEWED'  # MARK AS VIEWED
NOTIFICATION_ACTION_CHOICES = (
    (NOTIFICATION_ACTION_SNOOZE, 'Snooze'), (NOTIFICATION_ACTION_VIEWED, 'Viewed')
)


class LeadQuerySet(models.QuerySet):

    def for_user(self, user):
        if user.is_superuser:
            return self.all()
        elif user.organization and user.is_active:
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
    primary_description = models.CharField(max_length=150, blank=True)
    secondary_description = models.CharField(max_length=150, blank=True)
    rating = models.IntegerField(choices=LEAD_RATING_CHOCIES, default=1)
    account = models.ForeignKey('organization.Account', related_name="leads",
                                on_delete=models.CASCADE, blank=False, null=True)
    created_by = models.ForeignKey(
        "core.User", related_name="created_leads", null=True, on_delete=models.SET_NULL)
    linked_contacts = models.ManyToManyField(
        'organization.Contact', related_name='leads', blank=True)
    status = models.CharField(
        max_length=255, choices=LEAD_STATUS_CHOICES, help_text="Status in the sale process", null=True)
    claimed_by = models.ForeignKey(
        "core.User", related_name="claimed_leads", null=True, on_delete=models.SET_NULL, help_text="Leads can only be closed by their claimed_by rep")
    last_updated_by = models.ForeignKey(
        "core.User", related_name="updated_leads", null=True, on_delete=models.SET_NULL)
    objects = LeadQuerySet.as_manager()

    class Meta:
        ordering = ['-datetime_created']

    @property
    def is_claimed(self):
        """ property to define if lead is claimed or not """
        if self.claimed_by:
            return True
        return False

    @property
    def contract_file(self):
        """ property to define contract file if a lead is not closed it has not contract """
        if self.status == lead_constants.LEAD_STATUS_CLOSED:
            try:
                return File.objects.get(doc_type=lead_constants.FILE_TYPE_CONTRACT, lead=self.id).id

            except File.DoesNotExist:
                return None
        return None

    @property
    def list_count(self):
        """ property to define count of lists a lead is on """
        return self.lists.count()


class ListQuerySet(models.QuerySet):

    def for_user(self, user):

        if user.is_superuser:
            return self.all()
        elif user.organization and user.is_active:
            return self.filter(created_by__organization=user.organization_id)
        else:
            return None


class List(TimeStampModel):
    title = models.CharField(max_length=255, blank=False, null=False)
    created_by = models.ForeignKey(
        "core.User", null=True, on_delete=models.SET_NULL)
    leads = models.ManyToManyField('Lead', blank=True, related_name="lists")
    objects = ListQuerySet.as_manager()

    class Meta:
        ordering = ['-datetime_created']


class FileQuerySet(models.QuerySet):
    def for_user(self, user):

        if user.is_superuser:
            return self.all()
        elif user.organization and user.is_active:
            return self.filter(uploaded_by__organization=user.organization_id)
        else:
            return None


class File(TimeStampModel):
    doc_type = models.CharField(
        max_length=255, choices=lead_constants.FILE_TYPE_CHOICES, default=lead_constants.FILE_TYPE_OTHER)
    uploaded_by = models.ForeignKey(
        "core.User", null=True, on_delete=models.SET_NULL, related_name="files_uploaded")
    lead = models.ForeignKey(
        'Lead', null=True, on_delete=models.CASCADE, related_name="files")
    file = models.FileField(
        upload_to=datetime_appended_filepath, max_length=255, null=True)

    objects = FileQuerySet.as_manager()

    def save(self, *args, **kwargs):
        """ unset other files that are set as contract """
        if self.doc_type == lead_constants.FILE_TYPE_CONTRACT:
            File.objects.filter(doc_type=lead_constants.FILE_TYPE_CONTRACT, lead=self.lead.id).exclude(
                pk=self.id).update(doc_type="OTHER")
        return super(File, self).save(*args, **kwargs)

    class Meta:
        ordering = ['-datetime_created']


class BaseNoteQuerySet(models.QuerySet):

    def for_user(self, user):
        if user.is_superuser:
            return self.all()
        elif user.organization and user.is_active:
            return self.filter(created_by__organization=user.organization_id)
        else:
            return None


class BaseNote(TimeStampModel):
    """
        This is a Base model for all note style models
        Reminders, Notes and CallNotes all inherit from this base model
        Notes does not override or add any extra fields, however the other two do.
        Note all models inherit the parent queryset manager
    """
    title = models.CharField(max_length=255, blank=False, null=False)
    content = models.CharField(max_length=255, blank=False, null=False)
    created_by = models.ForeignKey(
        "core.User", null=True, on_delete=models.SET_NULL, related_name='created_%(app_label)s_%(class)s')
    updated_by = models.ForeignKey(
        "core.User", null=True, related_name="updated_%(app_label)s_%(class)s", on_delete=models.SET_NULL)
    created_for = models.ForeignKey(
        'Lead', related_name='%(app_label)s_%(class)ss', null=True, on_delete=models.SET_NULL)

    objects = BaseNoteQuerySet.as_manager()

    class Meta:
        abstract = True

        ordering = ['-datetime_created']


class Note(BaseNote):

    class Meta:
        ordering = ['-datetime_created']


class Reminder(BaseNote):
    """
        Reminders are like notes they are created with a date time, a title and content
        Reminders are not auto set to notify, in order to notify they will need to be attached to a notification

    """
    datetime_for = models.DateTimeField(null=True)
    completed = models.BooleanField(default=False)
    # TODO: - will build this out on a separate branch pb
    notification = models.ForeignKey(
        'Notification', on_delete=models.CASCADE, related_name="reminders", null=True)
    # this is a temporary field for a reminder the view status will be handled by notifications in V2
    viewed = models.BooleanField(default=False)

    class Meta:
        ordering = ['-datetime_for']

    def mark_as_viewed(self, user):
        self.updated_by = user
        self.viewed = True
        self.save()

    def mark_as_completed(self, user):
        self.updated_by = user
        self.completed = True
        self.save()


class CallNote(BaseNote):
    """ this class (distinct from the call class) is also inherited from the base note class
        It will contain data that refers to a call (like call notes)
    """
    # TODO: Ask marcy about who the participants are, if they are only internal we can use a UserModel FK
    # otherwise we should just save a json.string
    # participants = models.

    call_date = models.DateField(help_text="The date the call occured")


class ForecastQuerySet(models.QuerySet):

    def for_user(self, user):

        if user.is_superuser:
            return self.all()
        elif user.organization and user.is_active:
            return self.filter(lead__account__organization=user.organization_id)
        else:
            return None


class Forecast(TimeStampModel):
    """ only one forecast per lead is allowed """
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
    action_taken_by = models.ForeignKey(
        "core.User", null=True, on_delete=models.SET_NULL)
    lead = models.ForeignKey(
        'Lead', null=True, on_delete=models.SET_NULL)
    meta = models.CharField(
        max_length=255, help_text="Extra details about activity", blank=True)

    class Meta:
        ordering = ['-datetime_created']


class Notification(TimeStampModel):
    """
        There are various types of notifications (that are not going to be built until V2) in order to handle all notification in one central location we are creating a quick version here
        One of those notifications is a reminder, in order to be reminded of a reminder it must have a notification attached to it.

    """
    notify_at = models.DateTimeField(null=True, help_text="Set a time for the notification to be executed, if this is a reminder it can be something like 5 minutes before time\
                                        if it is an email it can be the time the email is received ")
    notified_at = models.DateTimeField(null=True,
                                       help_text="date time when the notification was executed")
    title = models.CharField(max_length=255, null=True,
                             help_text="a title for the notification")
    action_taken = models.CharField(
        choices=NOTIFICATION_ACTION_CHOICES, max_length=255, null=True, help_text="a notification can either be viewed or snoozed")


class ActionChoiceQuerySet(models.QuerySet):
    def for_user(self, user):
        if user.is_superuser:
            return self.all()
        elif user.organization and user.is_active:
            return self.filter(organization=user.organization_id)
        else:
            return None


class ActionChoice(TimeStampModel):
    title = models.CharField(max_length=255, blank=True, null=False)
    description = models.CharField(max_length=255, blank=True, null=False)
    organization = models.ForeignKey(
        'organization.Organization', on_delete=models.CASCADE, related_name="action_choices")

    objects = ActionChoiceQuerySet.as_manager()

    class Meta:
        ordering = ['title']


class ActionQuerySet(models.QuerySet):
    def for_user(self, user):

        if user.is_superuser:
            return self.all()
        elif user.organization and user.is_active:
            return self.filter(action_type__organization=user.organization_id)
        else:
            return None


class Action(TimeStampModel):
    action_type = models.ForeignKey(
        'ActionChoice', on_delete=models.PROTECT, null=True, blank=False)
    action_detail = models.CharField(max_length=255, blank=True, null=False)
    lead = models.ForeignKey(
        'Lead', on_delete=models.CASCADE, null=True, blank=False, related_name="actions")
    objects = ActionQuerySet.as_manager()

    class Meta:
        ordering = ['-datetime_created']
