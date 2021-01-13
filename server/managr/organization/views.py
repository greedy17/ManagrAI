import copy

from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.db import transaction
from django.db import IntegrityError

from django.core.exceptions import ValidationError as V
from django.core import serializers
from django.template.exceptions import TemplateDoesNotExist
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q

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

from rest_framework import viewsets, mixins, generics, status, filters, permissions
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.authtoken.models import Token


from managr.opportunity.models import Opportunity

from managr.core import constants as core_consts
from managr.core.permissions import (
    IsOrganizationManager,
    IsSuperUser,
    IsSalesPerson,
    CanEditResourceOrReadOnly,
    SuperUserCreateOnly,
    IsExternalIntegrationAccount,
)


from .models import Organization, Account, Contact, Stage
from . import constants as org_consts
from .serializers import (
    OrganizationSerializer,
    AccountSerializer,
    ContactSerializer,
    StageSerializer,
)


class OrganizationViewSet(
    viewsets.GenericViewSet,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
):
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (
        SuperUserCreateOnly,
        CanEditResourceOrReadOnly,
    )

    def get_queryset(self):
        return Organization.objects.for_user(self.request.user)

    def get_serializer_class(self):
        is_verbose = self.request.GET.get("verbose", None)
        if is_verbose is not None and is_verbose.lower() == "true":
            return OrganizationVerboseSerializer
        return OrganizationSerializer

    @action(
        methods=["GET"],
        permission_classes=(IsExternalIntegrationAccount,),
        detail=False,
        url_path="list-org-tokens",
    )
    def list_org_tokens(self, request, *args, **kwargs):
        """Endpoint to list orgs and tokens for integration accounts """
        param = request.query_params.get("name", None)

        qs = self.get_queryset().filter(is_externalsyncenabled=True)
        if param:
            qs = qs.filter(name=param)
        serializer = OrganizationRefSerializer(qs, many=True)

        return Response(serializer.data)


class AccountViewSet(
    viewsets.GenericViewSet,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
):
    """ Accounts can only be created, updated or deleted by Managers of an Organization All users can list/retrieve  """

    authentication_classes = (authentication.TokenAuthentication,)
    serializer_class = AccountSerializer
    # filter_class = AccountFilterSet
    permission_classes = (IsSalesPerson,)
    filter_backends = (
        filters.OrderingFilter,
        DjangoFilterBackend,
    )
    # Explicit fields the API may be ordered against
    ordering_fields = ("name",)

    def get_queryset(self):
        return Account.objects.for_user(self.request.user)

    def create(self, request, *args, **kwargs):
        user = request.user
        # passing in the request as a context to manually add the organization
        # checking to see if this is a bulk add or not if it is set to many

        serializer = AccountSerializer(
            data=request.data,
            context={"request": request},
            many=isinstance(request.data, list),
        )
        serializer.is_valid(raise_exception=True)

        self.perform_create(serializer)
        response_data = serializer.data
        return Response(response_data)

    def update(self, request, *args, **kwargs):
        user = request.user
        acc = self.get_object
        serializer = self.serializer_class(
            acc, data=request.data, context={"request": request}, partial=True
        )
        serializer.is_valid(raise_exception=True)
        if (
            user.organization != acc.organization
            or user.type != core_consts.ACCOUNT_TYPE_MANAGER
        ):
            return Response(
                {"non_field_errors": ("Not Authorized")},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        serializer.save()

        response_data = serializer.data
        return Response(response_data)

    def destroy(self, request, *args, **kwargs):
        user = request.user
        if user.is_superuser:
            Organization.objects.get(pk=kwargs["pk"]).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(
                {"non_field_errors": ("Not Authorized")},
                status=status.HTTP_401_UNAUTHORIZED,
            )

    @action(
        methods=["POST"],
        permission_classes=(IsSalesPerson,),
        detail=False,
        url_path="bulk-update",
    )
    def bulk_update(self, request, *args, **kwargs):
        accounts = request.data
        query = Q()
        for acc in accounts:
            query |= Q(id=acc["id"])

        accs = Account.objects.for_user(request.user).filter(query)
        updated_accounts = []
        for account in accs:

            for updated_data in accounts:
                if updated_data["id"] == str(account.id):
                    serializer = AccountSerializer(
                        account, data=updated_data, context={"request": request}
                    )
                    serializer.is_valid(raise_exception=True)
                    serializer.save()
                    updated_accounts.append(serializer.data)

        return Response(updated_accounts)


class ContactViewSet(
    viewsets.GenericViewSet,
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
):
    """ All memebers of the organization can add, create and update contacts """

    authentication_classes = (authentication.TokenAuthentication,)
    serializer_class = ContactSerializer
    permissions_class = (IsSalesPerson,)
    # filter_class = ContactFilterSet

    def get_queryset(self):
        return Contact.objects.for_user(self.request.user)

    def create(self, request, *args, **kwargs):
        # check if this is a bulk add

        serializer = ContactSerializer(
            data=request.data,
            context={"request": request},
            many=isinstance(request.data, list),
        )

        serializer.is_valid(raise_exception=True)

        try:
            serializer.save()
            res = serializer.data

        except IntegrityError:
            # an integrity error here means two contacts with the same info are added
            # if both are the same and not unique then django returns an array of errors
            return Response(
                data={"non_field_errors": "One of More Contacts already exist"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(res)

    @action(
        methods=["PATCH"],
        permission_classes=(IsSalesPerson,),
        detail=False,
        url_path="bulk-update",
    )
    def bulk_update(self, request, *args, **kwargs):
        # check if this is a bulk add
        contacts = request.data
        updated_contacts = []
        for contact in contacts:
            contact_obj = None
            try:
                contact_obj = Contact.objects.for_user(request.user).get(
                    email=contact["email"], account=contact["account"]
                )
            except Contact.DoesNotExist:
                # pass if the contact doesn't exist
                # TODO: Could have it create the contact if it does not exist PB 07/06
                pass
            if contact_obj:
                serializer = ContactSerializer(
                    contact_obj, data=contact, context={"request": request}
                )

                serializer.is_valid(raise_exception=True)

                serializer.save()
                updated_contacts.append(serializer.data)

        return Response(updated_contacts)

    @action(
        methods=["POST"],
        permission_classes=(IsSalesPerson,),
        detail=False,
        url_path="link-to-leads",
    )
    def add_to_lead(self, request, *args, **kwargs):
        """ special endpoint to add a contact to a lead or leads, takes a list of contact ids and lead ids"""

        d = request.data
        contacts = d.get("contacts", [])
        leads = d.get("leads", [])
        for_payload = None
        for (index, lead) in enumerate(leads):
            try:
                lead = Lead.objects.get(pk=lead)
                lead.linked_contacts.set(contacts)
                for_payload = lead.linked_contacts
            except (
                V,
                Lead.DoesNotExist,
                ValueError,
            ):
                pass
        payload = [ContactSerializer(contact).data for contact in for_payload.all()]
        return Response(data=payload)

    @action(
        methods=["POST"],
        permission_classes=(IsSalesPerson,),
        detail=False,
        url_path="remove-from-lead",
    )
    def remove_from_lead(self, request, *args, **kwargs):
        """ special method to remove a contact from a leads linked contacts list, expects array of contacts and lead"""
        request_data = request.data
        contacts = request_data.get("contacts", [])
        contacts_removed = list()
        lead_id = request_data.get("lead", None)
        if not lead_id:
            raise ValidationError({"detail": "a lead is required for this operation"})

        for contact in contacts:
            lead = Lead.objects.get(pk=lead_id)
            if lead.linked_contacts.filter(pk=contact).exists():
                lead.linked_contacts.remove(contact)
                # if a contact does not exist no error is thrown it will continue as though it removed a contact
                lead.save()
                contacts_removed.append(contact)

        return Response(data={"removed_contacts": contacts_removed})


class StageViewSet(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
):
    """ endpoint to retrieve all stages for an org """

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (IsSalesPerson,)
    serializer_class = StageSerializer

    def get_queryset(self):
        return Stage.objects.for_user(self.request.user)

    def create(self, request, *args, **kwargs):
        d = request.data
        user = request.user
        if not user.is_superuser:
            # only super users can create public items
            d["type"] = org_consts.STAGE_TYPE_PRIVATE
            # only super users can create items for other orgs
            d["organization"] = user.organization.id

        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        response_data = serializer.data
        return Response(response_data)

    def update(self, request, *args, **kwargs):

        request_data = request.data
        user = request.user
        instance = self.get_object()
        if not user.is_superuser:
            # only super users can create public items
            request_data["type"] = org_consts.STAGE_TYPE_PRIVATE
            # only super users can update items for other orgs
            request_data["organization"] = user.organization.id

        serializer = self.serializer_class(
            instance, data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        response_data = serializer.data
        return Response(response_data)
