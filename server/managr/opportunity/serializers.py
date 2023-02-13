from datetime import datetime
from collections import OrderedDict


from django.core.paginator import Paginator


from rest_framework import serializers
from rest_framework.exceptions import ValidationError, PermissionDenied
from rest_framework import status, filters, permissions
from rest_framework.response import Response

from managr.organization.models import Stage, Account, Contact
from managr.organization.serializers import (
    AccountSerializer,
    ContactSerializer,
    StageSerializer,
)
from managr.crm.serializers import BaseAccountSerializer
from managr.salesforce.models import SalesforceAuthAccount
from managr.salesforce.exceptions import ResourceAlreadyImported
from managr.organization import constants as org_consts
from managr.core.models import User, Notification
from . import constants as opp_consts


from .models import Opportunity, Lead
from . import constants as opp_consts


class UserRefSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "full_name",
            "first_name",
            "last_name",
            "profile_photo",
        )

    def get_full_name(self, instance):
        return f"{instance.first_name} {instance.last_name}"


class OpportunitySerializer(serializers.ModelSerializer):
    account_ref = AccountSerializer(source="account", required=False)
    owner_ref = UserRefSerializer(source="owner", required=False)

    class Meta:
        model = Opportunity
        fields = (
            "id",
            "integration_id",
            "integration_source",
            "name",
            "amount",
            "close_date",
            "forecast_category",
            "account",
            "account_ref",
            "stage",
            "owner",
            "owner_ref",
            "last_stage_update",
            "last_activity_date",
            "external_account",
            "external_owner",
            "imported_by",
            "contacts",
            "is_stale",
            "secondary_data",
        )

    def _format_date_time_from_api(self, d):
        if d and len(d) > 10:
            return datetime.strptime(d, "%Y-%m-%dT%H:%M:%S.%f%z")
        elif d and len(d) <= 10:
            return datetime.strptime(d, "%Y-%m-%d")
        return None

    def to_internal_value(self, data):
        imported_by = data.get("imported_by")
        owner = data.get("external_owner", None)
        account = data.get("external_account", None)
        if not data.get("external_account", None):
            data.update({"external_account": ""})
        if not data.get("external_owner", None):
            data.update({"external_owner": ""})
        if owner:
            sf_account = (
                SalesforceAuthAccount.objects.filter(salesforce_id=owner)
                .select_related("user")
                .first()
            )
            user = sf_account.user.id if sf_account else sf_account
            data.update({"owner": user})
        if account:
            acct = Account.objects.filter(
                integration_id=account, organization__users__id=imported_by
            ).first()
            acct = acct.id if acct else acct
            data.update({"account": acct})
        if data.get("last_activity_date"):
            data["last_activity_date"] = self._format_date_time_from_api(data["last_activity_date"])
        # remove contacts from validation

        contacts = data.pop("contacts", [])
        contacts = Contact.objects.filter(integration_id__in=contacts).values_list("id", flat=True)
        data.update({"contacts": contacts})
        internal_data = super().to_internal_value(data)
        return internal_data

    def create(self, validated_data):
        try:
            return super().create(validated_data)
        except ResourceAlreadyImported:
            pass

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)


class LeadSerializer(serializers.ModelSerializer):
    """
    Serializer for Accounts tied to organization
    Only Organization Managers can add, update, delete accounts
    Other users can list
    """

    # account_ref = BaseAccountSerializer(source="account", required=False)
    owner_ref = UserRefSerializer(source="owner", required=False)

    class Meta:
        model = Lead
        fields = (
            "id",
            "name",
            "integration_id",
            "integration_source",
            "imported_by",
            "owner",
            "owner_ref",
            "secondary_data",
            "email",
        )

    def to_internal_value(self, data):
        owner = data.get("external_owner", None)
        if data.get("email", None) in ["", None]:
            data.update({"email": ""})
        if not data.get("external_owner", None):
            data.update({"external_owner": ""})
        imported_by = data.get("imported_by", None)
        if owner:
            sf_account = (
                SalesforceAuthAccount.objects.filter(salesforce_id=owner)
                .select_related("user")
                .first()
            )
            user = sf_account.user.id if sf_account else imported_by
            data.update({"owner": user})
        # remove contacts from validation
        internal_data = super().to_internal_value(data)
        return internal_data
