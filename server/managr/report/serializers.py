from rest_framework import serializers

from .models import StoryReport
from managr.lead.serializers import LeadRefSerializer
from managr.organization.serializers import AccountRefSerializer


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
