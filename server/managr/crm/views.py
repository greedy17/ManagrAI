import json
import logging
import time
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import (
    filters,
    permissions,
    status,
    mixins,
    viewsets,
)
from django.utils import timezone
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
)
from managr.salesforce.background import _send_instant_alert
from .utils import create_form_instance, process_text_field_format

from managr.slack.models import OrgCustomSlackFormInstance

# Create your views here.
logger = logging.getLogger("managr")


class ObjectFieldViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):
    serializer_class = ObjectFieldSerializer
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
    def get_serializer_class(self):
        routes = model_routes(self.request.user.crm)
        param_object = self.request.GET.get("crm_object")
        sobject = routes[param_object]
        return sobject["serializer"]

    def get_queryset(self, request):
        routes = model_routes(self.request.user.crm)
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
            sf = user.salesforce_account
            try:
                if main_form.template.resource == "OpportunityLineItem":
                    all_form_data["OpportunityId"] = opp_ref
                resource = model_routes[main_form.resource_type]["model"].create(
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
                    print(e)
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
                if all_form_data.get("meeting_comments", None) is not None:
                    (str(main_form.id))
                if user.has_slack_integration and len(
                    user.slack_integration.realtime_alert_configs
                ):
                    _send_instant_alert(form_ids)
                all_forms.update(
                    is_submitted=True, update_source="pipeline", submission_date=timezone.now()
                )
                value_update = main_form.resource_object.update_database_values(all_form_data)
                # from_workflow = data.get("from_workflow")
                # title = data.get("workflow_title", None)
                # if from_workflow:
                #     user.activity.increment_untouched_count("workflows")
                #     user.activity.add_workflow_activity(str(main_form.id), title)
                return Response(data=data)
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data=data)
