import jwt
import pytz
import math
import logging

from datetime import datetime
from django.db import models
from django.utils import timezone

from django.contrib.postgres.fields import JSONField, ArrayField

from background_task.models import Task

from managr.zoom.utils import score_meeting
from managr.core import constants as core_consts
from managr.core.models import TimeStampModel
from managr.organization.models import ActionChoice
from managr.organization.models import Stage
from managr.opportunity import constants as opp_consts
from managr.salesforce.adapter.models import ActivityAdapter
from managr.core.background import emit_generate_morning_digest, emit_generate_afternoon_digest


from . import constants as zoom_consts
from .zoom_helper.models import ZoomAcct

logger = logging.getLogger("managr")


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
    email = models.CharField(max_length=255)
    type = models.PositiveSmallIntegerField()
    role_name = models.CharField(max_length=255, null=True, blank=True)
    timezone = models.CharField(max_length=255)
    host_key = models.CharField(max_length=255, blank=True)
    account_id = models.CharField(max_length=255)
    language = models.CharField(max_length=150, null=True, blank=True)
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
        try:
            if self.is_refresh_token_expired and self.is_token_expired:
                pass
            elif self.is_token_expired and not self.is_refresh_token_expired:
                # first refresh and then revoke
                self.regenerate_token()
                self.helper_class.revoke()
            else:
                self.helper_class.revoke()
        except Exception as e:
            pass

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

    def __str__(self):
        return f"{self.topic} meeting for user with email: {self.zoom_account.user.email} with id: {self.zoom_account.user.id}"

    @property
    def readable_score_message(self):
        if self.meeting_score_components:

            stage = ""
            forecast = ""
            close_date = ""
            attendance = ""
            duration = ""
            for comp in self.meeting_score_components:
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
            return f"{stage} {forecast} {close_date} {attendance} {duration}"
        return "This Meeting has not been scored yet"

    def delete(self, *args, **kwargs):
        if hasattr(self, "workflow"):
            if self.workflow.slack_interaction and len(self.workflow.slack_interaction):
                from managr.slack.helpers import block_builders
                from managr.slack.helpers import requests as slack_requests
                from managr.slack.helpers.block_sets import get_block_set
                from managr.slack.helpers.exceptions import (
                    UnHandeledBlocksException,
                    InvalidBlocksFormatException,
                    InvalidBlocksException,
                    InvalidAccessToken,
                )

                slack_access_token = self.workflow.user.organization.slack_integration.access_token
                ts, channel = self.workflow.slack_interaction.split("|")
                try:
                    res = slack_requests.update_channel_message(
                        channel,
                        ts,
                        slack_access_token,
                        block_set=[
                            block_builders.simple_section(
                                ":put_litter_in_its_place: This meeting was removed from our records",
                                "mrkdwn",
                            )
                        ],
                    )
                except InvalidBlocksException as e:
                    return logger.exception(
                        f"Failed To Generate Slack Workflow Interaction for user with workflow {str(self.workflow.id)} email {self.workflow.user.email} {e}"
                    )
                except InvalidBlocksFormatException as e:
                    return logger.exception(
                        f"Failed To Generate Slack Workflow Interaction for user with workflow {str(self.workflow.id)} email {self.workflow.user.email} {e}"
                    )
                except UnHandeledBlocksException as e:
                    return logger.exception(
                        f"Failed To Generate Slack Workflow Interaction for user with workflow {str(self.workflow.id)} email {self.workflow.user.email} {e}"
                    )
                except InvalidAccessToken as e:
                    return logger.exception(
                        f"Failed To Generate Slack Workflow Interaction for user with workflow {str(self.workflow.id)} email {self.workflow.user.email} {e}"
                    )

                self.workflow.slack_interaction = f"{res['ts']}|{res['channel']}"
        return super(ZoomMeeting, self).delete(*args, **kwargs)
