import datetime
from dateutil import parser
from rest_framework import serializers

from managr.crm.models import BaseAccount, BaseContact, BaseOpportunity

from .models import HubspotAuthAccount, Company, HubspotContact, Deal, HObjectField
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


class HubspotAuthAccountSerializer(serializers.ModelSerializer):
    extra_pipeline_fields_ref = serializers.SerializerMethodField("get_extra_pipeline_fields")

    class Meta:
        model = HubspotAuthAccount
        fields = (
            "id",
            "user",
            "access_token",
            "refresh_token",
            "hubspot_id",
            "hubspot_app_id",
            "hobjects",
            "custom_objects",
            "extra_pipeline_fields_ref",
        )

    def get_extra_pipeline_fields(self, instance):
        extra_fields_obj = {}
        for field in instance.extra_pipeline_fields:
            field_split = field.split(",")
            extra_fields_obj[field_split[0]] = field_split[1:]
        return extra_fields_obj


class CompanySerializer(serializers.ModelSerializer):
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
        owner = data.get("external_owner", None)
        if not owner:
            data.update({"external_owner": ""})
        if owner:
            hs_account = (
                HubspotAuthAccount.objects.filter(hubspot_id=owner).select_related("user").first()
            )
            user = hs_account.user.id if hs_account else hs_account
            data.update({"owner": user})
        org = Organization.objects.get(users__id=imported_by)
        data.update({"organization": org.id})
        # remove contacts from validation
        internal_data = super().to_internal_value(data)
        return internal_data


class HubspotContactSerializer(serializers.ModelSerializer):
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
        company = data.get("external_account", None)
        if not data.get("external_account", None):
            data.update({"external_account": ""})
        if not data.get("external_owner", None):
            data.update({"external_owner": ""})
        if not data.get("email", None):
            data.update({"email": ""})
        if owner:
            hs_account = (
                HubspotAuthAccount.objects.filter(hubspot_id=owner).select_related("user").first()
            )
            user = hs_account.user.id if hs_account else imported_by
            data.update({"owner": user})
        if company:
            acct = Company.objects.filter(
                integration_id=company, organization__users__id=imported_by
            ).first()
            acct = acct.id if acct else acct
            data.update({"account": acct})

        # remove contacts from validation
        internal_data = super().to_internal_value(data)
        return internal_data


class DealSerializer(serializers.ModelSerializer):
    account_ref = CompanySerializer(source="company", required=False)
    owner_ref = UserRefSerializer(source="owner", required=False)

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
            "stage",
            "owner",
            "external_account",
            "external_owner",
            "imported_by",
            "contacts",
            "is_stale",
            "secondary_data",
            "owner_ref",
            "account_ref",
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
        close_date = data.get("close_date", None)
        if close_date:
            try:
                new_date = parser.parse(close_date).date()
                data.update({"close_date": new_date})
            except Exception:
                print(f"There was an error parsing close date for {data}")
        account = data.get("external_account", None)
        if not data.get("external_account", None):
            data.update({"external_account": ""})
        if not data.get("external_owner", None):
            data.update({"external_owner": ""})
        if owner:
            hs_account = (
                HubspotAuthAccount.objects.filter(hubspot_id=owner).select_related("user").first()
            )
            user = hs_account.user.id if hs_account else hs_account
            data.update({"owner": user})
        if account:
            acct = BaseAccount.objects.filter(
                integration_id=account, organization__users__id=imported_by
            ).first()
            acct = acct.id if acct else acct
            data.update({"account": acct})
        # remove contacts from validation

        contacts = data.pop("contacts", [])
        contacts = HubspotContact.objects.filter(integration_id__in=contacts).values_list(
            "id", flat=True
        )
        data.update({"contacts": contacts})
        internal_data = super().to_internal_value(data)
        return internal_data


class HObjectFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = HObjectField
        fields = (
            "hubspot_account",
            "hubspot_object",
            "name",
            "label",
            "type",
            "field_type",
            "calculated",
            "external_options",
            "has_unique_value",
            "hidden",
            "display_value",
            "group_name",
            "options",
            "display_order",
            "hubspot_defined",
            "modification_metadata",
            "form_field",
            "integration_source",
            "integration_id",
            "imported_by",
        )
