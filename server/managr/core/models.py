from urllib.parse import urlencode
import uuid
import json
import logging
from datetime import datetime
from urllib.error import HTTPError
from django.db.models.fields.related import ForeignKey
import requests

from rest_framework.authtoken.models import Token
from rest_framework.exceptions import ValidationError

from django.db import models, IntegrityError
from django.contrib.auth.models import AbstractUser, BaseUserManager, AnonymousUser
from django.db.models import Q
from django.contrib.auth import login
from django.contrib.postgres.fields import JSONField, ArrayField
from managr.utils import sites as site_utils
from managr.utils.misc import datetime_appended_filepath, phrase_to_snake_case
from managr.utils.client import HttpClient, Variable_Client
from managr.core import constants as core_consts
from managr.organization import constants as org_consts
from managr.slack.helpers import block_builders
from managr.core.nylas.auth import convert_local_time_to_unix

from .nylas.exceptions import NylasAPIError
from managr.core.nylas.auth import gen_auth_url, revoke_access_token

client = HttpClient().client
logger = logging.getLogger("managr")


def defaultClickActivity():
    return {
        "meeting": {"untouched": 0, "touched": []},
        "workflows": {"untouched": 0, "touched": []},
    }


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
        max_length=255,
        choices=org_consts.INTEGRATION_SOURCES,
        blank=True,
    )
    imported_by = models.ForeignKey(
        "core.User", on_delete=models.CASCADE, null=True, related_name="imported_%(class)s"
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
    # TODO pb 10/15/20: Ideally, we are trying to attach user roles so that
    #       INTEGRATION can assume roles for managr
    def for_user(self, user):
        if user.is_superuser or user.is_staff:
            return self.all()
        elif user.is_active:
            if user.user_level == core_consts.USER_LEVEL_MANAGER:
                return self.filter(organization=user.organization, is_active=True)
            if user.user_level == core_consts.USER_LEVEL_REP:
                return self.filter(id=user.id)
            elif user.user_level == core_consts.USER_LEVEL_SDR:
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
        extra_fields["is_active"] = True
        extra_fields["is_admin"] = False
        return self._create_user(email, password, **extra_fields)

    def create_admin_user(self, email, password=None, **extra_fields):
        """An Admin user is the one who set up the initial account and org"""
        extra_fields["is_staff"] = False
        extra_fields["is_superuser"] = False
        extra_fields["is_active"] = True
        extra_fields["is_admin"] = True
        extra_fields["user_level"] = core_consts.USER_LEVEL_REP
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create a superuser with the given email and password."""
        extra_fields["is_staff"] = True
        extra_fields["is_superuser"] = True
        extra_fields["is_active"] = True
        return self._create_user(email, password, **extra_fields)

    class Meta:
        ordering = ("id",)


class CustomJSONField(models.TextField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("default", "{}")
        super().__init__(*args, **kwargs)


class Message(TimeStampModel):
    user_type = models.CharField(max_length=100)
    value = models.TextField()
    resource_id = models.CharField(max_length=100)
    resource_type = models.CharField(max_length=100)
    updated = models.BooleanField(blank=False, null=False, default=False)
    failed = models.BooleanField(blank=False, null=False, default=False)
    generated = models.BooleanField(blank=False, null=False, default=False)
    data = CustomJSONField()
    generated_title = models.CharField(max_length=100)
    generated_type = models.CharField(max_length=100)
    form_id = models.CharField(max_length=100)
    error = models.TextField(null=True)
    resource = models.CharField(max_length=100, null=True)
    integration_id = models.CharField(max_length=100, null=True)
    form_type = models.CharField(max_length=100, null=True)
    conversation = ForeignKey(
        "core.Conversation", on_delete=models.CASCADE, related_name="messages"
    )

    class Meta:
        ordering = ["datetime_created"]


class Conversation(TimeStampModel):
    user = models.ForeignKey("core.User", on_delete=models.CASCADE, related_name="conversations")
    title = models.CharField(
        max_length=255,
        blank=True,
    )
    members = ArrayField(models.CharField(max_length=1000), default=list, blank=True)


class User(AbstractUser, TimeStampModel):
    # Override the Django-provided username field and replace with email
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    username = None
    email = models.EmailField(unique=True)

    # User role options
    # LEADERSHIP = "LEADERSHIP"
    # FRONTLINE_MANAGER = "FRONTLINE_MANAGER"
    # ACCOUNT_EXEC = "ACCOUNT_EXEC"
    # ACCOUNT_MANAGER = "ACCOUNT MANAGER"
    # OPERATIONS = "OPERATIONS"
    # ENABLEMENT = "ENABLEMENT"
    # SDR = "SDR"
    SALES = "SALES"
    PR = "PR"
    ROLE_CHOICES = [
        (
            SALES,
            "Sales",
        ),
        (
            PR,
            "PR",
        ),
        # (LEADERSHIP, "Leadership",),
        # (FRONTLINE_MANAGER, "Frontline Manager",),
        # (ACCOUNT_EXEC, "Account Executive",),
        # (ACCOUNT_MANAGER, "Account Manager",),
        # (OPERATIONS, "OPERATIONS",),
        # (ENABLEMENT, "Enablement",),
        # (SDR, "SDR",),
    ]
    role = models.CharField(max_length=32, choices=ROLE_CHOICES, blank=True)

    is_active = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    onboarding = models.BooleanField(default=False)
    organization = models.ForeignKey(
        "organization.Organization",
        related_name="users",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    user_level = models.CharField(
        choices=core_consts.USER_LEVELS,
        max_length=255,
        default=core_consts.USER_LEVEL_REP,
    )
    first_name = models.CharField(
        max_length=255,
        blank=True,
    )
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
    timezone = models.CharField(default="UTC", max_length=255)
    activated_managr_configs = ArrayField(
        models.CharField(max_length=255),
        default=list,
        help_text="List of activated Managr templates",
        blank=True,
    )
    reminders = JSONField(
        default=core_consts.REMINDERS,
        null=True,
        blank=True,
        help_text="Object for reminder setting",
    )
    crm = models.CharField(
        choices=core_consts.CRM_CHOICES,
        max_length=25,
        null=True,
        blank=True,
    )
    team = models.ForeignKey(
        "organization.Team", related_name="users", on_delete=models.SET_NULL, null=True
    )
    make_team_lead = models.BooleanField(default=False)
    meta_data = JSONField(
        default=dict,
        null=True,
        blank=True,
    )
    objects = UserManager()

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def activation_link(self):
        """Generate A Link for the User who has been invited to complete registration"""
        base_url = site_utils.get_site_url()
        return f"{base_url}/activation/{self.pk}/{self.magic_token}/"

    @property
    def email_auth_link(self):
        """
        This property sets the user specific url for authorizing
        the users email to give Nylas access.
        """

        return gen_auth_url(email=self.email)

    @property
    def as_slack_option(self):
        return block_builders.option(self.name, str(self.id))

    def regen_magic_token(self):
        """Generate a new magic token. Set expiration of magic token to 30 days"""
        self.magic_token = uuid.uuid4()
        self.save()
        return self.magic_token

    def login(self, request, serializer_type):
        from managr.api.models import ManagrToken

        """Log in user and append authentication token to serialized response."""
        login(request, self, backend="django.contrib.auth.backends.ModelBackend")
        auth_token, _ = ManagrToken.objects.get_or_create(user=self)

        serializer = serializer_type(self, context={"request": request})
        response_data = serializer.data
        response_data["token"] = auth_token.key
        return response_data

    def remove_user(self):
        """
        Revoke the user's Slack, Zoom, Salesforce and Nylas authentication tokens, then delete.
        """
        from managr.slack.helpers import requests as slack_requests

        user = self
        organization = user.organization
        if user.is_admin and hasattr(organization, "slack_integration"):
            slack_int = organization.slack_integration
            r = slack_requests.revoke_access_token(slack_int.access_token)
            slack_int.delete()

        if hasattr(user, "slack_integration"):
            user.slack_integration.delete()

        if hasattr(user, "salesforce_account"):
            sf_acc = user.salesforce_account
            sf_acc.revoke()

        if hasattr(user, "zoom_account"):
            zoom = user.zoom_account
            try:
                zoom.helper_class.revoke()
            except Exception:
                # revoke token will fail if ether token is expired
                pass
            if zoom.refresh_token_task:
                from background_task.models import Task

                task = Task.objects.filter(id=zoom.refresh_token_task).first()
                if task:
                    task.delete()
            zoom.delete()

        if hasattr(user, "nylas"):
            nylas = user.nylas
            try:
                nylas.revoke()
            except Exception as e:
                logger.info(
                    f"Error occured removing user token from nylas for user {self.email} {self.nylas.email_address} {err}"
                )
                pass
        self.delete()

    def deactivate_user(self):
        """
        Revoke the user's Slack, Zoom, Salesforce and Nylas authentication tokens, but doesn't delete user.
        """
        user = self
        if hasattr(user, "slack_integration"):
            user.slack_integration.delete()

        if hasattr(user, "salesforce_account"):
            sf_acc = user.salesforce_account
            sf_acc.revoke(False)

        if hasattr(user, "zoom_account"):
            zoom = user.zoom_account
            try:
                zoom.helper_class.revoke()
            except Exception:
                # revoke token will fail if ether token is expired
                pass
            if zoom.refresh_token_task:
                from background_task.models import Task

                task = Task.objects.filter(id=zoom.refresh_token_task).first()
                if task:
                    task.delete()
        if hasattr(user, "nylas"):
            nylas = user.nylas
            try:
                nylas.revoke()
            except Exception as e:
                logger.info(
                    f"Error occured removing user token from nylas for user {self.email} {nylas.email_address} {e}"
                )
                pass
        self.is_active = False
        return self.save()

    @property
    def has_zoom_integration(self):
        # when a user integrates we set the info once
        # when the user then removes the integration we keep the account
        # but we only remove the token and refresh tokens
        if hasattr(self, "zoom_account"):
            zoom_acct = self.zoom_account
            return not zoom_acct.is_revoked
        else:
            return False

    @property
    def crm_account(self):
        if self.crm is None:
            return None
        elif self.crm == "SALESFORCE":
            return self.salesforce_account
        else:
            return self.hubspot_account

    @property
    def engagement_account(self):
        if not self.has_outreach_integration and not self.has_salesloft_integration:
            return None
        elif self.has_outreach_integration:
            return self.outreach_account
        else:
            return self.salesloft_account

    @property
    def has_slack_integration(self):
        return hasattr(self, "slack_integration")

    @property
    def has_salesforce_integration(self):
        return hasattr(self, "salesforce_account")

    @property
    def has_nylas_integration(self):
        return hasattr(self, "nylas")

    @property
    def has_salesloft_integration(self):
        return hasattr(self, "salesloft_account")

    @property
    def has_gong_integration(self):
        return hasattr(self, "gong_account")

    @property
    def has_outreach_integration(self):
        return hasattr(self, "outreach_account")

    @property
    def has_hubspot_integration(self):
        return hasattr(self, "hubspot_account")

    @property
    def is_team_lead(self):
        return hasattr(self, "team_lead_of")

    @property
    def as_slack_option(self):
        return block_builders.option(self.full_name, str(self.id))

    @property
    def note_templates(self):
        return NoteTemplate.objects.for_user(self)

    def __str__(self):
        return f"{self.full_name} <{self.email}>"

    class Meta:
        ordering = ["email"]


class NylasAuthAccount(TimeStampModel):
    """Records Nylas OAuth authentication information for a user.

    Nylas is used to access the user's calendar information.

    The Nylas email integration follows the standard OAuth protocol. Once a user has
    authorized Nylas, we will receive an access_token and related information required
    to call the Nylas APIs. That information is stored in this model.
    """

    access_token = models.CharField(max_length=255, null=True)
    account_id = models.CharField(max_length=255, null=True)
    email_address = models.CharField(max_length=255, null=True)
    provider = models.CharField(max_length=255, null=True)
    event_calendar_id = models.CharField(max_length=255, null=True, blank=True)
    sync_state = models.CharField(
        max_length=255,
        null=True,
        help_text="sync state is managed by web_hook after it is set for the first time",
    )
    name = models.CharField(max_length=255, null=True)
    user = models.OneToOneField("User", on_delete=models.CASCADE, related_name="nylas")

    def __str__(self):
        return f"{self.email_address}"

    def revoke(self):
        """method to revoke access if account is changed, user is removed"""
        revoke_access_token(self.access_token)
        return self.delete()

    class Meta:
        ordering = ["email_address"]

    def save(self, *args, **kwargs):
        try:
            return super().save(*args, **kwargs)
        except IntegrityError:
            raise ValidationError(
                {
                    "non_form_errors": {
                        "access_token": "This User already has an access Token \
                    please revoke the access token first"
                    }
                }
            )

    def schedule_meeting(
        self, title, start_time, end_time, participants, meeting_link, description
    ):
        url = f"{core_consts.NYLAS_API_BASE_URL}/{core_consts.EVENT_POST}"
        calendar_description = f"Meeting link: {meeting_link}"
        if description:
            calendar_description = f"Meeting link: {meeting_link} \n{description}"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "Cache-Control": "no-cache",
        }
        data = {
            "title": title,
            "calendar_id": f"{self.event_calendar_id}",
            "status": "confirmed",
            "description": calendar_description,
            "when": {
                "start_time": start_time,
                "end_time": end_time,
                "start_timezone": f"{self.user.timezone}",
                "end_timezone": f"{self.user.timezone}",
            },
            "busy": True,
        }
        if len(participants) > 0:
            data["participants"] = participants
        r = client.post(url, json.dumps(data), headers=headers)
        response_data = self._handle_response(r)
        return response_data

    @staticmethod
    def _handle_response(response, fn_name=None):
        if not hasattr(response, "status_code"):
            raise ValueError

        elif response.status_code == 200 or response.status_code == 201:
            try:
                data = response.json()
            except Exception as e:
                NylasAPIError(e)
            except json.decoder.JSONDecodeError as e:
                return logger.error(f"An error occured with a nylas integration, {e}")

        else:
            status_code = response.status_code
            error_data = response.json()
            error_param = error_data.get("error", None)
            error_message = error_data.get("message", None)
            error_code = error_data.get("code", None)
            kwargs = {
                "status_code": status_code,
                "error_code": error_code,
                "error_param": error_param,
                "error_message": error_message,
            }
            return NylasAPIError(error_message)
        return data

    def _get_calendar_data(self, date=None):
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }
        user_timezone = f"{self.user.timezone}"
        starts_after = convert_local_time_to_unix(user_timezone, 7, 00, date)
        ends_before = convert_local_time_to_unix(user_timezone, 20, 00, date)
        query = dict(
            {
                "starts_after": starts_after,
                "ends_before": ends_before,
            }
        )
        if self.event_calendar_id:
            query["calendar_id"] = self.event_calendar_id
        params = urlencode(query)
        with Variable_Client() as client:
            events = client.get(
                f"{core_consts.NYLAS_API_BASE_URL}/{core_consts.EVENT_POST}?{params}",
                headers=headers,
            )
        return self._handle_response(events)


class NotificationQuerySet(models.QuerySet):
    def for_user(self, user):
        if user.is_superuser:
            return self.all()
        elif user.organization and user.is_active:
            return self.filter(user=user.id)


class Notification(TimeStampModel):
    """By default Notifications will only return alerts
    We also will allow the code to access all types of notifications
    SLACK, EMAIL, ALERT when checking whether or not it should create an alert
    """

    notify_at = models.DateTimeField(
        null=True,
        help_text=(
            "Set a time for the notification to be executed, "
            "if this is a reminder it can be something like 5 "
            "minutes before time if it is an email it can be "
            "the time the email is received "
        ),
    )
    notified_at = models.DateTimeField(
        null=True, help_text="date time when the notification was executed"
    )
    title = models.CharField(max_length=255, null=True, help_text="a title for the notification")
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


class MeetingPrepQuerySet(models.QuerySet):
    def for_user(self, user):
        if user.is_superuser:
            return self.all()
        elif user.organization and user.is_active:
            return self.filter(user=user.id)


class MeetingPrepInstance(TimeStampModel):
    user = models.ForeignKey(
        "core.User", on_delete=models.CASCADE, related_name="meeting_preps", null=True
    )
    participants = ArrayField(
        JSONField(max_length=128, default=dict),
        default=list,
        blank=True,
        null=True,
        help_text="Json object of participants",
    )
    event_data = JSONField(max_length=128, default=dict)
    resource_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="The id of the related resource unopinionated",
    )
    resource_type = models.CharField(
        max_length=255, null=True, blank=True, help_text="The class name of the resource"
    )
    invocation = models.PositiveIntegerField(
        default=0,
        help_text="Keeps track of the number of times the meeting instance was called",
    )
    form = models.OneToOneField(
        "slack.OrgCustomSlackFormInstance",
        on_delete=models.CASCADE,
        related_name="meeting_prep_instance",
        null=True,
        blank=True,
    )
    objects = MeetingPrepQuerySet.as_manager()

    class Meta:
        ordering = ["datetime_created"]

    @property
    def title(self):
        return self.event_data["title"]


class UserActivity(models.Model):
    user = models.OneToOneField(
        "core.User", on_delete=models.SET_NULL, related_name="activity", null=True
    )
    clicks = JSONField(default=defaultClickActivity)

    def __str__(self):
        return f"Activity for {self.user.email}"

    @classmethod
    def create_for_existing_users(cls):
        users = User.objects.all()
        for user in users:
            if not hasattr(user, "activity"):
                UserActivity.objects.create(user=user)
                logger.info(f"Created activity model for user {user.email}")
        return

    def increment_untouched_count(self, type, amount=1):
        if type == "meeting":
            self.clicks["meeting"]["untouched"] += amount
        else:
            self.clicks["workflows"]["untouched"] += amount
        return self.save()

    def add_meeting_activity(self, meeting_id):
        from managr.salesforce.models import MeetingWorkflow

        workflow = MeetingWorkflow.objects.get(id=meeting_id)
        main_form = workflow.forms.filter(resource_id=workflow.resource_id).first()
        saved_data = [
            key
            for key in main_form.saved_data.keys()
            if key not in ["meeting_comments", "meeting_type"]
            and (
                key not in main_form.previous_data.keys()
                or main_form.previous_data[key] != main_form.saved_data[key]
            )
        ]
        contact_forms = workflow.forms.filter(
            template__resource="Contact", template__form_type="CREATE"
        )
        no_last_name = [
            form
            for form in contact_forms
            if (not len(form.saved_data) or form.saved_data["LastName"] is None)
        ]
        note_added = False if main_form.saved_data["meeting_comments"] is None else True
        obj = dict(
            source=main_form.update_source if main_form.update_source else "meeting",
            new_attendees=dict(
                saved=len(contact_forms) - len(no_last_name), unsaved=len(no_last_name)
            ),
            fields=saved_data,
            note_added=note_added,
        )
        self.clicks["meeting"]["untouched"] -= 1
        self.clicks["meeting"]["touched"].append(obj)
        return self.save()

    def add_workflow_activity(self, form_id, alert_name):
        from managr.slack.models import OrgCustomSlackFormInstance

        workflow = OrgCustomSlackFormInstance.objects.get(id=form_id)

        saved_data = [
            key
            for key in workflow.saved_data.keys()
            if key not in ["meeting_comments", "meeting_type"]
            and (
                key not in workflow.previous_data.keys()
                or workflow.previous_data[key] != workflow.saved_data[key]
            )
        ]

        note_added = (
            True
            if (
                "meeting_comments" in workflow.saved_data.keys()
                and workflow.saved_data["meeting_comments"] is not None
            )
            else False
        )
        obj = dict(
            source=workflow.update_source,
            name=alert_name,
            fields=saved_data,
            note_added=note_added,
        )
        self.clicks["workflows"]["untouched"] -= 1
        self.clicks["workflows"]["touched"].append(obj)
        return self.save()


class UserForecast(models.Model):
    user = models.OneToOneField(
        "core.User", on_delete=models.CASCADE, related_name="current_forecast"
    )
    state = JSONField(
        default=dict,
        null=True,
    )

    def __str__(self):
        return f"Forecast for {self.user.email}"

    @classmethod
    def create_for_existing_users(cls):
        users = User.objects.all()
        for user in users:
            if not hasattr(user, "current_forecast"):
                UserForecast.objects.create(user=user)
                logger.info(f"Created forecast model for user {user.email}")
        return

    def add_to_state(self, id):
        from managr.opportunity.models import Opportunity

        opp = Opportunity.objects.get(integration_id=id)
        if opp.integration_id not in self.state.keys():
            current_date = str(datetime.now())
            self.state[opp.integration_id] = {
                "date_added": current_date,
                "data": opp.secondary_data,
            }
            self.save()
            return "Opportunity saved to current forecast state"
        return "Opportunity already in current forecast state"

    def remove_from_state(self, id):
        if id in self.state.keys():
            del self.state[id]
            self.save()
            return "Opportunity removed from current forecast state"
        return "Opportunity not in current forecast state"

    def get_current_values(self):
        res = self.user.salesforce_account.adapter_class.get_resource_in_list(
            "Opportunity", list(self.state.keys())
        )
        return res


class NoteTemplateQuerySet(models.QuerySet):
    def for_user(self, user):
        if user.is_superuser:
            return self.all()
        elif user.organization and user.is_active:
            return self.filter(
                Q(user=user.id) | Q(is_shared=True, user__organization=user.organization)
            )


class NoteTemplate(TimeStampModel):
    subject = models.CharField(max_length=255)
    body = models.TextField()
    user = models.ForeignKey("core.User", on_delete=models.CASCADE)
    is_shared = models.BooleanField(default=False)

    objects = NoteTemplateQuerySet.as_manager()

    def __str__(self):
        return f"{self.subject} {self.user}"

    @property
    def as_slack_option(self):
        value = phrase_to_snake_case(self.subject)
        return block_builders.option(self.subject, value)

    class Meta:
        ordering = ["datetime_created"]
