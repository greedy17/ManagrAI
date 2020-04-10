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


class LeadViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin, mixins.ListModelMixin):
    authentication_classes = (authentication.TokenAuthentication,)
    permission_class = (IsSalesPerson,)
    serializer_class = LeadSerializer

    def get_queryset(self):
        return Lead.objects.for_user(self.request.user)

    def create(self, request, *args, **kwargs):
        """ manually set org and only allow accounts in org """
        user = request.user
        # check account to be sure it is in org
        account_for = request.data.get('account')
        if account_for not in user.organization.accounts:
            raise PermissionDenied({'detail': 'Account Not In Organization'})
        serializer = self.serializer_class(
            data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data)
