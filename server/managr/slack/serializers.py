from rest_framework import serializers

from .models import OrganizationSlackIntegration, OrgCustomSlackForm, UserSlackIntegration


class OrganizationSlackIntegrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganizationSlackIntegration
        fields = (
            "datetime_created",
            "team_name",
            "team_id",
        )


class UserSlackIntegrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSlackIntegration
        fields = (
            "slack_id",
            "datetime_created",
        )


class OrgCustomSlackFormSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrgCustomSlackForm
        fields = ("id", "organization", "config")
        read_only_fields = ("organization",)
