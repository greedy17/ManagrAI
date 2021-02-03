import uuid
import json

from django.db import models
from django.db.models import F, Q, Count
from rest_framework.exceptions import ValidationError
from django.contrib.postgres.fields import JSONField
from django.utils import timezone
from django.core import serializers

from managr.salesforce.exceptions import ResourceAlreadyImported
from managr.core.models import TimeStampModel, IntegrationModel
from managr.utils.misc import datetime_appended_filepath
from managr.slack.helpers import block_builders
from managr.organization import constants as org_consts
from managr.core import constants as core_consts
from managr.salesforce.adapter.models import OpportunityAdapter

# from managr.core import background as bg_task
from . import constants as opp_consts


class OpportunityQuerySet(models.QuerySet):
    def for_user(self, user):
        if user.is_superuser:
            return self.all()
        elif user.organization and user.is_active:
            return self.filter(account__organization=user.organization_id)
        else:
            return None


class Opportunity(TimeStampModel, IntegrationModel):
    """Leads are collections of Accounts with forecasting, status and Notes attached.

    Currently we are setting on_delete to null and allowing null values. However we may
    choose to use PROTECT and require that leads are transferred before delete.
    """

    title = models.CharField(max_length=255, blank=True, null=False)
    amount = models.DecimalField(
        max_digits=13, decimal_places=2, default=0.00, help_text="This field is editable",
    )
    forecast_category = models.CharField(max_length=255, choices=opp_consts.FORECAST_CHOICES)

    close_date = models.DateField(null=True)
    description = models.TextField(blank=True)
    next_step = models.TextField(blank=True)
    account = models.CharField(max_length=255, blank=True, help_text="Retrieved from Integration")
    contacts = models.ManyToManyField(
        "organization.Contact", related_name="opportunities", blank=True
    )
    external_account = models.CharField(
        max_length=255, blank=True, help_text="value from the integration"
    )
    external_stage = models.CharField(
        max_length=255, blank=True, help_text="value from the integration"
    )
    external_owner = models.CharField(
        max_length=255, blank=True, help_text="value from the integration"
    )

    owner = models.ForeignKey(
        "core.User",
        related_name="owned_opportunities",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    stage = models.ForeignKey(
        "organization.Stage",
        related_name="opportunities",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    account = models.ForeignKey(
        "organization.Account",
        related_name="opportunities",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )

    type = models.CharField(max_length=255, blank=True,)
    lead_source = models.CharField(max_length=255, blank=True)
    last_activity_date = models.DateTimeField(null=True)
    last_stage_update = models.DateTimeField(null=True)
    is_stale = models.BooleanField(default=False)
    objects = OpportunityQuerySet.as_manager()

    class Meta:
        ordering = ["-datetime_created"]

    @property
    def as_slack_option(self):
        return block_builders.option(self.title, str(self.id))

    @property
    def adapter_class(self):
        data = self.__dict__
        data["id"] = str(data.get("id"))
        return OpportunityAdapter(**data)

    def update_in_salesforce(self, data):
        if self.owner and hasattr(self.owner, "salesforce_account"):
            token = self.owner.salesforce_account.access_token
            base_url = self.owner.salesforce_account.instance_url
            OpportunityAdapter.update_opportunity(data, token, base_url, self.integration_id)
            self.is_stale = True
            self.save()

    def add_contact_role(self, access_token, base_url, contact_integration_id):

        return OpportunityAdapter.add_contact_role(
            access_token, base_url, contact_integration_id, self.integration_id
        )

    def __str__(self):
        return f"Lead '{self.title}' ({self.id})"

    def save(self, *args, **kwargs):
        obj = (
            Opportunity.objects.filter(
                integration_id=self.integration_id, imported_by=self.imported_by
            )
            .exclude(id=self.id)
            .first()
        )
        if obj:
            raise ResourceAlreadyImported()
        return super(Opportunity, self).save(*args, **kwargs)


class LeadActivityLogQuerySet(models.QuerySet):
    def for_user(self, user):
        if user.is_superuser:
            return self.all()
        elif user.organization and user.is_active:
            return self.filter(lead__account__organization=user.organization_id)


class OpportunityScoreQuerySet(models.QuerySet):
    def for_lead(self, lead):
        return self.filter(lead=lead)


class OpportunityScore(TimeStampModel):
    """
    A Lead can have many LeadScores.
    A OpportunityScore represents a cached score
    for a Lead, with the current OpportunityScore
    for a Lead being the newest OpportunityScore.
    A OpportunityScore is 1-100, and is made up of
    an aggregate of the 6 sub-scores.
    """

    # score validations in self.clean()
    final_score = models.IntegerField()

    actions_score = models.IntegerField()
    actions_insight = models.CharField(max_length=255, blank=True)

    recent_action_score = models.IntegerField()
    recent_action_insight = models.CharField(max_length=255, blank=True)

    incoming_messages_score = models.IntegerField()
    incoming_messages_insight = models.CharField(max_length=255, blank=True)

    days_in_stage_score = models.IntegerField()
    days_in_stage_insight = models.CharField(max_length=255, blank=True,)

    forecast_table_score = models.IntegerField()
    forecast_table_insight = models.CharField(max_length=255, blank=True,)

    expected_close_date_score = models.IntegerField()
    expected_close_date_insight = models.CharField(max_length=255, blank=True,)

    date_range_end = models.DateTimeField()
    date_range_start = models.DateTimeField()

    opportunity = models.ForeignKey("Opportunity", related_name="scores", on_delete=models.CASCADE,)
    previous_score = models.ForeignKey("OpportunityScore", on_delete=models.CASCADE, blank=True)

    objects = OpportunityScoreQuerySet.as_manager()

    def clean(self, *args, **kwargs):
        # validate final_score, 0-100
        if self.final_score < 0 or self.final_score > 100:
            raise ValidationError("OpportunityScore.final_score should be 0-100")
        # validate actions_score, 0-25
        if self.actions_score < 0 or self.actions_score > 25:
            raise ValidationError("OpportunityScore.actions_score should be 0-25")
        # validate recent_action_score, 0-5
        if self.recent_action_score < 0 or self.recent_action_score > 25:
            raise ValidationError("OpportunityScore.recent_action_score should be 0-5")
        # validate incoming_messages_score, 0-20
        if self.incoming_messages_score < 0 or self.incoming_messages_score > 20:
            raise ValidationError("OpportunityScore.incoming_messages_score should be 0-20")
        # validate days_in_stage_score, 0-20
        if self.days_in_stage_score < 0 or self.days_in_stage_score > 20:
            raise ValidationError("OpportunityScore.days_in_stage_score should be 0-20")
        # validate forecast_table_score, 0-20
        if self.forecast_table_score < 0 or self.forecast_table_score > 20:
            raise ValidationError("OpportunityScore.forecast_table_score should be 0-20")
        # validate expected_close_date_score, -15-15
        if self.expected_close_date_score < -15 or self.expected_close_date_score > 15:
            raise ValidationError("OpportunityScore.expected_close_date_score should be -15-15")
        super().clean(*args, **kwargs)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        ordering = ["-datetime_created"]
