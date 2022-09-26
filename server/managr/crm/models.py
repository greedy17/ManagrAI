import pytz
from datetime import datetime
from django.db import models
from managr.core.models import TimeStampModel, IntegrationModel
from django.contrib.postgres.fields import JSONField, ArrayField

from managr.crm import routes as adapters
from managr.crm import constants as crm_consts
from background_task.models import CompletedTask


# Create your models here.
class BaseAccountQuerySet(models.QuerySet):
    def for_user(self, user):
        if user.organization and user.is_active:
            if user.user_level in ["SDR", "MANAGER"]:
                return self.filter(organization=user.organization)
            else:
                return self.filter(organization=user.organization, owner=user)
        else:
            return None


class BaseAccount(TimeStampModel, IntegrationModel):
    name = models.CharField(max_length=255)
    organization = models.ForeignKey(
        "organization.Organization", related_name="base_accounts", on_delete=models.CASCADE,
    )
    owner = models.ForeignKey(
        "core.User", on_delete=models.CASCADE, related_name="base_accounts", blank=True, null=True
    )
    external_owner = models.CharField(max_length=255, blank=True)
    secondary_data = JSONField(
        default=dict,
        null=True,
        help_text="All non primary fields that are on the model each org may have its own",
        max_length=500,
    )
    objects = BaseAccountQuerySet.as_manager()

    def __str__(self):
        return f"{self.name} {self.organization}"

    class Meta:
        ordering = ["-datetime_created"]

    @property
    def adapter_class(self):
        data = self.__dict__
        data["id"] = str(data["id"])
        data["owner"] = str(self.owner.id)
        return adapters[self.integration_source]["Account"](**data)


class BaseOpportunityQuerySet(models.QuerySet):
    def for_user(self, user):
        if user.organization and user.is_active:
            if user.user_level in ["SDR", "MANAGER"]:
                return self.filter(owner__organization=user.organization)
            else:
                return self.filter(owner__organization=user.organization, owner=user)
        else:
            return None


class BaseOpportunity(TimeStampModel, IntegrationModel):
    name = models.CharField(max_length=255, blank=True, null=False)
    amount = models.DecimalField(max_digits=30, decimal_places=15, default=0.00, null=True,)
    forecast_category = models.CharField(max_length=255, null=True)
    close_date = models.DateField(null=True)
    account = models.ForeignKey(
        "BaseAccount",
        related_name="opportunities",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    contacts = models.ManyToManyField("BaseContact", related_name="contacts", blank=True)
    external_account = models.CharField(
        max_length=255, blank=True, help_text="value from the integration"
    )
    external_owner = models.CharField(
        max_length=255, blank=True, help_text="value from the integration"
    )

    owner = models.ForeignKey(
        "core.User",
        related_name="base_opportunities",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    stage = models.CharField(max_length=255, null=True)
    is_stale = models.BooleanField(default=False)
    secondary_data = JSONField(
        default=dict,
        null=True,
        help_text="All non primary fields that are on the model each org may have its own",
        max_length=500,
    )
    objects = BaseOpportunityQuerySet.as_manager()

    def __str__(self):
        return f"{self.name} {self.stage}"

    class Meta:
        ordering = ["-datetime_created"]

    @property
    def adapter_class(self):
        data = self.__dict__
        data["id"] = str(data["id"])
        data["owner"] = str(self.owner.id)
        return adapters[self.integration_source]["Opportunity"](**data)


class BaseContactQuerySet(models.QuerySet):
    def for_user(self, user):
        if user.organization and user.is_active:
            if user.user_level in ["SDR", "MANAGER"]:
                return self.filter(organization=user.organization)
            else:
                return self.filter(organization=user.organization, owner=user)
        else:
            return None


class BaseContact(TimeStampModel, IntegrationModel):
    email = models.CharField(max_length=255, blank=True)
    owner = models.ForeignKey(
        "core.User", on_delete=models.CASCADE, related_name="base_contacts", blank=True, null=True
    )
    account = models.ForeignKey(
        "BaseAccount", on_delete=models.SET_NULL, related_name="contacts", null=True, blank=True,
    )
    external_owner = models.CharField(max_length=255, blank=True)
    external_account = models.CharField(max_length=255, blank=True)
    secondary_data = JSONField(
        default=dict,
        null=True,
        help_text="All non primary fields that are on the model each org may have its own",
        max_length=500,
    )
    objects = BaseContactQuerySet.as_manager()

    class Meta:
        ordering = ["-datetime_created"]

    @property
    def adapter_class(self):
        data = self.__dict__
        data["id"] = str(data["id"])
        data["owner"] = str(self.owner.id)
        return adapters[self.integration_source]["Contact"](**data)


class ObjectFieldQuerySet(models.QuerySet):
    def for_user(self, user):
        if user.organization and user.is_active:
            if user.user_level in ["SDR", "MANAGER"]:
                return self.filter(user=user)
            else:
                return self.filter(user=user)
        else:
            return None


class ObjectField(TimeStampModel, IntegrationModel):
    user = models.ForeignKey("core.User", on_delete=models.CASCADE, related_name="object_fields")
    crm_object = models.CharField(max_length=255, null=True)
    api_name = models.CharField(max_length=255)
    createable = models.BooleanField(default=False)
    updateable = models.BooleanField(default=False)
    required = models.BooleanField(default=False)
    data_type = models.CharField(max_length=255)
    display_value = models.CharField(
        max_length=255,
        blank=True,
        help_text="if this is a reference field we save the display value as well",
    )
    label = models.CharField(max_length=255)
    reference = models.BooleanField(default=False)
    relationship_name = models.CharField(max_length=255, null=True)
    reference_to_infos = ArrayField(
        JSONField(max_length=128, default=dict),
        default=list,
        blank=True,
        help_text="An of objects containing the API Name references",
    )
    options = ArrayField(
        JSONField(max_length=255, blank=True, null=True, default=dict),
        default=list,
        blank=True,
        help_text="if this is a custom managr field pass a dict of label, value, if this is not a custom managr field then construct the values dynamically",
    )
    is_public = models.BooleanField(
        default=False,
        help_text="Indicates whether or not this is a managr_created field that is not part of the user's object fields",
    )
    filterable = models.BooleanField(
        default=False, help_text="Indicates if we can filter queries against this field"
    )
    objects = ObjectFieldQuerySet.as_manager()
