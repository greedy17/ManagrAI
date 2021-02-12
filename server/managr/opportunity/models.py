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
from managr.salesforce.adapter.models import SalesforceAuthAccountAdapter, OpportunityAdapter

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
    forecast_category = models.CharField(max_length=255, null=True)

    close_date = models.DateField(null=True)

    account = models.CharField(max_length=255, blank=True, help_text="Retrieved from Integration")
    contacts = models.ManyToManyField(
        "organization.Contact", related_name="opportunities", blank=True
    )
    external_account = models.CharField(
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
    stage = models.CharField(max_length=255, null=True)
    account = models.ForeignKey(
        "organization.Account",
        related_name="opportunities",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )

    last_activity_date = models.DateTimeField(
        null=True
    )  # sf has this as a datetime field but returns a date field only
    last_stage_update = models.DateTimeField(null=True)
    is_stale = models.BooleanField(default=False)
    secondary_data = JSONField(
        default=dict,
        null=True,
        help_text="All non primary fields that are on the model each org may have its own",
        max_length=500,
    )
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

    @staticmethod
    def generate_slack_form_config(user, type):
        """Helper class to generate a slack form config for an org"""
        sf_account = user.salesforce_account if user.has_salesforce_integration else None
        if sf_account:
            # return an object with creatable and required fields
            fields = sf_account.object_fields.get("Opportunity", {}).get("fields", {})
            validations = sf_account.object_fields.get("Opportunity", {}).get("validations", {})
            if type == "CREATE":

                return dict(
                    fields=list(
                        filter(
                            lambda field: field["required"]
                            and field["createable"]
                            and field["type"] != "Reference",
                            fields.values(),
                        )
                    ),
                )
            if type == "UPDATE":
                # no required fields for update
                return dict(fields=list())

            if type == "MEETING_REVIEW":
                meeting_type_field = SalesforceAuthAccountAdapter.custom_field(
                    "Meeting Type", "meeting_type", type="Picklist", required=True, options=["test"]
                )
                meeting_notes_field = SalesforceAuthAccountAdapter.custom_field(
                    "Meeting Notes", "meeting_notes", type="String", required=True
                )
                # this is a managr form make forecast_category_name required
                forecast_category_name = (
                    sf_account.object_fields.get("Opportunity", {})
                    .get("fields")
                    .get("ForecastCategoryName", None)
                )
                if forecast_category_name:
                    forecast_category_name["required"] = True
                stage = (
                    sf_account.object_fields.get("Opportunity", {})
                    .get("fields")
                    .get("StageName", None)
                )
                close_date = (
                    sf_account.object_fields.get("Opportunity", {})
                    .get("fields")
                    .get("CloseDate", None)
                )
                return {
                    "fields": [
                        meeting_type_field,
                        meeting_notes_field,
                        stage,
                        forecast_category_name,
                        close_date,
                    ],
                }

        return

    def update_in_salesforce(self, data):
        if self.owner and hasattr(self.owner, "salesforce_account"):
            token = self.owner.salesforce_account.access_token
            base_url = self.owner.salesforce_account.instance_url
            res = OpportunityAdapter.update_opportunity(data, token, base_url, self.integration_id)
            self.is_stale = True
            self.save()
            return res

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

