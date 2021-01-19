import uuid

from django.db import models
from django.db.models import F, Q, Count
from rest_framework.exceptions import ValidationError
from django.contrib.postgres.fields import JSONField
from django.utils import timezone
from django.core import serializers
import json
from managr.core.models import TimeStampModel, IntegrationModel
from managr.utils.misc import datetime_appended_filepath
from managr.slack.helpers import block_builders
from managr.organization import constants as org_consts
from managr.core import constants as core_consts


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

    def open_leads(self):
        return self.exclude(
            status__title__in=[opp_consts.LEAD_STATUS_CLOSED, opp_consts.LEAD_STATUS_LOST,],
            status__type=org_consts.STAGE_TYPE_PUBLIC,
        )

    def closed_leads(self, date_range_from=None, date_range_to=None):
        qs = self.filter(status__title__in=[opp_consts.LEAD_STATUS_CLOSED])
        if date_range_from:
            qs = qs.filter(expected_close_date__gte=date_range_from)
        if date_range_to:
            qs = qs.filter(expected_close_date__lte=date_range_to)
        return qs


class Opportunity(TimeStampModel, IntegrationModel):
    """Leads are collections of Accounts with forecasting, status and Notes attached.

    Currently we are setting on_delete to null and allowing null values. However we may
    choose to use PROTECT and require that leads are transferred before delete.
    """

    title = models.CharField(max_length=255, blank=True, null=False)
    current_score = models.ForeignKey(
        "OpportunityScore",
        related_name="leads",
        on_delete=models.PROTECT,
        blank=True,
        help_text="The has-many to this field should never be greater than 1. "
        "This FK is added for queryset purposes (see LeadFilterSet.by_score), "
        "even though Lead has-many LeadScores (see OpportunityScore.lead).",
    )
    amount = models.DecimalField(
        max_digits=13, decimal_places=2, default=0.00, help_text="This field is editable",
    )
    forecast_category = models.CharField(max_length=255, choices=opp_consts.FORECAST_CHOICES)

    expected_close_date = models.DateTimeField(blank=True)
    primary_description = models.TextField(blank=True)
    next_step = models.TextField(blank=True)
    rating = models.IntegerField(choices=opp_consts.LEAD_RATING_CHOICES, default=1)
    account = models.ForeignKey(
        "organization.Account", related_name="leads", on_delete=models.CASCADE, blank=True,
    )
    created_by = models.ForeignKey(
        "core.User", related_name="created_leads", blank=True, on_delete=models.SET_NULL, null=True,
    )
    linked_contacts = models.ManyToManyField(
        "organization.Contact", related_name="leads", blank=True
    )
    stage_last_update = models.DateTimeField(default=timezone.now, blank=True)

    stage = models.ForeignKey(
        "organization.Stage",
        related_name="leads",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )

    claimed_by = models.ForeignKey(
        "core.User",
        related_name="claimed_leads",
        on_delete=models.SET_NULL,
        help_text="Leads can only be closed by their claimed_by rep",
        blank=True,
        null=True,
    )
    last_updated_by = models.ForeignKey(
        "core.User", related_name="updated_leads", blank=True, on_delete=models.SET_NULL, null=True,
    )

    type = models.CharField(
        choices=opp_consts.OPPORTUNITY_TYPE_CHOICES, max_length=255, blank=True,
    )
    lead_source = models.CharField(max_length=255, blank=True)

    objects = OpportunityQuerySet.as_manager()

    class Meta:
        ordering = ["-datetime_created"]

    @property
    def is_claimed(self):
        """ property to define if lead is claimed or not """
        if self.claimed_by:
            return True
        return False

    @property
    def activity_log_meta(self):
        linked_contacts = serializers.serialize("json", self.linked_contacts.all())
        linked_contacts = json.loads(linked_contacts)
        linked_contacts = [c["fields"] for c in linked_contacts]
        activity = serializers.serialize("json", [self,],)
        activity = json.loads(activity)

        activity = activity[0]

        activity["fields"]["linked_contacts_ref"] = linked_contacts

        return activity["fields"]

    @property
    def as_slack_option(self):
        return block_builders.option(self.title, str(self.id))

    def __str__(self):
        return f"Lead '{self.title}' ({self.id})"

    def save(self, *args, **kwargs):
        # do not allow duplicates of lead titles in a single org
        opps = (
            Opportunity.objects.filter(
                title=self.title, account__organization__id=self.account.organization.id
            )
            .exclude(id=self.id)
            .exists()
        )
        if opps:
            raise ValidationError(
                {
                    "non_form_errors": {
                        "lead_title": "A lead with this title already exists\
            in your organization"
                    }
                }
            )
        if float(self.amount) < 0:
            raise ValidationError(
                {"non_form_errors": {"lead_amount": "Amount must be a positive integer or float"}}
            )

        return super(Opportunity, self).save(*args, **kwargs)


class LeadActivityLogQuerySet(models.QuerySet):
    def for_user(self, user):
        if user.is_superuser:
            return self.all()
        elif user.organization and user.is_active:
            return self.filter(lead__account__organization=user.organization_id)


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
        "organization.Organization", on_delete=models.CASCADE, related_name="action_choices",
    )

    objects = ActionChoiceQuerySet.as_manager()

    @property
    def as_slack_option(self):
        return block_builders.option(self.title, str(self.id))

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return f" ActionChoice ({self.id}) -- Title: {self.title}, Organization: {self.organization.name}"


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
