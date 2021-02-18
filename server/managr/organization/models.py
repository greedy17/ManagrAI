import json


from django.db import models
from django.core import serializers
from django.db.models import Sum, Avg, Q
from django.db.models.functions import Concat
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils import timezone
from django.contrib.postgres.fields import JSONField, ArrayField

from rest_framework.authtoken.models import Token
from rest_framework.exceptions import ValidationError


from managr.salesforce.adapter.models import SalesforceAuthAccountAdapter, OpportunityAdapter
from managr.utils.numbers import format_phone_number
from managr.utils.misc import datetime_appended_filepath
from managr.core.models import UserManager, TimeStampModel, IntegrationModel, User
from managr.salesforce.exceptions import ResourceAlreadyImported
from managr.core import constants as core_consts
from managr.core import nylas as email_client
from managr.slack.helpers import block_builders
from managr.salesforce.adapter.models import ContactAdapter
from managr.opportunity import constants as opp_consts
from . import constants as org_consts


class OrganizationQuerySet(models.QuerySet):
    def for_user(self, user):
        if user.is_superuser:
            return self.all()
        elif user.organization and user.is_active:
            return self.filter(pk=user.organization_id)
        else:
            return None


class Organization(TimeStampModel):
    """
    Main Organization Model, Users are attached to this model
    Users can either be limited, or Manager (possibly also have a main admin for the org)
    """

    name = models.CharField(max_length=255, blank=True)
    photo = models.ImageField(upload_to=datetime_appended_filepath, max_length=255, blank=True)
    state = models.CharField(
        max_length=255, choices=org_consts.STATE_CHOCIES, default=org_consts.STATE_ACTIVE,
    )
    is_trial = models.BooleanField(default=False)

    objects = OrganizationQuerySet.as_manager()

    @property
    def deactivate_all_users(self):
        # TODO: When deleting an org also remember to revoke nylas tokens and request delete
        """ helper method to deactivate all users if their org is deactivated """
        users = User.objects.filter(organization=self)
        for u in users:
            u.state = org_consts.STATE_INACTIVE
            u.save()

    def __str__(self):
        return f"{self.name}"

    class Meta:
        ordering = ["-datetime_created"]

    @property
    def has_stages_integrated(self):
        """ if an org already has stages assume we already synced and dont try again """

        return self.stages.count() > 0


class AccountQuerySet(models.QuerySet):
    def for_user(self, user):
        if user.is_superuser:
            return self.all()
        elif user.organization and user.is_active:
            return self.filter(organization=user.organization)
        else:
            return None


class Account(TimeStampModel, IntegrationModel):
    """
    Accounts are potential and exisiting clients that
    can be made into leads and added to lists

    """

    name = models.CharField(max_length=255)
    organization = models.ForeignKey(
        "Organization", related_name="accounts", on_delete=models.CASCADE,
    )
    parent = models.ForeignKey(
        "organization.Account",
        on_delete=models.SET_NULL,
        related_name="parent_account",
        blank=True,
        null=True,
    )
    parent_integration_id = models.CharField(
        max_length=255,
        blank=True,
        help_text="UUID from integration for parent account, saved in case of errors",
    )
    owner = models.ForeignKey(
        "core.User", on_delete=models.CASCADE, related_name="accounts", blank=True, null=True
    )
    external_owner = models.CharField(max_length=255, blank=True)
    secondary_data = JSONField(
        default=dict,
        null=True,
        help_text="All non primary fields that are on the model each org may have its own",
        max_length=500,
    )
    objects = AccountQuerySet.as_manager()

    def __str__(self):
        return f"{self.name} {self.organization}"

    class Meta:
        ordering = ["-datetime_created"]

    def save(self, *args, **kwargs):
        """ In case of duplicates update not save"""
        obj = (
            Account.objects.filter(
                integration_id=self.integration_id, organization=self.organization
            )
            .exclude(id=self.id)
            .first()
        )
        if obj:
            return

        return super(Account, self).save(*args, **kwargs)

    @property
    def as_slack_option(self):
        return block_builders.option(self.name, str(self.id))

    @staticmethod
    def generate_slack_form_config(user, type):
        """Helper class to generate a slack form config for an org"""
        sf_account = user.salesforce_account if user.has_salesforce_integration else None
        if sf_account:
            # return an object with creatable and required fields
            fields = sf_account.object_fields.get("Account", {}).get("fields", {})
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
                meeting_types = sf_account.user.organization.action_choices.all()
                meeting_type_field = SalesforceAuthAccountAdapter.custom_field(
                    "Meeting Type",
                    "meeting_type",
                    type="Picklist",
                    required=True,
                    length=25,
                    value=None,
                    options=[m_type.as_sf_option for m_type in meeting_types],
                )
                meeting_notes_field = SalesforceAuthAccountAdapter.custom_field(
                    "Meeting Notes",
                    "meeting_notes",
                    type="String",
                    required=True,
                    length=250,
                    value=None,
                )
                return {
                    "fields": [meeting_type_field, meeting_notes_field,],
                }

        return


class ContactQuerySet(models.QuerySet):
    def for_user(self, user):
        if user.is_superuser:
            return self.all()
        elif user.organization and user.is_active:
            return self.filter(account__organization=user.organization)
        else:
            return self.none()


class Contact(TimeStampModel, IntegrationModel):

    email = models.CharField(max_length=255, blank=True)
    owner = models.ForeignKey(
        "core.User", on_delete=models.CASCADE, related_name="contacts", blank=True, null=True
    )
    account = models.ForeignKey(
        "organization.Account",
        on_delete=models.SET_NULL,
        related_name="contacts",
        null=True,
        blank=True,
    )
    external_owner = models.CharField(max_length=255, blank=True)
    external_account = models.CharField(max_length=255, blank=True)
    secondary_data = JSONField(
        default=dict,
        null=True,
        help_text="All non primary fields that are on the model each org may have its own",
        max_length=500,
    )
    objects = ContactQuerySet.as_manager()

    class Meta:
        ordering = ["-datetime_created"]

    @property
    def adapter_class(self):
        data = self.__dict__
        data["id"] = str(data["id"])
        data["owner"] = str(self.owner.id)
        return ContactAdapter(**data)

    def __str__(self):
        return f"contact integration: {self.integration_source}: {self.integration_id}"

    def save(self, *args, **kwargs):
        # if there is an integration id make sure it is unique
        if self.integration_id:
            existing = (
                Contact.objects.filter(
                    integration_id=self.integration_id, imported_by=self.imported_by
                )
                .exclude(id=self.id)
                .first()
            )
            if existing:
                raise ResourceAlreadyImported()
        return super(Contact, self).save(*args, **kwargs)


class StageQuerySet(models.QuerySet):
    def for_user(self, user):
        if user.is_superuser:
            return self.all()
        elif user.organization and user.is_active:
            return self.filter(Q(organization=user.organization))
        else:
            return self.none()


class Stage(TimeStampModel, IntegrationModel):
    """
    Each Org Will have its own stages on set up
    """

    label = models.CharField(max_length=255)
    description = models.CharField(max_length=255, blank=True)
    color = models.CharField(max_length=255, default="#9B9B9B", help_text="hex code for color")
    value = models.CharField(
        max_length=255, blank=True, help_text="This may be use as a unique value, if it exists"
    )
    organization = models.ForeignKey(
        "Organization", related_name="stages", on_delete=models.CASCADE,
    )
    order = models.IntegerField(blank=True, null=True)
    is_closed = models.BooleanField(default=False)
    is_won = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    forecast_category = models.CharField(
        max_length=255, choices=opp_consts.FORECAST_CHOICES, blank=True
    )

    objects = StageQuerySet.as_manager()

    @property
    def as_slack_option(self):
        return block_builders.option(self.label, self.id)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"Stage ({self.id}) -- label: {self.label}"

    def save(self, *args, **kwargs):
        obj = (
            Stage.objects.filter(integration_id=self.integration_id, organization=self.organization)
            .exclude(id=self.id)
            .first()
        )
        if obj:
            return
        return super(Stage, self).save(*args, **kwargs)


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
        return block_builders.option(self.title, self.title)

    @property
    def as_sf_option(self):
        # model these into sf optiona key value pairs to be then changed into slack options
        return dict(attributes={}, label=self.title, value=self.title, validFor=[])

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return f" ActionChoice ({self.id}) -- Title: {self.title}, Organization: {self.organization.name}"
