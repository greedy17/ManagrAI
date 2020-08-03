from rest_framework import serializers
from rest_framework.exceptions import ValidationError, PermissionDenied
from .models import Organization, Account, Contact
from managr.lead.models import ActionChoice

from rest_framework import (
    status, filters, permissions
)
from rest_framework.response import Response
from managr.utils.numbers import validate_phone_number


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
        fields = ('id', 'name', 'organization', 'url',)


class OrganizationVerboseSerializer(serializers.ModelSerializer):
    """ Special Serializer that is called when the flag ---verbose=true is sent """

    accounts_ref = AccountRefSerializer(
        many=True, source='accounts', read_only=True)
    action_choices_ref = ActionChoiceRefSerializer(
        source="action_choices", many=True, read_only=True)

    class Meta:
        model = Organization
        fields = (
            'id', 'name', 'state', 'accounts', 'accounts_ref',
            'action_choices', 'action_choices_ref', 'total_amount_closed_contracts', 'avg_amount_closed_contracts'
        )
        read_only_fields = ('accounts', 'action_choices', )


class OrganizationSerializer(serializers.ModelSerializer):
    """ Only Super Users can create, edit and delete Organizations """

    class Meta:
        model = Organization
        fields = (
            'id', 'name', 'state', 'total_amount_closed_contracts', 'avg_amount_closed_contracts'
        )


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
        fields = ('id', 'name', 'url', 'type',
                  'organization', 'state', 'lead_count',)
        read_only_fields = ('state', 'organization',)


class ContactSerializer(serializers.ModelSerializer):

    def validate_account(self, value):
        accounts = Account.objects.filter(
            organization=self.context['request'].user.organization)
        if not value in accounts:
            raise PermissionDenied()
        return value

    def validate_phone_number_1(self, value):
        if value:
            try:
                validate_phone_number(value)
            except ValueError:
                raise ValidationError()
        return value

    def validate_phone_number_2(self, value):
        if value:
            try:
                validate_phone_number(value)
            except ValueError:
                raise ValidationError()
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
