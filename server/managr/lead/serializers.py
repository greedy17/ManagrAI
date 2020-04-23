from rest_framework import serializers
from rest_framework.exceptions import ValidationError, PermissionDenied
from .models import Lead, Note, ActivityLog, List, File, Forecast, Reminder
from managr.api.serializers import AccountRefSerializer
from managr.core.models import User

from rest_framework import (
    status, filters, permissions
)


from rest_framework.response import Response


class UserRefSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'email', 'full_name')

    def get_full_name(self, instance):
        return f'{instance.first_name} {instance.last_name}'


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


class LeadSerializer(serializers.ModelSerializer):

    account_ref = AccountRefSerializer(
        source='account', read_only=True)
    created_by_ref = UserRefSerializer(source='created_by', read_only=True)
    claimed_by_ref = UserRefSerializer(source='claimed_by', read_only=True)
    last_updated_by_ref = UserRefSerializer(
        source='last_updated_by', read_only=True)
    forecast_ref = ForecastSerializer(source='forecast', read_only=True)

    class Meta:
        model = Lead
        fields = ('id', 'title', 'amount', 'closing_amount', 'primary_description', 'secondary_description', 'rating', 'status',
                  'account', 'account_ref', 'created_by', 'created_by_ref', 'forecast', 'forecast_ref', 'linked_contacts', 'last_updated_at', 'contract',  'datetime_created', 'notes', 'claimed_by', 'claimed_by_ref', 'last_updated_by', 'last_updated_by_ref')
        # forecasts are set on the forecast table, in order to add a forecast hit the create/update/delete end points for forecasts
        read_only_fields = ('closing_amount', 'contract', 'forecast',)
