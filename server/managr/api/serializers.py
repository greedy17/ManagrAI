from rest_framework import serializers
from rest_framework.exceptions import ValidationError, PermissionDenied
from .models import Organization, Account, Contact
from managr.lead.models import ActionChoice


from rest_framework import (
    status, filters, permissions
)
from rest_framework.response import Response


class ActionChoiceRefSerializer(serializers.ModelSerializer):
    """
        Read Only Ref Serializer for ActionChoices Tied to an Organization
    """
    class Meta:
        model = ActionChoice
        fields = ('title', 'description',)


class OrganizationRefSerializer(serializers.ModelSerializer):
    """ 
        Read Only Serializer for ref of the organization used for UserSerializer
    """

    class Meta:
        model = Organization
        fields = (
            'id', 'name', 'state',
        )


class AccountRefSerializer(serializers.ModelSerializer):
    """
        Read only serializer for ref of the Account used for the AccountSerializer
    """
    class Meta:
        model = Account
        fields = ('id', 'name', 'organization',)


class OrganizationSerializer(serializers.ModelSerializer):
    """ Only Super Users can create, edit and delete Organizations """

    accounts_ref = AccountRefSerializer(
        many=True, source='accounts', read_only=True)
    action_choices_ref = ActionChoiceRefSerializer(
        source="action_choices", many=True, read_only=True)

    class Meta:
        model = Organization
        fields = (
            'id', 'name', 'state', 'accounts', 'accounts_ref', 'action_choices', 'action_choices_ref',
        )
        read_only_fields = ('accounts', 'action_choices', )


class AccountSerializer(serializers.ModelSerializer):
    """ 
        Serializer for Accounts tied to organization 
        Only Organization Managers can add, update, delete accounts
        Other users can list  
    """

    def to_internal_value(self, data):
        """ Backend Setting organization by default """
        internal_data = super().to_internal_value(data)
        internal_data.update(
            {'organization': self.context['request'].user.organization})

        return internal_data

    class Meta:
        model = Account
        fields = ('id', 'name', 'url', 'type', 'organization', 'state',)
        read_only_fields = ('state', 'organization',)


class ContactSerializer(serializers.ModelSerializer):

    def validate_account(self, value):
        accounts = Account.objects.filter(
            organization=self.context['request'].user.organization)
        if not value in accounts:
            raise PermissionDenied()
        return value

    class Meta:
        model = Contact
        fields = ('id', 'title', 'full_name', 'first_name', 'last_name', 'email',
                  'phone_number_1', 'phone_number_2', 'account',)
        extra_kwargs = {
            'email': {'required': True},
            'phone_number_1': {'required': True},
            'account': {'required': True}
        }
