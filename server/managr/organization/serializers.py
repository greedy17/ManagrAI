import json
from rest_framework import serializers
from rest_framework.exceptions import ValidationError, PermissionDenied
from .models import Organization, Account, Contact, Stage
from managr.lead.models import ActionChoice

from rest_framework import status, filters, permissions
from rest_framework.response import Response
from managr.utils.numbers import validate_phone_number


class ActionChoiceRefSerializer(serializers.ModelSerializer):
    """
        Read Only Ref Serializer for ActionChoices Tied to an Organization
    """

    class Meta:
        model = ActionChoice
        fields = (
            "title",
            "description",
        )


class OrganizationRefSerializer(serializers.ModelSerializer):
    """
        Read Only Serializer for ref of the organization
    """

    class Meta:
        model = Organization
        fields = (
            "id",
            "name",
            "photo",
            "state",
            "org_token",
            "is_externalsyncenabled",
        )


class StageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stage
        fields = "__all__"


class AccountRefSerializer(serializers.ModelSerializer):
    """
        Read only serializer for ref of the Account
        used for the AccountSerializer
    """

    class Meta:
        model = Account
        fields = ("id", "name", "organization", "url", "logo")


class OrganizationVerboseSerializer(serializers.ModelSerializer):
    """ Special Serializer that is called when the flag ---verbose=true is sent """

    accounts_ref = AccountRefSerializer(many=True, source="accounts", read_only=True)
    action_choices_ref = ActionChoiceRefSerializer(
        source="action_choices", many=True, read_only=True
    )

    class Meta:
        model = Organization
        fields = (
            "id",
            "name",
            "photo",
            "state",
            "accounts",
            "accounts_ref",
            "action_choices",
            "action_choices_ref",
            "total_amount_closed_contracts",
            "avg_amount_closed_contracts",
            "is_externalsyncenabled",
        )
        read_only_fields = (
            "accounts",
            "action_choices",
        )


class OrganizationSerializer(serializers.ModelSerializer):
    """ Only Super Users can create, edit and delete Organizations """

    class Meta:
        model = Organization
        fields = (
            "id",
            "name",
            "photo",
            "state",
            "total_amount_closed_contracts",
            "avg_amount_closed_contracts",
            "is_externalsyncenabled",
        )


class AccountSerializer(serializers.ModelSerializer):
    """ 
        Serializer for Accounts tied to organization
        Only Organization Managers can add, update, delete accounts
        Other users can list
    """

    lead_count = serializers.SerializerMethodField()

    def to_internal_value(self, data):
        """ Backend Setting organization by default """
        internal_data = super().to_internal_value(data)
        internal_data.update(
            {"organization": self.context["request"].user.organization}
        )

        return internal_data

    class Meta:
        model = Account
        fields = (
            "id",
            "name",
            "url",
            "type",
            "organization",
            "state",
            "lead_count",
        )
        read_only_fields = (
            "state",
            "organization",
        )

    def get_lead_count(self, instance):
        request = self.context.get("request")
        by_params = request.GET.get("by_params", None)

        if by_params:
            params = json.loads(by_params)
            only_unclaimed = params.get("only_unclaimed", False)
            representatives = params.get("representatives", [])
            search_term = params.get("search_term", "")

            # if search term and unclaimed
            if search_term and only_unclaimed:
                return instance.leads.filter(
                    title__icontains=search_term, claimed_by__isnull=True
                ).count()

            # if search term and representatives
            if search_term and len(representatives):
                return instance.leads.filter(
                    title__icontains=search_term, claimed_by__in=representatives
                ).count()

            # if search only
            if search_term:
                return instance.leads.filter(title__icontains=search_term).count()

            # if unclaimed
            if only_unclaimed:
                return instance.leads.filter(claimed_by__isnull=True).count()

            # if representatives
            if len(representatives):
                return instance.leads.filter(claimed_by__in=representatives).count()

        return instance.leads.count()


class ContactSerializer(serializers.ModelSerializer):
    def validate_account(self, value):
        accounts = Account.objects.filter(
            organization=self.context["request"].user.organization
        )
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
        fields = (
            "id",
            "title",
            "full_name",
            "first_name",
            "last_name",
            "email",
            "phone_number_1",
            "phone_number_2",
            "account",
        )
        extra_kwargs = {
            "email": {"required": True},
            "phone_number_1": {"required": True},
            "account": {"required": True},
        }
