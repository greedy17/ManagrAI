import logging
import random
import pytz
import json
import uuid
from urllib.parse import unquote
from datetime import datetime

from .routes import routes
import time
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
    status,
    mixins,
    viewsets,
)

from rest_framework.decorators import (
    api_view,
    permission_classes,
)
from managr.core.permissions import IsStaff

from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from managr.core.models import User
from managr.slack import constants as slack_const
from managr.api.emails import send_html_email
from managr.slack.helpers import requests as slack_requests
from managr.slack.helpers.block_sets import get_block_set
from managr.slack.models import OrgCustomSlackFormInstance
from managr.salesforce.utils import process_text_field_format

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
    emit_gen_next_object_field_sync,
    emit_generate_form_template,
    _send_instant_alert,
    emit_meeting_workflow_tracker,
    create_form_instance,
    emit_process_bulk_update,
    emit_generate_team_form_templates,
)
from managr.salesforce import constants as sf_consts
from managr.crm.exceptions import (
    TokenExpired,
    FieldValidationError,
    RequiredFieldError,
    UnhandledCRMError,
    SFNotFoundError,
    InvalidRefreshToken,
)
from managr.crm.models import ObjectField
from .filters import SObjectFieldFilterSet, SalesforceSObjectFilterSet
from managr.core.background import _process_change_team_lead

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
            logger.exception(f"Failed to validate Salesforce account due to <{e}>")
            raise ValidationError(detail="An integration with this salesforce id already exists")
        # create sf sync object

        operations = [
            *serializer.instance.field_sync_opts,
            *serializer.instance.validation_sync_opts,
        ]
        request.user.crm = "SALESFORCE"
        request.user.save()
        scheduled_time = timezone.now()
        formatted_time = scheduled_time.strftime("%Y-%m-%dT%H:%M%Z")
        emit_gen_next_object_field_sync(str(request.user.id), operations, False, formatted_time)
        # generate forms
        if serializer.instance.user.is_admin:
            form_check = request.user.team.team_forms.all()
            schedule = (
                (timezone.now() + timezone.timedelta(minutes=2))
                if len(form_check) > 0
                else timezone.now()
            )
            if settings.IN_DEV:
                schedule = timezone.now() + timezone.timedelta(minutes=2)
            emit_generate_form_template(data.user, schedule=schedule)
        if (
            not serializer.instance.user.organization.is_paid
            and not serializer.instance.user.is_admin
        ):
            emit_generate_team_form_templates(
                str(serializer.instance.user.id),
                schedule=(timezone.now() + timezone.timedelta(minutes=2)),
            )
        user = User.objects.get(id=request.user.id)
        if user.make_team_lead:
            _process_change_team_lead(
                str(user.id), schedule=(timezone.now() + timezone.timedelta(minutes=2))
            )
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
        resource_type = self.request.data.get("resource_type")
        crm = user.crm_account
        data = self.request.data
        ids = data.get("field_ids")
        for id in ids:
            crm.add_to_pipeline_fields(resource_type, id)
        return Response()

    @action(
        methods=["post"],
        permission_classes=[permissions.IsAuthenticated],
        detail=False,
        url_path="remove-pipeline-fields",
    )
    def remove_pipeline_fields(self, request, *args, **kwargs):
        user = self.request.user
        resource_type = self.request.data.get("resource_type")
        crm = user.crm_account
        data = self.request.data
        ids = data.get("field_ids")
        for id in ids:
            crm.remove_pipeline_fields(resource_type, id)
        return Response()

    @action(
        methods=["get"],
        permission_classes=[permissions.IsAuthenticated],
        detail=False,
        url_path="sobject-picklist-values",
    )
    def get_sobject_picklist_values(self, request, *args, **kwargs):
        user = self.request.user
        sobject_id = request.GET.get("sobject_id", None)
        value = request.GET.get("value", None)
        sobject_field = ObjectField.objects.get(id=sobject_id)
        for_meetings = self.request.GET.get("for_meetings", False)
        attempts = 1
        while True:
            crm_account = user.crm_account
            crm_adapter = crm_account.adapter_class
            try:
                res = crm_adapter.list_relationship_data(
                    sobject_field.display_value_keys["api_name"],
                    sobject_field.display_value_keys["name_fields"],
                    value,
                    sobject_field.crm_object,
                    include_owner=for_meetings,
                )
                break
            except TokenExpired:
                if attempts >= 5:
                    return logger.exception(
                        f"Failed to retrieve reference data for {sobject_field.display_value_keys['api_name']} data for user {str(user.id)} after {attempts} tries"
                    )
                else:
                    try:
                        crm_account.regenerate_token()
                        attempts += 1
                    except InvalidRefreshToken:
                        return Response(
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            data={
                                "error": "There was a problem with your connection to Salesforce, please reconnect to SFDC"
                            },
                        )
            except Exception as e:
                return logger.exception(
                    f"Failed to retrieve reference data for {sobject_field.display_value_keys['api_name']} data for user {str(user.id)} after {attempts} tries: {e}"
                )

        data = list(map(lambda val: {"name": val.get("Name"), "id": val.get("Id")}, res))
        return Response(data=data)


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

    @action(
        methods=["get"],
        permission_classes=[permissions.IsAuthenticated],
        detail=False,
        url_path="stage-by-record-id",
    )
    def get_stage_picklist_values_by_record_id(self, request, *args, **kwargs):
        record_id = self.request.GET.get("record_id")
        user = self.request.user
        attempts = 1
        while True:
            try:
                res = user.crm_account.adapter_class.get_stage_picklist_values_by_record_type(
                    record_id
                )
                break
            except TokenExpired:
                if attempts >= 5:
                    logger.exception(
                        f"Refresh token on get stage by picklist value endpoint failed due to <{e}>"
                    )
                    break
                else:
                    user.salesforce_account.regenerate_token()
                    attempts += 1
            except Exception as e:
                return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data={})
        return Response(data=res)

    @action(
        methods=["get"],
        permission_classes=[permissions.IsAuthenticated],
        detail=False,
        url_path="record_type_picklist",
    )
    def get_record_type_picklist(self, request, *args, **kwargs):
        user = self.request.user
        attempts = 1
        while True:
            try:
                picklist = user.crm_account.get_record_type_picklist()
                break
            except TokenExpired:
                if attempts >= 5:
                    logger.exception(
                        f"Refresh token on get stage by picklist value endpoint failed due to <{e}>"
                    )
                    break
                else:
                    user.salesforce_account.regenerate_token()
                    attempts += 1
            except Exception as e:
                return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data={})
        return Response(data=picklist)


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
        methods=["post"],
        permission_classes=[permissions.IsAuthenticated],
        detail=False,
        url_path="bulk-update",
    )
    def bulk_update_sobjects(self, request, *args, **kwargs):
        verbose_name = f"bulk_update-{request.user.email}-{str(uuid.uuid4())}"
        task = emit_process_bulk_update(request.data, str(request.user.id), verbose_name)
        data = {"verbose_name": verbose_name}
        return Response(data)

    @action(
        methods=["get"],
        permission_classes=[permissions.IsAuthenticated],
        detail=False,
        url_path="create-bulk-form-instance",
    )
    def create_bulk_form_instance(self, request, *args, **kwargs):
        from managr.slack.models import OrgCustomSlackForm, OrgCustomSlackFormInstance

        user = self.request.user
        resource_id = self.request.GET.get("resource_id", None)
        template_list = OrgCustomSlackForm.objects.for_user(user).filter(
            Q(resource="Opportunity", form_type="UPDATE")
        )
        template = template_list.first()
        slack_form = OrgCustomSlackFormInstance.objects.create(
            template=template, user=user, resource_id=resource_id
        )
        attempts = 1
        while True:
            try:

                data = {
                    "form_id": str(slack_form.id),
                    "success": True,
                }
                break
            except TokenExpired:
                if attempts >= 5:
                    logger.info(f"CREATE FORM INSTANCE TOKEN EXPIRED ERROR ---- {e}")
                    break
                else:
                    user.salesforce_account.regenerate_token()
                    attempts += 1
            except Exception as e:
                logger.info(f"CREATE FORM INSTANCE ERROR ---- {e}")
                data = {"error": str(e), "success": False}
                break
        return Response(data=data)

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
        stage_name = self.request.GET.get("stage_name", None)
        template_list = OrgCustomSlackForm.objects.for_user(user).filter(
            Q(resource=resource_type, form_type=form_type)
        )
        template = (
            template_list.filter(stage=stage_name).first() if stage_name else template_list.first()
        )
        slack_form = (
            OrgCustomSlackFormInstance.objects.create(
                template=template, user=user, resource_id=resource_id, update_source="pipeline"
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
                    "success": True,
                }
                break
            except TokenExpired as e:
                if attempts >= 5:
                    logger.info(f"CREATE FORM INSTANCE TOKEN EXPIRED ERROR ---- {e}")
                    break
                else:
                    user.salesforce_account.regenerate_token()
                    attempts += 1
            except Exception as e:
                logger.info(f"CREATE FORM INSTANCE ERROR ---- {e}")
                data = {"error": str(e), "success": False}
                break
        if data["success"] is True and (resource_type == "Opportunity" and form_type == "UPDATE"):
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
        methods=["get"],
        permission_classes=[permissions.IsAuthenticated],
        detail=False,
        url_path="get-current-values",
    )
    def get_current_values(self, request, *args, **kwargs):
        user = request.user
        resource_type = request.GET.get("resource_type")
        resource_id = request.GET.get("resource_id", None)
        route = model_routes[resource_type]
        model_class = route["model"]
        model_object = model_class.objects.filter(id=resource_id).first()
        attempts = 1
        while True:
            try:
                current_values = model_object.get_current_values()
                data = {
                    "current_values": current_values.secondary_data,
                    "success": True,
                }
                break
            except TokenExpired as e:
                if attempts >= 5:
                    logger.info(f"CREATE FORM INSTANCE TOKEN EXPIRED ERROR ---- {e}")
                    data = {"error": str(e), "success": False}
                    break
                else:
                    if model_object.owner == user:
                        user.salesforce_account.regenerate_token()
                    else:
                        model_object.owner.salesforce_account.regenerate_token()
                    attempts += 1
            except Exception as e:
                logger.info(f"CREATE FORM INSTANCE ERROR ---- {e}")
                data = {"error": str(e), "success": False}
                break
        if data["success"] is True and user.organization.has_products:
            current_products = user.salesforce_account.list_resource_data(
                "OpportunityLineItem",
                0,
                filter=[
                    "AND IsDeleted = false",
                    f"AND OpportunityId = '{model_object.integration_id}'",
                ],
            )
            product_values = [product.integration_id for product in current_products]
            internal_products = routes["OpportunityLineItem"]["model"].objects.filter(
                integration_id__in=product_values
            )
            product_as_dict = [item.adapter_class.as_dict for item in internal_products]
            data["current_products"] = product_as_dict
        return Response(data=data)

    @action(
        methods=["post"],
        permission_classes=[permissions.IsAuthenticated],
        detail=False,
        url_path="update",
    )
    def update_resource(self, request, *args, **kwargs):
        from managr.core.models import User

        data = self.request.data
        logger.info(f"UPDATE START ---- {data}")
        user = User.objects.get(id=self.request.user.id)
        integration_ids = data.get("integration_ids")
        form_data = data.get("form_data")
        form_type = data.get("form_type")
        resource_type = data.get("resource_type")
        resource_id = data.get("resource_id", None)
        stage_name = data.get("stage_name", None)
        instance_data = {
            "user": user,
            "resource_type": resource_type,
            "form_type": form_type,
            "resource_id": resource_id,
            "stage_name": stage_name,
        }
        data = None
        for id in integration_ids:
            form_ids = create_form_instance(**instance_data)

            all_forms = OrgCustomSlackFormInstance.objects.filter(id__in=form_ids)
            forms = all_forms.filter(template__custom_object__isnull=True)
            main_form = forms.filter(template__form_type="UPDATE").first()
            custom_object_forms = all_forms.filter(template__custom_object__isnull=False)
            stage_form_data_collector = {}
            for form in forms:
                form.save_form(form_data, False)
                stage_form_data_collector = {**stage_form_data_collector, **form.saved_data}
            all_form_data = {**stage_form_data_collector, **main_form.saved_data}
            custom_object_data_collector = {}
            if len(custom_object_forms):
                for custom_form in custom_object_forms:
                    custom_form.save_form(form_data, False)
                    custom_object_data_collector = {
                        **custom_object_data_collector,
                        **custom_form.saved_data,
                    }
            formatted_saved_data = process_text_field_format(
                str(user.id), main_form.template.resource, all_form_data
            )
            attempts = 1
            while True:
                sf = user.salesforce_account
                try:
                    if resource_type == "OpportunityLineItem":
                        resource = main_form.resource_object.update_in_salesforce(
                            str(user.id), all_form_data
                        )
                    else:
                        resource = main_form.resource_object.update(all_form_data)
                        if len(custom_object_forms):
                            sf.create_custom_object(
                                custom_object_data_collector,
                                sf.access_token,
                                sf.instance_url,
                                sf.salesforce_id,
                                custom_object_forms.first().template.custom_object,
                            )
                    data = {
                        "success": True,
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
                except UnhandledCRMError as e:
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
                        if main_form.resource_object.owner == user:
                            sf.regenerate_token()
                        else:
                            main_form.resource_object.owner.salesforce_account.regenerate_token()
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
                    data = {"success": False, "error": f"UPDATE ERROR {e}"}
                    break
            if data["success"]:
                if all_form_data.get("meeting_comments", None) is not None:
                    (str(main_form.id))
                if user.has_slack_integration and len(
                    user.slack_integration.realtime_alert_configs
                ):
                    _send_instant_alert(form_ids)
                forms.update(is_submitted=True, submission_date=timezone.now())
                value_update = main_form.resource_object.update_database_values(all_form_data)
                # from_workflow = data.get("from_workflow")
                # title = data.get("workflow_title", None)
                # if from_workflow:
                #     user.activity.increment_untouched_count("workflows")
                #     user.activity.add_workflow_activity(str(main_form.id), title)
                return Response(data=data)
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data=data)

    @action(
        methods=["post"],
        permission_classes=[permissions.IsAuthenticated],
        detail=False,
        url_path="create",
    )
    def create_resource(self, request, *args, **kwargs):
        data = self.request.data
        logger.info(f"CREATE START ---- {data}")
        user = User.objects.get(id=self.request.user.id)
        integration_ids = data.get("integration_ids")
        form_data = data.get("form_data")
        form_type = data.get("form_type")
        resource_type = data.get("resource_type")
        resource_id = data.get("resource_id", None)
        stage_name = data.get("stage_name", None)
        instance_data = {
            "user": user,
            "resource_type": resource_type,
            "form_type": form_type,
            "resource_id": resource_id,
            "stage_name": stage_name,
        }
        form_ids = create_form_instance(**instance_data)
        forms = OrgCustomSlackFormInstance.objects.filter(id__in=form_ids)
        main_form = forms.filter(template__form_type="CREATE").first()
        if main_form.template.resource == "OpportunityLineItem":
            opp_ref = integration_ids[0]
        stage_form_data_collector = {}
        for form in forms:
            form.save_form(form_data, False)
            stage_form_data_collector = {**stage_form_data_collector, **form.saved_data}
        all_form_data = {**stage_form_data_collector, **main_form.saved_data}

        data = None
        attempts = 1
        while True:
            sf = user.salesforce_account
            try:
                if main_form.template.resource == "OpportunityLineItem":
                    all_form_data["OpportunityId"] = opp_ref
                resource = model_routes[main_form.resource_type]["model"].create_in_salesforce(
                    all_form_data, user.id
                )
                data = {"success": True, "integration_id": resource.integration_id}
                break
            except FieldValidationError as e:
                data = {"success": False, "error": str(e)}
                break

            except RequiredFieldError as e:
                data = {"success": False, "error": str(e)}
                break
            except UnhandledCRMError as e:
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
            except Exception as e:
                data = {"success": False, "error": str(e)}
                break
        if data["success"]:
            return Response(data=data)
        else:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data=data)

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
        if user.has_slack_integration and len(user.slack_integration.realtime_alert_configs):
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
        operations = ["Account", "Opportunity", "OpportunityLineItem"]
        currenttime = datetime.now()
        to_sync_ids = []
        synced_ids = []
        # if user.user_level in ["MANAGER", "SDR"]:
        #     users = User.objects.filter(Q(organization=user.organization, is_active=True))
        #     for user in users:
        #         if hasattr(user, "salesforce_account"):
        #             sync = SFResourceSync.objects.create(
        #                 user=user,
        #                 operations_list=operations,
        #                 operation_type=sf_consts.SALESFORCE_RESOURCE_SYNC,
        #             )
        #             user_timezone = pytz.timezone(user.timezone)
        #             current = (
        #                 pytz.utc.localize(currenttime)
        #                 .astimezone(user_timezone)
        #                 .strftime("%Y-%m-%d %H:%M:%S")
        #             )
        #             user.salesforce_account.last_sync_time = current
        #             user.salesforce_account.save()
        #             to_sync_ids.append(str(sync.id))
        #             _process_pipeline_sync(str(sync.id))
        # else:
        sync = SFResourceSync.objects.create(
            user=user,
            operations_list=operations,
            operation_type=sf_consts.SALESFORCE_RESOURCE_SYNC,
        )
        user_timezone = pytz.timezone(user.timezone)

        current = (
            pytz.utc.localize(currenttime).astimezone(user_timezone).strftime("%Y-%m-%d %H:%M:%S")
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

    @action(
        methods=["get"],
        permission_classes=[permissions.IsAuthenticated],
        detail=False,
        url_path="custom-objects",
    )
    def get_custom_objects(self, request, *args, **kwargs):
        user = request.user
        attempts = 1
        while True:
            try:
                objects = user.salesforce_account.list_objects()
                break
            except TokenExpired:
                if attempts >= 5:
                    return logger.exception(
                        f"Failed to retrieve all object from Salesforce for user {str(user.id)} after {attempts} tries"
                    )
                else:
                    try:
                        user.crm_account.regenerate_token()
                        attempts += 1
                    except InvalidRefreshToken:
                        return Response(
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            data={
                                "error": "There was a problem with your connection to Salesforce, please reconnect to SFDC"
                            },
                        )
            except Exception as e:
                logger.exception("Error fetching all Salesforce Objects")
        return Response(data={"sobjects": objects})

    @action(
        methods=["post"],
        permission_classes=[permissions.IsAuthenticated],
        detail=False,
        url_path="custom-objects-field-sync",
    )
    def sync_custom_object_fields(self, request, *args, **kwargs):
        user = request.user
        object = request.data.get("sobject")
        if object not in user.salesforce_account.sobjects.keys():
            user.salesforce_account.add_to_sobjects(object, True)
        scheduled_time = timezone.now()
        formatted_time = scheduled_time.strftime("%Y-%m-%dT%H:%M%Z")
        verbose_name = f"custom-field-sync-{request.user.email}-{str(uuid.uuid4())}"
        task = emit_gen_next_object_field_sync(
            str(user.id),
            [f"{sf_consts.SALESFORCE_OBJECT_FIELDS}.{object}"],
            schedule_time=formatted_time,
            verbose_name=verbose_name,
            priority=-1,
        )
        return Response(data={"verbose_name": task.verbose_name})


class MeetingWorkflowViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):
    serializer_class = MeetingWorkflowSerializer
    filter_backends = (
        DjangoFilterBackend,
        filters.SearchFilter,
    )

    def get_queryset(self):
        if self.request.data.get("date", False):
            return MeetingWorkflow.objects.for_user(
                self.request.user, date=self.request.data.get("date")
            ).order_by("meeting__start_time")
        else:
            return MeetingWorkflow.objects.filter(user=self.request.user)

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
        workflow.add_form(
            resource_type, slack_const.FORM_TYPE_UPDATE,
        )
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
        meeting = workflow.meeting
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
        form.save_form(request_data.get("form_data"), False)
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
        data = meeting.participants
        return Response(data=data)

    @action(
        methods=["post"],
        permission_classes=[permissions.IsAuthenticated],
        detail=False,
        url_path="remove-participant",
    )
    def remove_participant(self, request, *args, **kwargs):
        request_data = self.request.data
        workflow = MeetingWorkflow.objects.get(id=request_data.get("workflow_id"))
        meeting = workflow.meeting
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
        user = request.user
        stage_form_ids = request_data.get("stage_form_id", None)
        workflow = MeetingWorkflow.objects.get(id=request_data.get("workflow_id"))
        forms = (
            OrgCustomSlackFormInstance.objects.filter(id__in=request_data.get("stage_form_id"))
            if stage_form_ids
            else []
        )
        current_form_ids = []
        main_form = workflow.forms.filter(resource_id=workflow.resource_id).first()
        current_form_ids.append(str(main_form.id))
        main_form.save_form(request_data.get("form_data"), False)
        if len(forms):
            for form in forms:
                current_form_ids.append(str(form.id))
                form.workflow = workflow
                form.save_form(request_data.get("form_data"), False)

        # otherwise we save the meeting review form
        contact_forms = workflow.forms.filter(template__resource=slack_const.FORM_RESOURCE_CONTACT)
        ops = [
            f"{sf_consts.MEETING_REVIEW__UPDATE_RESOURCE}.{str(workflow.id)}",
            f"{sf_consts.MEETING_REVIEW__SAVE_CALL_LOG}.{str(workflow.id)}",
            # save meeting data
        ]

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
        if len(workflow.operations_list):
            workflow.operations_list = [*workflow.operations_list, *ops]
        else:
            workflow.operations_list = ops

        if user.has_slack_integration and len(user.slack_integration.realtime_alert_configs):
            _send_instant_alert(current_form_ids)

        workflow.save()
        workflow.begin_tasks()
        emit_meeting_workflow_tracker(str(workflow.id))
        serializer = MeetingWorkflowSerializer(instance=workflow)
        data = {"success": True, "workflow": serializer.data}
        return Response(data=data)

    @action(
        methods=["GET"], permission_classes=(IsStaff,), detail=False, url_path="admin",
    )
    def admin_meetings(self, request, *args, **kwargs):
        """Endpoint to list orgs and tokens for integration accounts"""
        org_param = request.query_params.get("org_id", None)
        meetings = MeetingWorkflow.objects.filter(user__organization=org_param)[:100]
        serialized = self.get_serializer(meetings, many=True).data
        return Response(serialized)
