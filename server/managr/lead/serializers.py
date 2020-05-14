from rest_framework import serializers
from rest_framework.exceptions import ValidationError, PermissionDenied
from .models import Lead, Note, ActivityLog, List, File, Forecast, Reminder, ActionChoice, Action, CallNote
from managr.api.serializers import AccountRefSerializer, ContactSerializer
from managr.core.models import User
from managr.lead import constants as lead_constants
from django.core.paginator import Paginator
from collections import OrderedDict


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
    created_by_ref = UserRefSerializer(source="created_by", read_only=True)
    updated_by_ref = UserRefSerializer(source="updated_by", read_only=True)

    class Meta:
        model = Note
        fields = ('id', 'title', 'content', 'created_by', 'datetime_created',
                  'updated_by', 'created_for', 'last_edited', 'created_by_ref', 'updated_by_ref',)


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

        }

    def get_lead_count(self, obj):
        return obj.leads.count()


class LeadRefSerializer(serializers.ModelSerializer):

    """ serializer for forecast """

    class Meta:
        model = Lead
        fields = ('id', 'title', 'rating', 'amount', 'lists',
                  'primary_description', 'secondary_description', 'status',)


class FileSerializer(serializers.ModelSerializer):

    def to_internal_value(self, data):
        internal_data = super().to_internal_value(data)
        internal_data.update({'uploaded_by': self.context['request'].user})
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
        fields = ('id', 'doc_type', 'uploaded_by',
                  'lead',  'file', )


class ForecastSerializer(serializers.ModelSerializer):
    lead_ref = LeadRefSerializer(source='lead', read_only=True)
    # lead_count = serializers.SerializerMethodField()

    class Meta:
        model = Forecast
        fields = ('id', 'datetime_created', 'last_edited',
                  'forecast', 'lead', 'lead_ref', )

#    def get_lead_count(self, instance):
#        # TODO: Make this more efficient (try aggregating results rather than count) PB 05/06/20
#        # TODO: add error handling if user is not real/id is not valid PB 05/06/20
#        request = self.context.get('request')
#        user_query = request.GET.get('by_user', None)
#        if user_query:
#            user_list = user_query.split(',')
#            return Forecast.objects.filter(forecast=instance.forecast, lead__claimed_by__in=user_list).count()
#        return Forecast.objects.filter(forecast=instance.forecast).count()


class ReminderSerializer(serializers.ModelSerializer):
    created_by_ref = UserRefSerializer(source="created_by")
    updated_by_ref = UserRefSerializer(source="updated_by")

    def to_internal_value(self, data):
        """ sanitize datetime_for it is not a required field but if passed and is null or blank
            pop it off so the serializer does not complain
        """

        datetime_for = data.get('datetime_for', None)
        if datetime_for:
            if (datetime_for == 'null' or datetime_for == ''):
                data.pop('datetime_for', [])
        else:
            data.pop('datetime_for', [])

        return super().to_internal_value(data)

    class Meta:
        model = Reminder
        fields = ('id', 'title', 'content', 'datetime_for', 'datetime_created',
                  'completed', 'created_for', 'created_by', 'updated_by',
                  'viewed', 'last_edited', 'updated_by_ref', 'created_by_ref', )
        read_only_fields = ('viewed', 'completed',)


class CallNoteSerializer(serializers.ModelSerializer):
    created_by_ref = UserRefSerializer(source="created_by")
    updated_by_ref = UserRefSerializer(source="updated_by")

    class Meta:
        model = CallNote
        fields = ('id', 'title', 'content',
                  'created_for', 'created_by', 'updated_by',  'last_edited', 'updated_by_ref', 'created_by_ref', 'call_date')


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
    """ verbose seriliazer for leads"""

    def validate_status(self, value):
        if value == lead_constants.LEAD_STATUS_CLOSED:
            raise serializers.ValidationError(
                {'detail': 'Cannot Close Lead by Update'})
        return value

    account_ref = AccountRefSerializer(
        source='account', read_only=True)
    created_by_ref = UserRefSerializer(source='created_by', read_only=True)
    claimed_by_ref = UserRefSerializer(source='claimed_by', read_only=True)
    last_updated_by_ref = UserRefSerializer(
        source='last_updated_by', read_only=True)
    forecast_ref = ForecastSerializer(source='forecast', read_only=True)
    actions_ref = ActionSerializer(source='actions', read_only=True, many=True)
    contract = serializers.SerializerMethodField()

    class Meta:
        model = Lead
        fields = ('id', 'title', 'amount', 'closing_amount', 'primary_description', 'secondary_description', 'rating', 'status',
                  'account', 'account_ref', 'created_by', 'created_by_ref', 'forecast', 'forecast_ref',
                        'datetime_created',  'claimed_by', 'claimed_by_ref', 'contract', 'last_updated_by',
                  'last_updated_by_ref', 'actions', 'actions_ref', 'files', )
        # forecasts are set on the forecast table, in order to add a forecast hit the create/update/delete end points for forecasts
        read_only_fields = ('closing_amount',
                            'forecast', 'actions', 'files',)

    def get_contract(self, instance):
        return instance.contract_file


class LeadVerboseSerializer(serializers.ModelSerializer):
    """ verbose seriliazer for leads"""

    def validate_status(self, value):
        if value == lead_constants.LEAD_STATUS_CLOSED:
            raise serializers.ValidationError(
                {'detail': 'Cannot Close Lead by Update'})
        return value

    account_ref = AccountRefSerializer(
        source='account', read_only=True)
    created_by_ref = UserRefSerializer(source='created_by', read_only=True)
    claimed_by_ref = UserRefSerializer(source='claimed_by', read_only=True)
    last_updated_by_ref = UserRefSerializer(
        source='last_updated_by', read_only=True)
    forecast_ref = ForecastSerializer(source='forecast', read_only=True)
    actions_ref = ActionSerializer(source='actions', read_only=True, many=True)
    contract = serializers.SerializerMethodField()
    linked_contacts_ref = ContactSerializer(
        source='linked_contacts', read_only=True, many=True)

    class Meta:
        model = Lead
        fields = ('id', 'title', 'amount', 'closing_amount', 'primary_description', 'secondary_description', 'rating', 'status',
                  'account', 'account_ref', 'created_by', 'created_by_ref', 'forecast', 'forecast_ref', 'linked_contacts', 'linked_contacts_ref',
                        'datetime_created',  'claimed_by', 'claimed_by_ref', 'contract', 'last_updated_by',
                  'last_updated_by_ref', 'actions', 'actions_ref', 'files', 'lists', 'lists_ref')
        # forecasts are set on the forecast table, in order to add a forecast hit the create/update/delete end points for forecasts
        read_only_fields = ('closing_amount',
                            'forecast', 'actions', 'files',)

    def get_contract(self, instance):
        return instance.contract_file
