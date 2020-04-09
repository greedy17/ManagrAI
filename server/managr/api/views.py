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
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from .models import Organization, Account, Contact, Lead
from .serializers import OrganizationSerializer, AccountSerializer, LeadSerializer, ContactSerializer
from managr.core.models import ACCOUNT_TYPE_MANAGER

from managr.core.permissions import (IsOrganizationManager, IsSuperUser)


class OrganizationViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin, mixins.ListModelMixin):
    authentication_classes = (authentication.TokenAuthentication,)
    serializer_class = OrganizationSerializer
    permissions_class = (IsSuperUser | IsOrganizationManager,)

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Organization.objects.all()
        elif self.request.user.type == ACCOUNT_TYPE_MANAGER and self.request.user.organization:
            return Organization.objects.filter(pk=self.request.user.organization.id)
        else:
            return None

    def destroy(self, request, *args, **kwargs):
        user = request.user
        if user.is_superuser:
            Organization.objects.get(pk=kwargs['pk']).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({'non_field_errors': ('Not Authorized')}, status=status.HTTP_401_UNAUTHORIZED)


class AccountViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.ListModelMixin):
    """ Accounts can only be created, updated or deleted by Managers of an Organization All users can list/retrieve  """

    authentication_classes = (authentication.TokenAuthentication,)
    serializer_class = AccountSerializer
    permissions_class = (IsOrganizationManager,)

    def get_queryset(self):
        if self.request.user.type == ACCOUNT_TYPE_MANAGER and self.request.user.organization:
            return Account.objects.filter(organization=self.request.user.organization.id)
        else:
            return None

    def create(self, request, *args, **kwargs):
        user = request.user
        serializer = AccountSerializer(
            data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        if user.type != ACCOUNT_TYPE_MANAGER:
            return Response({'non_field_errors': ('Not Authorized')}, status=status.HTTP_401_UNAUTHORIZED)
        self.perform_create(serializer)
        response_data = serializer.data
        return Response(response_data)

    def update(self, request, *args, **kwargs):
        user = request.user
        acc = Account.objects.get(pk=kwargs['pk'])
        serializer = self.serializer_class(acc,
                                           data=request.data, context={'request': request}, partial=True)
        serializer.is_valid(raise_exception=True)
        if user.organization != acc.organization or user.type != ACCOUNT_TYPE_MANAGER:
            return Response({'non_field_errors': ('Not Authorized')}, status=status.HTTP_401_UNAUTHORIZED)
        serializer.save()

        response_data = serializer.data
        return Response(response_data)

    def destroy(self, request, *args, **kwargs):
        user = request.user
        if user.is_superuser:
            Organization.objects.get(pk=kwargs['pk']).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({'non_field_errors': ('Not Authorized')}, status=status.HTTP_401_UNAUTHORIZED)


class ContactViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin):
    authentication_classes = (authentication.TokenAuthentication,)
    serializer_class = ContactSerializer
    permissions_class = (IsOrganizationManager,)

    def get_queryset(self):
        if self.request.user.type == ACCOUNT_TYPE_MANAGER and self.request.user.organization:
            return Contact.objects.filter(account__organization=self.request.user.organization.id)
        else:
            return None

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        contact = Contact.objects.get(pk=kwargs['pk'])
        serializer = self.serializer_class(contact,
                                           data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data)


class LeadViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin):
    authentication_classes = (authentication.TokenAuthentication,)
    serializer_class = AccountSerializer
    permissions_class = (IsOrganizationManager,)

    def get_queryset(self):
        if self.request.user.type == ACCOUNT_TYPE_MANAGER and self.request.user.organization:
            return Lead.objects.filter(account__organization=self.request.user.organization.id)
        else:
            return None
