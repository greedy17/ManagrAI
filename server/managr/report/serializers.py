from rest_framework import serializers

from .models import StoryReport, PerformanceReport
from managr.lead.serializers import LeadRefSerializer, UserRefSerializer
from managr.organization.serializers import AccountRefSerializer, OrganizationRefSerializer


class StoryReportSerializer(serializers.ModelSerializer):
    lead_ref = LeadRefSerializer(source='lead', read_only=True)
    account_ref = AccountRefSerializer(source='lead.account', read_only=True)

    class Meta:
        model = StoryReport
        fields = (
            'id',
            'datetime_generated',
            'data',
            'generated_by',
            'lead_ref',
            'account_ref',
        )


class PerformanceReportSerializer(serializers.ModelSerializer):
    representative_ref = UserRefSerializer(source='representative', read_only=True)
    organization_ref = serializers.SerializerMethodField()

    def get_organization_ref(self, instance):
        return OrganizationRefSerializer(instance.generated_by.organization).data

    class Meta:
        model = PerformanceReport
        fields = (
            'id',
            'representative',
            'representative_ref',
            'organization_ref',
            'date_range_preset',
            'date_range_from',
            'date_range_to',
            'datetime_generated',
            'datetime_created',
            'data',
            'generated_by',
            'is_representative_report',
            'is_organization_report',
        )
