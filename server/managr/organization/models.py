from django.db import models
from managr.core.models import UserManager, TimeStampModel
from django.db.models import Sum, Avg, Q

from . import constants as org_consts
# Create your models here.


ACCOUNT_TYPE_RENEWAL = 'RENEWAL'
ACCOUNT_TYPE_NEW = 'NEW'
ACCOUNT_TYPES = (
    (ACCOUNT_TYPE_RENEWAL, 'Renewal'),
    (ACCOUNT_TYPE_NEW, 'New')
)
STATE_ACTIVE = 'ACTIVE'
STATE_INACTIVE = 'INACTIVE'
STATE_CHOCIES = ((STATE_ACTIVE, 'Active'), (STATE_INACTIVE, 'Inactive'))


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

    name = models.CharField(max_length=255, null=True)
    state = models.CharField(max_length=255, choices=STATE_CHOCIES,
                             default=STATE_ACTIVE, null=False, blank=False)

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
        return f'{self.name}'

    class Meta:
        ordering = ['-datetime_created']

    @property
    def total_amount_closed_contracts(self):
        total = Organization.objects.aggregate(
            Sum('accounts__leads__closing_amount'))
        if total:
            return total
        else:
            return 0

    @property
    def avg_amount_closed_contracts(self):
        return Organization.objects.aggregate(Avg('accounts__leads__amount'))


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
        Accounts are potential and exisiting clients that can be made into leads and added to lists
        Accounts are associated with organizations (question can an account exist in a different organization, or can an organization have a different version of an account)
    """
    name = models.CharField(max_length=255, null=True)
    url = models.CharField(max_length=255, null=True)
    type = models.CharField(choices=ACCOUNT_TYPES,
                            default=ACCOUNT_TYPE_NEW,  max_length=255)
    organization = models.ForeignKey(
        'Organization', related_name="accounts", blank=False, null=True, on_delete=models.CASCADE)
    state = models.CharField(max_length=255, choices=STATE_CHOCIES,
                             default=STATE_ACTIVE, null=False, blank=False)
    objects = AccountQuerySet.as_manager()

    def __str__(self):
        return f'{self.name} {self.organization}'

    class Meta:
        ordering = ['-datetime_created']

    @property
    def lead_count(self):
        return self.leads.count()


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
        Contacts are the point of contacts that belong to an account, they must be unique (by email) and can only belong to one account
        If we have multiple organizations per account then that will also be unique and added here
    """
    title = models.CharField(max_length=255, blank=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255, blank=True)
    email = models.CharField(max_length=255)
    phone_number_1 = models.CharField(max_length=255)
    phone_number_2 = models.CharField(max_length=255, blank=True)
    account = models.ForeignKey(
        'Account', related_name="contacts", blank=False, null=True, on_delete=models.CASCADE)
    objects = ContactQuerySet.as_manager()

    class Meta:
        ordering = ['first_name']
        # unique hash so only one contact with the same email can be created per account
        unique_together = ('email', 'account',)

    def __str__(self):
        return f'{self.full_name} {self.account}'

    @property
    def full_name(self):
        """ Property for a user's full name """
        return f'{self.first_name} {self.last_name}'

    def save(self, *args, **kwargs):
        self.email = self.email.lower()

        return super(Contact, self).save(*args, **kwargs)


class StageQuerySet(models.QuerySet):
    def for_user(self, user):
        if user.is_superuser:
            return self.all()
        elif user.organization and user.is_active:
            return self.filter(Q(type='PUBLIC') | Q(organization=user.organization))
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
        max_length=255, default="rgb(155,155,155)", help_text="hex code for color or rgba")
    type = models.CharField(max_length=255, choices=(
        org_consts.STAGE_TYPES))

    organization = models.ForeignKey(
        'Organization', related_name="stages", blank=False, null=True, on_delete=models.CASCADE)

    objects = StageQuerySet.as_manager()

    class Meta:
        ordering = ['-datetime_created']
