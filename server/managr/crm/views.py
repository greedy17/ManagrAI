import json
import logging
import time
import random
import pytz
from datetime import datetime
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import (
    filters,
    permissions,
    status,
    mixins,
    viewsets,
)
from managr.api.models import ExpiringTokenAuthentication
from django.utils import timezone
from django.db.models import Q
from rest_framework.response import Response
from rest_framework.decorators import action
from managr.crm.models import ObjectField
from managr.crm.serializers import ObjectFieldSerializer
from managr.crm.filters import ObjectFieldFilterSet, CrmObjectFilterSet
from managr.crm.routes import model_routes
from managr.core.models import User
from managr.crm.exceptions import (
    TokenExpired,
    FieldValidationError,
    RequiredFieldError,
    UnhandledCRMError,
    SFNotFoundError,
    InvalidRefreshToken,
)
from managr.salesforce.background import (
    _send_instant_alert,
    _process_pipeline_sf_sync,
    emit_add_update_to_sf,
)
from managr.salesforce.models import SFResourceSync
from managr.hubspot.models import HSResourceSync
from .utils import create_form_instance, process_text_field_format
from managr.hubspot.tasks import _process_pipeline_hs_sync
from managr.slack.models import OrgCustomSlackFormInstance
from managr.hubspot.tasks import emit_add_update_to_hs

# Create your views here.
logger = logging.getLogger("managr")


def ADD_UPDATE_TO_CRM_FUNCTION(crm):
    if crm == "SALESFORCE":
        return emit_add_update_to_sf
    else:
        return emit_add_update_to_hs


class ObjectFieldViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):
    serializer_class = ObjectFieldSerializer
    authentication_classes = [ExpiringTokenAuthentication]
    filter_backends = (
        DjangoFilterBackend,
        filters.SearchFilter,
    )
    search_fields = ("label",)
    filter_class = ObjectFieldFilterSet

    def get_queryset(self):
        return ObjectField.objects.for_user(self.request.user)


class CRMObjectViewSet(
    viewsets.GenericViewSet,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.UpdateModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
):
    authentication_classes = [ExpiringTokenAuthentication]

    def get_serializer_class(self):
        routes = model_routes(self.request.user.crm)
        param_object = self.request.GET.get("crm_object")
        sobject = routes[param_object]
        return sobject["serializer"]

    def get_queryset(self):
        routes = model_routes(self.request.user.crm)
        param_sobject = self.request.GET.get("crm_object")
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
            filtered_query = CrmObjectFilterSet.for_filter(
                query, json.loads(self.request.GET.get("filters"))
            )
            return filtered_query
        return query

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
            sf = user.crm_account
            model_route = model_routes(user.crm)
            try:
                if main_form.template.resource == "OpportunityLineItem":
                    all_form_data["OpportunityId"] = opp_ref
                resource_model = model_route[main_form.resource_type]["model"]
                resource = resource_model.create(all_form_data, str(user.id), resource_type)
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
                logger.info(f"Error {e}")
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
        chat_form_id = data.get("chat_form_id", None)
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
            main_form = all_forms.filter(template__form_type="UPDATE").first()
            stage_form_data_collector = {}
            for form in all_forms:
                form.save_form(form_data, False)
                stage_form_data_collector = {**stage_form_data_collector, **form.saved_data}
            all_form_data = {**stage_form_data_collector, **main_form.saved_data}
            formatted_saved_data = process_text_field_format(
                str(user.id), main_form.template.resource, all_form_data
            )
            attempts = 1
            while True:
                crm = user.crm_account

                if "meeting_comments" in all_form_data.keys() and not chat_form_id:
                    if all_form_data.get("meeting_comments", None) is not None:
                        ADD_UPDATE_TO_CRM_FUNCTION(user.crm)(str(main_form.id))
                    data = {
                        "success": True,
                    }
                    break
                try:
                    if resource_type == "OpportunityLineItem":
                        resource = main_form.resource_object.update_in_salesforce(
                            str(user.id), all_form_data
                        )
                    else:
                        resource = main_form.resource_object.update(all_form_data)
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
                            crm.regenerate_token()
                        else:
                            main_form.resource_object.owner.crm_account.regenerate_token()
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
                if user.has_slack_integration and len(
                    user.slack_integration.realtime_alert_configs
                ):
                    _send_instant_alert(form_ids)
                all_forms.update(is_submitted=True, submission_date=timezone.now())
                value_update = main_form.resource_object.update_database_values(all_form_data)
                # from_workflow = data.get("from_workflow")
                # title = data.get("workflow_title", None)
                # if from_workflow:
                #     user.activity.increment_untouched_count("workflows")
                #     user.activity.add_workflow_activity(str(main_form.id), title)
                return Response(data=data)
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data=data)

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
                    "success": True,
                }
                break
            except TokenExpired as e:
                if attempts >= 5:
                    logger.info(f"CREATE FORM INSTANCE TOKEN EXPIRED ERROR ---- {e}")
                    break
                else:
                    user.crm_account.regenerate_token()
                    attempts += 1
            except Exception as e:
                logger.info(f"CREATE FORM INSTANCE ERROR ---- {e}")
                data = {"error": str(e), "success": False}
                break
        if data["success"] is True and (resource_type == "Opportunity" and form_type == "UPDATE"):
            current_products = user.crm_account.list_resource_data(
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
        url_path="notes",
    )
    def get_resource_notes(self, request, *args, **kwargs):
        from managr.slack.models import OrgCustomSlackFormInstance

        resource_id = self.request.GET.get("resource_id")
        new_stage = (
            "saved_data__StageName"
            if self.request.user.crm == "SALESFORCE"
            else "saved_data__dealname"
        )
        pre_stage = (
            "previous_data__StageName"
            if self.request.user.crm == "SALESFORCE"
            else "previous_data__dealstage"
        )
        note_data = (
            OrgCustomSlackFormInstance.objects.filter(resource_id=resource_id)
            .filter(is_submitted=True)
            .values(
                "submission_date",
                "saved_data__meeting_type",
                "saved_data__meeting_comments",
                new_stage,
                pre_stage,
            )
        )
        if note_data:
            return Response(data=note_data)
        return Response(data=[])

    @action(
        methods=["get"],
        permission_classes=[permissions.IsAuthenticated],
        detail=False,
        url_path="get-current-values",
    )
    def get_current_values(self, request, *args, **kwargs):
        user = request.user
        routes = model_routes(user.crm)
        resource_type = request.GET.get("resource_type")
        resource_id = request.GET.get("resource_id", None)
        route = routes[resource_type]
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
                        user.crm_account.regenerate_token()
                    else:
                        model_object.owner.crm_account.regenerate_token()
                    attempts += 1
            except Exception as e:
                logger.info(f"CREATE FORM INSTANCE ERROR ---- {e}")
                data = {"error": str(e), "success": False}
                break
        if data["success"] is True and user.organization.has_products and user.crm == "SALESFORCE":
            current_products = user.crm_account.list_resource_data(
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
        methods=["get"],
        permission_classes=[permissions.IsAuthenticated],
        detail=False,
        url_path="resource-sync",
    )
    def resource_sync(self, request, *args, **kwargs):
        user = self.request.user
        operations = (
            ["Account", "Opportunity", "OpportunityLineItem", "Contact"]
            if user.crm == "SALESFORCE"
            else ["Deal", "Contact", "Company"]
        )
        currenttime = datetime.now()
        to_sync_ids = []
        synced_ids = []
        sync_class = SFResourceSync if user.crm == "SALESFORCE" else HSResourceSync
        type = "SALESFORCE_RESOURCE_SYNC" if user.crm == "SALESFORCE" else "HUBSPOT_RESOURCE_SYNC"
        sync = sync_class.objects.create(
            user=user,
            operations_list=operations,
            operation_type=type,
        )
        user_timezone = pytz.timezone(user.timezone)

        current = (
            pytz.utc.localize(currenttime).astimezone(user_timezone).strftime("%Y-%m-%d %H:%M:%S")
        )
        user.crm_account.last_sync_time = current
        user.crm_account.save()
        to_sync_ids.append(str(sync.id))
        sync_function = (
            _process_pipeline_sf_sync if user.crm == "SALESFORCE" else _process_pipeline_hs_sync
        )
        sync_function(str(sync.id))
        attempts = 1
        # logger.info(f"TO SYNC: {to_sync_ids}")
        # logger.info(f"SYNCED: {synced_ids}")
        has_error = False
        while True:
            for index, id in enumerate(to_sync_ids):
                resource_sync = sync_class.objects.get(id=id)
                try:
                    if len(resource_sync.operations) < 1:
                        has_error = True
                        break
                    if resource_sync.status == "Completed":
                        synced_ids.append(id)
                        to_sync_ids.pop(index)
                        # logger.info(f"IN LOOP TO SYNC: {to_sync_ids}")
                        # logger.info(f"IN LOOP SYNCED: {synced_ids}")
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
