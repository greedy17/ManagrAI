from django.db import models
from django.contrib.postgres.fields import JSONField, ArrayField

from managr.core import constants as core_consts
from managr.core.models import TimeStampModel

from . import constants as zoom_consts


class ZoomAuthAccountQuerySet(models.QuerySet):
    def for_user(self, user):
        if user.is_superuser:
            return self.all()
        if user.organization and user.is_active:
            if user.type == core_consts.ACCOUNT_TYPE_MANAGER:
                return self.filter(user__organization=user.organization)
            elif user.type == core_consts.ACCOUNT_TYPE_REP:
                return self.filter(user=user)
            else:
                return self.none()


class ZoomAuthAccount(TimeStampModel):
    user = models.ForeignKey(
        "core.User", on_delete=models.CASCADE, related_name="zoom_account"
    )
    zoom_id = models.CharField(max_length=255, unique=True)
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    email = models.CharField(max_length=255)
    type = models.PositiveSmallIntegerField()
    role_name = models.CharField(max_length=255, null=True, blank=True)
    personal_meeting_uri = models.CharField(max_length=255)
    timezone = models.CharField(max_length=255)
    verified = models.PositiveSmallIntegerField()
    dept = models.CharField(max_length=255, blank=True, null=True)
    pic_url = models.CharField(max_length=255, blank=True, null=True)
    pmi = models.CharField(
        max_length=255, blank=True, null=True, help_text="personal meeting id"
    )
    user_pmi = models.BooleanField(default=False)
    host_key = models.CharField(max_length=255)
    jid = models.CharField(max_length=255)
    account_id = models.CharField(max_length=255, unique=True)
    language = models.CharField(max_length=150, null=True, blank=True)
    phone_country = models.CharField(max_length=150, null=True, blank=True)
    phone_number = models.CharField(max_length=150, null=True, blank=True)
    status = models.CharField(max_length=150)
    token = models.CharField(max_length=255)
    refresh_token = models.CharField(max_length=255)

    class Meta:
        ordering = ["-datetime_created"]


class ZoomMeeting(TimeStampModel):
    # account_id might refer to organization account (not entirely sure so making it an FK)
    account_id = models.CharField(max_length=255, blank=True, null=True)
    operator = models.EmailField()
    meeting_id = models.CharField(max_length=255, help_text="Aka meeting number")
    meeting_uuid = models.CharField(max_length=255)
    host_id = models.CharField(max_length=255)
    topic = models.CharField(max_length=255)
    type = models.PositiveSmallIntegerField()
    start_time = models.DateTimeField()
    duration = models.PositiveSmallIntegerField()
    timezone = models.CharField(max_length=255)
    occurences = ArrayField(
        JSONField(max_length=128, default=dict),
        default=list,
        blank=True,
        help_text="if recurring meeting",
    )
    password = models.CharField(max_length=255, blank=True, null=True)
    operator_id = models.ForeignKey(
        ZoomAuthAccount,
        on_delete=models.CASCADE,
        related_name="meetings",
        to_field="zoom_id",
    )
    status = models.CharField(
        max_length=255,
        choices=zoom_consts.MEETING_STATUSES,
        help_text="Status of the meeting, only takes 2 values and is supplied by retrieve from zoom",
    )
    start_url = models.CharField(max_length=255)
    join_url = models.CharField(max_length=255)

    recurrence = ArrayField(
        JSONField(max_length=128, default=dict),
        default=list,
        blank=True,
        help_text="if recurring meeting",
    )

    participants = models.ManyToManyField(
        "organization.Contact", related_name="meetings"
    )
    lead = models.ForeignKey(
        "lead.Lead",
        on_delete=models.SET_NULL,
        related_name="meetings",
        null=True,
        blank=True,
    )

    def get_meeting_meta(self):
        """ helper to get meeting not passed down from webhook"""
        return

