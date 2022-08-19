import logging
import random
from django.utils import timezone

from background_task import background
from managr.api.decorators import log_all_exceptions
from managr.core.models import User
from managr.crm import constants as crm_consts
from managr.crm.models import CrmObjectFieldsOperation, CrmResourceSync

logger = logging.getLogger("managr")


def emit_sync_object_fields(user_id, sync_id, resource, scheduled_for=timezone.now()):
    return _process_object_fields_sync(user_id, sync_id, resource, schedule=scheduled_for)


@background(schedule=0)
@log_all_exceptions
def _process_stale_data_for_delete(batch):
    for record in batch:
        # running this as for loop instead of bulk delete to keep track of records deleted
        try:
            u = User.objects.filter(id=record["user_id"]).first()
            if u:
                for resource, values in record["resource"].items():
                    qs = getattr(u, f"imported_{resource}").filter(id__in=values)
                    logger.info(
                        f"Deleting {qs.count()} {resource} for user {u.email} with id {str(u.id)}"
                    )
                    qs.delete()

        except Exception as e:
            logger.exception(e)
            pass
    return


@background(schedule=0)
@log_all_exceptions
def _process_gen_next_hubspot_field_sync(user_id, operations_list):
    user = User.objects.filter(id=user_id).first()
    if not user:
        return logger.exception(f"User not found sync operation not created {user_id}")
    sync = CrmObjectFieldsOperation.objects.create(
        user=user, operations_list=operations_list, operation_type=hs_consts.HUBSPOT_FIELD_SYNC
    )
    return sync.begin_tasks()


@background(schedule=0)
@log_all_exceptions
def _process_gen_next_hubspot_sync(user_id, operations_list):
    user = User.objects.filter(id=user_id).first()
    if not user:
        return logger.exception(f"User not found sync operation not created {user_id}")
    return CrmResourceSync.objects.create(
        user=user, operations_list=operations_list, operation_type=hs_consts.HUBSPOT_RESOURCE_SYNC,
    ).begin_tasks()


@background(schedule=0, queue=crm_consts.CRM_FIELD_SYNC_QUEUE)
@log_all_exceptions
def _process_object_fields_sync(user_id, sync_id, resource):
    user = User.objects.filter(id=user_id).first()
    if not hasattr(user, "hubspot_account"):
        return
    attempts = 1
    while True:
        crm = user.crm_account
        try:
            fields = crm.adapter_class.list_fields(resource)
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
        existing = ObjectField.objects.filter(
            name=field.name, crm_account=field.crm_account, crm_object=resource,
        ).first()
        if existing:
            serializer = ObjectFieldSerializer(data=field.as_dict, instance=existing)
        else:
            serializer = ObjectFieldSerializer(data=field.as_dict)
        serializer.is_valid(raise_exception=True)
        serializer.save()
    return
