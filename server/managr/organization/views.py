from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.db import transaction
from django.db import IntegrityError
from rest_framework.authtoken.models import Token
from django.core.exceptions import ValidationError as V
from django.template.exceptions import TemplateDoesNotExist
from django_filters.rest_framework import DjangoFilterBackend
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
from managr.lead.models import Lead
from .serializers import OrganizationSerializer, OrganizationVerboseSerializer, AccountSerializer, ContactSerializer
from .filters import ContactFilterSet
from managr.core.models import ACCOUNT_TYPE_MANAGER

from managr.core.permissions import (
    IsOrganizationManager, IsSuperUser, IsSalesPerson, CanEditResourceOrReadOnly, SuperUserCreateOnly,)


class OrganizationViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin, mixins.ListModelMixin):
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (SuperUserCreateOnly, CanEditResourceOrReadOnly,)

    def get_queryset(self):
        return Organization.objects.for_user(self.request.user)

    def get_serializer_class(self):
        is_verbose = self.request.GET.get('verbose', None)
        if is_verbose is not None and is_verbose.lower() == 'true':
            return OrganizationVerboseSerializer
        return OrganizationSerializer


class AccountViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.ListModelMixin):
    """ Accounts can only be created, updated or deleted by Managers of an Organization All users can list/retrieve  """

    authentication_classes = (authentication.TokenAuthentication,)
    serializer_class = AccountSerializer
    permission_classes = (IsSalesPerson,)
    filter_backends = (filters.OrderingFilter, DjangoFilterBackend,)
    # Explicit fields the API may be ordered against
    ordering_fields = ('name',)

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

    @action(methods=["POST"], permission_classes=(IsSalesPerson,), detail=False, url_path="link-to-leads")
    def add_to_lead(self, request, *args, **kwargs):
        """ special endpoint to add a contact to a lead or leads, takes a list of contact ids and lead ids"""
        u = request.user
        d = request.data
        contacts = d.get('contacts', [])
        contacts_added = list()
        leads = d.get('leads', [])
        for (index, lead)in enumerate(leads):
            for contact in contacts:
                try:
                    l = Lead.objects.get(pk=lead)
                except (V, Lead.DoesNotExist, ValueError,):
                    # if any exceptions of the 3 above occur remove the lead from the list and continue
                    # with the rest
                    del leads[index]
                    l = None
                    pass
                if l:
                    try:
                        l.linked_contacts.add(contact)
                        l.save()
                        contacts_added.append(contact)
                    except IntegrityError:
                        # passing the integrity error, it is triggered if a contact already exists on a user
                        # it means that a contact is already added to this user
                        pass

        return Response(data={'linked_contacts_added': contacts_added})

    @action(methods=["POST"], permission_classes=(IsSalesPerson,), detail=False, url_path="remove-from-lead")
    def remove_from_lead(self, request, *args, **kwargs):
        """ special method to remove a contact from a leads linked contacts list, expects array of contacts and lead"""
        d = request.data
        contacts = d.get('contacts', [])
        contacts_removed = list()
        l = d.get('lead', None)
        if not l:
            raise ValidationError(
                {'detail': 'a lead is required for this operation'})

        for contact in contacts:
            lead = Lead.objects.get(pk=l)
            if lead.linked_contacts.filter(pk=contact).exists():
                lead.linked_contacts.remove(contact)
            # if a contact does not exist no error is thrown it will continue as though it removed a contact
                lead.save()
                contacts_removed.append(contact)

        return Response(data={'removed_contacts': contacts_removed})
