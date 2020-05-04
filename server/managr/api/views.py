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
from .models import Organization, Account, Contact
from .serializers import OrganizationSerializer, AccountSerializer, ContactSerializer
from .filters import ContactFilterSet
from managr.core.models import ACCOUNT_TYPE_MANAGER

from managr.core.permissions import (
    IsOrganizationManager, IsSuperUser, IsSalesPerson, CanEditResourceOrReadOnly, SuperUserCreateOnly,)


class OrganizationViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin, mixins.ListModelMixin):
    authentication_classes = (authentication.TokenAuthentication,)
    serializer_class = OrganizationSerializer
    permission_classes = (SuperUserCreateOnly, CanEditResourceOrReadOnly,)

    def get_queryset(self):
        return Organization.objects.for_user(self.request.user)


class AccountViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.ListModelMixin):
    """ Accounts can only be created, updated or deleted by Managers of an Organization All users can list/retrieve  """

    authentication_classes = (authentication.TokenAuthentication,)
    serializer_class = AccountSerializer
    permission_classes = (IsSalesPerson,)

    def get_queryset(self):
        return Account.objects.for_user(self.request.user)

    def create(self, request, *args, **kwargs):
        user = request.user
        # passing in the request as a context to manually add the organization
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


class ContactViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin, mixins.ListModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin):
    """ All memebers of the organization can add, create and update contacts """
    authentication_classes = (authentication.TokenAuthentication,)
    serializer_class = ContactSerializer
    permissions_class = (IsSalesPerson,)
    filter_class = ContactFilterSet

    def get_queryset(self):
        return Contact.objects.for_user(self.request.user)
