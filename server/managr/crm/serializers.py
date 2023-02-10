import datetime
from dateutil import parser
from rest_framework import serializers

from .models import BaseOpportunity, BaseAccount, BaseContact, ObjectField
from managr.organization.models import Organization
from managr.core.models import User


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


class BaseAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = BaseAccount
        fields = (
            "id",
            "name",
            "organization",
            "integration_id",
            "integration_source",
            "imported_by",
            "owner",
            "external_owner",
            "secondary_data",
        )

    def to_internal_value(self, data):
        imported_by = data.get("imported_by")
        org = Organization.objects.get(users__id=imported_by)
        user = org.users.all().get(id=imported_by)
        data.update({"organization": org.id})
        data.update({"owner": user.id})
        # remove contacts from validation
        internal_data = super().to_internal_value(data)
        return internal_data


class BaseContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = BaseContact
        fields = (
            "id",
            "email",
            "account",
            "external_owner",
            "external_account",
            "owner",
            "integration_source",
            "integration_id",
            "imported_by",
            "secondary_data",
        )
        extra_kwargs = {}

    def to_internal_value(self, data):
        imported_by = data.get("imported_by")
        owner = data.get("external_owner", None)
        account = data.get("external_account", None)
        if not data.get("external_account", None):
            data.update({"external_account": "N/A"})
        if not data.get("external_owner", None):
            data.update({"external_owner": "N/A"})
        if not data.get("email", None):
            data.update({"email": ""})
        if owner:
            user = User.objects.get(id=imported_by)
            data.update({"owner": user.id})
        if account:
            acct = BaseAccount.objects.filter(integration_id=account, owner=imported_by).first()
            acct = acct.id if acct else None
            data.update({"account": acct})

        # remove contacts from validation
        internal_data = super().to_internal_value(data)
        return internal_data


class BaseOpportunitySerializer(serializers.ModelSerializer):
    owner_ref = UserRefSerializer(source="owner", required=False)
    account_ref = BaseAccountSerializer(source="account", required=False)

    class Meta:
        model = BaseOpportunity
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
            "external_account",
            "external_owner",
            "imported_by",
            "contacts",
            "secondary_data",
            "last_stage_update",
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
        close_date = data.get("close_date")
        new_date = parser.parse(close_date).date()
        data.update({"close_date": new_date})
        account = data.get("external_account", None)
        if not data.get("external_account", None):
            data.update({"external_account": "N/A"})
        if not data.get("external_owner", None):
            data.update({"external_owner": "N/A"})
        if owner:
            user = User.objects.get(id=imported_by)
            data.update({"owner": user.id})
        if account:
            acct = BaseAccount.objects.filter(
                integration_id=account, organization__users__id=imported_by
            ).first()
            acct = acct.id if acct else acct
            data.update({"account": acct})
        # remove contacts from validation

        contacts = data.pop("contacts", [])
        contacts = BaseContact.objects.filter(integration_id__in=contacts).values_list(
            "id", flat=True
        )
        data.update({"contacts": contacts})
        internal_data = super().to_internal_value(data)
        return internal_data


class ObjectFieldSerializer(serializers.ModelSerializer):
    options_ref = serializers.SerializerMethodField("get_options_ref")

    class Meta:
        model = ObjectField
        fields = (
            "id",
            "user",
            "crm_object",
            "api_name",
            "createable",
            "updateable",
            "data_type",
            "data_type_details",
            "display_value",
            "label",
            "length",
            "reference",
            "reference_to_infos",
            "relationship_name",
            "options",
            "options_ref",
            "integration_source",
            "integration_id",
            "is_public",
            "imported_by",
            "filterable",
            "reference_display_label",
        )

    def get_options_ref(self, instance, *args, **kwargs):
        if instance.api_name == "dealstage":
            options = []
            for pipeline in instance.options[0].values():
                options.append(pipeline["stages"])
        else:
            options = instance.options
        return options
