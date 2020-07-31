from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import login

from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.authtoken.models import Token

from managr.lead.models import Lead
from managr.organization.serializers import (
    OrganizationRefSerializer,
    AccountRefSerializer,
)
from managr.organization.models import Account

from .nylas import emails as nylas_emails
from .models import User, EmailAuthAccount
from .models import EmailTemplate


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
    """ UserSerializer to update user fields, only managers with admin access and
    superusers can update email """

    organization_ref = OrganizationRefSerializer(
        many=False, source="organization", read_only=True
    )
    accounts_ref = AccountRefSerializer(
        many=True, source="organization.accounts", read_only=True
    )
    email_auth_account_ref = EmailAuthAccountSerializer(
        source="email_auth_account", read_only=True
    )

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "organization",
            "organization_ref",
            "accounts_ref",
            "type",
            "is_active",
            "is_invited",
            "is_serviceaccount",
            "is_staff",
            "full_name",
            "email_auth_link",
            "email_auth_account",
            "email_auth_account_ref",
            "quota",
            "upside",
            "commit",
            "unviewed_notifications_count",
        )

    read_only_fields = (
        "email",
        "organization",
        "type",
        "is_active",
        "is_invited",
        "full_name",
        "email_auth_account",
        "is_serviceaccount",
        "is_staff"
    )


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
        auth_token, token_created = Token.objects.get_or_create(user=user)
        serializer = UserSerializer(user, context={"request": request})
        response_data = serializer.data
        response_data["token"] = auth_token.key
        return response_data


class UserInvitationSerializer(serializers.ModelSerializer):
    """
        Serializer for Inviting users to the platform.
        Only Managers can invite users, and only to their organization
    """

    organization_ref = OrganizationRefSerializer(
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
            "type",
        )
        extra_kwargs = {
            "email": {"required": True},
            "organization": {"required": True},
        }
        read_only_fields = ("organization_ref",)


class ContactDictField(serializers.DictField):
    child = serializers.CharField()


class EmailSerializer(serializers.Serializer):
    """Serializer for verifying Emails to be sent via Nylas."""

    subject = serializers.CharField(allow_blank=False, required=True)
    body = serializers.CharField(allow_blank=False, required=True)

    lead = serializers.UUIDField(required=True)

    to = serializers.ListField(
        child=ContactDictField(), required=True, allow_empty=False, allow_null=False,
    )
    cc = serializers.ListField(
        child=ContactDictField(), required=False, allow_null=True
    )
    bcc = serializers.ListField(
        child=ContactDictField(), required=False, allow_null=True
    )

    reply_to_message_id = serializers.CharField(
        allow_blank=True, required=False)
    file_ids = serializers.ListField(
        child=serializers.CharField(), allow_empty=True, required=False
    )
    variables = serializers.DictField(
        child=serializers.CharField(allow_blank=True), allow_empty=True, required=False
    )

    def validate_lead(self, value):
        user = self.context["request"].user
        try:
            lead = Lead.objects.for_user(user).get(id=value)
        except Lead.DoesNotExist:
            raise ValidationError(
                "The given lead ID does not exist or you do not have permission to modify it."
            )
        return lead

    def send(self):
        """Send the email via Nylas."""
        sender = self.context["request"].user
        response = nylas_emails.send_new_email(sender, **self.validated_data)
        return response

    def preview(self):
        """Render the email to be sent and return data to preview the result."""
        sender = self.context["request"].user
        return nylas_emails.generate_preview_email_data(sender, **self.validated_data,)


class EmailTemplateSerializer(serializers.ModelSerializer):
    """Serializer for Email Templates."""

    class Meta:
        model = EmailTemplate
        fields = (
            "id",
            "name",
            "subject",
            "body_html",
        )

    def create(self, validated_data):
        # Add the requesting user as the template user.
        user = self.context["request"].user
        validated_data["user"] = user
        request = super().create(validated_data)
        return request
