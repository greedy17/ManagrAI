import uuid
from datetime import datetime, timedelta
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.contrib.auth import login
from django.utils import timezone
from rest_framework.authtoken.models import Token
from managr.utils import sites as site_utils


ACCOUNT_TYPE_LIMITED = 'LIMITED'
ACCOUNT_TYPE_MANAGER = 'MANAGER'
ACCOUNT_TYPES = (
    (ACCOUNT_TYPE_LIMITED, 'LIMITED'), (ACCOUNT_TYPE_MANAGER, 'MANAGER')
)

STATE_ACTIVE = 'ACTIVE'
STATE_INACTIVE = 'INACTIVE'
STATE_INVITED = 'INVITED'
STATE_CHOCIES = ((STATE_ACTIVE, 'Active'), (STATE_INACTIVE,
                                            'Inactive'), (STATE_INVITED, 'Invited'))


class TimeStampModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    datetime_created = models.DateTimeField(auto_now_add=True)
    last_edited = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class UserManager(BaseUserManager):
    """Custom User model manager, eliminating the 'username' field."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """
        Create and save a User with the given email and password.

        All emails are lowercased automatically.
        """
        email = self.normalize_email(email).lower()
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create a superuser with the given email and password."""
        extra_fields['is_staff'] = True
        extra_fields['is_superuser'] = True
        extra_fields['state'] = STATE_ACTIVE
        return self._create_user(email, password, **extra_fields)

    class Meta:
        ordering = ('id',)


class User(AbstractUser, TimeStampModel):
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    username = None
    email = models.EmailField(unique=True)
    organization = models.ForeignKey(
        'api.Organization', related_name="users", on_delete=models.SET_NULL, null=True)
    type = models.CharField(choices=ACCOUNT_TYPES,
                            max_length=255, default=ACCOUNT_TYPE_MANAGER)
    first_name = models.CharField(max_length=255, blank=True, null=False)
    last_name = models.CharField(max_length=255, blank=True, null=False)
    phone_number = models.CharField(
        max_length=255, blank=True, null=False, default='')
    state = models.CharField(max_length=255, choices=STATE_CHOCIES,
                             default=STATE_INVITED, null=False, blank=False)
    magic_token = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        help_text=('The magic token is a randomly-generated uuid that can be '
                   'used to identify the user in a non-password based login flow. ')
    )
    magic_token_expiration = models.DateTimeField(
        help_text='The datetime when the magic token is expired.',
        default=timezone.now()+timedelta(days=30)
    )

    objects = UserManager()

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    @property
    def activation_link(self):
        """ Generate A Link for the User who has been invited to complete registration """
        base_url = site_utils.get_site_url()
        return f'{base_url}/activation/{self.pk}/{self.magic_token}/'

    @property
    def magic_token_expired(self):
        now = timezone.now()
        return now > self.magic_token_expiration

    def regen_magic_token(self):
        """Generate a new magic token. Set expiration of magic token to 30 days"""
        self.magic_token = uuid.uuid4()
        self.magic_token_expiration = timezone.now() + timedelta(days=30)
        self.save()
        return self.magic_token

    def login(self, request, serializer_type):
        """
        Log-in user and append authentication token to serialized response.
        """
        login(
            request, self,
            backend='django.contrib.auth.backends.ModelBackend'
        )
        auth_token, token_created = Token.objects.get_or_create(user=self)

        serializer = serializer_type(self, context={'request': request})
        response_data = serializer.data
        response_data['token'] = auth_token.key
        return response_data

    def __str__(self):
        return f'{self.full_name} <{self.email}>'

    class Meta:
        ordering = ['email']
