import jwt
import pytz
import math

from datetime import datetime
from django.db import models
from django.utils import timezone

from django.contrib.postgres.fields import JSONField, ArrayField

from background_task.models import Task

from managr.core import constants as core_consts
from managr.core.models import TimeStampModel
from managr.organization.models import ActionChoice
from managr.organization.models import Stage
from managr.opportunity import constants as opp_consts
from managr.salesforce.adapter.models import ActivityAdapter


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
    user = models.OneToOneField("core.User", on_delete=models.CASCADE, related_name="zoom_account")
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
    pmi = models.CharField(max_length=255, blank=True, null=True, help_text="personal meeting id")
    use_pmi = models.BooleanField(default=False)
    host_key = models.CharField(max_length=255)
    jid = models.CharField(max_length=255)
    account_id = models.CharField(max_length=255)
    language = models.CharField(max_length=150, null=True, blank=True)
    phone_country = models.CharField(max_length=150, null=True, blank=True)
    phone_number = models.CharField(max_length=150, null=True, blank=True)
    status = models.CharField(max_length=150)
    access_token = models.TextField(blank=True)
    refresh_token = models.TextField(blank=True)
    token_generated_date = models.DateTimeField()
    token_scope = models.CharField(max_length=150, null=True, blank=True)
    is_revoked = models.BooleanField(default=False)
    refresh_token_task = models.CharField(
        max_length=55,
        blank=True,
        help_text="Automatically Send a Refresh task to be executed 15 mins before expiry to reduce errors",
    )

    objects = ZoomAuthAccountQuerySet.as_manager()

    class Meta:
        ordering = ["-datetime_created"]

    @property
    def helper_class(self):
        if self.is_token_expired and self.is_refresh_token_expired:
            self.is_revoked = True
            self.save()

        elif self.is_token_expired and not self.is_refresh_token_expired:
            self.regenerate_token()
        data = self.__dict__
        data["id"] = str(data.get("id"))
        return ZoomAcct(**data)

    @property
    def is_refresh_token_expired(self):
        if self.refresh_token:
            decoded = jwt.decode(
                self.refresh_token, algorithms="HS512", options={"verify_signature": False}
            )
            exp = decoded["exp"]

            return exp <= datetime.timestamp(timezone.now() - timezone.timedelta(minutes=5))
        return True

    @property
    def is_token_expired(self):
        if self.access_token:
            decoded = jwt.decode(
                self.refresh_token, algorithms="HS512", options={"verify_signature": False}
            )
            exp = decoded["exp"]

            return exp <= datetime.timestamp(timezone.now() - timezone.timedelta(minutes=5))
        return True

    def regenerate_token(self):
        if not self.is_revoked:
            data = self.__dict__
            data["id"] = str(data.get("id"))

            helper = ZoomAcct(**data)
            res = helper.refresh_access_token()
            self.token_generated_date = timezone.now()
            self.access_token = res.get("access_token", None)
            self.refresh_token = res.get("refresh_token", None)
            self.is_revoked = False
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

    def save(self, *args, **kwargs):
        if not self.is_revoked:
            # check token if its not expired
            # emit an event to refresh a token at a certain time
            if self.access_token:
                decoded = jwt.decode(
                    self.access_token, algorithms="HS512", options={"verify_signature": False}
                )
                exp = decoded["exp"]
                expiration = datetime.fromtimestamp(exp) - timezone.timedelta(minutes=10)
                # send a refresh 10 mins before expiration only if there is a refresh token and it is not expired
                if self.refresh_token and not self.is_refresh_token_expired:
                    # check for current task if it exists
                    from .background import emit_refresh_zoom_token

                    t = emit_refresh_zoom_token(str(self.id), expiration.strftime("%Y-%m-%dT%H:%M"))
                    self.refresh_token_task = str(t.id)

        if self.is_revoked:
            # find the refresh task and delete it
            if self.refresh_token_task:
                t = Task.objects.filter(id=self.refresh_token_task).first()
                if t:

                    t.save()

        return super(ZoomAuthAccount, self).save(*args, **kwargs)


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
        max_length=255, blank=True, null=True, help_text="Operation on all or single occurences",
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
    participants = ArrayField(
        JSONField(max_length=128, default=dict),
        default=list,
        blank=True,
        null=True,
        help_text="Json object of participants",
    )

    latest_attempt = models.DateTimeField(auto_now_add=True, blank=True, null=True)

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
    def readable_score_message(self):
        if self.meeting_score_components:
            sentiment = ""
            stage = ""
            forecast = ""
            close_date = ""
            attendance = ""
            duration = ""
            for comp in self.meeting_score_components:
                if comp["type"] == "sentiment":
                    sentiment = comp.get("message", "N/A")
                if comp["type"] == "stage":
                    stage = comp.get("message", "N/A")
                if comp["type"] == "forecast_category":
                    forecast = comp.get("message", "N/A")
                if comp["type"] == "close_date":
                    close_date = comp.get("message", "N/A")
                if comp["type"] == "attendance":
                    attendance = comp.get("message", "N/A")
                if comp["type"] == "duration":
                    duration = comp.get("message", "N/A")
            return f"{sentiment} {stage} {forecast} {close_date} {attendance} {duration}"
        return "This Meeting has not been scored yet"

    def delete(self, *args, **kwargs):
        return super(ZoomMeeting, self).delete(*args, **kwargs)


class MeetingReview(TimeStampModel):
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
    forecast_category = models.CharField(blank=True, null=True, max_length=255)
    stage = models.CharField(blank=True, null=True, max_length=255,)
    meeting_comments = models.TextField(blank=True, null=True, max_length=255)
    sentiment = models.CharField(
        max_length=255, choices=zoom_consts.MEETING_SENTIMENT_OPTIONS, blank=True, null=True,
    )
    amount = models.DecimalField(
        max_digits=13,
        decimal_places=2,
        default=0.00,
        help_text="This field is editable",
        null=True,
        blank=True,
    )
    close_date = models.DateField(null=True, blank=True)
    prev_forecast = models.CharField(
        choices=opp_consts.FORECAST_CHOICES, blank=True, null=True, max_length=255
    )
    prev_stage = models.CharField(
        blank=True,
        null=True,
        max_length=255,
        help_text="The values must correspond to the values in the Stage model and by Org",
    )
    prev_close_date = models.DateField(null=True, blank=True)

    prev_amount = models.DecimalField(
        max_digits=13,
        decimal_places=2,
        default=0.00,
        help_text="This field is editable",
        null=True,
        blank=True,
    )
    custom_data = JSONField(
        default=dict,
        null=True,
        help_text="All data that is added to a form is saved as a json object for update",
        max_length=500,
    )

    def get_event_data_salesforce(self):
        user_timezone = self.meeting.zoom_account.timezone
        start_time = self.meeting.start_time
        end_time = self.meeting.end_time
        formatted_start = (
            datetime.strftime(
                start_time.astimezone(pytz.timezone(user_timezone)), "%a, %B, %Y %I:%M %p"
            )
            if start_time
            else start_time
        )
        formatted_end = (
            datetime.strftime(
                end_time.astimezone(pytz.timezone(user_timezone)), "%a, %B, %Y %I:%M %p"
            )
            if end_time
            else end_time
        )

        data = dict(
            Subject=f"Meeting - {self.meeting_type}",
            Description=f"{self.meeting_comments}, this meeting started on {formatted_start} and ended on {formatted_end} ",
            WhatId=self.meeting.opportunity.integration_id
            if self.meeting.meeting_resource == "Opportunity"
            else self.meeting.linked_account.integration_id,
            ActivityDate=self.meeting.start_time.strftime("%Y-%m-%d"),
            Status="Completed",
            TaskSubType="Call",
        )
        return data

    @property
    def meeting_resource(self):
        """ determines whether this is a meeting review for a meeting with an opp or an acct"""
        return self.meeting.meeting_resource

    @property
    def as_sf_update(self):
        """ return data as an sf updateable object """
        data = dict()
        standard_fields = zoom_consts.STANDARD_MEETING_FIELDS[self.meeting_resource]
        for field in self.__dict__:
            if field in standard_fields:
                if field == "amount":
                    data["amount"] = str(self.amount)
                elif field == "close_date":
                    data["close_date"] = self.close_date.strftime("%Y-%m-%d")
                else:
                    data[field] = self.__dict__[field]

        if self.custom_data:
            data = {**data, **self.custom_data}
        return data

    @property
    def stage_progress(self):
        # Moving from 'None' to a stage is progress
        if not self.prev_stage and self.stage:
            return zoom_consts.MEETING_REVIEW_PROGRESSED

        # Moving from a stage to 'None' is a regression
        if self.prev_stage and not self.stage:
            return zoom_consts.MEETING_REVIEW_REGRESSED

        user = self.meeting.zoom_account.user
        sf_account = user.salesforce_account
        stage_field = (
            sf_account.object_fields.get("Opportunity", {}).get("fields", {}).get("StageName", None)
        )
        opts = []
        if stage_field:
            opts = stage_field.get("options", [])
        # Check moving from any stage to another
        if self.prev_stage and self.stage:
            for index, stage in enumerate(opts):
                if self.prev_stage == stage["value"]:
                    prev_stage_order = index
                if self.stage == stage["value"]:
                    current_stage_order = index

            if prev_stage_order < current_stage_order:
                return zoom_consts.MEETING_REVIEW_PROGRESSED
            if prev_stage_order > current_stage_order:
                return zoom_consts.MEETING_REVIEW_REGRESSED

        # Otherwise, assume unchanged
        return zoom_consts.MEETING_REVIEW_UNCHANGED

    @property
    def forecast_progress(self):
        # Moving from 'None' to a forecast is progress
        if not self.prev_forecast and self.forecast_category:
            return zoom_consts.MEETING_REVIEW_PROGRESSED

        # Moving from a forecast to 'None' is a regression
        if self.prev_forecast and not self.forecast_category:
            return zoom_consts.MEETING_REVIEW_REGRESSED

        if self.prev_forecast and self.forecast_category:
            # fetch the picklist values and check ordering
            user = self.meeting.zoom_account.user
            sf_account = user.salesforce_account
            forecast_field = (
                sf_account.object_fields.get("Opportunity", {})
                .get("fields", {})
                .get("ForecastCategoryName", None)
            )
            opts = []
            if forecast_field:
                opts = forecast_field.get("options", [])

            for index, forecast in enumerate(opts):
                if self.prev_forecast == forecast["value"]:
                    prev_forecast_rank = index
                if self.forecast_category == forecast["value"]:
                    current_forecast_rank = index

            if prev_forecast_rank > current_forecast_rank:
                return zoom_consts.MEETING_REVIEW_REGRESSED
            elif prev_forecast_rank < current_forecast_rank:
                return zoom_consts.MEETING_REVIEW_PROGRESSED

        return zoom_consts.MEETING_REVIEW_UNCHANGED

    @property
    def close_date_progress(self):
        if not self.prev_close_date and not self.close_date:
            return zoom_consts.MEETING_REVIEW_UNCHANGED

        if not self.prev_close_date and self.close_date:
            return zoom_consts.MEETING_REVIEW_PROGRESSED

        if self.prev_close_date and not self.close_date:
            return zoom_consts.MEETING_REVIEW_REGRESSED

        if self.prev_close_date > self.close_date:
            return zoom_consts.MEETING_REVIEW_PROGRESSED

        elif self.prev_close_date < self.close_date:
            return zoom_consts.MEETING_REVIEW_REGRESSED

        return zoom_consts.MEETING_REVIEW_UNCHANGED

    @property
    def meeting_type_string(self):
        if self.meeting.type == 1:
            return "instant"
        return "planned"

    @property
    def duration_score(self):
        if not self.meeting.duration:
            return "unknown"

        duration = self.meeting.duration
        original_duration = self.meeting.original_duration

        if self.meeting_type_string == "instant":
            if duration >= 60:
                return "instant_over_60"
            elif duration < 60 and duration >= 30:
                return "instant_over_30"
            elif duration >= 20 and duration < 30:
                return "instant_over_20"

        if self.meeting_type_string == "planned":
            diff = duration - original_duration

            if diff >= 15:
                return "planned_over_15"
            elif 5 < diff < 15:
                return "planned_over_5"
            elif -15 < diff <= 5:
                return "planned_over_2"
            elif diff < -15:
                return "planned_under_15"

        # The above logic should capture all possiblities
        return "unknown"

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
            score = max(0, min(math.ceil(avg_percent_time * 10), 10))
            return score
        return 0

    def save(self, *args, **kwargs):
        opportunity = self.meeting.opportunity

        # fill previous values if the
        if self.forecast_category:
            current_forecast = opportunity.forecast_category
            if current_forecast:
                self.prev_forecast = current_forecast

        if self.stage and opportunity.stage:
            self.prev_stage = opportunity.stage
            # update stage
        # Update the opportunity with the new data
        if self.close_date:
            # Override previous close date with whatever is on the Opportunity
            if opportunity.close_date:
                self.prev_close_date = opportunity.close_date
        if self.amount:
            self.prev_amount = opportunity.amount
        return super(MeetingReview, self).save(*args, **kwargs)
