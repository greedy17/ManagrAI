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


from managr.core.models import UserManager, TimeStampModel
from managr.core import constants as core_consts
from managr.core import nylas as email_client
from managr.lead.models import Notification
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
    photo = models.ImageField(
        upload_to=datetime_appended_filepath, max_length=255, blank=True
    )
    state = models.CharField(
        max_length=255,
        choices=org_consts.STATE_CHOCIES,
        default=org_consts.STATE_ACTIVE,
        null=False,
        blank=False,
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


class Account(TimeStampModel):
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
    logo = models.ImageField(
        upload_to=datetime_appended_filepath, max_length=255, blank=True
    )
    parent = models.ForeignKey(
        "organization.Account",
        on_delete=models.SET_NULL,
        related_name="parent_account",
        blank=True,
    )
    integration_source = models.CharField(
        max_length=255, choices=org_consts.INTEGRATION_SOURCES, blank=True,
    )

    objects = AccountQuerySet.as_manager()

    def __str__(self):
        return f"{self.name} {self.organization}"

    class Meta:
        ordering = ["-datetime_created"]


class ContactQuerySet(models.QuerySet):
    def for_user(self, user):
        if user.is_superuser:
            return self.all()
        elif user.organization and user.is_active:
            return self.filter(account__organization=user.organization)
        else:
            return self.none()


class Contact(TimeStampModel):
    """
    Contacts are the point of contacts that belong to
    an account, they must be unique (by email) and can
    only belong to one account
    If we have multiple organizations per account
    then that will also be unique and added here
    """

    title = models.CharField(max_length=255, blank=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255, blank=True)
    email = models.CharField(max_length=255)
    phone_number_1 = models.CharField(max_length=255)
    phone_number_2 = models.CharField(max_length=255, blank=True)
    account = models.ForeignKey(
        "Account",
        related_name="contacts",
        blank=False,
        null=True,
        on_delete=models.CASCADE,
    )
    # since we are no longer requiring accounts we support orgs
    organization = models.ForeignKey(
        "Organization",
        related_name="contacts",
        blank=False,
        null=True,
        on_delete=models.CASCADE,
    )
    objects = ContactQuerySet.as_manager()

    class Meta:
        ordering = ["first_name"]
        # unique hash so only one contact with the same email can be created per account
        unique_together = (
            "email",
            "organization",
        )

    def __str__(self):
        return f"{self.full_name} {self.organization}"

    @property
    def full_name(self):
        """ Property for a user's full name """
        return f"{self.first_name} {self.last_name}"

    def save(self, *args, **kwargs):
        self.email = BaseUserManager.normalize_email(self.email).lower()
        self.phone_number_1 = (
            format_phone_number(self.phone_number_1, format="+1%d%d%d%d%d%d%d%d%d%d")
            if self.phone_number_1
            else ""
        )
        self.phone_number_2 = (
            format_phone_number(self.phone_number_2, format="+1%d%d%d%d%d%d%d%d%d%d")
            if self.phone_number_2
            else ""
        )
        contact = (
            Contact.objects.filter(email=self.email, account=self.account)
            .exclude(id=self.id)
            .first()
        )
        if contact:
            raise ValidationError(
                detail={
                    "contact_exists": "A contact in the same org and account already exist"
                }
            )

        return super(Contact, self).save(*args, **kwargs)


class StageQuerySet(models.QuerySet):
    def for_user(self, user):
        if user.is_superuser:
            return self.all()
        elif user.organization and user.is_active:
            return self.filter(Q(type="PUBLIC") | Q(organization=user.organization))
        else:
            return self.none()


class Stage(TimeStampModel):
    """
    Stages are Opportunity statuses each organization can set their own (if they have an SF integration these are merged from there)
    There are some static stages available to all organizations and private ones that belong only to certain organizations.
    """

    title = models.CharField(max_length=255)
    description = models.CharField(max_length=255, blank=True)
    color = models.CharField(
        max_length=255, default="#9B9B9B", help_text="hex code for color"
    )
    type = models.CharField(max_length=255, choices=(org_consts.STAGE_TYPES))

    organization = models.ForeignKey(
        "Organization",
        related_name="stages",
        null=True,
        blank=True,
        default="",
        on_delete=models.CASCADE,
    )
    # currently setting default to 6 we have 5 public tags that are taking 1-5
    order = models.IntegerField(blank=False,)

    objects = StageQuerySet.as_manager()

    @property
    def as_slack_option(self):
        return block_builders.option(self.title, str(self.id))

    class Meta:
        ordering = ["order"]

    def __str__(self):
        if self.organization:
            return f"Stage ({self.id}) -- Title: {self.title}, Organization: {self.organization.name}"
        else:
            return f"Stage ({self.id}) -- Title: {self.title}, Organization: None (is Public)"

    def save(self, *args, **kwargs):
        if self.type == org_consts.STAGE_TYPE_PRIVATE:
            users = self.organization.users.filter(is_active=True)
            allowed_notifications = []
            for user in users:
                ## get user selection for this notification
                if user.check_notification_enabled_setting(
                    core_consts.NOTIFICATION_OPTION_KEY_ORGANIZATION_STAGES,
                    core_consts.NOTIFICATION_TYPE_EMAIL,
                ):
                    allowed_notifications.append(user)

            recipients = [
                {"email": user.email, "name": user.full_name}
                for user in allowed_notifications
            ]

            message = {
                "subject": f"Stages Updated",
                "body": f"Your organization has added new stages, please log out and login to update your list",
            }
            email_client.emails.send_system_email(recipients, message)
            for user in users:
                if user.check_notification_enabled_setting(
                    core_consts.NOTIFICATION_OPTION_KEY_ORGANIZATION_STAGES,
                    core_consts.NOTIFICATION_TYPE_ALERT,
                ):

                    Notification.objects.create(
                        notify_at=timezone.now(),
                        title="Stages Updated",
                        notification_type="SYSTEM",
                        resource_id=self.id,
                        notification_class="ALERT",
                        user=user,
                        meta={
                            "content": "Your organization has added new stages, please log out and login to update your list"
                        },
                    )

        # save all as upper case
        self.title = self.title.upper()
        if (
            Stage.objects.filter(title=self.title, organization=self.organization)
            .exclude(id=self.id)
            .exists()
        ):
            raise ValidationError(
                detail={"key_error": "A stage with this title already exists"}
            )

        return super(Stage, self).save(*args, **kwargs)
