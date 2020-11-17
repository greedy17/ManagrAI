import uuid
from datetime import datetime, timedelta
import pytz

from rest_framework.authtoken.models import Token
from rest_framework.exceptions import ValidationError

from django.db import models, IntegrityError
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.contrib.auth import login
from django.utils import timezone
from django.contrib.postgres.fields import JSONField, ArrayField

from managr.utils import sites as site_utils
from managr.utils.misc import datetime_appended_filepath
from managr.core import constants as core_consts

from managr.core.nylas.auth import gen_auth_url, revoke_access_token


ACCOUNT_TYPE_LIMITED = "LIMITED"
ACCOUNT_TYPE_MANAGER = "MANAGER"
ACCOUNT_TYPES = ((ACCOUNT_TYPE_LIMITED, "LIMITED"), (ACCOUNT_TYPE_MANAGER, "MANAGER"))

STATE_ACTIVE = "ACTIVE"
STATE_INACTIVE = "INACTIVE"
STATE_INVITED = "INVITED"
STATE_CHOCIES = (
    (STATE_ACTIVE, "Active"),
    (STATE_INACTIVE, "Inactive"),
    (STATE_INVITED, "Invited"),
)


class TimeStampModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    datetime_created = models.DateTimeField(auto_now_add=True)
    last_edited = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class UserQuerySet(models.QuerySet):
    # TODO: Ideally I am trying to attach user roles so that INTEGRATION can assume roles for manager pb 10/15/20
    def for_user(self, user):
        if user.is_superuser:
            return self.all()
        elif user.is_active:
            if (
                user.type == core_consts.ACCOUNT_TYPE_MANAGER
                or user.type == core_consts.ACCOUNT_TYPE_INTEGRATION
            ):
                return self.filter(organization=user.organization)
            if user.type == core_consts.ACCOUNT_TYPE_REP:
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
        extra_fields["is_serviceaccount"] = False
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create a superuser with the given email and password."""
        extra_fields["is_staff"] = True
        extra_fields["is_superuser"] = True
        extra_fields["is_active"] = True
        extra_fields["is_serviceaccount"] = False
        return self._create_user(email, password, **extra_fields)

    def create_serviceaccount(self, email, password, service_for, **extra_fields):
        """ Create service accounts that will be used to send emails/notifications etc """
        extra_fields["is_staff"] = False
        extra_fields["is_superuser"] = False
        extra_fields["is_active"] = True
        extra_fields["is_serviceaccount"] = True
        extra_fields["service_for"] = service_for
        password = self.make_random_password()
        return self._create_user(email, password, **extra_fields)

    class Meta:
        ordering = ("id",)


class User(AbstractUser, TimeStampModel):
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    username = None
    email = models.EmailField(unique=True)
    is_serviceaccount = models.BooleanField(default=False)
    service_for = models.CharField(
        choices=core_consts.SERVICE_TYPES, max_length=255, null=True
    )
    is_active = models.BooleanField(default=False)
    organization = models.ForeignKey(
        "organization.Organization",
        related_name="users",
        on_delete=models.SET_NULL,
        null=True,
    )
    type = models.CharField(
        choices=core_consts.ACCOUNT_TYPES,
        max_length=255,
        default=core_consts.ACCOUNT_TYPE_REP,
    )
    first_name = models.CharField(max_length=255, blank=True, null=False)
    last_name = models.CharField(max_length=255, blank=True, null=False)
    phone_number = models.CharField(max_length=255, blank=True, null=False, default="")
    is_invited = models.BooleanField(max_length=255, default=True)
    magic_token = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        help_text=(
            "The magic token is a randomly-generated uuid that can be "
            "used to identify the user in a non-password based login flow. "
        ),
    )
    # may need to make this a property as it keeps re-running a migration
    # is_invited = models.BooleanField(max_length=255, default=False)
    magic_token_expiration = models.DateTimeField(
        help_text="The datetime when the magic token is expired.", null=True
    )
    quota = models.PositiveIntegerField(
        help_text="Target sell amount for some defined timespan "
        "set by their Organization.",
        default=0,
    )
    commit = models.PositiveIntegerField(help_text="Worst-case quota.", default=0)
    upside = models.PositiveIntegerField(help_text="Optimistic quota.", default=0)
    profile_photo = models.ImageField(
        upload_to=datetime_appended_filepath, max_length=255, null=True
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
    def magic_token_expired(self):
        if not self.magic_token_expiration:
            self.magic_token_expiration = timezone.now() + timedelta(days=30)

        now = timezone.now()
        return now > self.magic_token_expiration

    @property
    def email_auth_link(self):
        """
        This property sets the user specific url for authorizing the users email to give Nylas access
        """
        if self.magic_token_expired:
            self.regen_magic_token()

        return gen_auth_url(
            email=self.email,
            magic_token=str(self.magic_token),
        )

    @property
    def unviewed_notifications_count(self):
        return self.notifications.filter(viewed=False).count()

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
        login(request, self, backend="django.contrib.auth.backends.ModelBackend")
        auth_token, token_created = Token.objects.get_or_create(user=self)

        serializer = serializer_type(self, context={"request": request})
        response_data = serializer.data
        response_data["token"] = auth_token.key
        return response_data

    def get_contacts_from_leads(self):
        return self.claimed_leads

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


class UserSlackIntegrationQuerySet(models.QuerySet):
    def for_user(self, user):
        if user.is_superuser or user.is_serviceaccount:
            return self.all()
        elif user.organization and user.is_active:
            return self.filter(user=user.id)
        else:
            return None


class UserSlackIntegration(TimeStampModel):
    user = models.OneToOneField(
        "User",
        related_name="slack_integration",
        blank=False,
        null=False,
        on_delete=models.CASCADE,
    )
    slack_id = models.CharField(
        max_length=255, null=False, help_text="Slack ID of the User, for this workspace"
    )

    objects = UserSlackIntegrationQuerySet.as_manager()


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
    linked_at = models.DateTimeField(null=True)
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
        utc_time = datetime.utcfromtimestamp(self.linked_at)
        self.linked_at = utc_time.replace(tzinfo=pytz.utc)
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


class MessageAuthAccount(TimeStampModel):
    account_sid = models.CharField(max_length=128)
    capabilities = JSONField(max_length=128, default=dict)
    date_created = models.DateTimeField(max_length=128)
    date_updated = models.DateTimeField(max_length=128)
    friendly_name = models.CharField(max_length=128)
    identity_sid = models.CharField(max_length=128, null=True)
    origin = models.CharField(max_length=128)
    sid = models.CharField(max_length=128, null=True)
    phone_number = models.CharField(max_length=128, blank=True)
    sms_method = models.CharField(max_length=128)
    sms_url = models.CharField(
        max_length=128, help_text="the webhook url for incoming messages"
    )
    status_callback = models.CharField(
        max_length=128, help_text="the webhook url for message status"
    )
    status_callback_method = models.CharField(max_length=128)
    uri = models.CharField(max_length=128)
    voice_method = models.CharField(max_length=128)
    voice_url = models.CharField(max_length=128, null=True)
    status = models.CharField(max_length=128)
    user = models.OneToOneField(
        "User", on_delete=models.CASCADE, related_name="message_auth_account"
    )

    def __str__(self):
        return f"{self.user.full_name}, {self.friendly_name}"

    class Meta:
        ordering = ["datetime_created"]


class EmailTemplateQuerySet(models.QuerySet):
    def for_user(self, user):

        if user.is_superuser:
            return self.all()
        elif user.is_active:
            return self.filter(user=user)
        else:
            return None


class EmailTemplate(TimeStampModel):
    user = models.ForeignKey(
        "core.User", on_delete=models.CASCADE, related_name="email_templates"
    )
    name = models.CharField(max_length=128)
    subject = models.TextField(blank=True)
    body_html = models.TextField(
        help_text="WARNING: This content is not auto-escaped. Generally take care not to "
        "render user-provided data to avoid a possible HTML-injection."
    )

    objects = EmailTemplateQuerySet.as_manager()

    def __str__(self):
        return f"{self.user} - {self.name}"

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Email Templates"
        unique_together = ["user", "name"]


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
    """ a model for the selection made by the user for the option """

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
    """Manage Email and Alert Notifications (Alerts are notfications
    they receive on the Notifications side nav) options"""

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
        choices=core_consts.NOTIFICATION_TYPES,
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
