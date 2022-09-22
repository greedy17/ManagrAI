import datetime
from dateutil import parser
from rest_framework import serializers

from .models import BaseOpportunity, BaseAccount, BaseContact, ObjectField
from managr.organization.models import Organization


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


class BaseContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = BaseContact
        fields = (
            "id",
            "email",
            "company",
            "external_owner",
            "external_company",
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
        company = data.get("external_company", None)
        if not data.get("external_company", None):
            data.update({"external_company": ""})
        if not data.get("external_owner", None):
            data.update({"external_owner": ""})
        if not data.get("email", None):
            data.update({"email": ""})
        if owner:
            hs_account = (
                HubspotAuthAccount.objects.filter(hubspot_id=owner).select_related("user").first()
            )
            user = hs_account.user.id if hs_account else hs_account
            data.update({"owner": user})
        if company:
            acct = Company.objects.filter(
                integration_id=company, organization__users__id=imported_by
            ).first()
            acct = acct.id if acct else acct
            data.update({"company": acct})

        # remove contacts from validation
        internal_data = super().to_internal_value(data)
        return internal_data


class BaseOpportunitySerializer(serializers.ModelSerializer):
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
            "company",
            "stage",
            "owner",
            "external_company",
            "external_owner",
            "imported_by",
            "contacts",
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
        close_date = data.get("close_date")
        new_date = parser.parse(close_date).date()
        data.update({"close_date": new_date})
        company = data.get("external_company", None)
        if not data.get("external_company", None):
            data.update({"external_company": ""})
        if not data.get("external_owner", None):
            data.update({"external_owner": ""})
        if owner:
            hs_account = (
                HubspotAuthAccount.objects.filter(hubspot_id=owner).select_related("user").first()
            )
            user = hs_account.user.id if hs_account else hs_account
            data.update({"owner": user})
        if company:
            acct = Company.objects.filter(
                integration_id=company, organization__users__id=imported_by
            ).first()
            acct = acct.id if acct else acct
            data.update({"company": acct})
        # remove contacts from validation

        contacts = data.pop("contacts", [])
        contacts = HubspotContact.objects.filter(integration_id__in=contacts).values_list(
            "id", flat=True
        )
        data.update({"contacts": contacts})
        internal_data = super().to_internal_value(data)
        return internal_data


class ObjectFieldSerializer(serializers.ModelSerializer):
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
            "display_value",
            "label",
            "reference",
            "reference_to_infos",
            "relationship_name",
            "options",
            "integration_source",
            "integration_id",
            "is_public",
            "imported_by",
            "filterable",
        )
