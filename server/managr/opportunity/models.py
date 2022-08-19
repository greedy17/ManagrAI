import uuid
import json

from django.db import models
from django.contrib.postgres.fields import JSONField, ArrayField

from managr.salesforce.exceptions import ResourceAlreadyImported
from managr.core.models import TimeStampModel, IntegrationModel
from managr.slack.helpers import block_builders
from managr.salesforce.adapter.models import (
    SalesforceAuthAccountAdapter,
    OpportunityAdapter,
    LeadAdapter,
)
from managr.core.models import User


class LeadQuerySet(models.QuerySet):
    def for_user(self, user):
        if user.organization and user.is_active:
            if user.user_level in ["SDR", "MANAGER"]:
                return self.filter(owner__organization=user.organization)
            else:
                return self.filter(owner=user)
        else:
            return None


class Lead(TimeStampModel, IntegrationModel):
    email = models.CharField(max_length=255, blank=True)
    external_owner = models.CharField(
        max_length=255, blank=True, help_text="value from the integration"
    )
    name = models.CharField(max_length=255, blank=True)
    secondary_data = JSONField(
        default=dict,
        null=True,
        help_text="All non primary fields that are on the model each org may have its own",
        max_length=500,
    )
    owner = models.ForeignKey(
        "core.User", related_name="owned_leads", on_delete=models.SET_NULL, blank=True, null=True,
    )
    objects = LeadQuerySet.as_manager()

    def __str__(self):
        return f"name{self.name}, email {self.email}, owner: {self.owner}, integration_id: {self.integration_id}"

    @property
    def as_slack_option(self):
        return block_builders.option(self.name, str(self.id))

    @property
    def adapter_class(self):
        data = self.__dict__
        data["id"] = str(data.get("id"))
        return LeadAdapter(**data)

    def update_in_salesforce(self, data):
        if self.owner and hasattr(self.owner, "salesforce_account"):
            token = self.owner.salesforce_account.access_token
            base_url = self.owner.salesforce_account.instance_url
            object_fields = self.owner.salesforce_account.object_fields.filter(
                salesforce_object="Lead"
            ).values_list("api_name", flat=True)
            res = LeadAdapter.update_lead(data, token, base_url, self.integration_id, object_fields)
            self.is_stale = True
            self.save()
            return res

    def convert_in_salesforce(self, data):
        if self.owner and hasattr(self.owner, "salesforce_account"):
            token = self.owner.salesforce_account.access_token
            base_url = self.owner.salesforce_account.instance_url
            res = LeadAdapter.convert_lead(data, token, base_url, str(self.owner.id))
            self.is_stale = True
            self.save()
            return res

    def create_in_salesforce(self, data=None, user_id=None):
        if self.owner and hasattr(self.owner, "salesforce_account"):
            token = self.owner.salesforce_account.access_token
            base_url = self.owner.salesforce_account.instance_url
            object_fields = self.owner.salesforce_account.object_fields.filter(
                salesforce_object="Lead"
            ).values_list("api_name", flat=True)
            res = LeadAdapter.create(data, token, base_url, self.integration_id, object_fields)
            from managr.salesforce.routes import routes

            serializer = routes["Lead"]["serializer"](data=res.as_dict)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return serializer.instance

    def get_current_values(self, *args, **kwargs):
        integration_id = self.integration_id
        token = self.owner.salesforce_account.access_token
        base_url = self.owner.salesforce_account.instance_url
        return LeadAdapter.get_current_values(integration_id, token, base_url, self.owner.id)


class OpportunityQuerySet(models.QuerySet):
    def for_user(self, user):
        if user.organization and user.is_active:
            if user.user_level in ["SDR", "MANAGER"]:
                return self.filter(owner__organization=user.organization)
            else:
                return self.filter(owner=user)
        else:
            return None


class Opportunity(TimeStampModel, IntegrationModel):
    """Leads are collections of Accounts with forecasting, status and Notes attached.

    Currently we are setting on_delete to null and allowing null values. However we may
    choose to use PROTECT and require that leads are transferred before delete.
    """

    name = models.CharField(max_length=255, blank=True, null=False)
    amount = models.DecimalField(max_digits=30, decimal_places=15, default=0.00, null=True,)
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
    reference_data = ArrayField(
        JSONField(max_length=128, default=dict),
        default=list,
        blank=True,
        help_text="An array of objects containing the API Name references and values for displaying",
    )
    objects = OpportunityQuerySet.as_manager()

    class Meta:
        ordering = ["-datetime_created"]

    @property
    def as_slack_option(self):
        return block_builders.option(self.name, str(self.id))

    @property
    def adapter_class(self):
        data = self.__dict__
        data["id"] = str(data.get("id"))
        return OpportunityAdapter(**data)

    def update_in_salesforce(self, data):
        if self.owner and hasattr(self.owner, "salesforce_account"):
            token = self.owner.salesforce_account.access_token
            base_url = self.owner.salesforce_account.instance_url
            object_fields = self.owner.salesforce_account.object_fields.filter(
                salesforce_object="Opportunity"
            ).values_list("api_name", flat=True)
            res = OpportunityAdapter.update_opportunity(
                data, token, base_url, self.integration_id, object_fields
            )
            self.is_stale = True
            self.save()
            return res

    @staticmethod
    def create_in_salesforce(data=None, user_id=None):
        """when synchronous create in db first to be able to use immediately"""
        user = User.objects.get(id=user_id)
        if user and hasattr(user, "salesforce_account"):
            token = user.salesforce_account.access_token
            base_url = user.salesforce_account.instance_url
            object_fields = user.salesforce_account.object_fields.filter(
                salesforce_object="Opportunity"
            ).values_list("api_name", flat=True)
            res = OpportunityAdapter.create(data, token, base_url, object_fields, user_id)
            from managr.salesforce.routes import routes

            serializer = routes["Opportunity"]["serializer"](data=res.as_dict)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return serializer.instance

    def add_contact_role(self, access_token, base_url, contact_integration_id):

        return OpportunityAdapter.add_contact_role(
            access_token, base_url, contact_integration_id, self.integration_id
        )

    def __str__(self):
        return f"Opportunity '{self.name}' ({self.id})"

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

    def get_current_values(self, *args, **kwargs):
        integration_id = self.integration_id
        token = self.owner.salesforce_account.access_token
        base_url = self.owner.salesforce_account.instance_url
        return OpportunityAdapter.get_current_values(integration_id, token, base_url, self.owner.id)

    def update_database_values(self, data, *args, **kwargs):
        data.pop("meeting_comments", None)
        data.pop("meeting_type", None)
        self.secondary_data.update(data)
        return self.save()
