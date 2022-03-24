import logging
import time
import random
from datetime import datetime
from django.utils import timezone
from background_task import background

from managr.api.decorators import log_all_exceptions

from managr.core.models import User

from managr.hubspot.models import HSObjectFieldsOperation, HObjectField
from managr.hubspot.serializers import HObjectFieldSerializer

from managr.hubspot import constants as hs_consts
from managr.hubspot.adapter.exceptions import (
    TokenExpired,
    CannotRetreiveObjectType,
)
from server.managr.hubspot.models import HSResourceSync

logger = logging.getLogger("managr")


def emit_hs_sync(user_id, sync_id, resource, limit, offset):
    user_id = str(user_id)
    sync_id = str(sync_id)
    return _process_resource_sync(user_id, sync_id, resource, limit, offset)


def emit_gen_next_hubspot_field_sync(user_id, ops_list, schedule_time=timezone.now()):
    schedule = datetime.strptime(schedule_time, "%Y-%m-%dT%H:%M%Z")
    return _process_gen_next_hubspot_field_sync(user_id, ops_list, schedule=schedule)


def emit_gen_next_hubspot_sync(user_id, ops_list, schedule_time=timezone.now()):
    schedule = datetime.strptime(schedule_time, "%Y-%m-%dT%H:%M%Z")
    return _process_gen_next_hubspot_sync(user_id, ops_list, schedule=schedule)


def emit_sync_hobject_fields(user_id, sync_id, resource, scheduled_for=timezone.now()):
    return _process_hobject_fields_sync(user_id, sync_id, resource, schedule=scheduled_for)


@background(schedule=0)
@log_all_exceptions
def _process_gen_next_hubspot_field_sync(user_id, operations_list):
    user = User.objects.filter(id=user_id).first()
    if not user:
        return logger.exception(f"User not found sync operation not created {user_id}")
    sync = HSObjectFieldsOperation.objects.create(
        user=user, operations_list=operations_list, operation_type=hs_consts.HUBSPOT_FIELD_SYNC
    )
    return sync.begin_tasks()


@background(schedule=0)
@log_all_exceptions
def _process_gen_next_hubspot_sync(user_id, operations_list):
    user = User.objects.filter(id=user_id).first()
    if not user:
        return logger.exception(f"User not found sync operation not created {user_id}")
    return HSResourceSync.objects.create(
        user=user, operations_list=operations_list, operation_type=hs_consts.HUBSPOT_RESOURCE_SYNC,
    ).begin_tasks()


@background(schedule=0, queue=hs_consts.HUBSPOT_FIELD_SYNC_QUEUE)
@log_all_exceptions
def _process_hobject_fields_sync(user_id, sync_id, resource):
    user = User.objects.filter(id=user_id).select_related("hubspot_account").first()
    if not hasattr(user, "hubspot_account"):
        return
    attempts = 1
    while True:
        hs = user.hubspot_account
        try:
            fields = hs.adapter_class.list_fields(resource)
            attempts = 1
            break
        except TokenExpired:
            if attempts >= 5:
                return logger.exception(
                    f"Failed to sync {resource} data for user {hs.user.id}-{hs.user.email} after {attempts} tries"
                )
            else:
                sleep = 1 * 2 ** attempts + random.uniform(0, 1)
                time.sleep(sleep)
                hs.regenerate_token()
                attempts += 1
        except CannotRetreiveObjectType:
            hs.hobjects[resource] = False
    for field in fields:
        existing = HObjectField.objects.filter(
            name=field.name, hubspot_account=field.hubspot_account, hubspot_object=resource,
        ).first()
        if existing:
            serializer = HObjectFieldSerializer(data=field.as_dict, instance=existing)
        else:
            serializer = HObjectFieldSerializer(data=field.as_dict)
        serializer.is_valid(raise_exception=True)
        serializer.save()
    return


@background(schedule=0, queue=hs_consts.HUBSPOT_RESOURCE_SYNC_QUEUE)
@log_all_exceptions
def _process_resource_sync(user_id, sync_id, resource, limit, offset, attempts=1):
    user = User.objects.filter(id=user_id).select_related("hubspot_account").first()
    if not hasattr(user, "hubspot_account"):
        return

    # if route doesnt exist catch all will catch the value error here
    route = routes[resource]
    model_class = route["model"]
    serializer_class = route["serializer"]

    while True:
        sf = user.hubspot_account
        try:
            res = sf.list_resource_data(resource, offset, limit=limit)
            logger.info(f"Pulled total {len(res)} from request for {resource}")
            attempts = 1
            break
        except TokenExpired:
            if attempts >= 5:
                return logger.exception(
                    f"Failed to sync {resource} data for user {user_id} after {attempts} tries"
                )
            else:
                sleep = 1 * 2 ** attempts + random.uniform(0, 1)
                time.sleep(sleep)
                sf.regenerate_token()
                attempts += 1
        except SFQueryOffsetError:
            return logger.warning(
                f"Failed to sync some data for resource {resource} for user {user_id} because of SF LIMIT"
            )
    for item in res:
        existing = model_class.objects.filter(integration_id=item.integration_id).first()
        if existing:
            serializer = serializer_class(data=item.as_dict, instance=existing)
        else:
            serializer = serializer_class(data=item.as_dict)
        # check if already exists and update
        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError as e:
            error_str = f"Failed to save data for {resource} {item.name if item.name else 'N/A'} with hubspot id {item.integration_id} due to the following error {e.detail}"

            # context = dict(email=user.email, error=error_str)
            # subject = render_to_string("hubspot/error_saving_resource_data.txt")
            # recipient = [settings.STAFF_EMAIL]
            # send_html_email(
            #     subject,
            #     "hubspot/error_saving_resource_data.html",
            #     settings.SERVER_EMAIL,
            #     recipient,
            #     context={**context},
            # )
            logger.exception(error_str)
            continue
        serializer.save()

    return
