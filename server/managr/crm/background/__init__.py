import logging
import random
from django.utils import timezone

from background_task import background
from managr.api.decorators import log_all_exceptions
from managr.core.models import User
from managr.crm import constants as crm_consts

logger = logging.getLogger("managr")


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

