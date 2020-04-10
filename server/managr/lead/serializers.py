from rest_framework import serializers
from rest_framework.exceptions import ValidationError, PermissionDenied
from .models import Lead, Note, ActivityLog, List, File, Forecast, Reminder

from rest_framework import (
    status, filters, permissions
)


from rest_framework.response import Response


class LeadSerializer(serializers.ModelSerializer):
    def to_internal_value(self, data):
        """setting user created_by """
        d = data
        d['created_by'] = self.context['request'].user
        return super().to_internal_value(data)

    class Meta:
        model = Lead
        fields = ('id', 'title', 'amount', 'closing_amount', 'primary_description', 'secondary_description', 'rank',
                  'account', 'created_by', 'linked_contacts', 'last_updated_at', 'contract', 'datetime_created',)

        read_only_fields = ('closing_amount', 'contract', )


class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = ('__all__')


class ListSerializer(serializers.ModelSerializer):
    class Meta:
        model = List
        fields = ('__all__')


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = ('__all__')


class ForecastSerializer(serializers.ModelSerializer):
    class Meta:
        model = Forecast
        fields = ('__all__')


class ReminderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reminder
        fields = ('__all__')


class ActivityLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityLog
        fields = ('__all__')
