import uuid
from datetime import datetime, timedelta
import pytz

from rest_framework.authtoken.models import Token
from rest_framework.exceptions import ValidationError

from django.db import models, IntegrityError
from django.contrib.auth.models import AbstractUser, BaseUserManager, AnonymousUser
from django.contrib.auth import login
from django.utils import timezone
from django.contrib.postgres.fields import JSONField, ArrayField

from managr.utils import sites as site_utils
from managr.utils.misc import datetime_appended_filepath
from managr.core import constants as core_consts
from managr.organization import constants as org_consts

from managr.core.nylas.auth import gen_auth_url, revoke_access_token


class TimeStampModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    datetime_created = models.DateTimeField(auto_now_add=True)
    last_edited = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class IntegrationModel(models.Model):
    integration_id = models.CharField(
        max_length=255, blank=True, help_text="The UUID from the integration source"
    )
    integration_source = models.CharField(
        max_length=255, choices=org_consts.INTEGRATION_SOURCES, blank=True,
    )

    class Meta:
        abstract = True


class WebhookAuthUser(AnonymousUser):
    @property
    def is_authenticated(self):
        # this purposefully always returns True and gives us a user for the webhook auth
        # the check for the token occurs in the custom authentication class
        return True


class UserQuerySet(models.QuerySet):
    # TODO: Ideally I am trying to attach user roles so that INTEGRATION can assume roles for manager pb 10/15/20
    def for_user(self, user):
        if user.is_superuser:
            return self.all()
        elif user.is_active:
            if user.user_level == core_consts.ACCOUNT_TYPE_MANAGER:
                return self.filter(organization=user.organization)
            if user.user_level == core_consts.ACCOUNT_TYPE_REP:
                return self.filter(id=user.id)
        else:
            return self.none()


class UserManager(BaseUserManager.from_queryset(UserQuerySet)):
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
        extra_fields["is_staff"] = False
        extra_fields["is_superuser"] = False
        extra_fields["is_active"] = False
        extra_fields["is_admin"] = False
        return self._create_user(email, password, **extra_fields)

    def create_admin_user(self, email, password=None, **extra_fields):
        """ An Admin user is the one who set up the initial account and org """
        extra_fields["is_staff"] = False
        extra_fields["is_superuser"] = False
        extra_fields["is_active"] = False
        extra_fields["is_admin"] = True
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create a superuser with the given email and password."""
        extra_fields["is_staff"] = True
        extra_fields["is_superuser"] = True
        extra_fields["is_active"] = True
        return self._create_user(email, password, **extra_fields)

    class Meta:
        ordering = ("id",)


class User(AbstractUser, TimeStampModel):
    # Override the Django-provided username field and replace with email
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    username = None
    email = models.EmailField(unique=True)

    # User role options
    LEADERSHIP = 'LEADERSHIP'
    FRONTLINE_MANAGER = 'FRONTLINE_MANAGER'
    ACCOUNT_EXEC = 'ACCOUNT_EXEC'
    ACCOUNT_MANAGER = 'ACCOUNT MANAGER' 
    OPERATIONS = 'OPERATIONS'
    ENABLEMENT = 'ENABLEMENT'
    ROLE_CHOICES = [
        (LEADERSHIP, 'Leadership', ),
        (FRONTLINE_MANAGER, 
        'Frontline Manager', ),
        (ACCOUNT_EXEC, 'Account Executive', ),
        (ACCOUNT_MANAGER, 'Account Manager', ),
        (OPERATIONS, 'OPERATIONS', ),
        (ENABLEMENT, 'Enablement', ),
    ]

    is_active = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    organization = models.ForeignKey(
        "organization.Organization",
        related_name="users",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    user_level = models.CharField(
        choices=core_consts.ACCOUNT_TYPES,
        max_length=255,
        default=core_consts.ACCOUNT_TYPE_REP,
    )
    first_name = models.CharField(max_length=255, blank=True,)
    last_name = models.CharField(max_length=255, blank=True, null=False)
    phone_number = models.CharField(max_length=255, blank=True, default="")
    is_invited = models.BooleanField(max_length=255, default=True)
    magic_token = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        help_text=(
            "The magic token is a randomly-generated uuid that can be "
            "used to identify the user in a non-password based login flow. "
        ),
        blank=True,
    )
    profile_photo = models.ImageField(
        upload_to=datetime_appended_filepath, max_length=255, null=True, blank=True
    )

    objects = UserManager()

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def activation_link(self):
        """ Generate A Link for the User who has been invited to complete registration """
        base_url = site_utils.get_site_url()
        return f"{base_url}/activation/{self.pk}/{self.magic_token}/"

    @property
    def email_auth_link(self):
        """
        This property sets the user specific url for authorizing the users email to give Nylas access
        """

        return gen_auth_url(email=self.email)

    def regen_magic_token(self):
        """Generate a new magic token. Set expiration of magic token to 30 days"""
        self.magic_token = uuid.uuid4()
        self.save()
        return self.magic_token

    def login(self, request, serializer_type):
        """
        Log-in user and append authentication token to serialized response.
        """
        login(request, self, backend="django.contrib.auth.backends.ModelBackend")
        auth_token, token_created = Token.objects.get_or_create(user=self)

        serializer = serializer_type(self, context={"request": request})
        response_data = serializer.data
        response_data["token"] = auth_token.key
        return response_data

    def check_notification_enabled_setting(self, key, type):
        setting_value = self.notification_settings.filter(
            option__key=key, option__notification_type=type, user=self
        ).first()
        if setting_value:
            return setting_value.value
        else:
            # if a user does not have a value then assume True which is the default
            return True

    def __str__(self):
        return f"{self.full_name} <{self.email}>"

    class Meta:
        ordering = ["email"]


class EmailAuthAccount(TimeStampModel):
    """Records Nylas OAuth authentication information for a user.

    The Nylas email integration follows the standard OAuth protocol. Once a user has
    authorized Nylas, we will receive an access_token and related information required
    to call the Nylas APIs. That information is stored in this model.
    """

    access_token = models.CharField(max_length=255, null=True)
    account_id = models.CharField(max_length=255, null=True)
    email_address = models.CharField(max_length=255, null=True)
    provider = models.CharField(max_length=255, null=True)
    sync_state = models.CharField(
        max_length=255,
        null=True,
        help_text="sync state is managed by web_hook after it is set for the first time",
    )
    name = models.CharField(max_length=255, null=True)
    user = models.OneToOneField(
        "User", on_delete=models.CASCADE, related_name="email_auth_account"
    )

    def __str__(self):
        return f"{self.email_address}"

    def revoke(self):
        """ method to revoke access if account is changed, user is removed"""
        revoke_access_token(self.access_token)
        return self.delete()

    class Meta:
        ordering = ["email_address"]

    def save(self, *args, **kwargs):
        try:
            return super(EmailAuthAccount, self).save(*args, **kwargs)
        except IntegrityError:
            raise ValidationError(
                {
                    "non_form_errors": {
                        "access_token": "This User already has an access Token \
                    please revoke the access token first"
                    }
                }
            )


""" 
class NotificationOptionQuerySet(models.QuerySet):

    ### NOTE We are using __contains here as the field type is text[] in sql __in will search equality
    ### this will throw a mismatch type error
    def for_user(self, user):
        if user.is_superuser:
            return self.all()
        elif user.is_active:
            if user.type == core_consts.ACCOUNT_TYPE_MANAGER:
                return self.filter(
                    user_groups__contains=[core_consts.ACCOUNT_TYPE_MANAGER]
                )
            elif user.type == core_consts.ACCOUNT_TYPE_REP:
                return self.filter(user_groups__contains=[core_consts.ACCOUNT_TYPE_REP])
            elif user.type == core_consts.ACCOUNT_TYPE_ADMIN:
                return self.filter(
                    user_groups__contains=[core_consts.ACCOUNT_TYPE_ADMIN]
                )
        else:
            return None


class NotificationSelectionQuerySet(models.QuerySet):
    def for_user(self, user):
        if user.is_superuser:
            return self.all()
        elif user.is_active:
            return self.filter(user=user)
        else:
            return None


class NotificationSelection(TimeStampModel):

    option = models.ForeignKey(
        "core.NotificationOption", on_delete=models.CASCADE, related_name="selections"
    )
    user = models.ForeignKey(
        "core.User", on_delete=models.CASCADE, related_name="notification_settings"
    )
    value = models.BooleanField(
        help_text="If no option is selected it will take the default value",
    )

    def __str__(self):
        return f"user:{self.user}, option: {self.option}, value: {self.value}"

    class Meta:
        ordering = ["-datetime_created"]
        # only allow one selection per option for each user
        unique_together = (
            "user",
            "option",
        )


class NotificationOption(TimeStampModel):

    # user groups will be used to populate the options for each user type
    title = models.CharField(max_length=128, help_text="Friendly Name")
    description = models.TextField(
        blank=True, help_text="this will show up as a tooltip for the option"
    )
    default_value = models.BooleanField(
        default=True,
        help_text="All options are Boolean, the value here populates the default for the user",
    )
    user_groups = ArrayField(
        models.CharField(max_length=255, choices=core_consts.ACCOUNT_TYPES, blank=True),
        default=list,
        blank=True,
        help_text="An Array of user types that have access to this setting",
    )
    notification_type = models.CharField(
        choices=core_consts.NOTIFICATION_TYPE_CHOICES,
        max_length=255,
        help_text="Email or Alert",
    )

    resource = models.CharField(
        max_length=255,
        choices=core_consts.NOTIFICATION_RESOURCES,
        null=True,
        help_text="select a resource to apply notification to",
    )
    key = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="unique identifier for notification option",
    )
    objects = NotificationOptionQuerySet.as_manager()

    def __str__(self):
        return f"{self.title} - {self.notification_type}"

    class Meta:
        ordering = ["-datetime_created"]

    def get_value(self, user):
        selection = self.selections.filter(user=user)
        if selection.exists():
            return selection.first()
        else:
            # create an option for the user with the default value
            selection = NotificationSelection.objects.create(
                option=self, user=user, value=self.default_value
            )
            return selection
 """


class NotificationQuerySet(models.QuerySet):
    def for_user(self, user):
        if user.is_superuser:
            return self.all()
        elif user.organization and user.is_active:
            return self.filter(user=user.id)


class Notification(TimeStampModel):
    """ By default Notifications will only return alerts 
        We also will allow the code to access all types of notificaitons 
        SLACK, EMAIL, ALERT when checking whether or not it should create an alert
    """

    notify_at = models.DateTimeField(
        null=True,
        help_text="Set a time for the notification to be executed, if this is a reminder it can be something like 5 minutes before time\
                                        if it is an email it can be the time the email is received ",
    )
    notified_at = models.DateTimeField(
        null=True, help_text="date time when the notification was executed"
    )
    title = models.CharField(
        max_length=255, null=True, help_text="a title for the notification"
    )
    notification_type = models.CharField(
        max_length=255,
        choices=core_consts.NOTIFICATION_TYPE_CHOICES,
        null=True,
        help_text="type of Notification being created",
    )
    resource_id = models.CharField(
        max_length=255,
        null=True,
        help_text="Id of the resource if it is an email it will be the thread id",
    )
    notification_class = models.CharField(
        max_length=255,
        help_text="Classification of notification, email, alert, slack",
        choices=core_consts.NOTIFICATION_CLASS_CHOICES,
    )
    viewed = models.BooleanField(blank=False, null=False, default=False)
    meta = JSONField(help_text="Details about the notification", default=dict)
    user = models.ForeignKey(
        "core.User", on_delete=models.SET_NULL, related_name="notifications", null=True
    )

    objects = NotificationQuerySet.as_manager()

    class Meta:
        ordering = ["-notify_at"]

