from rest_framework import serializers
from rest_framework.exceptions import ValidationError, PermissionDenied
from .models import (
    Opportunity,
    OpportunityScore,
)
from managr.organization.models import Stage
from managr.organization.serializers import (
    AccountSerializer,
    ContactSerializer,
    StageSerializer,
)
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


class PrevLeadScoreSerializer(serializers.ModelSerializer):
    score = serializers.SerializerMethodField()

    class Meta:
        model = OpportunityScore
        fields = (
            "id",
            "score",
        )

    def get_score(self, instance):
        return instance.final_score


class LeadScoreSerializer(serializers.ModelSerializer):
    previous_ref = PrevLeadScoreSerializer(source="previous_score", read_only=True)
    current = serializers.SerializerMethodField()

    class Meta:
        model = OpportunityScore
        fields = (
            "id",
            "current",
            "previous_ref",
            "actions_insight",
            "recent_action_insight",
            "incoming_messages_insight",
            "days_in_stage_insight",
            "forecast_table_insight",
            "expected_close_date_insight",
        )

    def get_current(self, instance):
        return instance.final_score

