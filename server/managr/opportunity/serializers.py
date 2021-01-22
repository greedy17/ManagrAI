from rest_framework import serializers
from rest_framework.exceptions import ValidationError, PermissionDenied
from .models import (
    Opportunity,
    OpportunityScore,
)
from managr.organization.models import Stage, Account
from managr.organization.serializers import (
    AccountSerializer,
    ContactSerializer,
    StageSerializer,
)
from managr.salesforce.models import SalesforceAuthAccount
from managr.organization import constants as org_consts
from managr.core.models import User, Notification
from managr.organization import constants as opp_consts
from django.core.paginator import Paginator
from collections import OrderedDict

from rest_framework import status, filters, permissions

from rest_framework.response import Response


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
            "title",
            "description",
            "amount",
            "close_date",
            "type",
            "next_step",
            "lead_source",
            "forecast_category",
            "account",
            "stage",
            "owner",
            "last_stage_update",
            "last_activity_date",
            "external_account",
            "external_owner",
            "external_stage",
            "imported_by",
        )

