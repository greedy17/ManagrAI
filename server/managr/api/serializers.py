from rest_framework import serializers
from rest_framework.exceptions import ValidationError, PermissionDenied
from .models import Organization, Account, Lead, Contact

from rest_framework import (
    status, filters, permissions
)


from rest_framework.response import Response


class OrganizationRefSerializer(serializers.ModelSerializer):
    """ Read Only Serializer for ref of the organization """

    class Meta:
        model = Organization
        fields = (
            '__all__'
        )


class OrganizationSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        # only superusers can create new organizations
        if not self.context['request'].user.is_superuser:
            raise ValidationError(detail="Not Authorized")

        return Organization.objects.create(**validated_data)

    class Meta:
        model = Organization
        fields = (
            '__all__'
        )


class AccountSerializer(serializers.ModelSerializer):
    """ Serializer for Accounts tied to organization """

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

    def to_internal_value(self, data):
        """ Backend Setting organization by default """
        internal_data = super().to_internal_value(data)
        internal_data.update(
            {'organization': self.context['request'].user.organization})

        return internal_data

    def validate_account(self, value):
        accounts = Account.objects.filter(
            organization=self.context['request'].user.organization)
        if not value in accounts:
            raise PermissionDenied()
        return value

    class Meta:
        model = Contact
        fields = ('id', 'full_name', 'first_name', 'last_name', 'email',
                  'phone_number_1', 'phone_number_2', 'account', 'organization',)
        extra_kwargs = {
            'email': {'required': True},
            'phone_number_1': {'required': True},
            'account': {'required': True}
        }
        read_only_fields = ('organization',)


class LeadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead
        fields = ('__all__')
