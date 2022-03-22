import logging
import time

from django.utils import timezone
from django.conf import settings
from background_task import background
from managr.api.decorators import log_all_exceptions
from background_task.models import CompletedTask, Task
from managr.core.models import User

from .. import constants as hs_consts
from ..adapter.exceptions import (
    TokenExpired,
    FieldValidationError,
    RequiredFieldError,
    UnableToUnlockRow,
    CannotRetreiveObjectType,
)

logger = logging.getLogger("managr")


def emit_sync_sobject_fields(user_id, sync_id, resource, scheduled_for=timezone.now()):
    return _process_sobject_fields_sync(user_id, sync_id, resource, schedule=scheduled_for)


@background(schedule=0, queue=hs_consts.SALESFORCE_FIELD_SYNC_QUEUE)
@log_all_exceptions
def _process_sobject_fields_sync(user_id, sync_id, resource):
    user = User.objects.filter(id=user_id).select_related("salesforce_account").first()
    if not hasattr(user, "salesforce_account"):
        return
    attempts = 1
    while True:
        sf = user.salesforce_account
        try:
            fields = sf.get_fields(resource)
            attempts = 1
            break
        except TokenExpired:
            if attempts >= 5:
                return logger.exception(
                    f"Failed to sync {resource} data for user {sf.user.id}-{sf.user.email} after {attempts} tries"
                )
            else:
                sleep = 1 * 2 ** attempts + random.uniform(0, 1)
                time.sleep(sleep)
                sf.regenerate_token()
                attempts += 1
        except CannotRetreiveObjectType:
            sf.sobjects[resource] = False
