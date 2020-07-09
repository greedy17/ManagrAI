import uuid

from django.db import models
from django.db.models import F, Q, Count
from django.contrib.postgres.fields import JSONField
from django.utils import timezone
from django.core import serializers
import json
from managr.core.models import TimeStampModel
from managr.utils.misc import datetime_appended_filepath
from . import constants as lead_constants
from managr.core import constants as core_consts


class LeadQuerySet(models.QuerySet):
    def for_user(self, user):
        if user.is_superuser:
            return self.all()
        elif user.organization and user.is_active:
            return self.filter(account__organization=user.organization_id)
        else:
            return None

    def open_leads(self):
        return self.exclude(
            status__in=[
                lead_constants.LEAD_STATUS_CLOSED,
                lead_constants.LEAD_STATUS_LOST,
            ]
        )

    def closed_leads(self):
        return self.filter(status__in=[lead_constants.LEAD_STATUS_CLOSED])


class Lead(TimeStampModel):
    """Leads are collections of Accounts with forecasting, status and Notes attached.

    Currently we are setting on_delete to null and allowing null values. However we may
    choose to use PROTECT and require that leads are transferred before delete.
    """

    title = models.CharField(max_length=255, blank=True, null=False)
    amount = models.PositiveIntegerField(
        help_text="This field is editable", default=0)
    closing_amount = models.PositiveIntegerField(
        help_text="This field is set at close and non-editable", default=0
    )
    primary_description = models.TextField(blank=True)
    secondary_description = models.TextField(blank=True)
    rating = models.IntegerField(
        choices=lead_constants.LEAD_RATING_CHOICES, default=1)
    account = models.ForeignKey(
        "organization.Account",
        related_name="leads",
        on_delete=models.CASCADE,
        blank=False,
        null=True,
    )
    created_by = models.ForeignKey(
        "core.User", related_name="created_leads", null=True, on_delete=models.SET_NULL
    )
    linked_contacts = models.ManyToManyField(
        "organization.Contact", related_name="leads", blank=True
    )
    status = models.CharField(
        max_length=255,
        choices=lead_constants.LEAD_STATUS_CHOICES,
        help_text="Status in the sale process",
        null=True,
    )
    status_last_update = models.DateTimeField(default=timezone.now, blank=True)
    claimed_by = models.ForeignKey(
        "core.User",
        related_name="claimed_leads",
        null=True,
        on_delete=models.SET_NULL,
        help_text="Leads can only be closed by their claimed_by rep",
    )
    last_updated_by = models.ForeignKey(
        "core.User", related_name="updated_leads", null=True, on_delete=models.SET_NULL
    )
    objects = LeadQuerySet.as_manager()

    class Meta:
        ordering = ["-datetime_created"]

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
                return File.objects.get(
                    doc_type=lead_constants.FILE_TYPE_CONTRACT, lead=self.id
                ).id

            except File.DoesNotExist:
                return None
        return None

    @property
    def list_count(self):
        """ property to define count of lists a lead is on """
        return self.lists.count()

    @property
    def activity_log_meta(self):
        linked_contacts = serializers.serialize(
            'json', self.linked_contacts.all())
        linked_contacts = json.loads(
            linked_contacts)
        linked_contacts = [c['fields'] for c in linked_contacts]
        activity = serializers.serialize('json', [self, ])
        activity = json.loads(activity)

        activity = activity[0]

        activity['fields']['linked_contacts_ref'] = linked_contacts

        return activity['fields']

    def __str__(self):
        return f"Lead '{self.title}' ({self.id})"


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
    leads = models.ManyToManyField("Lead", blank=True, related_name="lists")
    objects = ListQuerySet.as_manager()

    class Meta:
        ordering = ["-datetime_created"]


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
        max_length=255,
        choices=lead_constants.FILE_TYPE_CHOICES,
        default=lead_constants.FILE_TYPE_OTHER,
    )
    uploaded_by = models.ForeignKey(
        "core.User", null=True, on_delete=models.SET_NULL, related_name="files_uploaded"
    )
    lead = models.ForeignKey(
        "Lead", null=True, on_delete=models.CASCADE, related_name="files"
    )
    file = models.FileField(
        upload_to=datetime_appended_filepath, max_length=255, null=True
    )

    objects = FileQuerySet.as_manager()

    @property
    def filename(self):
        return self.file.name

    def save(self, *args, **kwargs):
        """ unset other files that are set as contract """
        if self.doc_type == lead_constants.FILE_TYPE_CONTRACT:
            File.objects.filter(
                doc_type=lead_constants.FILE_TYPE_CONTRACT, lead=self.lead.id
            ).exclude(pk=self.id).update(doc_type="OTHER")
        return super(File, self).save(*args, **kwargs)

    class Meta:
        ordering = ["-datetime_created"]


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
    content = models.TextField(blank=True)
    created_by = models.ForeignKey(
        "core.User",
        null=True,
        on_delete=models.SET_NULL,
        related_name="created_%(app_label)s_%(class)s",
    )
    updated_by = models.ForeignKey(
        "core.User",
        null=True,
        related_name="updated_%(app_label)s_%(class)s",
        on_delete=models.SET_NULL,
    )
    created_for = models.ForeignKey(
        "Lead",
        related_name="%(app_label)s_%(class)ss",
        null=True,
        on_delete=models.SET_NULL,
        help_text="The Lead that this note was created for.",
    )
    linked_contacts = models.ManyToManyField(
        "organization.Contact", related_name="%(app_label)s_%(class)s", blank=True
    )

    objects = BaseNoteQuerySet.as_manager()

    class Meta:
        abstract = True
        ordering = ["-datetime_created"]

    @property
    def activity_log_meta(self):
        """A metadata dict for activity logs"""
        return {
            "id": str(self.id),
            "title": self.title,
            "content": self.content,
            "created_by": {
                "id": str(self.created_by.id),
                "full_name": self.created_by.full_name,
            },
            "linked_contacts": [
                {"id": str(c.id), "full_name": c.full_name, }
                for c in self.linked_contacts.all()
            ],
        }


class Note(BaseNote):
    class Meta:
        ordering = ["-datetime_created"]


class Reminder(BaseNote):
    """Reminders are like notes they are created with a date time, a title and content.

    Reminders are not automatically set to notify, in order to notify they will need to be
    attached to a notification.
    """

    datetime_for = models.DateTimeField(null=True)
    completed = models.BooleanField(default=False)
    # TODO: - will build this out on a separate branch pb
    notification = models.ForeignKey(
        "Notification", on_delete=models.CASCADE, related_name="reminders", null=True
    )
    # this is a temporary field for a reminder the view status will be handled by notifications in V2
    viewed = models.BooleanField(default=False)

    class Meta:
        ordering = ["-datetime_for"]

    def mark_as_viewed(self, user):
        self.updated_by = user
        self.viewed = True
        self.save()

    def mark_as_completed(self, user):
        self.updated_by = user
        self.completed = True
        self.save()


class CallNote(BaseNote):
    """Record notes from a phone call.

    This class (distinct from the call class) is also inherited from the base note class
    It will contain data that refers to a call (like call notes).
    """

    call_date = models.DateTimeField(help_text="The date the call occurred")


class ForecastQuerySet(models.QuerySet):
    def for_user(self, user):

        if user.is_superuser:
            return self.all()
        elif user.organization and user.is_active:
            return self.filter(lead__account__organization=user.organization_id)
        else:
            return None


class Forecast(TimeStampModel):
    """ """

    # Only one forecast per lead is allowed.
    lead = models.OneToOneField("Lead", null=True, on_delete=models.CASCADE)
    forecast = models.CharField(
        max_length=255,
        choices=lead_constants.FORECAST_CHOICES,
        default=lead_constants.FORECAST_NA,
        null=True,
    )

    objects = ForecastQuerySet.as_manager()

    # 'created by' and 'updated by' are not used here since they can be taken from logs

    class Meta:
        ordering = ["-datetime_created"]


class LeadActivityLogQuerySet(models.QuerySet):
    def for_user(self, user):
        if user.is_superuser:
            return self.all()
        elif user.organization and user.is_active:
            return self.filter(lead__account__organization=user.organization_id)


class LeadActivityLog(TimeStampModel):
    """Log all activity taken on a Lead.

    An ActivityLog record is created whenever an activity occurs.
    """

    lead = models.ForeignKey("Lead", null=True, on_delete=models.SET_NULL)
    action_timestamp = models.DateTimeField(
        help_text=(
            "Keep track of when the action happened so we can construct "
            "a timeline for the lead, since this might be different from the "
            "'datetime_created' timestamp."
        )
    )
    activity = models.CharField(
        max_length=255,
        choices=lead_constants.ACTIVITY_CHOICES,
        help_text="records any actions taken on a lead",
    )
    action_taken_by = models.ForeignKey(
        "core.User", on_delete=models.SET_NULL, null=True
    )
    meta = JSONField(help_text="Details about the activity", default=dict)

    objects = LeadActivityLogQuerySet.as_manager()

    class Meta:
        ordering = ["-action_timestamp", "-datetime_created"]


class Notification(TimeStampModel):
    """
        Pari: There are various types of notifications (that are not going to be built until V2)
        in order to handle all notification in one central location we are creating a quick
        version here.

        One of those notifications is a reminder, in order to be reminded of a reminder it
        must have a notification attached to it.
    """

    notify_at = models.DateTimeField(
        null=True,
        help_text="Set a time for the notification to be executed, if this is a reminder it can be something like 5 minutes before time\
                                        if it is an email it can be the time the email is received ",
    )
    notified_at = models.DateTimeField(
        null=True, help_text="date time when the notification was executed"
    )
    title = models.CharField(
        max_length=255, null=True, help_text="a title for the notification"
    )
    action_taken = models.CharField(
        max_length=255,
        choices=lead_constants.NOTIFICATION_ACTION_CHOICES,
        help_text="a notification can either be viewed or snoozed",
        null=True,
    )


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
        "organization.Organization",
        on_delete=models.CASCADE,
        related_name="action_choices",
    )

    objects = ActionChoiceQuerySet.as_manager()

    class Meta:
        ordering = ["title"]


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
        "ActionChoice", on_delete=models.PROTECT, null=True, blank=False
    )
    created_by = models.ForeignKey(
        "core.User",
        null=True,
        on_delete=models.SET_NULL,
        related_name="created_actions",
    )
    action_detail = models.CharField(max_length=255, blank=True)
    lead = models.ForeignKey(
        "Lead", on_delete=models.CASCADE, null=True, blank=False, related_name="actions"
    )
    linked_contacts = models.ManyToManyField(
        "organization.Contact", related_name="actions", blank=True
    )

    objects = ActionQuerySet.as_manager()

    class Meta:
        ordering = ["-datetime_created"]

    @property
    def activity_log_meta(self):
        """Generate a JSON-serializable dictionary for the activity log."""
        return {
            "id": str(self.id),
            "action_type": str(self.action_type.id),
            "action_type_ref": {
                "id": str(self.action_type.id),
                "title": self.action_type.title,
                "description": self.action_type.description,
            },
            "action_detail": self.action_detail,
            "created_by": {
                "id": str(self.created_by.id),
                "full_name": self.created_by.full_name,
            },
            "linked_contacts": [str(c.id) for c in self.linked_contacts.all()],
            "linked_contacts_ref": [
                {"id": str(c.id), "full_name": c.full_name, }
                for c in self.linked_contacts.all()
            ],
        }


class LeadEmail(models.Model):
    """Tie a lead to a Nylas email thread."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    datetime_created = models.DateTimeField(auto_now_add=True)
    last_edited = models.DateTimeField(auto_now=True)

    created_by = models.ForeignKey(
        "core.User",
        related_name="created_email_threads",
        null=True,
        on_delete=models.SET_NULL,
    )

    lead = models.ForeignKey(
        "Lead",
        on_delete=models.CASCADE,
        null=True,
        blank=False,
        related_name="email_threads",
    )

    thread_id = models.CharField(max_length=128)

    @property
    def activity_log_meta(self):
        """A metadata dict for activity logs"""
        return {
            "id": str(self.id),
            "lead": str(self.lead.id),
            "thread_id": self.thread_id,
            "created_by": str(self.created_by.id),
            "created_by_ref": {
                "id": str(self.created_by.id),
                "full_name": self.created_by.full_name,
            },
        }
