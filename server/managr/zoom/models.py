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
        data = self.__dict__
        data["id"] = str(data.get("id"))
        return ZoomAcct(**data)

    @property
    def is_expired(self):
        return self.token_generated_date < timezone.now()

    def generate_token(self):
        res = self.helper_class.refresh_token()
        self.token_generated_date = timezone.now()
        self.access_token = res.access_token
        self.refresh_token = res.refresh_token

    def delete(self, *args, **kwargs):
        ## revoking a token is the same as deleting
        # - we no longer have a token to access data
        # - cannot refresh a token
        self.helper_class.revoke()
        return super(ZoomAuthAccount, self).delete(*args, **kwargs)


class ZoomMeeting(TimeStampModel):
    zoom_account = models.ForeignKey(
        "ZoomAuthAccount", related_name="meetings", on_delete=models.CASCADE,
    )
    account_id = models.CharField(max_length=255, blank=True, null=True)
    operator = models.EmailField()
    meeting_id = models.CharField(max_length=255, help_text="Aka meeting number")
    meeting_uuid = models.CharField(max_length=255, unique=True)
    host_id = models.CharField(max_length=255, null=True, blank=True)
    topic = models.CharField(max_length=255, null=True, blank=True)
    type = models.PositiveSmallIntegerField()
    start_time = models.DateTimeField(null=True, blank=True)
    duration = models.PositiveSmallIntegerField(null=True, blank=True)
    operation = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Operation on all or single occurences",
    )
    timezone = models.CharField(max_length=255)
    occurences = ArrayField(
        JSONField(max_length=128, default=dict),
        default=list,
        blank=True,
        null=True,
        help_text="if recurring meeting",
    )
    password = models.CharField(max_length=255, blank=True, null=True)
    operator_id = models.CharField(max_length=255, blank=True, null=True)
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
        null=True,
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

    should_track = models.CharField(
        max_length=255,
        default="NOT_SELECTED",
        choices=zoom_consts.MEETING_TRACKING_OPTIONS,
        help_text="FUTURE DEVELOPMENT",
    )


class MeetinReview(TimeStampModel):

    # work required to get limit choices to by orgs not currently available
    # could use thread locals or check on save method
    # https://stackoverflow.com/questions/232435/how-do-i-restrict-foreign-keys-choices-to-related-objects-only-in-django

    meeting = models.OneToOneField(
        "ZoomMeeting",
        on_delete=models.CASCADE,
        related_name="meeting_reviews",
        blank=True,
        null=True,
    )
    meeting_type = models.ForeignKey(
        "lead.ActionChoice",
        on_delete=models.SET_NULL,
        related_name="meeting_reviews",
        blank=True,
        null=True,
    )
    forecast_strength = models.ForeignKey(
        "lead.Forecast",
        on_delete=models.SET_NULL,
        related_name="meeting_reviews",
        blank=True,
        null=True,
    )
    update_stage = models.ForeignKey(
        "organization.Stage",
        on_delete=models.SET_NULL,
        related_name="meeting_reviews",
        blank=True,
        null=True,
    )
    description = models.TextField(blank=True, null=True)
    updated_close_date = models.DateTimeField(null=True, blank=True)
    next_steps = models.TextField(blank=True, null=True)
    sentiment = models.CharField(
        max_length=255,
        choices=zoom_consts.MEETING_SENTIMENT_OPTIONS,
        default=zoom_consts.MEETING_SENTIMENT_NA,
    )

