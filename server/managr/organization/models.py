import json


from django.db import models
from django.core import serializers
from django.db.models import Sum, Avg, Q
from django.db.models.functions import Concat
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils import timezone

from rest_framework.authtoken.models import Token

from managr.utils.numbers import format_phone_number

from django.db.models import Sum, Avg, Q
from rest_framework.exceptions import ValidationError

from managr.utils.numbers import format_phone_number
from managr.utils.misc import datetime_appended_filepath

from . import constants as org_consts


from managr.core.models import (
    UserManager,
    TimeStampModel,
    IntegrationModel,
    Notification,
)
from managr.core import constants as core_consts
from managr.core import nylas as email_client
from managr.organization.models import Notification
from managr.slack.helpers import block_builders

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

    @property
    def total_amount_closed_contracts(self):
        total = Organization.objects.aggregate(Sum("accounts__leads__closing_amount"))
        if total:
            return total
        else:
            return 0

    @property
    def avg_amount_closed_contracts(self):
        return Organization.objects.aggregate(Avg("accounts__leads__amount"))


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
    url = models.CharField(max_length=255, blank=True)
    type = models.CharField(blank=True, max_length=255)
    organization = models.ForeignKey(
        "Organization", related_name="accounts", on_delete=models.CASCADE,
    )
    logo = models.CharField(max_length=500, blank=True)
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


class ContactQuerySet(models.QuerySet):
    def for_user(self, user):
        if user.is_superuser:
            return self.all()
        elif user.organization and user.is_active:
            return self.filter(account__organization=user.organization)
        else:
            return self.none()


class Contact(TimeStampModel, IntegrationModel):
    """
    Contacts are the point of contacts that belong to
    an account, they must be unique (by email) and can
    only belong to one account
    If we have multiple organizations per account
    then that will also be unique and added here
    """

    title = models.CharField(max_length=255, blank=True)
    name = models.CharField(max_length=255, blank=True)
    email = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=255, blank=True)
    mobile_phone = models.CharField(max_length=255, blank=True)
    user = models.ForeignKey(
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

    objects = ContactQuerySet.as_manager()

    class Meta:
        ordering = ["name"]
        # unique hash so only one contact with the same email can be created per account
        unique_together = (
            "email",
            "user",
        )

    def __str__(self):
        return f"{self.full_name} {self.organization}"

    def save(self, *args, **kwargs):
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
    # currently setting default to 6 we have 5 public tags that are taking 1-5
    order = models.IntegerField(blank=True, null=True)
    is_closed = models.BooleanField(default=False)
    is_won = models.BooleanField(default=False)
    objects = StageQuerySet.as_manager()

    @property
    def as_slack_option(self):
        return block_builders.option(self.label, str(self.id))

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
