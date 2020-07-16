from django_filters.rest_framework import DjangoFilterBackend

from rest_framework.authtoken.models import Token
from rest_framework import viewsets, mixins, generics, status, filters, permissions
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError, PermissionDenied
from rest_framework.response import Response
from django.db.models import Q
from django.shortcuts import render
from django.utils import timezone
from django.contrib.auth import authenticate, login
from django.db.models.functions import Lower
from django.db import transaction, IntegrityError
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

from managr.core.permissions import (
    IsOrganizationManager,
    IsSuperUser,
    IsSalesPerson,
    CanEditResourceOrReadOnly,
)
from managr.core.models import ACCOUNT_TYPE_MANAGER
from managr.organization.models import Contact, Account
from managr.lead import constants as lead_constants

from . import models as lead_models
from . import filters as lead_filters
from . import serializers as lead_serializers
from .background import emit_event
from .models import (
    Lead,
    Note,
    LeadActivityLog,
    CallNote,
    List,
    File,
    Forecast,
    Reminder,
    Action,
    ActionChoice,
    Notification
)
from .insights import LeadInsights


class LeadActivityLogViewSet(
    viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin
):
    permission_classes = (IsSalesPerson,)
    serializer_class = lead_serializers.LeadActivityLogSerializer
    filter_fields = ('lead',)
    filter_backends = (filters.SearchFilter, DjangoFilterBackend,)
    search_fields = ('meta',)

    def get_queryset(self):
        return LeadActivityLog.objects.for_user(self.request.user) \
            .exclude(activity__in=lead_constants.ACTIVITIES_TO_EXCLUDE_FROM_HISTORY)

    @action(
        methods=["GET"],
        permission_classes=(IsSalesPerson, CanEditResourceOrReadOnly),
        detail=False,
        url_path="insights",
    )
    def insights(self, request):
        """Compute summary stats for a lead.

        Query Parameters:
            leads (str):      Comma-separated list of Lead IDs. Insights
                                will be filtered to these leads.
            claimed_by (str)  Comma-separated list of User IDs. Insights
                                will be filtered to leads claimed by these
                                users.
        """
        # NOTE (Bruno 7-9-2020): self.get_queryset excludes
        # ACTIVITIES_TO_EXCLUDE_FROM_HISTORY, hence the following qs instead.
        qs = LeadActivityLog.objects.for_user(self.request.user)
        empty = request.query_params.get("empty")
        leads = request.query_params.get("leads")
        claimed_by = request.query_params.get("claimed_by")

        # IMPORTANT: For security reasons, first filter leads to
        #            those visible by this user.
        lead_qs = Lead.objects.for_user(request.user)
        if leads:
            lead_qs = lead_qs.filter(id__in=leads.split(","))
        if claimed_by:
            lead_qs = lead_qs.filter(claimed_by__in=claimed_by.split(","))

        # The Empty param overrides the others
        empty = empty is not None and empty.lower() == "true"

        insights = LeadInsights(lead_qs, qs, empty)
        return Response(insights.as_dict)


class NotificationViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (IsSalesPerson, CanEditResourceOrReadOnly,)
    serializer_class = lead_serializers.NotificationSerializer

    def get_queryset(self):
        return Notification.objects.for_user(self.request.user)

    def list(self, request, *args, **kwargs):
        """ override to set the notified_at field when an object is gotten"""
        queryset = self.filter_queryset(self.get_queryset())
        queryset.filter(notified_at__isnull=True).update(
            notified_at=timezone.now())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(
        methods=["GET"],
        authentication_classes=(authentication.TokenAuthentication,),
        detail=False,
        url_path="unviewed-count",
    )
    def get_unviewed_count(self, request, *args, **kwargs):
        user = self.request.user
        return Response(data={"count": user.unviewed_notifications_count})

    @action(methods=["POST"], authentication_classes=(authentication.TokenAuthentication,), detail=False, url_path="mark-as-viewed")
    def mark_as_viewed(self, request, *args, **kwargs):
        user = self.request.user
        query = Q()
        notifications = request.data.get('notifications', None)
        if not notifications:
            return ValidationError()

        for notification in notifications:
            query |= Q(id=notification)
        notifications_items = Notification.objects.for_user(user).filter(query)
        for n in notifications_items:
            n.viewed = True
            n.save()
        return Response()


class LeadViewSet(
    viewsets.GenericViewSet,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
):
    """ Viewset for leads Permissions are set on the Permissions.py"""

    authentication_classes = (authentication.TokenAuthentication,)

    permission_classes = (
        IsSalesPerson,
        CanEditResourceOrReadOnly,
    )
    serializer_class = lead_serializers.LeadSerializer
    filter_backends = (
        DjangoFilterBackend,
        filters.SearchFilter,
        lead_filters.LeadRatingOrderFiltering,
    )
    filter_class = lead_filters.LeadFilterSet
    ordering = ("rating",)
    search_fields = ("title",)

    def get_queryset(self):
        return Lead.objects.for_user(self.request.user) \
            .order_by(Lower("title")).prefetch_related('activity_logs')

    def get_serializer_class(self):
        is_verbose = self.request.GET.get("verbose", None)
        if is_verbose is not None and is_verbose.lower() == "true":
            return lead_serializers.LeadVerboseSerializer
        return lead_serializers.LeadSerializer

    def create(self, request, *args, **kwargs):
        """ manually set org and only allow accounts in org """
        user = request.user

        data = dict(request.data)
        # make sure the user that created the lead is in the created_by field

        data["created_by"] = user.id
        # set its status to claimed by assigning it to the user that created the lead
        data["claimed_by"] = user.id
        # check account to be sure it is in org
        account_for = request.data.get("account", None)
        if not account_for:
            raise ValidationError(
                detail={"detail": "Account is a required field"})
        # create method does returns true as object is not an instance of lead therefore we must check if account is part of user account
        try:
            account = Account.objects.for_user(
                request.user).get(pk=account_for)
        except Account.DoesNotExist:
            raise PermissionDenied()
        # if there are contacts to be added first check that contacts exist or create them
        # TODO: PB 05/15/20 fix issue where This get_or_create allows creating a user with a blank first_name and number
        contacts = data.pop("linked_contacts", [])
        contact_list = list()
        for contact in contacts:
            c, created = Contact.objects.for_user(request.user).get_or_create(
                email=contact["email"], defaults={"account": account}
            )
            if created:
                c.title = contact.get("title", c.title)
                c.first_name = contact.get("first_name", c.first_name)
                c.last_name = contact.get("last_name", c.last_name)
                c.phone_number_1 = contact.get(
                    "phone_number_1", c.phone_number_1)
                c.phone_number_2 = contact.get(
                    "phone_number_2", c.phone_number_2)
                c.save()
            contact_list.append(c.id)
        serializer = self.serializer_class(
            data=data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        # Attach contacts and create a Forecast
        serializer.instance.linked_contacts.add(*contact_list)
        Forecast.objects.create(lead=serializer.instance)

        emit_event(lead_constants.LEAD_CREATED, user, serializer.instance)

        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        """ cant update account, cant update created_by  """
        user = request.user
        current_lead = self.get_object()
        # restricted fields array to delete them if they are in
        restricted_fields = (
            "created_by",
            "account",
            "claimed_by",
            "contacts",
        )

        # create new dict to not affect request data
        data = dict(request.data)
        for field in restricted_fields:
            if field in data.keys():
                del data[field]

        # if updating status, also update status_last_update
        if "status" in data:
            data["status_last_update"] = timezone.now()

        # make sure the user that created the lead is not updated as well

        data["last_updated_by"] = user.id
        # set its status to claimed by assigning it to the user that created the lead
        serializer = self.serializer_class(
            current_lead, data=data, context={"request": request}, partial=True
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        emit_event(lead_constants.LEAD_UPDATED, user, serializer.instance)
        return Response(serializer.data)

    @action(
        methods=["POST"],
        permission_classes=(IsSalesPerson, CanEditResourceOrReadOnly),
        detail=True,
        url_path="claim",
    )
    def claim(self, request, *args, **kwargs):
        user = request.user
        lead = self.get_object()
        lead.claimed_by = user
        lead.save()
        emit_event(lead_constants.LEAD_CLAIMED, user, lead)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=["POST"],
        permission_classes=(IsSalesPerson, CanEditResourceOrReadOnly,),
        detail=True,
        url_path="un-claim",
    )
    def un_claim(self, request, *args, **kwargs):
        """ anyone  who is a salesperson can un-claim a lead that is claimed_by them """
        lead = self.get_object()

        lead.claimed_by = None
        lead.status = None
        lead.expected_close_date = None
        # delete lead forecast
        try:
            if lead.forecast:
                Forecast.objects.get(lead=lead).delete()
        except Forecast.DoesNotExist:
            pass
        lead.amount = 0
        lead.save()
        emit_event(lead_constants.LEAD_RELEASED, request.user, lead)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=["POST"],
        permission_classes=(IsSalesPerson,),
        detail=True,
        url_path="close",
    )
    def close_lead(self, request, *args, **kwargs):
        # TODO - add CanEditResourceOrReadOnly to ensure person closing is person claiming 05/02/20
        """ special endpoint to close a lead, requires a contract and a closing amount
            file must already exist and is expected to be identified by an ID
        """
        try:
            closing_amount = request.data.get("closing_amount")
            contract = request.data.get("contract")
        except KeyError:
            raise ValidationError(
                {"detail": "Closing Amount and Contract Required"})
        lead = self.get_object()
        try:
            contract = File.objects.get(pk=contract)
        except File.DoesNotExist:
            raise ValidationError({"detail": "File Not Found"})
        contract.doc_type = lead_constants.FILE_TYPE_CONTRACT
        contract.save()
        lead.status = lead_constants.LEAD_STATUS_CLOSED
        lead.closing_amount = closing_amount
        lead.save()
        emit_event(lead_constants.LEAD_CLOSED, request.user, lead)
        return Response()


class ListViewSet(
    viewsets.GenericViewSet,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
):
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (IsSalesPerson, CanEditResourceOrReadOnly)
    filter_class = lead_filters.ListFilterSet
    serializer_class = lead_serializers.ListSerializer
    filter_backends = (
        filters.OrderingFilter,
        DjangoFilterBackend,
    )
    # Explicit fields the API may be ordered against
    ordering_fields = ("title",)

    def get_queryset(self):
        return List.objects.for_user(self.request.user)

    def create(self, request, *args, **kwargs):
        """ manually set  created_by """
        user = request.user

        data = dict(request.data)
        # make sure the user that created the lead is in the created_by field

        data["created_by"] = user.id
        serializer = self.serializer_class(
            data=data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):

        data = dict(request.data)
        # do not allow users to change the created_by  info if added
        if "created_by" in data.keys():
            del data["created_by"]
        # do not allow updating on lists here as it may require the whole list to be sent back
        if "leads" in data.keys():
            del data["leads"]

        serializer = self.serializer_class(
            self.get_object(), data=data, context={"request": request}, partial=True
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    @action(
        methods=["POST"],
        permission_classes=(IsSalesPerson,),
        detail=True,
        url_path="add-to-list",
    )
    def add_to_list(self, request, *args, **kwargs):
        """ End point to allow addition of leads to list after created """
        l = self.get_object()
        # TODO: Check if lead is in org 05/02/20
        new_leads = request.data.get("leads", [])
        for lead in new_leads:
            try:
                l.leads.add(lead)
                l.save()
            except IntegrityError:
                # lead already on list so just skip
                pass

        serializer = self.serializer_class(self.get_object())
        return Response(serializer.data)

    @action(
        methods=["post"],
        permission_classes=(IsSalesPerson,),
        detail=True,
        url_path="remove-from-list",
    )
    def remove_from_list(self, request, *args, **kwargs):
        """ End point to allow removal of leads to list after created """
        l = self.get_object()
        # TODO: Check if lead is in org 05/02/20
        remove_leads = request.data.get("leads", [])
        for lead in remove_leads:
            l.leads.remove(lead)
            l.save()

        serializer = self.serializer_class(self.get_object())
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)

    @action(
        methods=["post"],
        permission_classes=(IsSalesPerson,),
        detail=False,
        url_path="bulk-update",
    )
    def bulk_update(self, request, *args, **kwargs):
        """ End point to allow for
        All leads in request params to be processed to only be in the lists present in request params"""
        for lead_id in request.data["leads"]:
            try:
                Lead.objects.get(pk=lead_id).lists.set(request.data["lists"])
            except Lead.DoesNotExist:
                raise ValidationError(
                    {"detail": f"Invalid Lead ID: {lead_id}"})
        return Response(status=status.HTTP_204_NO_CONTENT)


class NoteViewSet(
    viewsets.GenericViewSet,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
):
    """ Any one in org can create/edit/delete Notes on leads """

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (IsSalesPerson,)
    serializer_class = lead_serializers.NoteSerializer
    filter_class = lead_filters.NoteFilterSet

    def get_queryset(self):
        return Note.objects.for_user(self.request.user)

    def create(self, request, *args, **kwargs):
        u = request.user
        d = request.data
        d["created_by"] = u.id
        serializer = self.serializer_class(
            data=d, context={"request": request})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        emit_event(lead_constants.NOTE_CREATED, u, serializer.instance)
        return Response(serializer.data)

    @action(
        methods=["post"],
        permission_classes=(IsSalesPerson,),
        detail=False,
        url_path="bulk",
    )
    def bulk_create(self, request, *args, **kwargs):
        """Bulk create notes for multiple leads."""
        user = request.user
        data = dict(request.data)

        # make sure the user that created the lead is in the created_by field
        data["created_by"] = user.id

        notes_created = list()
        for lead in request.data.get("created_for", []):
            # decision here to create a new note for each lead to make them individually editable
            # TODO: check lead in org 05/02/20 PB
            d = {
                "title": data["note"]["title"],
                "content": data["note"]["content"],
                "created_for": lead,
                "created_by": user.id,
            }
            serializer = self.serializer_class(
                data=d, context={"request": request})
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            emit_event(lead_constants.NOTE_CREATED, user, serializer.instance)
            notes_created.append(serializer.data)
        return Response({"detail": notes_created})

    def update(self, request, *args, **kwargs):
        user = request.user
        data = dict(request.data)
        # cannot update created by
        # cannot update created for
        d = {
            "title": data["note"]["title"],
            "content": data["note"]["content"],
            "updated_by": user.id,
        }
        serializer = self.serializer_class(
            self.get_object(), data=d, context={"request": request}, partial=True
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        emit_event(lead_constants.NOTE_UPDATED, user, serializer.instance)
        return Response(serializer.data)


class ForecastViewSet(
    viewsets.GenericViewSet,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
):
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (IsSalesPerson,)
    serializer_class = lead_serializers.ForecastSerializer
    filter_class = lead_filters.ForecastFilterSet
    # TODO :- log activity 05/02/20 PB

    def get_queryset(self):
        return Forecast.objects.for_user(self.request.user)


class CallNoteViewSet(
    viewsets.GenericViewSet,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
):
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (IsSalesPerson,)
    serializer_class = lead_serializers.CallNoteSerializer
    filter_class = lead_filters.CallNoteFilterSet

    def get_queryset(self):
        return CallNote.objects.for_user(self.request.user)

    def create(self, request, *args, **kwargs):
        u = request.user
        d = request.data
        d["created_by"] = u.id
        serializer = self.serializer_class(
            data=d, context={"request": request})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        emit_event(lead_constants.CALL_NOTE_CREATED, u, serializer.instance)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        u = request.user
        d = request.data
        d["updated_by"] = u.id
        serializer = self.serializer_class(
            self.get_object(), data=d, context={"request": request}, partial=True
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        emit_event(lead_constants.CALL_NOTE_UPDATED, u, serializer.instance)
        return Response(serializer.data)


class ReminderViewSet(
    viewsets.GenericViewSet,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
):
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (IsSalesPerson,)
    serializer_class = lead_serializers.ReminderSerializer

    def get_queryset(self):
        return Reminder.objects.for_user(self.request.user)

    def create(self, request, *args, **kwargs):
        """ can create multiple leads """
        user = request.user
        # check if lead is in users lead list
        leads = request.data.get("created_for", [])
        created = list()
        if len(leads) < 1:
            raise ValidationError(
                {"detail": "lead or leads required in created_for"})
        # TODO: change this to create a list of items not created if a user does not exist instead
        for lead in leads:
            try:
                Lead.objects.for_user(request.user).get(pk=lead)
            except Lead.DoesNotExist:
                raise PermissionDenied()
            data = request.data.get("reminder", None)
            data["created_for"] = lead
            data["created_by"] = user.id

            serializer = self.serializer_class(
                data=data, context={"request": request})
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            created.append(serializer.data)
            return Response(data=created, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        """ can create multiple leads """
        user = request.user
        # remove any lead info
        data = dict(request.data.get("reminders"))
        data.pop("created_for", None)
        data.pop("created_by", None)
        data["updated_by"] = user.id
        reminder = self.get_object()
        serializer = self.serializer_class(
            reminder, data=data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        # check if a notification has been created, if the datetime has been updated and is out of range remove it

        return Response(serializer.data)

    @action(methods=["POST"], detail=True, url_path="mark-as-viewed")
    def mark_as_viewed(self, request, *args, **kwargs):
        u = request.user
        self.get_object().mark_as_viewed(u)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=["POST"], detail=True, url_path="mark-as-completed")
    def mark_as_completed(self, request, *args, **kwargs):
        u = request.user
        self.get_object().mark_as_completed(u)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ActionChoiceViewSet(
    viewsets.GenericViewSet,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
):
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (IsOrganizationManager,)
    serializer_class = lead_serializers.ActionChoiceSerializer
    filter_backends = (
        DjangoFilterBackend,
        lead_filters.LeadRatingOrderFiltering,
    )
    ordering = ("title",)

    def get_queryset(self):
        return ActionChoice.objects.for_user(self.request.user)

    def create(self, request, *args, **kwargs):
        user = request.user
        data = dict(request.data)
        data["organization"] = user.organization.id
        serializer = self.serializer_class(
            data=data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        # make sure org is not changed
        data = dict(request.data)
        if "organization" in data.keys():
            del data["organization"]

        serializer = self.serializer_class(
            self.get_object(), data=data, context={"request": request}, partial=True
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)


class ActionViewSet(
    viewsets.GenericViewSet,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
):
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (IsSalesPerson,)
    serializer_class = lead_serializers.ActionSerializer

    def get_queryset(self):
        return Action.objects.for_user(self.request.user)

    def create(self, request, *args, **kwargs):
        u = request.user
        d = request.data
        d["created_by"] = u.id
        serializer = self.serializer_class(
            data=d, context={"request": request})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        emit_event(lead_constants.ACTION_CREATED, u, serializer.instance)
        return Response(serializer.data)

    @action(
        methods=["post"],
        permission_classes=(IsSalesPerson,),
        detail=False,
        url_path="bulk",
    )
    def bulk_create(self, request, *args, **kwargs):
        """This expects an array of multiple leads to apply action to.

        It is a design decision to create separate actions per lead.
        """
        action_data = request.data.get("action", None)
        if not action_data:
            raise ValidationError(detail={"detail": "Action data Required"})

        leads = request.data.get("leads", None)
        if not leads:
            raise ValidationError(detail={"detail": "Leads Required"})
        created = list()
        for l in leads:
            d = {
                "created_by": str(request.user.id),
                "action_type": action_data["action_type"],
                "action_detail": action_data["action_detail"],
                "lead": l,
            }
            serializer = self.serializer_class(
                data=d, context={"request": request})
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            created.append(serializer.data)
            emit_event(lead_constants.ACTION_CREATED,
                       request.user, serializer.instance)
        return Response({"created": created})

    def update(self, request, *args, **kwargs):
        data = dict(request.data)
        serializer = self.serializer_class(
            self.get_object(), data=data, context={"request": request}, partial=True
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)


class FileViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
    mixins.DestroyModelMixin,
):
    """API to attach files to Leads.

    NOTE: Files can currently not be deleted
    """

    serializer_class = lead_serializers.FileSerializer
    permission_classes = (IsSuperUser | IsSalesPerson,)
    filter_class = lead_filters.FileFilterSet

    def get_queryset(self):
        return File.objects.for_user(self.request.user)

    def create(self, request, *args, **kwargs):
        data = request.data
        serializer = self.serializer_class(
            data=data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data)
