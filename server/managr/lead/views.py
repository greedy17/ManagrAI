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
    IsOrganizationManager, IsSuperUser, IsSalesPerson)
from .models import Lead, Note, ActivityLog,  List, File, Forecast, Reminder
from .serializers import LeadSerializer, NoteSerializer, ActivityLogSerializer, ListSerializer, FileSerializer, ForecastSerializer, ReminderSerializer
from managr.core.models import ACCOUNT_TYPE_MANAGER


class LeadViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin):
    authentication_classes = (authentication.TokenAuthentication,)
    permission_class = (IsSalesPerson,)
    serializer_class = LeadSerializer

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
        # restricted fields array to delete them if they are in
        restricted_fields = ('created_by',
                             'account', 'claimed_by',)
        # create new dict to not affect request data
        data = dict(request.data)
        for field in restricted_fields:
            if field in data.keys():
                del data[field]
        # make sure the user that created the lead is in the created_by field

        data['last_updated_by'] = user.id
        # set its status to claimed by assigning it to the user that created the lead
        # check account to be sure it is in org
        accounts_in_user_org = [
            str(acc.id) for acc in user.organization.accounts.all()]
        account_for = request.data.get('account')
        if account_for not in accounts_in_user_org:
            raise PermissionDenied({'detail': 'Account Not In Organization'})
        serializer = self.serializer_class(self.get_object(),
                                           data=data, context={'request': request}, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        user = request.user
        if user.type == ACCOUNT_TYPE_MANAGER:
            Lead.objects.get(pk=kwargs['pk']).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({'non_field_errors': ('Not Authorized')}, status=status.HTTP_401_UNAUTHORIZED)

    @action(methods=['POST'], permission_classes=(IsSalesPerson,), detail=True, url_path="claim")
    def claim(self, request, *args, **kwargs):
        user = request.user
        lead = self.get_object()
        if not lead.is_claimed and lead.account in user.organization.accounts.all():
            lead.claimed_by = user
            lead.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            raise PermissionDenied(
                {'detail': 'Leads can only be claimed if they were previously unclaimed'})

    @action(methods=['POST'], permission_classes=(IsSalesPerson,), detail=True, url_path="un-claim")
    def un_claim(self, request, *args, **kwargs):
        user = request.user
        lead = self.get_object()
        if not lead.account in user.organization.accounts.all():
            raise PermissionDenied()
        elif lead.is_claimed and lead.claimed_by != user:
            raise PermissionDenied(
                {'detail': 'Cannot un claim a Lead that is not claimed By You'})
        elif not lead.is_claimed:
            raise PermissionDenied({'detail': 'lead is not claimed'})
        else:
            lead.claimed_by = None
            lead.status = None
            # delete lead forecast
            lead.amount = 0
            lead.save()
            # register an action
            return Response(status=status.HTTP_204_NO_CONTENT)
