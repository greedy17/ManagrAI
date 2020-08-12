from rest_framework import serializers

from .models import StoryReport
from managr.lead.serializers import LeadRefSerializer


class StoryReportSerializer(serializers.ModelSerializer):
    lead_ref = LeadRefSerializer(source="lead", read_only=True)
    account_ref = serializers.SerializerMethodField()

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

    def get_account_ref(self, instance):
        account = instance.lead.account
        return {
            'id': account.id,
            'logo': account.logo
        }
