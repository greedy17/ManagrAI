import jwt
import pytz
import math
import logging
import json

from datetime import datetime
from django.db import models
from django.utils import timezone

from django.contrib.postgres.fields import JSONField, ArrayField
from django.db.models import Q
from django.db.models.constraints import UniqueConstraint

from managr.core.models import TimeStampModel, IntegrationModel
from managr.slack.helpers.exceptions import (
    UnHandeledBlocksException,
    InvalidBlocksFormatException,
    InvalidBlocksException,
    InvalidAccessToken,
)

from .adapter.models import HubspotAuthAccountAdapter
from .adapter.exceptions import (
    TokenExpired,
    InvalidFieldError,
    UnhandledHubspotError,
    InvalidRefreshToken,
    CannotRetreiveObjectType,
)
from . import constants as sf_consts

logger = logging.getLogger("managr")


class HubspotAuthAccount(TimeStampModel):
    user = models.OneToOneField(
        "core.User", on_delete=models.CASCADE, related_name="hubspot_account"
    )
    access_token = models.CharField(max_length=255, blank=True)
    refresh_token = models.CharField(max_length=255, blank=True)
    hubspot_id = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["-datetime_created"]
        constraints = [UniqueConstraint(fields=["hubspot_id"], name="unique_hubspot_id")]

    def __str__(self):
        return f"Hubspot-{self.user.email} {self.hubspot_id}"

    @property
    def adapter_class(self):
        data = self.__dict__
        data["id"] = str(data["id"])
        data["user"] = str(self.user.id)
        return HubspotAuthAccountAdapter(**data)

    @property
    def resource_sync_opts(self):
        return list(
            filter(
                lambda resource: f"{resource}"
                if self.sobjects.get(resource, None) not in ["", None, False]
                else False,
                self.sobjects,
            )
        )

    @property
    def field_sync_opts(self):
        return list(
            map(
                lambda resource: f"{sf_consts.SALESFORCE_OBJECT_FIELDS}.{resource}",
                filter(
                    lambda resource: resource
                    if self.sobjects.get(resource, None) not in ["", None, False]
                    else False,
                    self.sobjects,
                ),
            )
        )

    @property
    def picklist_sync_opts(self):
        return list(
            map(
                lambda resource: f"{sf_consts.SALESFORCE_PICKLIST_VALUES}.{resource}",
                filter(
                    lambda resource: resource
                    if self.sobjects.get(resource, None) not in ["", None, False]
                    else False,
                    self.sobjects,
                ),
            )
        )

    @property
    def validation_sync_opts(self):
        if self.user.is_admin:
            return list(
                map(
                    lambda resource: f"{sf_consts.SALESFORCE_VALIDATIONS}.{resource}",
                    filter(
                        lambda resource: resource
                        if self.sobjects.get(resource, None) not in ["", None, False]
                        else False,
                        self.sobjects,
                    ),
                )
            )
        return []

    def regenerate_token(self):
        res = self.adapter_class.refresh()
        self.access_token = res.get("access_token", None)
        self.refresh_token = res.get("refresh_token", None)
        self.save()

    def revoke(self):
        adapter = self.adapter_class
        adapter.revoke()
        self.delete()

    def get_fields(self, resource):

        fields, record_type_id = [*self.adapter_class.list_fields(resource).values()]
        if fields and record_type_id:
            self.default_record_id = record_type_id
            current_record_ids = self.default_record_ids if self.default_record_ids else {}
            current_record_ids[resource] = record_type_id
            self.default_record_ids = current_record_ids
            self.save()
        return fields

    def get_validations(self, resource):
        rules = self.adapter_class.list_validations(resource)
        return rules

    def get_picklist_values(self, resource):
        values = self.adapter_class.list_picklist_values(resource)
        return values

    def list_resource_data(self, resource, offset, *args, **kwargs):
        attempts = 1
        while True:
            try:
                return self.adapter_class.list_resource_data(resource, offset, *args, **kwargs)

            except InvalidFieldError as e:
                # catch all invalid fields on sync remove them from self and retry up to 20 times
                # this is done here rather than on the bg task to make it task agnostic
                # re raise the error for the decorator on the bg tasks to catch as well
                if attempts < 20:
                    attempts += 1
                    # remove the field from self
                    # get the field and make it into a string
                    try:
                        field_str = e.args[0].replace("'", "")
                        fields = self.object_fields.filter(
                            hubspot_object=resource, api_name=field_str
                        )
                        if fields.count():
                            fields.delete()
                        exclude_fields = self.exclude_fields if not None else {}
                        # add field to exclude fields for next sync
                        exclude_fields[resource] = [*exclude_fields.get(resource, []), field_str]
                        self.exclude_fields = exclude_fields
                        self.save()

                    except IndexError:
                        logger.exception(f"failed to parse invalid field {e}")
                        raise e
                else:
                    logger.exception(
                        f"Too many invalid fields for query, retry was ended at {attempts} for user {self.user.email} with id {self.user.id} current field {e}"
                    )
                    # re raise error for bg task to also handle
                    raise e
            except TokenExpired:
                if attempts >= 5:
                    return logger.exception(
                        f"Failed to retrieve resource data for user {str(self.user.id)}-{self.user.email} after {attempts} tries"
                    )
                else:
                    self.regenerate_token()
                    attempts += 1
        return

    def get_stage_picklist_values(self, resource):
        values = self.adapter_class.get_stage_picklist_values(resource)
        return values

    def get_individual_picklist_values(self, resource, field=None):
        attempts = 1
        while True:
            try:
                values = self.adapter_class.get_individual_picklist_values(
                    resource, field_name=field
                )
                break
            except TokenExpired:
                if attempts >= 5:
                    return logger.exception(
                        f"Failed to retrieve picklist values data for user {str(self.user.id)}-{self.user.email} after {attempts} tries"
                    )
                else:
                    self.regenerate_token()
                    attempts += 1

        return values

    def save(self, *args, **kwargs):
        return super(HubspotAuthAccount, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        return super().delete(*args, **kwargs)


class CompanyQuerySet(models.QuerySet):
    def for_user(self, user):
        if user.organization and user.is_active:
            if user.user_level in ["SDR", "MANAGER"]:
                return self.filter(organization=user.organization)
            else:
                return self.filter(organization=user.organization, owner=user)
        else:
            return None


class Company(TimeStampModel, IntegrationModel):
    """
    Accounts are potential and exisiting clients that
    can be made into leads and added to lists

    """

    name = models.CharField(max_length=255)
    organization = models.ForeignKey(
        "organization.Organization", related_name="companies", on_delete=models.CASCADE,
    )
    owner = models.ForeignKey(
        "core.User", on_delete=models.CASCADE, related_name="companies", blank=True, null=True
    )
    external_owner = models.CharField(max_length=255, blank=True)
    secondary_data = JSONField(
        default=dict,
        null=True,
        help_text="All non primary fields that are on the model each org may have its own",
        max_length=500,
    )
    objects = CompanyQuerySet.as_manager()

    def __str__(self):
        return f"{self.name} {self.organization}"

    class Meta:
        ordering = ["-datetime_created"]


class DealQuerySet(models.QuerySet):
    def for_user(self, user):
        if user.organization and user.is_active:
            if user.user_level in ["SDR", "MANAGER"]:
                return self.filter(organization=user.organization)
            else:
                return self.filter(organization=user.organization, owner=user)
        else:
            return None


class Deal(TimeStampModel, IntegrationModel):
    """Leads are collections of Accounts with forecasting, status and Notes attached.

    Currently we are setting on_delete to null and allowing null values. However we may
    choose to use PROTECT and require that leads are transferred before delete.
    """

    name = models.CharField(max_length=255, blank=True, null=False)
    amount = models.DecimalField(max_digits=30, decimal_places=15, default=0.00, null=True,)
    forecast_category = models.CharField(max_length=255, null=True)

    close_date = models.DateField(null=True)

    company = models.CharField(max_length=255, blank=True, help_text="Retrieved from Integration")
    contacts = models.ManyToManyField("HubspotContact", related_name="contacts", blank=True)
    external_company = models.CharField(
        max_length=255, blank=True, help_text="value from the integration"
    )

    external_owner = models.CharField(
        max_length=255, blank=True, help_text="value from the integration"
    )

    owner = models.ForeignKey(
        "core.User", related_name="owned_deals", on_delete=models.SET_NULL, blank=True, null=True,
    )
    stage = models.CharField(max_length=255, null=True)
    company = models.ForeignKey(
        "Company", related_name="companies", on_delete=models.SET_NULL, blank=True, null=True,
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
    objects = DealQuerySet.as_manager()

    class Meta:
        ordering = ["-datetime_created"]


class HubspotContactQuerySet(models.QuerySet):
    def for_user(self, user):
        if user.organization and user.is_active:
            if user.user_level in ["SDR", "MANAGER"]:
                return self.filter(organization=user.organization)
            else:
                return self.filter(organization=user.organization, owner=user)
        else:
            return None


class HubspotContact(TimeStampModel, IntegrationModel):

    email = models.CharField(max_length=255, blank=True)
    owner = models.ForeignKey(
        "core.User",
        on_delete=models.CASCADE,
        related_name="hubspot_contacts",
        blank=True,
        null=True,
    )
    company = models.ForeignKey(
        "Company", on_delete=models.SET_NULL, related_name="contacts", null=True, blank=True,
    )
    external_owner = models.CharField(max_length=255, blank=True)
    external_company = models.CharField(max_length=255, blank=True)
    secondary_data = JSONField(
        default=dict,
        null=True,
        help_text="All non primary fields that are on the model each org may have its own",
        max_length=500,
    )
    objects = HubspotContactQuerySet.as_manager()

    class Meta:
        ordering = ["-datetime_created"]


class HObjectFieldQuerySet(models.QuerySet):
    def for_user(self, user):
        if user.organization and user.is_active:
            return self.filter(hubspot_account__user__id=user.id, is_public=False)
        else:
            return self.none()

    def for_form_template(self, user, form_id=None):
        if form_id:
            # get the type and resource
            # get the fields
            return self.for_user(user)

        return self.none()


class HObjectField(TimeStampModel, IntegrationModel):
    hubspot_account = models.ForeignKey(
        "HubspotAuthAccount", on_delete=models.CASCADE, related_name="hubspot_fields", null=True,
    )
    hubspot_object = models.CharField(max_length=255, null=True)
    api_name = models.CharField(max_length=255)
    custom = models.BooleanField(default=False)
    createable = models.BooleanField(default=False)
    updateable = models.BooleanField(default=False)
    unique = models.BooleanField(default=False)
    required = models.BooleanField(default=False)
    data_type = models.CharField(max_length=255)
    display_value = models.CharField(
        max_length=255,
        blank=True,
        help_text="if this is a reference field we save the display value as well",
    )
    value = models.CharField(max_length=255, null=True, blank=True)
    label = models.CharField(max_length=255)
    length = models.PositiveIntegerField(default=0)
    reference = models.BooleanField(default=False)
    relationship_name = models.CharField(max_length=255, null=True)
    allow_multiple = models.BooleanField(default=False)
    default_filters = ArrayField(
        JSONField(max_length=255, blank=True, null=True, default=dict), default=list, blank=True
    )
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
    objects = HObjectFieldQuerySet.as_manager()

    def __str__(self):
        return f"{self.label} {self.hubspot_account} {self.hubspot_object}"
