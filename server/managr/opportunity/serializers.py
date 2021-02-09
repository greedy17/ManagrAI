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
from managr.salesforce.models import SalesforceAuthAccount
from managr.salesforce.exceptions import ResourceAlreadyImported
from managr.organization import constants as org_consts
from managr.core.models import User, Notification
from . import constants as opp_consts


from .models import Opportunity
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
    class Meta:
        model = Opportunity
        fields = (
            "id",
            "integration_id",
            "integration_source",
            "title",
            "amount",
            "close_date",
            "forecast_category",
            "account",
            "stage",
            "owner",
            "last_stage_update",
            "last_activity_date",
            "external_account",
            "external_owner",
            "imported_by",
            "contacts",
            "is_stale",
            "secondary_data",
        )

    def to_internal_value(self, data):
        imported_by = data.get("imported_by")
        owner = data.get("owner", None)
        account = data.get("account", None)
        stage = data.get("stage", None)
        forecast_category = data.get("forecast_category", None)
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
        if stage:
            stge = Stage.objects.filter(label=stage, organization__users__id=imported_by).first()
            stge = stge.id if stge else stge
            data.update({"stage": stge})
        if forecast_category:
            formatted_category = None
            for category in opp_consts.FORECAST_CHOICES:
                if category[1] == forecast_category:
                    formatted_category = category[0]
            if formatted_category:
                data.update({"forecast_category": formatted_category})
        # remove contacts from validation
        contacts = data.pop("contacts", [])
        internal_data = super().to_internal_value(data)
        internal_data.update({"contacts": contacts})
        return internal_data

    def create(self, validated_data):
        try:

            contacts_to_add = list()
            for contact in validated_data.pop("contacts", []):
                existing_contact = Contact.objects.filter(
                    integration_id=contact.get("integration_id"), user__id=contact.get("user"),
                ).first()
                if existing_contact:
                    serializer = ContactSerializer(
                        instance=existing_contact, data=contact, partial=True
                    )
                else:
                    serializer = ContactSerializer(data=contact)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                contacts_to_add.append(serializer.data["id"])
            validated_data.update({"contacts": contacts_to_add})
            return super().create(validated_data)
        except ResourceAlreadyImported:
            pass

    def update(self, instance, validated_data):
        contacts_to_add = list()
        for contact in validated_data.pop("contacts", []):
            existing_contact = Contact.objects.filter(
                integration_id=contact.get("integration_id"), user__id=contact.get("user"),
            ).first()
            if existing_contact:
                serializer = ContactSerializer(
                    instance=existing_contact, data=contact, partial=True
                )
            else:
                serializer = ContactSerializer(data=contact)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            contacts_to_add.append(serializer.data["id"])
        validated_data.update({"contacts": contacts_to_add})
        return super().update(instance, validated_data)

