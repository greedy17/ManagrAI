import logging
import requests
import json
from faker import Faker
from urllib.parse import urlencode, unquote
from datetime import datetime

from django.http import HttpResponse
from django.utils import timezone
from django.core.management import call_command
from django.shortcuts import render, redirect
from django.conf import settings
from django.template.loader import render_to_string

from rest_framework.views import APIView
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
from rest_framework.decorators import (
    api_view,
    permission_classes,
    authentication_classes,
)
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, PermissionDenied


from managr.api.decorators import log_all_exceptions
from managr.api.emails import send_html_email

from managr.slack.models import OrgCustomSlackForm
from .models import (
    SFSyncOperation,
    SFObjectFieldsOperation,
    SObjectField,
    SObjectValidation,
    SObjectPicklist,
)
from .serializers import (
    SalesforceAuthSerializer,
    SObjectFieldSerializer,
    SObjectValidationSerializer,
    SObjectPicklistSerializer,
)
from .adapter.models import SalesforceAuthAccountAdapter
from .background import (
    emit_sf_sync,
    emit_gen_next_sync,
    emit_gen_next_object_field_opp_sync,
    emit_generate_form_template,
    emit_sync_sobject_picklist,
)
from . import constants as sf_consts


@api_view(["post"])
@permission_classes([permissions.IsAuthenticated])
@log_all_exceptions
def authenticate(request):
    code = request.data.get("code", None)
    if code:
        data = SalesforceAuthAccountAdapter.create_account(unquote(code), str(request.user.id))
        serializer = SalesforceAuthSerializer(data=data.as_dict)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        # create sf sync object
        """
        operations = [
            sf_consts.RESOURCE_SYNC_CONTACT,
            sf_consts.RESOURCE_SYNC_ACCOUNT,
            sf_consts.RESOURCE_SYNC_OPPORTUNITY,
        ]
        scheduled_time = timezone.now()
        formatted_time = scheduled_time.strftime("%Y-%m-%dT%H:%M%Z")

        emit_gen_next_sync(str(request.user.id), operations, formatted_time)
        """
        operations = [
            f"{sf_consts.SALESFORCE_OBJECT_FIELDS}.{sf_consts.RESOURCE_SYNC_OPPORTUNITY}",
            f"{sf_consts.SALESFORCE_PICKLIST_VALUES}.{sf_consts.RESOURCE_SYNC_OPPORTUNITY}",
        ]
        if serializer.instance.user.is_admin:
            # we only need validations to show the user who is creating the forms

            operations.append(
                f"{sf_consts.SALESFORCE_VALIDATIONS}.{sf_consts.RESOURCE_SYNC_OPPORTUNITY}"
            )

        scheduled_time = timezone.now()
        formatted_time = scheduled_time.strftime("%Y-%m-%dT%H:%M%Z")
        emit_gen_next_object_field_opp_sync(str(request.user.id), operations, formatted_time)
        # generate forms
        if serializer.instance.user.is_admin:
            emit_generate_form_template(data.user)
        # initiate process
        return Response(data={"success": True})


@api_view(["get"])
@permission_classes([permissions.IsAuthenticated])
def salesforce_auth_link(request):
    link = SalesforceAuthAccountAdapter.generate_auth_link()
    return Response({"link": link})


@api_view(["post"])
@permission_classes([permissions.IsAuthenticated])
def revoke(request):
    user = request.user
    if hasattr(user, "salesforce_account"):
        sf_acc = user.salesforce_account
        sf_acc.revoke()
        if user.is_admin:
            OrgCustomSlackForm.objects.for_user(user).delete()
            # admins remove the forms since they created them to avoid duplication

        user_context = dict(organization=user.organization.name)
        admin_context = dict(
            id=str(user.id),
            email=user.email,
            is_admin=user.is_admin,
            revoked_at=datetime.now().date().strftime("%y-%m-%d"),
        )
        # send email to user
        subject = render_to_string("salesforce/access_token_revoked-subject.txt")
        recipient = [user.email]
        send_html_email(
            subject,
            "salesforce/access_token_revoked.html",
            settings.SERVER_EMAIL,
            recipient,
            context=user_context,
        )
        # send email to admin
        subject = render_to_string("salesforce/admin_access_token_revoked-subject.txt")
        recipient = [settings.STAFF_EMAIL]
        send_html_email(
            subject,
            "salesforce/admin_access_token_revoked.html",
            settings.SERVER_EMAIL,
            recipient,
            context={"data": admin_context},
        )
    return Response()


class SObjectValidationViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):
    serializer_class = SObjectValidationSerializer
    filter_fields = ("salesforce_object",)

    def get_queryset(self):
        return SObjectValidation.objects.for_user(self.request.user)


class SObjectFieldViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):
    serializer_class = SObjectFieldSerializer
    filter_fields = ("salesforce_object", "createable", "updateable")

    def get_queryset(self):
        return SObjectField.objects.for_user(self.request.user)


class SObjectPicklistViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):
    serializer_class = SObjectPicklistSerializer
    filter_fields = ("salesforce_object", "picklist_for")

    def get_queryset(self):
        return SObjectPicklist.objects.for_user(self.request.user)

