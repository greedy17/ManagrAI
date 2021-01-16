from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import login

from rest_framework import serializers
from rest_framework.authtoken.models import Token

from managr.organization.serializers import (
    OrganizationSerializer,
    AccountSerializer,
)
from managr.organization.models import Organization
from managr.slack.serializers import UserSlackIntegrationSerializer

from .models import (
    User,
    EmailAuthAccount,
)


class EmailAuthAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailAuthAccount
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


class UserSerializer(serializers.ModelSerializer):
    """UserSerializer to update user fields, only managers with admin access and
    superusers can update email"""

    organization_ref = OrganizationSerializer(
        many=False, source="organization", read_only=True
    )
    accounts_ref = AccountSerializer(
        many=True, source="organization.accounts", read_only=True
    )
    email_auth_account_ref = EmailAuthAccountSerializer(
        source="email_auth_account", read_only=True
    )

    slack_ref = UserSlackIntegrationSerializer(
        source="slack_integration", read_only=True
    )

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
            "accounts_ref",
            # user info
            "is_active",
            "is_invited",
            "is_staff",
            "is_admin",
            "is_superuser",
            "user_level",
            "profile_photo",
            # integrations
            "email_auth_account",
            "email_auth_account_ref",
            "salesforce_account",
            "slack_ref",
            "zoom_account",
        )

    read_only_fields = (
        "email",
        "organization",
        "type",
        "is_active",
        "is_invited",
        "full_name",
        "email_auth_account",
        "is_staff",
        "is_admin",
        "is_superuser",
    )


class UserRegistrationSerializer(serializers.ModelSerializer):
    # TODO: Add organization_name

    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "email",
            "password",
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
        org_name = validated_data.get('organization_name')
        Organization.objects.create(name=org_name)

        return User.objects.create_user(**validated_data)


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
        """
        Log-in user and append authentication token to serialized response.
        """
        login(request, user, backend="django.contrib.auth.backends.ModelBackend")
        auth_token, _ = Token.objects.get_or_create(user=user)
        serializer = UserSerializer(user, context={"request": request})
        response_data = serializer.data
        response_data["token"] = auth_token.key
        return response_data


class UserInvitationSerializer(serializers.ModelSerializer):
    """
    Serializer for Inviting users to the platform.
    Only Managers can invite users, and only to their organization
    """

    organization_ref = OrganizationSerializer(
        many=False, source="organization", read_only=True
    )

    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "email",
            "organization",
            "organization_ref",
            "user_level",
        )
        extra_kwargs = {
            "email": {"required": True},
            "organization": {"required": True},
        }
        read_only_fields = ("organization_ref",)


""" 
class NotificationSelectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationSelection
        fields = ("id", "option", "user", "value")


class NotificationOptionSerializer(serializers.ModelSerializer):
    value = serializers.SerializerMethodField("get_value")

    class Meta:
        model = NotificationOption
        fields = (
            "id",
            "title",
            "description",
            "default_value",
            "notification_type",
            "resource",
            "key",
            "value",
        )

    def get_value(self, instance):
        selection = instance.get_value(self.context["request"].user)
        serializer = NotificationSelectionSerializer(selection)

        return serializer.data
 """
