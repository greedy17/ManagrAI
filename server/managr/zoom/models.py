from django.db import models
from django.contrib.postgres.fields import JSONField, ArrayField
from django.utils import timezone

from managr.core import constants as core_consts
from managr.core.models import TimeStampModel

from . import constants as zoom_consts
from .zoom_helper.models import ZoomAcct


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
    user = models.OneToOneField(
        "core.User", on_delete=models.CASCADE, related_name="zoom_account"
    )
    zoom_id = models.CharField(max_length=255, unique=True)
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    email = models.CharField(max_length=255)
    type = models.PositiveSmallIntegerField()
    role_name = models.CharField(max_length=255, null=True, blank=True)
    personal_meeting_url = models.CharField(max_length=255)
    timezone = models.CharField(max_length=255)
    verified = models.PositiveSmallIntegerField()
    dept = models.CharField(max_length=255, blank=True, null=True)
    pic_url = models.CharField(max_length=255, blank=True, null=True)
    pmi = models.CharField(
        max_length=255, blank=True, null=True, help_text="personal meeting id"
    )
    use_pmi = models.BooleanField(default=False)
    host_key = models.CharField(max_length=255)
    jid = models.CharField(max_length=255)
    account_id = models.CharField(max_length=255)
    language = models.CharField(max_length=150, null=True, blank=True)
    phone_country = models.CharField(max_length=150, null=True, blank=True)
    phone_number = models.CharField(max_length=150, null=True, blank=True)
    status = models.CharField(max_length=150)
    access_token = models.TextField()
    refresh_token = models.TextField()
    token_generated_date = models.DateTimeField()
    token_scope = models.CharField(max_length=150, null=True, blank=True)

    class Meta:
        ordering = ["-datetime_created"]

    @property
    def helper_class(self):
        data = self.__data
        return ZoomAcct(**data)

    @property
    def is_expired(self):
        return self.token_generated_date < timezone.now()

    def generate_token(self):
        res = self.helper_class.refresh_token()
        self.token_generated_date = timezone.now()
        self.access_token = res.access_token
        self.refresh_token = res.refresh_token


"""
BLOCKED THIS OUT FOR NOW SO IT DOES NOT CREATE A MIGRATION

class ZoomMeeting(TimeStampModel):

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


"""
