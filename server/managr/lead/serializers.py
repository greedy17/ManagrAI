from rest_framework import serializers
from rest_framework.exceptions import ValidationError, PermissionDenied
from .models import Lead, Note, ActivityLog, List, File, Forecast, Reminder, ActionChoice, Action
from managr.api.serializers import AccountRefSerializer
from managr.core.models import User
from managr.lead import constants as lead_constants

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


class LeadListRefSerializer(serializers.ModelSerializer):
    # will be changing Lists to LeadLists to make it clearer that we are referring to a lead list model
    """
        Read Only Ref Serializer for Leads since we are not returning the list of leads in the LeadList Serializer

    """
    class Meta:
        model = Lead
        fields = ('__all__')


class ListSerializer(serializers.ModelSerializer):
    """
        In order to offer leads of a list as a paginated result set for the frontend
        we have decided to return only minimal list info and have the frontend then retrieve leads specific to a list
        as per our discussion with William and Bruno
    """
    lead_count = serializers.SerializerMethodField()

    class Meta:
        model = List
        fields = ('id', 'title', 'lead_count', 'leads',
                  'created_by',)
        extra_kwargs = {
            'leads': {'write_only': True},
            'created_by': {'write_only': True}
        }

    def get_lead_count(self, obj):
        return obj.leads.count()


class FileSerializer(serializers.ModelSerializer):

    def to_internal_value(self, data):

        internal_data = super().to_internal_value(data)
        doc_type = internal_data.get('doc_type', None)
        if doc_type == lead_constants.FILE_TYPE_CONTRACT:
            # check to see if the lead is closed  or closing

            lead = internal_data.get('lead', None)
            if not lead:
                raise serializers.ValidationError(
                    {'detail': 'Lead Required'})
            lead_status = lead.status
            if not lead_status == lead_constants.LEAD_STATUS_CLOSED:

                raise serializers.ValidationError(
                    {'non_field_errors': 'Lead Not Closed'})

        return internal_data

    class Meta:
        model = File
        fields = ('id', 'doc_type', 'uploaded_by', 'lead', 'file')


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


class ActionChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActionChoice
        fields = ('__all__')


class ActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Action
        fields = ('__all__')


class LeadSerializer(serializers.ModelSerializer):
    def validate_status(self, value):
        if value == lead_constants.LEAD_STATUS_CLOSED:
            raise serializers.ValidationError(
                {'detail': 'Cannot Close Lead by Update'})

    account_ref = AccountRefSerializer(
        source='account', read_only=True)
    created_by_ref = UserRefSerializer(source='created_by', read_only=True)
    claimed_by_ref = UserRefSerializer(source='claimed_by', read_only=True)
    last_updated_by_ref = UserRefSerializer(
        source='last_updated_by', read_only=True)
    forecast_ref = ForecastSerializer(source='forecast', read_only=True)
    actions_ref = ActionSerializer(source='actions', read_only=True, many=True)

    class Meta:
        model = Lead
        fields = ('id', 'title', 'amount', 'closing_amount', 'primary_description', 'secondary_description', 'rating', 'status',
                  'account', 'account_ref', 'created_by', 'created_by_ref', 'forecast', 'forecast_ref', 'linked_contacts', 'last_edited', 'contract',  'datetime_created', 'notes', 'claimed_by', 'claimed_by_ref', 'last_updated_by',
                  'last_updated_by_ref', 'actions', 'actions_ref', 'lists', 'files',)
        # forecasts are set on the forecast table, in order to add a forecast hit the create/update/delete end points for forecasts
        read_only_fields = ('closing_amount', 'contract',
                            'forecast', 'actions', 'files',)
