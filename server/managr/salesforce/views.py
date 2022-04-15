from audioop import tostereo
import logging
import random
import pytz
import json
from urllib.parse import unquote
from datetime import datetime

from .routes import routes
import time
from background_task.models import CompletedTask
from django.db.models import Q
from django.utils import timezone
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
from managr.slack import constants as slack_const
from managr.api.emails import send_html_email
from managr.slack.helpers import requests as slack_requests
from managr.slack.models import OrgCustomSlackForm
from managr.slack.helpers.block_sets import get_block_set
from managr.slack.models import OrgCustomSlackFormInstance
from managr.core.models import User
from .models import (
    SObjectField,
    SObjectValidation,
    SObjectPicklist,
    SFResourceSync,
    MeetingWorkflow,
)
from .serializers import (
    SalesforceAuthSerializer,
    SObjectFieldSerializer,
    SObjectValidationSerializer,
    SObjectPicklistSerializer,
    MeetingWorkflowSerializer,
)
from .adapter.models import SalesforceAuthAccountAdapter
from .background import (
    emit_gen_next_sync,
    emit_add_update_to_sf,
    emit_gen_next_object_field_sync,
    emit_generate_form_template,
    emit_add_update_to_sf,
    _send_instant_alert,
    _process_pipeline_sync,
    emit_meeting_workflow_tracker,
)
from managr.salesforce.utils import process_text_field_format
from managr.salesforce import constants as sf_consts
from managr.salesforce.adapter.exceptions import (
    TokenExpired,
    FieldValidationError,
    RequiredFieldError,
    UnhandledSalesforceError,
    SFNotFoundError,
    InvalidRefreshToken,
)

from .filters import SObjectFieldFilterSet, SalesforceSObjectFilterSet

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

    @action(
        methods=["post"],
        permission_classes=[permissions.IsAuthenticated],
        detail=False,
        url_path="update-pipeline-fields",
    )
    def update_pipeline_fields(self, request, *args, **kwargs):
        user = self.request.user
        sf = user.salesforce_account
        data = self.request.data
        ids = data.get("field_ids")
        for id in ids:
            if id not in sf.extra_pipeline_fields:
                sf.extra_pipeline_fields.append(id)
        sf.save()
        return Response()

    @action(
        methods=["post"],
        permission_classes=[permissions.IsAuthenticated],
        detail=False,
        url_path="remove-pipeline-fields",
    )
    def remove_pipeline_fields(self, request, *args, **kwargs):
        user = self.request.user
        sf = user.salesforce_account
        data = self.request.data
        ids = data.get("field_ids")
        for id in ids:
            sf.extra_pipeline_fields.remove(id)
        sf.save()
        return Response()


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
    filter_class = SalesforceSObjectFilterSet

    def get_serializer_class(self):
        param_sobject = self.request.GET.get("sobject")
        sobject = routes[param_sobject]
        return sobject["serializer"]

    def get_queryset(self):
        param_sobject = self.request.GET.get("sobject")
        param_resource_id = json.loads(self.request.GET.get("resource_id", None))
        for_filter = json.loads(self.request.GET.get("for_filter", None))
        if param_sobject == "User":
            return User.objects.filter(organization=self.request.user.organization)
        sobject = routes[param_sobject]

        query = (
            sobject["model"].objects.filter(id=param_resource_id)
            if param_resource_id
            else sobject["model"].objects.for_user(self.request.user)
        )
        if for_filter:
            filtered_query = SalesforceSObjectFilterSet.for_filter(
                query, json.loads(self.request.GET.get("filters"))
            )
            return filtered_query
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
        attempts = 1
        while True:
            try:
                current_values = slack_form.generate_form_values()
                data = {
                    "form_id": str(slack_form.id),
                    "current_values": current_values,
                }
                break
            except TokenExpired:
                if attempts >= 5:
                    logger.info(f"CREATE FORM INSTANCE TOKEN EXPIRED ERROR ---- {e}")

                else:
                    user.salesforce_account.regenerate_token()
                    attempts += 1
            except Exception as e:
                if attempts >= 5:

                    logger.info(f"CREATE FORM INSTANCE ERROR ---- {e}")

                    data = {"error": str(e)}
                else:
                    attempts += 1

        if resource_type == "Opportunity" and form_type == "UPDATE":
            current_products = user.salesforce_account.list_resource_data(
                "OpportunityLineItem",
                0,
                filter=[
                    "AND IsDeleted = false",
                    f"AND OpportunityId = '{slack_form.resource_object.integration_id}'",
                ],
            )
            product_values = [product.as_dict for product in current_products]
            data["current_products"] = product_values
        return Response(data=data)

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
        logger.info(f"UPDATE START ---- {data}")

        user = User.objects.get(id=self.request.user.id)
        form_id = data.get("form_id")
        form_data = data.get("form_data")
        alert_instance_id = data.get("alert_instance", None)
        main_form = OrgCustomSlackFormInstance.objects.get(id=form_id)
        stage_forms = []
        stage_form_data_collector = {}
        for form in stage_forms:
            form.save_form(form_data, False)
            stage_form_data_collector = {**stage_form_data_collector, **form.saved_data}
        if not len(stage_forms):
            main_form.save_form(form_data, False)
        all_form_data = {**stage_form_data_collector, **main_form.saved_data}
        formatted_saved_data = process_text_field_format(
            str(user.id), main_form.template.resource, all_form_data
        )
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
                logger.info(f"UPDATE FIELD VALIDATION ERROR {e}")
                data = {"success": False, "error": str(e)}
                break

            except RequiredFieldError as e:
                logger.info(f"UPDATE REQUIRED FIELD ERROR {e}")

                data = {"success": False, "error": str(e)}
                break
            except UnhandledSalesforceError as e:
                logger.info(f"UPDATE UNHANDLED SF ERROR {e}")
                data = {"success": False, "error": str(e)}
                break

            except SFNotFoundError as e:
                logger.info(f"UPDATE SF NOT FOUND ERROR {e}")
                data = {"success": False, "error": str(e)}
                break

            except TokenExpired:
                if attempts >= 5:
                    logger.info(f"UPDATE REFRESHING TOKEN ERROR {e}")
                    data = {"success": False, "error": "Could not refresh token"}
                    break
                else:
                    sf.regenerate_token()
                    attempts += 1

            except ConnectionResetError:
                if attempts >= 5:
                    logger.info(f"UPDATE CONNECTION RESET ERROR {e}")
                    data = {"success": False, "error": "Connection was reset"}
                    break
                else:
                    time.sleep(2)
                    attempts += 1
            except Exception as e:
                logger.info(f"UPDATE ERROR {e}")
                break
        if (
            all_form_data.get("meeting_comments") is not None
            and all_form_data.get("meeting_type") is not None
        ):
            emit_add_update_to_sf(str(main_form.id))
        if len(user.slack_integration.realtime_alert_configs):
            _send_instant_alert([form_id])
        if alert_instance_id:
            from managr.alerts.models import AlertInstance

            instance = AlertInstance.objects.get(id=alert_instance_id)
            current_forms.update(
                is_submitted=True,
                update_source="pipeline",
                submission_date=timezone.now(),
                alert_instance_id=instance,
            )
        else:
            current_forms.update(
                is_submitted=True, update_source="pipeline", submission_date=timezone.now()
            )
        value_update = main_form.resource_object.update_database_values(all_form_data)
        return Response(data={"success": True})
        # try:
        #     text = f"Managr updated {main_form.resource_type}"
        #     message = f":white_check_mark: Successfully updated *{main_form.resource_type}* _{main_form.resource_object.name}_"
        #     slack_requests.send_ephemeral_message(
        #         user.slack_integration.channel,
        #         user.organization.slack_integration.access_token,
        #         user.slack_integration.slack_id,
        #         text=text,
        #         block_set=get_block_set(
        #             "success_modal", {"message": message, "u": user.id, "form_ids": form_id}
        #         ),
        #     )

        # except Exception as e:
        #     logger.exception(
        #         f"Failed to send ephemeral message to user informing them of successful update {user.email} {e}"
        #     )
        # return Response(data=data)

    @action(
        methods=["get"],
        permission_classes=[permissions.IsAuthenticated],
        detail=False,
        url_path="confirm-update",
    )
    def confirm_update(self, request, *args, **kwargs):
        task_hash = self.request.GET.get("task_hash")
        verbose_name = self.request.GET.get("verbose_name")
        logger.info(
            f"CONFIRM UPDATE START FOR TASK HASH:<{task_hash}>, VERBOSE NAME:<{verbose_name}>"
        )

        attempts = 1
        has_error = False
        while True:
            if attempts >= 5:
                has_error = True
                break
            try:
                task = CompletedTask.objects.filter(task_hash=task_hash).order_by("-run_at").first()
                logger.info(f"CONFIRM UPDATE TASK ---- {task}")
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

    @action(
        methods=["post"],
        permission_classes=[permissions.IsAuthenticated],
        detail=False,
        url_path="send-recap",
    )
    def send_recaps(self, request, *args, **kwargs):
        data = self.request.data
        form_ids = data["form_ids"]
        bulk_status = data["bulk"]
        user = User.objects.get(id=self.request.user.id)
        main_form = OrgCustomSlackFormInstance.objects.get(id=form_ids[0])
        if len(user.slack_integration.realtime_alert_configs):
            _send_instant_alert(form_ids)
        try:
            if bulk_status:
                plural = (
                    f"Opportunities"
                    if main_form.resource_type == "Opportunity"
                    else f"{main_form.resource_type}s"
                )
                text = "Manager Bulk Update"
                message = f":white_check_mark: Successfully updated {len(form_ids)} {plural}"
            else:

                text = f"Managr update {main_form.resource_type}"
                message = f":white_check_mark: Successfully updated *{main_form.resource_type}* {main_form.resource}"
            slack_requests.send_ephemeral_message(
                user.slack_integration.channel,
                user.organization.slack_integration.access_token,
                user.slack_integration.slack_id,
                text=text,
                block_set=get_block_set(
                    "bulk_recap_block_set",
                    {
                        "message": message,
                        "u": user.id,
                        "form_ids": ",".join(form_ids),
                        "bulk_status": bulk_status,
                    },
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
        url_path="resource-sync",
    )
    def resource_sync(self, request, *args, **kwargs):
        user = self.request.user
        operations = ["Account", "Lead", "Opportunity", "Contact"]
        currenttime = datetime.now()
        to_sync_ids = []
        synced_ids = []
        if user.user_level in ["MANAGER", "SDR"]:
            users = User.objects.filter(Q(organization=user.organization, is_active=True))
            for user in users:
                if hasattr(user, "salesforce_account"):
                    sync = SFResourceSync.objects.create(
                        user=user,
                        operations_list=operations,
                        operation_type=sf_consts.SALESFORCE_RESOURCE_SYNC,
                    )
                    user_timezone = pytz.timezone(user.timezone)
                    current = (
                        pytz.utc.localize(currenttime)
                        .astimezone(user_timezone)
                        .strftime("%Y-%m-%d %H:%M:%S")
                    )
                    user.salesforce_account.last_sync_time = current
                    user.salesforce_account.save()
                    to_sync_ids.append(str(sync.id))
                    _process_pipeline_sync(str(sync.id))
        else:
            sync = SFResourceSync.objects.create(
                user=user,
                operations_list=operations,
                operation_type=sf_consts.SALESFORCE_RESOURCE_SYNC,
            )
            user_timezone = pytz.timezone(user.timezone)

            current = (
                pytz.utc.localize(currenttime)
                .astimezone(user_timezone)
                .strftime("%Y-%m-%d %H:%M:%S")
            )
            user.salesforce_account.last_sync_time = current
            user.salesforce_account.save()
            to_sync_ids.append(str(sync.id))
            _process_pipeline_sync(str(sync.id))
        attempts = 1
        logger.info(f"TO SYNC: {to_sync_ids}")
        logger.info(f"SYNCED: {synced_ids}")
        has_error = False
        while True:
            for index, id in enumerate(to_sync_ids):
                resource_sync = SFResourceSync.objects.get(id=id)
                try:
                    if len(resource_sync.operations) < 1:
                        has_error = True
                        break
                    if resource_sync.status == "Completed":
                        synced_ids.append(id)
                        to_sync_ids.pop(index)
                        logger.info(f"IN LOOP TO SYNC: {to_sync_ids}")
                        logger.info(f"IN LOOP SYNCED: {synced_ids}")
                        if len(to_sync_ids) == 0:
                            break
                        else:
                            continue
                    else:
                        attempts += 1
                        sleep = 1 * 1.15 ** attempts + random.uniform(0, 1)
                        time.sleep(sleep)
                except InvalidRefreshToken:
                    has_error = True
                    break
                except Exception as e:
                    if attempts >= 5:
                        has_error = True
                        logger.exception(f"Failed to receive complete status from sync from {e}")
                        break
                    else:
                        attempts += 1
            if len(to_sync_ids) == 0 or has_error:
                break
        data = {"success": False} if has_error else {"success": True}
        return Response(data=data)


class MeetingWorkflowViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):
    serializer_class = MeetingWorkflowSerializer
    filter_backends = (
        DjangoFilterBackend,
        filters.SearchFilter,
    )

    def get_queryset(self):
        user = self.request.user
        curr_date = datetime.now()
        start = curr_date.replace(hour=0, minute=0)
        end = curr_date.replace(hour=23, minute=59)
        meetings = MeetingWorkflow.objects.filter(
            Q(user=user, datetime_created__range=(start, end))
        )
        return meetings

    @action(
        methods=["post"],
        permission_classes=[permissions.IsAuthenticated],
        detail=False,
        url_path="map-workflow",
    )
    def map_workflow(self, request, *args, **kwargs):
        request_data = self.request.data
        workflow = MeetingWorkflow.objects.get(id=request_data.get("workflow_id"))
        resource_id = request_data.get("resource_id")
        resource_type = request_data.get("resource_type")
        workflow.resource_id = resource_id
        workflow.resource_type = resource_type
        workflow.save()
        data = MeetingWorkflowSerializer(instance=workflow).data
        return Response(data=data)

    @action(
        methods=["post"],
        permission_classes=[permissions.IsAuthenticated],
        detail=False,
        url_path="update-participant",
    )
    def update_participant(self, request, *args, **kwargs):
        from managr.organization.models import ContactAdapter

        request_data = self.request.data
        workflow = MeetingWorkflow.objects.get(id=request_data.get("workflow_id"))
        meeting = workflow.meeting if workflow.meeting else workflow.non_zoom_meeting
        contact = dict(
            *filter(
                lambda contact: contact["_tracking_id"] == request_data.get("tracking_id"),
                meeting.participants,
            )
        )
        form = (
            workflow.forms.get(id=contact["_form"])
            if workflow.meeting
            else OrgCustomSlackFormInstance.objects.get(id=contact.get("_form"))
        )
        form.save_form(request_data.get("form_data"))
        user_id = workflow.user.id if type else workflow.user_id
        # reconstruct the current data with the updated data
        adapter = ContactAdapter.from_api(
            {**contact.get("secondary_data", {}), **form.saved_data}, str(user_id)
        )
        new_contact = {
            **contact,
            **adapter.as_dict,
            "id": contact.get("id", None),
            "__has_changes": True,
        }
        if type:
            part_index = None
            for index, participant in enumerate(workflow.participants):
                if participant["_tracking_id"] == new_contact["_tracking_id"]:
                    part_index = index
                    break
            workflow.participants = [
                *workflow.participants[:part_index],
                new_contact,
                *workflow.participants[part_index + 1 :],
            ]
            workflow.save()
        else:
            part_index = None
            for index, participant in enumerate(meeting.participants):
                if participant["_tracking_id"] == new_contact["_tracking_id"]:
                    part_index = index
                    break
            meeting.participants = [
                *meeting.participants[:part_index],
                new_contact,
                *meeting.participants[part_index + 1 :],
            ]
            meeting.save()
        return Response()

    @action(
        methods=["post"],
        permission_classes=[permissions.IsAuthenticated],
        detail=False,
        url_path="remove-participant",
    )
    def remove_participant(self, request, *args, **kwargs):
        request_data = self.request.data
        workflow = MeetingWorkflow.objects.get(meeting=request_data.get("workflow_id"))
        meeting = workflow.meeting if workflow.meeting else workflow.non_zoom_meeting
        for i, part in enumerate(meeting.participants):
            if part["_tracking_id"] == request_data.get("tracking_id"):
                # remove its form if it exists
                if part["_form"] not in [None, ""]:
                    workflow.forms.filter(id=part["_form"]).delete()
                del meeting.participants[i]
                break
        meeting.save()
        return Response()

    @action(
        methods=["post"],
        permission_classes=[permissions.IsAuthenticated],
        detail=False,
        url_path="update-workflow",
    )
    def update_workflow(self, request, *args, **kwargs):
        request_data = self.request.data
        current_form_ids = request_data.get("form_ids")
        user = request.user
        workflow = MeetingWorkflow.objects.get(meeting=request_data.get("workflow_id"))

        forms = workflow.forms.filter(template__form_type=slack_const.FORM_TYPE_STAGE_GATING)
        current_form_ids = []
        if len(forms):
            for form in forms:
                current_form_ids.append(str(form.id))
                form.save_form(request_data.get("form_data"))
        # otherwise we save the meeting review form
        else:
            form = workflow.forms.filter(template__form_type=slack_const.FORM_TYPE_UPDATE).first()
            current_form_ids.append(str(form.id))
            form.save_form(request_data.get("form_data"))
        if workflow.meeting:
            contact_forms = workflow.forms.filter(
                template__resource=slack_const.FORM_RESOURCE_CONTACT
            )
        else:
            contact_ids = [
                participant["_form"] for participant in workflow.non_zoom_meeting.participants
            ]
            contact_forms = OrgCustomSlackFormInstance.objects.filter(id__in=contact_ids)
        ops = [
            f"{sf_consts.MEETING_REVIEW__SAVE_CALL_LOG}.{str(workflow.id)}",
            # save meeting data
        ]
        if request_data.get("form_data")["meeting_subject"] is not "No Update":
            ops.append(f"{sf_consts.MEETING_REVIEW__UPDATE_RESOURCE}.{str(workflow.id)}",)
        for form in contact_forms:
            if form.template.form_type == slack_const.FORM_TYPE_CREATE:
                ops.append(
                    f"{sf_consts.MEETING_REVIEW__CREATE_CONTACTS}.{str(workflow.id)},{str(form.id)}"
                )
            else:
                ops.append(
                    f"{sf_consts.MEETING_REVIEW__UPDATE_CONTACTS}.{str(workflow.id)},{str(form.id)}"
                )

        # emit all events
        print(ops)
        if len(workflow.operations_list):
            workflow.operations_list = [*workflow.operations_list, *ops]
        else:
            workflow.operations_list = ops

        if len(user.slack_integration.realtime_alert_configs):
            _send_instant_alert(current_form_ids)

        workflow.save()
        workflow.begin_tasks()
        emit_meeting_workflow_tracker(str(workflow.id))
        data = {"success": True}
        return Response(data=data)

