from django.db import models
from managr.core.models import UserManager, TimeStampModel


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


class Organization(TimeStampModel):
    """ 
        Main Organization Model, Users are attached to this model 
        Users can either be limited, or Manager (possibly also have a main admin for the org)
    """

    name = models.CharField(max_length=255, null=True)
    state = models.CharField(max_length=255, choices=STATE_CHOCIES,
                             default=STATE_ACTIVE, null=False, blank=False)

    def deactivate_all_users(self):
        """ helper method to deactivate all users if their org is deactivated """
        users = User.objects.filter(organization=self)
        for u in users:
            u.state = STATE_INACTIVE
            u.save()

    def __str__(self):
        return f'{self.name}'

    class Meta:
        ordering = ['-datetime_created']


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

    def __str__(self):
        return f'{self.name} {self.organization}'

    class Meta:
        ordering = ['-datetime_created']


class Contact(TimeStampModel):
    """
        Contacts are the point of contacts that belong to an account, they must be unique (by email) and can only belong to one account
        If we have multiple organizations per account then that will also be unique and added here
    """
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    phone_number_1 = models.CharField(max_length=255)
    phone_number_2 = models.CharField(max_length=255)
    account = models.ForeignKey(
        'Account', related_name="contacts", blank=False, null=True, on_delete=models.CASCADE)
    organization = models.ForeignKey(
        'Organization', related_name="contacts", blank=False, null=False, on_delete=models.CASCADE)

    class Meta:
        ordering = ['first_name']

    def __str__(self):
        return f'{self.full_name} {self.account} {self.organization}'

    @property
    def full_name(self):
        """ Property for a user's full name """
        return f'{self.first_name} {self.last_name}'
