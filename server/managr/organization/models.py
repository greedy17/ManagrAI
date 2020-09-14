import json

from django.db import models
from django.core import serializers
from django.db.models import Sum, Avg, Q
from django.contrib.auth.models import AbstractUser, BaseUserManager

from rest_framework.authtoken.models import Token

from managr.utils.numbers import format_phone_number

from django.db.models import Sum, Avg, Q
from rest_framework.exceptions import ValidationError

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db.models import Sum, Avg
from managr.utils.numbers import format_phone_number
from managr.utils.misc import datetime_appended_filepath

from managr.core.models import UserManager, TimeStampModel
from . import constants as org_consts


from managr.core.models import UserManager, TimeStampModel
from managr.core import constants as core_consts

from . import constants as org_consts


# Create your models here.


ACCOUNT_TYPE_RENEWAL = "RENEWAL"
ACCOUNT_TYPE_NEW = "NEW"
ACCOUNT_TYPES = ((ACCOUNT_TYPE_RENEWAL, "Renewal"), (ACCOUNT_TYPE_NEW, "New"))
STATE_ACTIVE = "ACTIVE"
STATE_INACTIVE = "INACTIVE"
STATE_CHOCIES = ((STATE_ACTIVE, "Active"), (STATE_INACTIVE, "Inactive"))


class OrganizationQuerySet(models.QuerySet):
    def for_user(self, user):
        if user.is_superuser or user.is_serviceaccount:
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

    name = models.CharField(max_length=255, null=True)
    state = models.CharField(
        max_length=255,
        choices=STATE_CHOCIES,
        default=STATE_ACTIVE,
        null=False,
        blank=False,
    )
    is_externalsyncenabled = models.BooleanField(default=False, null=False, blank=False)
    objects = OrganizationQuerySet.as_manager()

    @property
    def deactivate_all_users(self):
        # TODO: When deleting an org also remember to revoke nylas tokens and request delete
        """ helper method to deactivate all users if their org is deactivated """
        users = User.objects.filter(organization=self)
        for u in users:
            u.state = STATE_INACTIVE
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

    @property
    def message_auth_count(self):
        """ returns a count of how many message auth phone numbers an org has """
        return self.users.filter(message_auth_account__isnull=False).count()

    @property
    def org_token(self):
        if self.is_externalsyncenabled:
            integration = self.users.filter(
                type=core_consts.ACCOUNT_TYPE_INTEGRATION
            ).first()
            if integration:
                if integration.is_active and integration.is_invited:
                    auth_token, token_created = Token.objects.get_or_create(
                        user=integration
                    )
                    token = json.loads(serializers.serialize("json", [auth_token,]))
                    return token[0]["pk"]


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

    name = models.CharField(max_length=255, null=True)
    url = models.CharField(max_length=255, null=True)
    type = models.CharField(
        choices=ACCOUNT_TYPES, default=ACCOUNT_TYPE_NEW, max_length=255
    )
    organization = models.ForeignKey(
        "Organization",
        related_name="accounts",
        blank=False,
        null=True,
        on_delete=models.CASCADE,
    )
    state = models.CharField(
        max_length=255,
        choices=STATE_CHOCIES,
        default=STATE_ACTIVE,
        null=False,
        blank=False,
    )
    logo = models.ImageField(
        upload_to=datetime_appended_filepath, max_length=255, null=True
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
    objects = ContactQuerySet.as_manager()

    class Meta:
        ordering = ["first_name"]
        # unique hash so only one contact with the same email can be created per account
        unique_together = (
            "email",
            "account",
        )

    def __str__(self):
        return f"{self.full_name} {self.account}"

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
    order = models.IntegerField(blank=False, null=False, default=6)

    objects = StageQuerySet.as_manager()

    class Meta:
        ordering = ["order"]

    def save(self, *args, **kwargs):
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
