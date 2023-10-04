from datetime import datetime
import pytz
from django.utils import timezone
from django.db import IntegrityError
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import login
from rest_framework import serializers
import managr.core.constants as core_consts
from managr.comms.serializers import SearchSerializer
from managr.organization.serializers import OrganizationSerializer
from managr.salesforce.serializers import SalesforceAuthSerializer
from managr.organization.models import Organization
from managr.slack.serializers import (
    UserSlackIntegrationSerializer,
    UserFrontEndSlackIntegrationSerializer,
)
from managr.zoom.serializers import ZoomAuthSerializer
from managr.hubspot.serializers import HubspotAuthAccountSerializer
from .models import (
    User,
    NylasAuthAccount,
    NoteTemplate,
    Message,
    Conversation,
    Report,
)


class NylasAuthAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = NylasAuthAccount
        fields = "__all__"


class UserRefSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
        )


class UserClientSerializer(serializers.ModelSerializer):
    organization_ref = OrganizationSerializer(many=False, source="organization", read_only=True)
    salesforce_account_ref = SalesforceAuthSerializer(source="salesforce_account", read_only=True)
    hubspot_account_ref = HubspotAuthAccountSerializer(source="hubspot_account", read_only=True)
    slack_ref = UserSlackIntegrationSerializer(source="slack_integration", read_only=True)
    slack_account = UserFrontEndSlackIntegrationSerializer(
        source="slack_integration", read_only=True
    )
    activation_link_ref = serializers.SerializerMethodField("get_activation_link")

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "full_name",
            "first_name",
            "last_name",
            "organization",
            "organization_ref",
            "is_active",
            "is_admin",
            "is_superuser",
            "user_level",
            "role",
            "has_nylas_integration",
            "has_hubspot_integration",
            "has_salesloft_integration",
            "has_gong_integration",
            "has_outreach_integration",
            "has_zoom_integration",
            "has_salesforce_integration",
            "salesforce_account_ref",
            "slack_ref",
            "slack_account",
            "hubspot_account_ref",
            "timezone",
            "onboarding",
            "team",
            "is_team_lead",
            "crm",
            "meta_data",
            "activation_link_ref",
            "writing_style",
        )

    def get_activation_link(self, instance):
        return instance.activation_link


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = "__all__"


class ConversationSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True)

    class Meta:
        model = Conversation
        fields = "__all__"


class UserSerializer(serializers.ModelSerializer):
    """UserSerializer to update user fields, only managers with admin access and
    superusers can update email"""

    organization_ref = OrganizationSerializer(many=False, source="organization", read_only=True)
    nylas_ref = NylasAuthAccountSerializer(source="nylas", read_only=True)
    salesforce_account_ref = SalesforceAuthSerializer(source="salesforce_account", read_only=True)
    hubspot_account_ref = HubspotAuthAccountSerializer(source="hubspot_account", read_only=True)
    slack_ref = UserSlackIntegrationSerializer(source="slack_integration", read_only=True)
    slack_account = UserFrontEndSlackIntegrationSerializer(
        source="slack_integration", read_only=True
    )
    zoom_ref = ZoomAuthSerializer(source="zoom_account", read_only=True)
    activated_template_ref = serializers.SerializerMethodField("get_alert_template_refs")
    activation_link_ref = serializers.SerializerMethodField("get_activation_link")

    class Meta:
        model = User
        fields = (
            "id",
            # personal info
            "email",
            "full_name",
            "first_name",
            "last_name",
            # org info
            "organization",
            "organization_ref",
            # user info
            "is_active",
            "is_invited",
            "is_staff",
            "is_admin",
            "is_superuser",
            "user_level",
            "profile_photo",
            "role",
            "activation_link_ref",
            # integrations
            "nylas",
            "nylas_ref",
            "salesforce_account",
            "salesforce_account_ref",
            "hubspot_account",
            "hubspot_account_ref",
            "has_hubspot_integration",
            "slack_ref",
            "slack_account",
            "zoom_account",
            "zoom_ref",
            "salesloft_account",
            "has_salesloft_integration",
            "gong_account",
            "has_gong_integration",
            "outreach_account",
            "has_outreach_integration",
            "has_zoom_integration",
            "has_salesforce_integration",
            "timezone",
            "activated_template_ref",
            "onboarding",
            "team",
            "is_team_lead",
            "crm",
            "writing_style",
        )

    read_only_fields = (
        "email",
        "organization",
        "type",
        "is_active",
        "is_invited",
        "full_name",
        "nylas_auth_account",
        "is_staff",
        "is_admin",
        "is_superuser",
    )

    def get_alert_template_refs(self, instance):
        from managr.alerts.models import AlertTemplate

        templates = AlertTemplate.objects.for_user(instance).values_list("title", flat=True)
        return templates

    def get_activation_link(self, instance):
        return instance.activation_link


class UserRegistrationSerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(required=True)
    role = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "email",
            "password",
            "organization_name",
            "role",
            "timezone",
        )
        extra_kwargs = {
            "first_name": {"required": True},
            "last_name": {"required": True},
        }

    def validate(self, data):
        password = data.get("password")
        validate_password(password)

        return data

    def create(self, validated_data):
        # Pop off organization name and create an organization
        # TODO 2021-01-16 William: Users from the same organization should be able
        #      to register "trials" separately, but be tied to the same org in the back
        #      end. We will do this by looking at the domain name of the email.
        org_name = validated_data.pop("organization_name")
        try:
            org_check = Organization.objects.get(name__iexact=org_name)
            if org_check:
                raise IntegrityError("Organization already exists")
            return User.objects.create_user(
                organization=org_check, user_level=core_consts.ACCOUNT_TYPE_REP, **validated_data
            )
        except Organization.DoesNotExist:
            org = Organization.objects.create(name=org_name)
            return User.objects.create_admin_user(organization=org, **validated_data)
        except IntegrityError:
            raise IntegrityError("Organization already exists")


class UserAdminRegistrationSerializer(serializers.ModelSerializer):
    activation_link_ref = serializers.SerializerMethodField("get_activation_link")
    organization_name = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "email",
            "organization_name",
            "role",
            "activation_link_ref",
        )
        extra_kwargs = {
            "first_name": {"required": True},
            "last_name": {"required": True},
        }

    def get_activation_link(self, instance):
        return instance.activation_link

    def create(self, validated_data):
        org_name = validated_data.pop("organization_name")
        try:
            org = Organization.objects.create(name=org_name)
            return User.objects.create_admin_user(organization=org, **validated_data)
        except IntegrityError:
            raise IntegrityError("Organization already exists")


class UserLoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(allow_blank=False, required=True)
    password = serializers.CharField(allow_blank=False, required=True)

    class Meta:
        model = User
        fields = (
            "email",
            "password",
        )

    def validate_email(self, value):
        """Emails are always stored and compared in lowercase."""
        return value.lower()

    @staticmethod
    def login(user, request):
        from managr.api.models import ManagrToken

        """
        Log-in user and append authentication token to serialized response.
        """
        login(request, user, backend="django.contrib.auth.backends.ModelBackend")
        auth_token, _ = ManagrToken.objects.get_or_create(user=user)
        serializer = UserClientSerializer(user, context={"request": request})
        response_data = serializer.data
        response_data["token"] = auth_token.key
        return response_data


class UserSSOLoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(allow_blank=False, required=True)

    class Meta:
        model = User
        fields = ("email",)

    def validate_email(self, value):
        """Emails are always stored and compared in lowercase."""
        return value.lower()

    def get_password(self, instance):
        if instance:
            return instance.password
        return None

    @staticmethod
    def login(user, request):
        """
        Log-in user and append authentication token to serialized response.
        """
        login(request, user, backend="managr.core.custom_backends.SSOBackend")
        serializer = UserSerializer(user, context={"request": request})
        response_data = serializer.data
        return response_data


class UserInvitationSerializer(serializers.ModelSerializer):
    """
    Serializer for Inviting users to the platform.
    Only Managers can invite users, and only to their organization
    """

    organization_ref = OrganizationSerializer(many=False, source="organization", read_only=True)

    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "email",
            "organization",
            "organization_ref",
            "user_level",
            "role",
            "team",
            "make_team_lead",
        )
        extra_kwargs = {
            "email": {"required": True},
            "organization": {"required": True},
        }
        read_only_fields = ("organization_ref",)


class NoteTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = NoteTemplate
        fields = ("subject", "body", "user", "is_shared", "id")


class UserTrialSerializer(serializers.ModelSerializer):
    days_active = serializers.SerializerMethodField("get_days_active")
    updates_this_month = serializers.SerializerMethodField("get_updates_made_this_month")
    total_updates = serializers.SerializerMethodField("get_total_updates_made")
    searches_ref = serializers.SerializerMethodField("get_searches")

    class Meta:
        model = User
        fields = (
            "email",
            "datetime_created",
            "days_active",
            "total_updates",
            "updates_this_month",
            "crm",
            "salesforce_account",
            "outreach_account",
            "hubspot_account",
            "gong_account",
            "salesloft_account",
            "nylas",
            "slack_integration",
            "zoom_account",
            "meta_data",
            "searches_ref",
        )

    def get_days_active(self, instance):
        today = datetime.today().astimezone(pytz.UTC)
        return (today - instance.datetime_created).days

    def get_updates_made_this_month(self, instance):
        from managr.slack.models import OrgCustomSlackFormInstance

        today = datetime.today().astimezone(pytz.UTC)
        thirty_past = today - timezone.timedelta(30)
        updates = OrgCustomSlackFormInstance.objects.for_user(instance).filter(
            is_submitted=True, datetime_created__range=(thirty_past, today)
        )
        return len(updates)

    def get_total_updates_made(self, instance):
        from managr.slack.models import OrgCustomSlackFormInstance

        updates = OrgCustomSlackFormInstance.objects.for_user(instance).filter(is_submitted=True)
        return len(updates)

    def get_searches(self, instance):
        from managr.comms.models import Search

        searches = Search.objects.filter(user=instance)
        serialized = SearchSerializer(searches, many=True).data
        return serialized


class ReportSerializer(serializers.ModelSerializer):
    share_url = serializers.SerializerMethodField("get_share_url")

    class Meta:
        model = Report
        fields = ("title", "user", "main_image", "meta_data", "share_url", "id", "datetime_created")

    def get_share_url(self, instance):
        url = instance.generate_url()
        return url
