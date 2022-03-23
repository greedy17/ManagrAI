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

logger = logging.getLogger("managr")


def emit_gen_next_hubspot_field_sync(user_id, ops_list, schedule_time=timezone.now()):
    schedule = datetime.strptime(schedule_time, "%Y-%m-%dT%H:%M%Z")
    return _process_gen_next_hubspot_field_sync(user_id, ops_list)


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
