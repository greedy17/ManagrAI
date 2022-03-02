import logging
import random
from faker import Faker
from urllib.parse import urlencode, unquote
from datetime import datetime
from .routes import routes
import time
from background_task.models import CompletedTask
from django.db.models import Q
from django.utils import timezone
from django.core.management import call_command
from django.shortcuts import render, redirect
from django.conf import settings
from django.template.loader import render_to_string
from django_filters.rest_framework import DjangoFilterBackend
from django.db import IntegrityError
from managr.salesforce.routes import routes as model_routes
from rest_framework.decorators import action
from rest_framework import (
    filters,
    permissions,
    mixins,
    viewsets,
)
from rest_framework.decorators import (
    api_view,
    permission_classes,
)
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from managr.core.models import User
from managr.api.emails import send_html_email
from managr.slack.helpers import requests as slack_requests
from managr.slack.models import OrgCustomSlackForm
from managr.slack.helpers.block_sets import get_block_set

from .models import (
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
    emit_gen_next_sync,
    emit_gen_next_object_field_sync,
    emit_generate_form_template,
)
from managr.salesforce.adapter.exceptions import (
    TokenExpired,
    FieldValidationError,
    RequiredFieldError,
    UnhandledSalesforceError,
    SFNotFoundError,
)

from .filters import SObjectFieldFilterSet

logger = logging.getLogger("managr")


@api_view(["post"])
@permission_classes([permissions.IsAuthenticated])
def authenticate(request):
    code = request.data.get("code", None)
    if code:
        data = SalesforceAuthAccountAdapter.create_account(unquote(code), str(request.user.id))
        serializer = SalesforceAuthSerializer(data=data.as_dict)
        try:
            serializer.is_valid(raise_exception=True)
            serializer.save()
        except IntegrityError as e:
            print(e)
            raise ValidationError(detail="An integration with this salesforce id already exists")
        # create sf sync object

        operations = [
            *serializer.instance.field_sync_opts,
            *serializer.instance.validation_sync_opts,
        ]

        scheduled_time = timezone.now()
        formatted_time = scheduled_time.strftime("%Y-%m-%dT%H:%M%Z")
        emit_gen_next_object_field_sync(str(request.user.id), operations, formatted_time)
        # generate forms
        if serializer.instance.user.is_admin:
            emit_generate_form_template(data.user)
        user = User.objects.get(id=request.user.id)
        sync_operations = [*user.salesforce_account.resource_sync_opts]
        sync_time = (timezone.now() + timezone.timedelta(minutes=5)).strftime("%Y-%m-%dT%H:%M%Z")
        emit_gen_next_sync(str(request.user.id), sync_operations, sync_time)
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


# @api_view(["get"])
# @permission_classes([permissions.IsAuthenticated])
# def get_public_fields(request):
#     public_fields = SObjectField.objects.filter(is_public=True)
#     return Response({"data": json.dumps(public_fields)})


class SObjectValidationViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):
    serializer_class = SObjectValidationSerializer
    filter_fields = ("salesforce_object",)

    def get_queryset(self):
        return SObjectValidation.objects.for_user(self.request.user)


class PublicSObjectFieldViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):
    serializer_class = SObjectFieldSerializer
    filter_backends = (
        DjangoFilterBackend,
        filters.SearchFilter,
    )
    filter_class = SObjectFieldFilterSet

    def get_queryset(self):
        return SObjectField.objects.filter(is_public=True)


class SObjectFieldViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):
    serializer_class = SObjectFieldSerializer
    filter_backends = (
        DjangoFilterBackend,
        filters.SearchFilter,
    )
    search_fields = ("label",)
    filter_class = SObjectFieldFilterSet

    def get_queryset(self):
        return SObjectField.objects.for_user(self.request.user)


class SObjectPicklistViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):
    serializer_class = SObjectPicklistSerializer
    filter_fields = ("salesforce_object", "picklist_for")

    def get_queryset(self):
        return SObjectPicklist.objects.for_user(self.request.user)

    @action(
        methods=["get"],
        permission_classes=[permissions.IsAuthenticated],
        detail=False,
        url_path="refresh-stage",
    )
    def get_stage_picklist_values(self, request, *args, **kwargs):
        user = self.request.user

        attempts = 1
        while True:
            sf = user.salesforce_account
            try:
                res = sf.get_stage_picklist_values("Opportunity")
                break
            except TokenExpired:
                if attempts >= 3:
                    raise ValidationError()
                else:
                    sf.regenerate_token()
                    attempts += 1

        existing = SObjectPicklist.objects.filter(
            picklist_for=res.picklist_for,
            salesforce_account_id=res.salesforce_account,
            salesforce_object="Opportunity",
        ).first()
        if existing:
            serializer = SObjectPicklistSerializer(data=res.as_dict, instance=existing)
        else:
            serializer = SObjectPicklistSerializer(data=res.as_dict)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response()


class SalesforceSObjectViewSet(
    viewsets.GenericViewSet,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.UpdateModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
):
    def get_serializer_class(self):
        param_sobject = self.request.GET.get("sobject")
        sobject = routes[param_sobject]
        return sobject["serializer"]

    def get_queryset(self):
        param_sobject = self.request.GET.get("sobject")
        param_resource_id = self.request.GET.get("resource_id", None)
        sobject = routes[param_sobject]
        query = (
            sobject["model"].objects.get(id=param_resource_id)
            if param_resource_id
            else sobject["model"].objects.for_user(self.request.user)
        )
        return query

    @action(
        methods=["get"],
        permission_classes=[permissions.IsAuthenticated],
        detail=False,
        url_path="notes",
    )
    def get_resource_notes(self, request, *args, **kwargs):
        from managr.slack.models import OrgCustomSlackFormInstance

        resource_id = self.request.GET.get("resource_id")
        note_data = (
            OrgCustomSlackFormInstance.objects.filter(resource_id=resource_id)
            .filter(is_submitted=True)
            .values(
                "submission_date",
                "saved_data__meeting_type",
                "saved_data__meeting_comments",
                "saved_data__StageName",
                "previous_data__StageName",
            )
        )
        if note_data:
            return Response(data=note_data)
        return Response(data=[])

    @action(
        methods=["get"],
        permission_classes=[permissions.IsAuthenticated],
        detail=False,
        url_path="create-form-instance",
    )
    def create_form_instance(self, request, *args, **kwargs):
        from managr.slack.models import OrgCustomSlackForm, OrgCustomSlackFormInstance

        user = self.request.user
        form_type = self.request.GET.get("form_type")
        resource_type = self.request.GET.get("resource_type")
        resource_id = self.request.GET.get("resource_id", None)
        template = (
            OrgCustomSlackForm.objects.for_user(user)
            .filter(Q(resource=resource_type, form_type=form_type))
            .first()
        )
        slack_form = (
            OrgCustomSlackFormInstance.objects.create(
                template=template, user=user, resource_id=resource_id
            )
            if form_type == "UPDATE"
            else OrgCustomSlackFormInstance.objects.create(template=template, user=user)
        )

        return Response(data={"form_id": str(slack_form.id)})

    @action(
        methods=["post"],
        permission_classes=[permissions.IsAuthenticated],
        detail=False,
        url_path="update",
    )
    def update_resource(self, request, *args, **kwargs):
        from managr.slack.models import OrgCustomSlackFormInstance
        from managr.core.models import User

        data = self.request.data
        user = User.objects.get(id=self.request.user.id)
        form_id = data.get("form_id")
        form_data = data.get("form_data")
        main_form = OrgCustomSlackFormInstance.objects.get(id=form_id)
        stage_forms = []
        stage_form_data_collector = {}
        for form in stage_forms:
            form.save_form(form_data, False)
            stage_form_data_collector = {**stage_form_data_collector, **form.saved_data}
        if not len(stage_forms):
            main_form.save_form(form_data, False)
        all_form_data = {**stage_form_data_collector, **main_form.saved_data}
        current_forms = user.custom_slack_form_instances.filter(id__in=[form_id])
        data = None
        attempts = 1
        while True:
            sf = user.salesforce_account
            try:
                resource = main_form.resource_object.update_in_salesforce(all_form_data, True)
                data = {
                    "success": True,
                    "task_hash": resource["task_hash"],
                    "verbose_name": resource["verbose_name"],
                }
                break
            except FieldValidationError as e:
                data = {"success": False, "error": str(e)}
                break

            except RequiredFieldError as e:
                data = {"success": False, "error": str(e)}
                break
            except UnhandledSalesforceError as e:
                data = {"success": False, "error": str(e)}
                break

            except SFNotFoundError as e:
                data = {"success": False, "error": str(e)}
                break

            except TokenExpired:
                if attempts >= 5:
                    data = {"success": False, "error": "Could not refresh token"}
                    break
                else:
                    sf.regenerate_token()
                    attempts += 1

            except ConnectionResetError:
                if attempts >= 5:
                    data = {"success": False, "error": "Connection was reset"}
                    break
                else:
                    time.sleep(2)
                    attempts += 1
        current_forms.update(
            is_submitted=True, update_source="pipeline", submission_date=timezone.now()
        )
        try:
            text = f"Managr updated {main_form.resource_type}"
            message = f":white_check_mark: Successfully updated *{main_form.resource_type}* _{main_form.resource_object.name}_"
            slack_requests.send_ephemeral_message(
                user.slack_integration.channel,
                user.organization.slack_integration.access_token,
                user.slack_integration.slack_id,
                text=text,
                block_set=get_block_set(
                    "success_modal", {"message": message, "u": user.id, "form_id": form_id}
                ),
            )

        except Exception as e:
            logger.exception(
                f"Failed to send ephemeral message to user informing them of successful update {user.email} {e}"
            )
        return Response(data=data)

    @action(
        methods=["get"],
        permission_classes=[permissions.IsAuthenticated],
        detail=False,
        url_path="confirm-update",
    )
    def confirm_update(self, request, *args, **kwargs):

        task_hash = self.request.GET.get("task_hash")
        verbose_name = self.request.GET.get("verbose_name")
        attempts = 1
        has_error = False
        while True:
            if attempts >= 10:
                has_error = True
                break
            try:
                task = CompletedTask.objects.filter(task_hash=task_hash).order_by("-run_at").first()
                if task and task.verbose_name == verbose_name:
                    break
                else:
                    attempts += 1
                    sleep = 1 * 2 ** attempts + random.uniform(0, 1)
                    time.sleep(sleep)
            except Exception as e:
                logger.exception(
                    f"Error retreiving update status from task {verbose_name}, <HASH: {task_hash}> because of: {e}"
                )
                attempts += 1
        if has_error:
            return Response(data={"success": False})
        return Response(data={"success": True})

    @action(
        methods=["post"],
        permission_classes=[permissions.IsAuthenticated],
        detail=False,
        url_path="create",
    )
    def create_resource(self, request, *args, **kwargs):
        from managr.slack.models import OrgCustomSlackFormInstance
        from managr.core.models import User

        data = self.request.data
        user = User.objects.get(id=self.request.user.id)
        form_id = data.get("form_id")
        form_data = data.get("form_data")
        main_form = OrgCustomSlackFormInstance.objects.get(id=form_id)
        stage_forms = []
        stage_form_data_collector = {}
        for form in stage_forms:
            form.save_form(form_data, False)
            stage_form_data_collector = {**stage_form_data_collector, **form.saved_data}
        if not len(stage_forms):
            main_form.save_form(form_data, False)

        all_form_data = {**stage_form_data_collector, **main_form.saved_data}

        data = None
        attempts = 1
        while True:
            sf = user.salesforce_account
            try:
                resource = model_routes[main_form.resource_type]["model"].create_in_salesforce(
                    all_form_data, user.id
                )
                data = {
                    "success": True,
                }
                break
            except FieldValidationError as e:
                data = {"success": False, "error": str(e)}
                break

            except RequiredFieldError as e:
                data = {"success": False, "error": str(e)}
                break
            except UnhandledSalesforceError as e:
                data = {"success": False, "error": str(e)}
                break

            except SFNotFoundError as e:
                data = {"success": False, "error": str(e)}
                break

            except TokenExpired:
                if attempts >= 5:
                    data = {"success": False, "error": "Could not refresh token"}
                    break
                else:
                    sf.regenerate_token()
                    attempts += 1

            except ConnectionResetError:
                if attempts >= 5:
                    data = {"success": False, "error": "Connection was reset"}
                    break
                else:
                    time.sleep(2)
                    attempts += 1
        return Response(data=data)
