import logging
import time
import random
from datetime import datetime
from django.utils import timezone
from django.conf import settings
from background_task import background
from background_task.models import CompletedTask, Task

from managr.api.decorators import log_all_exceptions

from managr.core.models import User

from ..models import HSObjectFieldsOperation, HObjectField
from ..serializers import HObjectFieldSerializer

from .. import constants as hs_consts
from ..adapter.exceptions import (
    TokenExpired,
    FieldValidationError,
    RequiredFieldError,
    UnableToUnlockRow,
    CannotRetreiveObjectType,
)

logger = logging.getLogger("managr")


def emit_gen_next_hubspot_field_sync(user_id, ops_list, schedule_time=timezone.now()):
    schedule = datetime.strptime(schedule_time, "%Y-%m-%dT%H:%M%Z")
    return _process_gen_next_hubspot_field_sync(user_id, ops_list, schedule=schedule)


def emit_sync_hobject_fields(user_id, sync_id, resource, scheduled_for=timezone.now()):
    return _process_hobject_fields_sync(user_id, sync_id, resource, schedule=scheduled_for)


@background(schedule=0)
def _process_gen_next_hubspot_field_sync(user_id, operations_list):
    user = User.objects.filter(id=user_id).first()
    if not user:
        return logger.exception(f"User not found sync operation not created {user_id}")

    sync = HSObjectFieldsOperation.objects.create(
        user=user, operations_list=operations_list, operation_type=hs_consts.HUBSPOT_FIELD_SYNC
    )
    sync.begin_tasks()
    return


@background(schedule=0)
def _process_hobject_fields_sync(user_id, sync_id, resource):
    user = User.objects.filter(id=user_id).select_related("hubspot_account").first()
    print(user)
    print(resource)
    if not hasattr(user, "hubspot_account"):
        return
    attempts = 1
    while True:
        hs = user.hubspot_account
        try:
            fields = hs.adapter_class.list_fields(resource)
            print(fields)
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
            name=field.name, hubspot_account_id=field.hubspot_account, hubspot_object=resource,
        ).first()
        if existing:
            serializer = HObjectFieldSerializer(data=field.as_dict, instance=existing)
        else:
            serializer = HObjectFieldSerializer(data=field.as_dict)
        serializer.is_valid(raise_exception=True)
        serializer.save()
    return
