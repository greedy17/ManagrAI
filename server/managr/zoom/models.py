import jwt
import pytz
import math

from datetime import datetime
from django.db import models
from django.contrib.postgres.fields import JSONField, ArrayField
from django.utils import timezone
from django.contrib.postgres.fields import JSONField

from managr.core import constants as core_consts
from managr.core.models import TimeStampModel
from managr.lead.models import Forecast, Action, ActionChoice
from managr.organization.models import Stage
from managr.lead import constants as lead_consts
from managr.lead.background import emit_event

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

    objects = ZoomAuthAccountQuerySet.as_manager()

    class Meta:
        ordering = ["-datetime_created"]

    @property
    def helper_class(self):
        if self.is_token_expired and self.is_refresh_token_expired:
            self.delete()

        elif self.is_token_expired and not self.is_refresh_token_expired:
            self.regenerate_token()
        data = self.__dict__
        data["id"] = str(data.get("id"))
        return ZoomAcct(**data)

    @property
    def is_refresh_token_expired(self):
        if self.refresh_token:
            decoded = jwt.decode(self.refresh_token, verify=False)
            exp = decoded["exp"]

            return exp <= datetime.timestamp(
                timezone.now() - timezone.timedelta(minutes=5)
            )
        return True

    @property
    def is_token_expired(self):
        if self.access_token:
            decoded = jwt.decode(self.access_token, verify=False)
            exp = decoded["exp"]

            return exp <= datetime.timestamp(
                timezone.now() - timezone.timedelta(minutes=5)
            )
        return True

    def regenerate_token(self):
        data = self.__dict__
        data["id"] = str(data.get("id"))

        helper = ZoomAcct(**data)
        res = helper.refresh_access_token()
        self.token_generated_date = timezone.now()
        self.access_token = res.get("access_token", None)
        self.refresh_token = res.get("refresh_token", None)
        self.save()

    def delete(self, *args, **kwargs):
        ## revoking a token is the same as deleting
        # - we no longer have a token to access data
        # - cannot refresh a token if it is also expired

        if self.is_refresh_token_expired and self.is_token_expired:
            pass
        elif self.is_token_expired and not self.is_refresh_token_expired:
            # first refresh and then revoke
            self.regenerate_token()

            self.helper_class.revoke()
        else:
            self.helper_class.revoke()

        return super(ZoomAuthAccount, self).delete(*args, **kwargs)


class ZoomMeetingQuerySet(models.QuerySet):
    def for_user(self, user):
        if user.is_superuser:
            return self.all()
        if user.organization and user.is_active:
            if user.type == core_consts.ACCOUNT_TYPE_MANAGER:
                return self.filter(zoom_account__user__organization=user.organization)
            elif user.type == core_consts.ACCOUNT_TYPE_REP:
                return self.filter(zoom_account__user=user)
            else:
                return self.none()


class ZoomMeeting(TimeStampModel):
    zoom_account = models.ForeignKey(
        "ZoomAuthAccount", related_name="meetings", on_delete=models.CASCADE,
    )
    account_id = models.CharField(max_length=255, blank=True, null=True)
    operator = models.EmailField(null=True, blank=True)
    meeting_id = models.CharField(max_length=255, help_text="Aka meeting number")
    meeting_uuid = models.CharField(max_length=255, unique=True)
    host_id = models.CharField(max_length=255, null=True, blank=True)
    topic = models.CharField(max_length=255, null=True, blank=True)
    type = models.PositiveSmallIntegerField()
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    duration = models.PositiveSmallIntegerField(null=True, blank=True)
    operation = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Operation on all or single occurences",
    )
    timezone = models.CharField(max_length=255, null=True, blank=True)
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
        null=True,
        blank=True,
    )
    start_url = models.CharField(max_length=255, blank=True, null=True)
    join_url = models.CharField(max_length=255, blank=True, null=True)

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

    notification_attempts = models.PositiveSmallIntegerField(
        help_text="We make an attempt immedietly and after 2 hours", default=0
    )
    scoring_in_progress = models.BooleanField(
        default=False,
        help_text="if an event is emitted to generate a score dont do it again",
    )
    current_interaction = models.PositiveSmallIntegerField(
        default=1, help_text="current slack form"
    )
    is_closed = models.BooleanField(
        default=False,
        help_text="is closed is true when we expire attempts or a user has completed all steps",
    )
    latest_attempt = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    interaction_status = models.CharField(
        choices=zoom_consts.MEETING_INTERACTION_STATUSES,
        max_length=255,
        default=zoom_consts.MEETING_INTERACTION_STATUS_NOT_STARTED,
    )
    participants_count = models.SmallIntegerField(null=True, blank=True)
    total_minutes = models.SmallIntegerField(null=True, blank=True)

    # Meeting scores
    meeting_score = models.SmallIntegerField(null=True, blank=True)
    meeting_score_components = JSONField(default=dict, blank=True, null=True,)
    original_duration = models.SmallIntegerField(
        null=True,
        blank=True,
        help_text="Original duration is the duration sent from the meeting.end webhook, it is updated to the real duration when retrieving from the meetin endpoint so we save it for scoring",
    )
    #
    objects = ZoomMeetingQuerySet.as_manager()

    class Meta:
        ordering = ["-datetime_created"]

    @property
    def should_retry(self):
        # is complete
        # is_closed
        # notification_attempts <=1
        # latest_attempt > 2hrs
        # if the latest attempt is 2 hours after the first attempt try again
        two_hour_timeline = (timezone.now() - self.latest_attempt).seconds >= (
            60 * 3600
        )
        return (
            self.interaction_status != zoom_consts.MEETING_INTERACTION_STATUS_COMPLETE
            or not self.is_closed
            and (self.notification_attempts <= 1 and two_hour_timeline)
        )

    def retry_slack_integration(self):
        # retries slack message at a step
        from .background import _kick_off_slack_interaction

        return _kick_off_slack_interaction(
            str(self.zoom_account.user.id), str(self.id), self.current_interaction
        )


class MeetingReview(TimeStampModel):

    # work required to get limit choices to by orgs not currently available
    # could use thread locals or check on save method
    # https://stackoverflow.com/questions/232435/how-do-i-restrict-foreign-keys-choices-to-related-objects-only-in-django

    meeting = models.OneToOneField(
        "ZoomMeeting",
        on_delete=models.CASCADE,
        related_name="meeting_review",
        blank=True,
        null=True,
    )
    meeting_type = models.CharField(
        blank=True,
        null=True,
        max_length=255,
        help_text="The value must corespond to the values in the ActionChoice Model",
    )
    forecast_strength = models.CharField(
        choices=lead_consts.FORECAST_CHOICES, blank=True, null=True, max_length=255
    )
    update_stage = models.CharField(
        blank=True,
        null=True,
        max_length=255,
        help_text="The values must correspond to the values in the Stage model and by Org",
    )
    description = models.TextField(blank=True, null=True, max_length=255)
    next_steps = models.TextField(
        blank=True, null=True, help_text="populates secondary description"
    )
    sentiment = models.CharField(
        max_length=255,
        choices=zoom_consts.MEETING_SENTIMENT_OPTIONS,
        blank=True,
        null=True,
    )
    amount = models.DecimalField(
        max_digits=13,
        decimal_places=2,
        default=0.00,
        help_text="This field is editable",
        null=True,
        blank=True,
    )
    prev_forecast = models.CharField(
        choices=lead_consts.FORECAST_CHOICES, blank=True, null=True, max_length=255
    )
    prev_stage = models.CharField(
        blank=True,
        null=True,
        max_length=255,
        help_text="The values must correspond to the values in the Stage model and by Org",
    )
    prev_expected_close_date = models.DateTimeField(null=True, blank=True)
    updated_close_date = models.DateTimeField(null=True, blank=True)
    prev_amount = models.DecimalField(
        max_digits=13,
        decimal_places=2,
        default=0.00,
        help_text="This field is editable",
        null=True,
        blank=True,
    )

    @property
    def stage_progress(self):
        # Moving from 'None' to a stage is progress
        if not self.prev_stage and self.update_stage:
            return zoom_consts.MEETING_REVIEW_PROGRESSED

        # Moving from a stage to 'None' is a regression
        if self.prev_stage and not self.update_stage:
            return zoom_consts.MEETING_REVIEW_REGRESSED

        # Check moving from any stage to another
        if self.prev_stage and self.update_stage:
            prev_stage_order = Stage.objects.get(id=self.prev_stage).order
            current_stage_order = Stage.objects.get(id=self.update_stage).order

            if prev_stage_order < current_stage_order:
                return zoom_consts.MEETING_REVIEW_PROGRESSED
            if prev_stage_order > current_stage_order:
                return zoom_consts.MEETING_REVIEW_REGRESSED

        # Otherwise, assume unchanged
        return zoom_consts.MEETING_REVIEW_UNCHANGED

    @property
    def forecast_progress(self):
        # Moving from 'None' to a forecast is progress
        if not self.prev_forecast and self.forecast_strength:
            return zoom_consts.MEETING_REVIEW_PROGRESSED

        # Moving from a forecast to 'None' is a regression
        if self.prev_forecast and not self.forecast_strength:
            return zoom_consts.MEETING_REVIEW_REGRESSED

        if self.prev_forecast and self.forecast_strength:
            for index, forecast in enumerate(lead_consts.FORECAST_CHOICES):
                if self.prev_forecast == forecast[0]:
                    prev_forecast_rank = index
                if self.forecast_strength == forecast[0]:
                    current_forecast_rank = index

            if prev_forecast_rank > current_forecast_rank:
                return zoom_consts.MEETING_REVIEW_REGRESSED
            elif prev_forecast_rank < current_forecast_rank:
                return zoom_consts.MEETING_REVIEW_PROGRESSED

        return zoom_consts.MEETING_REVIEW_UNCHANGED

    @property
    def expected_close_date_progress(self):
        if not self.prev_expected_close_date and not self.updated_close_date:
            return zoom_consts.MEETING_REVIEW_UNCHANGED

        if not self.prev_expected_close_date and self.updated_close_date:
            return zoom_consts.MEETING_REVIEW_PROGRESSED

        if self.prev_expected_close_date and not self.updated_close_date:
            return zoom_consts.MEETING_REVIEW_REGRESSED

        if self.prev_expected_close_date > self.updated_close_date:
            return zoom_consts.MEETING_REVIEW_PROGRESSED

        elif self.prev_expected_close_date < self.updated_close_date:
            return zoom_consts.MEETING_REVIEW_REGRESSED

        return zoom_consts.MEETING_REVIEW_UNCHANGED

    @property
    def meeting_type_string(self):
        if self.meeting.type == 1:
            return "instant"
        return "planned"

    @property
    def meeting_duration_score_parameter(self):
        # TODO: PB Ignore this for now as we do not get the accurate duration from the past meeting webhook
        if self.meeting_type_string == "instant":
            if int(self.meeting.duration) >= 60:
                return "60"

            elif int(self.meeting.duration) < 60 and int(self.meeting.duration) >= 30:
                return "30"

            elif int(self.meeting.duration) >= 20 and int(self.meeting.duration) < 30:
                return "20"
        elif self.meeting_type_string == "planned":
            if int(self.meeting.duration) >= 60:
                return "60"

            elif int(self.meeting.duration) < 60 and int(self.meeting.duration) >= 30:
                return "30"

            elif int(self.meeting.duration) >= 20 and int(self.meeting.duration) < 30:
                return "20"

        return

    @property
    def participant_count_weighted(self):
        # None, zero, or one participant
        if not self.meeting.participants_count or self.meeting.participants_count == 1:
            return 0

        # Two to five
        if 2 <= self.meeting.participants_count <= 5:
            return self.meeting.participants_count

        # Five or more
        return 5

    @property
    def participation_score(self):
        total_minutes = self.meeting.total_minutes
        duration = self.meeting.duration
        participants = self.meeting.participants_count

        if total_minutes and duration:
            avg_participation_time = (total_minutes - duration) / (participants - 1)
            avg_percent_time = avg_participation_time / duration
            score = math.ceil(avg_percent_time * 10)
            return score
        return 0

    def save(self, *args, **kwargs):
        lead = self.meeting.lead

        # adjust lead data based on these fields
        if self.forecast_strength:
            current_forecast = Forecast.objects.filter(lead=lead).first()
            if current_forecast:
                self.prev_forecast = current_forecast.forecast
                current_forecast.forecast = self.forecast_strength
                current_forecast.save()
            else:
                Forecast.objects.create(lead=lead, forecast=self.forecast_strength)
            # update lead forcecase

        if self.update_stage and lead.status:
            self.prev_stage = lead.status.id
            lead.status = Stage.objects.filter(id=self.update_stage).first()

            # update stage
        if self.next_steps:
            lead.secondary_description = self.next_steps
            # update secondary desc

        if self.meeting_type:
            # create action from action choice
            action = Action.objects.create(
                lead=lead,
                created_by=lead.claimed_by,
                action_detail=self.description
                if self.description
                else "NO DESCRIPTION",
                action_type=ActionChoice.objects.filter(id=self.meeting_type).first(),
            )

        # Override previous close date with whatever is on the Lead
        if lead.expected_close_date:
            self.prev_expected_close_date = lead.expected_close_date

        # Update the lead with the new data
        if self.updated_close_date:
            lead.expected_close_date = self.updated_close_date

        if self.amount:
            self.prev_amount = lead.amount
            lead.amount = float(self.amount)

        lead.save()

        return super(MeetingReview, self).save(*args, **kwargs)

