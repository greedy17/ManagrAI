from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import login

from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.authtoken.models import Token

from .models import User, STATE_ACTIVE, STATE_INACTIVE, STATE_INVITED
from managr.api.serializers import OrganizationRefSerializer, AccountRefSerializer
from managr.api.models import Account


class UserSerializer(serializers.ModelSerializer):
    """ UserSerializer to update user fields, only managers with admin access and superusers can update email """

    organization_ref = OrganizationRefSerializer(
        many=False, source='organization', read_only=True)
    accounts_ref = AccountRefSerializer(
        many=True, source='organization.accounts', read_only=True)

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'first_name',
            'last_name',
            'organization',
            'organization_ref',
            'accounts_ref',
            'type',
            'is_active',
            'is_invited',
            'full_name',


        )
    read_only_fields = ('email', 'organization', 'type',
                        'is_active', 'is_invited', 'full_name',)


class UserLoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(allow_blank=False, required=True)
    password = serializers.CharField(allow_blank=False, required=True)

    class Meta:
        model = User
        fields = (
            'email',
            'password',
        )

    def validate_email(self, value):
        """Emails are always stored and compared in lowercase."""
        return value.lower()

    @staticmethod
    def login(user, request):
        """
        Log-in user and append authentication token to serialized response.
        """
        login(
            request, user,
            backend='django.contrib.auth.backends.ModelBackend'
        )
        auth_token, token_created = Token.objects.get_or_create(user=user)
        serializer = UserSerializer(user, context={'request': request})
        response_data = serializer.data
        response_data['token'] = auth_token.key
        return response_data


class UserInvitationSerializer(serializers.ModelSerializer):
    """
        Serializer for Inviting users to the platform. 
        Only Managers can invite users, and only to their organization

    """
    organization_ref = OrganizationRefSerializer(
        many=False, source='organization', read_only=True)

    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'email',
            'organization',
            'organization_ref',
            'type',
        )
        extra_kwargs = {
            'email': {'required': True},
            'organization': {'required': True},
        }
        read_only_fields = ('organization_ref',)
