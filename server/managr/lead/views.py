from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.db import transaction
from rest_framework.authtoken.models import Token
from django.template.exceptions import TemplateDoesNotExist
from rest_framework import (
    authentication,
    filters,
    permissions,
    generics,
    mixins,
    status,
    views,
    viewsets,
)
from rest_framework import (
    viewsets, mixins, generics, status, filters, permissions
)
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError, PermissionDenied
from rest_framework.response import Response
from managr.core.permissions import (
    IsOrganizationManager, IsSuperUser, IsSalesPerson, CanEditResourceOrReadOnly,)
from .models import Lead, Note, ActivityLog,  List, File, Forecast, Reminder, LEAD_STATUS_CLOSED
from .serializers import LeadSerializer, NoteSerializer, ActivityLogSerializer, ListSerializer, FileSerializer, ForecastSerializer, ReminderSerializer
from managr.core.models import ACCOUNT_TYPE_MANAGER
from .filters import LeadFilterSet


class LeadViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin):
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (IsSalesPerson, CanEditResourceOrReadOnly, )
    serializer_class = LeadSerializer
    filter_class = LeadFilterSet

    def get_queryset(self):
        return Lead.objects.for_user(self.request.user)

    def create(self, request, *args, **kwargs):
        """ manually set org and only allow accounts in org """
        user = request.user

        data = dict(request.data)
        # make sure the user that created the lead is in the created_by field

        data['created_by'] = user.id
        # set its status to claimed by assigning it to the user that created the lead
        data['claimed_by'] = user.id
        # check account to be sure it is in org
        accounts_in_user_org = [
            str(acc.id) for acc in user.organization.accounts.all()]
        account_for = request.data.get('account')
        if account_for not in accounts_in_user_org:
            raise PermissionDenied({'detail': 'Account Not In Organization'})
        serializer = self.serializer_class(
            data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        """ cant update account, cant update created_by  """
        user = request.user
        current_lead = self.get_object()
        # restricted fields array to delete them if they are in
        restricted_fields = ('created_by',
                             'account', 'claimed_by',)

        # create new dict to not affect request data
        data = dict(request.data)
        for field in restricted_fields:
            if field in data.keys():
                del data[field]
        # TODO:- make sure closing amount is not allowed unless lead is being closed or is already closed
        status_update = request.data.get('state', None)
        if current_lead.status != LEAD_STATUS_CLOSED and (not status_update or status_update != LEAD_STATUS_CLOSED):
            if 'closing_amount' in request.data.keys():
                del data['closing_amount']
            if 'contract' in request.data.keys():
                del data['contract']
        # make sure the user that created the lead is not updated as well

        data['last_updated_by'] = user.id
        # set its status to claimed by assigning it to the user that created the lead
        # check account to be sure it is in org
        accounts_in_user_org = [
            str(acc.id) for acc in user.organization.accounts.all()]
        # if lead account is being updated make sure the account it is added to is in the Users org
        account_for = request.data.get('account', None)

        if account_for:
            if account_for not in accounts_in_user_org:
                raise PermissionDenied(
                    {'detail': 'Account Not In Organization'})
        serializer = self.serializer_class(current_lead,
                                           data=data, context={'request': request}, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    @action(methods=['POST'], permission_classes=(IsSalesPerson, CanEditResourceOrReadOnly), detail=True, url_path="claim")
    def claim(self, request, *args, **kwargs):
        user = request.user
        lead = self.get_object()
        lead.claimed_by = user
        lead.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['POST'], permission_classes=(IsSalesPerson, CanEditResourceOrReadOnly,), detail=True, url_path="un-claim")
    def un_claim(self, request, *args, **kwargs):
        """ anyone  who is a salesperson can un-claim a lead that is claimed_by them """
        lead = self.get_object()

        lead.claimed_by = None
        lead.status = None
        # delete lead forecast
        if lead.forecast:
            Forecast.objects.get(lead=lead).delete()
        lead.amount = 0
        lead.save()
        # register an action
        return Response(status=status.HTTP_204_NO_CONTENT)


class ListViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin):
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (IsSalesPerson, )
    serializer_class = ListSerializer

    def get_queryset(self):
        # TODO: - set manager
        return List.objects.for_user(self.request.user)

    def create(self, request, *args, **kwargs):
        """ manually set org and created_by """
        user = request.user

        data = dict(request.data)
        # make sure the user that created the lead is in the created_by field

        data['created_by'] = user.id
        data['organization'] = user.organization.id
        serializer = self.serializer_class(
            data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):

        data = dict(request.data)
        # do not allow users to change the created_by or organization info if added
        if 'created_by' in data.keys():
            del data['created_by']
        if 'organization' in data.keys():
            del data['organization']
         # do not allow updating on lists here as it may require the whole list to be sent back
        if 'leads' in data.keys():
            del data['leads']

        serializer = self.serializer_class(self.get_object(),
                                           data=data, context={'request': request}, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    @action(methods=['POST'], permission_classes=(IsSalesPerson, ), detail=True, url_path="add-to-list")
    def add_to_list(self, request, *args, **kwargs):
        """ End point to allow addition of leads to list after created """
        l = self.get_object()
        # TODO: Check if lead is in org
        new_leads = request.data.get('leads', [])
        for lead in new_leads:
            l.leads.add(lead)
            l.save()

        serializer = self.serializer_class(self.get_object())
        return Response(serializer.data)

    @action(methods=['delete'], permission_classes=(IsSalesPerson, ), detail=True, url_path="remove-from-list")
    def remove_from_list(self, request, *args, **kwargs):
        """ End point to allow addition of leads to list after created """
        l = self.get_object()
        # TODO: Check if lead is in org
        remove_leads = request.data.get('leads', [])
        for lead in remove_leads:
            l.leads.remove(lead)
            l.save()

        serializer = self.serializer_class(self.get_object())
        return Response(serializer.data)


class NoteViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin):
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (IsSalesPerson, )
    serializer_class = NoteSerializer

    def get_queryset(self):
        # TODO: create manager
        return Note.objects.for_user(self.request.user)

    def create(self, request, *args, **kwargs):
        """ manually set org and created_by """
        user = request.user

        data = dict(request.data)
        # make sure the user that created the lead is in the created_by field

        data['created_by'] = user.id
        notes_created = list()
        for lead in request.data.get('created_for', []):
            # decision here to create a new note for each lead to make them individually editable
            # TODO: check lead in org
            d = {'title': data['note']['title'],
                 'content': data['note']['content'], 'created_for': lead, 'created_by': user.id}
            serializer = self.serializer_class(
                data=d, context={'request': request})
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            notes_created.append(serializer.data)
        return Response({'detail': notes_created})

    def update(self, request, *args, **kwargs):
        user = request.user
        data = dict(request.data)
        # cannot update created by
        # cannot update created for
        d = {'title': data['note']['title'],
             'content': data['note']['content'], 'updated_by': user.id}
        serializer = self.serializer_class(self.get_object(),
                                           data=d, context={'request': request}, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        # TODO :- add activity log here
        return Response(serializer.data)


class ForecastViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin):
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (IsSalesPerson, )
    serializer_class = ForecastSerializer
    # TODO :- log activity

    def get_queryset(self):
        return Forecast.objects.for_user(self.request.user)
