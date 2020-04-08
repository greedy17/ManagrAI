from rest_framework import serializers
from rest_framework.exceptions import ValidationError
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
        data['organization'] = self.instance.organization.id
        internal_data = super().to_internal_value(data)

        return internal_data

    class Meta:
        model = Account
        fields = ('name', 'url', 'type', 'organization', 'state',)
        read_only_fields = ('state',)


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ('__all__')


class LeadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead
        fields = ('__all__')
