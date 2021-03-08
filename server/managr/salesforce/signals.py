import logging
import json

from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save

from background_task.models import CompletedTask, Task
from managr.opportunity.models import Opportunity

from .models import SFSyncOperation
from . import constants as sf_consts

logger = logging.getLogger("managr")


@receiver(post_save, sender=CompletedTask)
def update_succesful_operations(sender, instance=None, created=False, **kwargs):
    """When A background task is completed from the sf sync """
    if created:
        # check that the user has the sf
        task_id = instance.id
        queue = instance.queue
        if queue == sf_consts.SALESFORCE_RESOURCE_SYNC_QUEUE:
            # sf sync is second item
            sync_id = json.loads(instance.task_params)[0][1]
            operation = SFSyncOperation.objects.filter(id=sync_id).first()
            if operation:
                operation.completed_operations.append(str(instance.task_hash))
                operation.save()
            else:
                logger.info(
                    f"The SfSync Object was deleted before the sync operation completed, sync: {sync_id}, task: {task_id}"
                )


@receiver(post_save, sender=Task)
def check_failed_operations(sender, instance=None, created=False, **kwargs):
    """When A background task is saved check to see if it has failed too many times from the sf sync """
    if created:
        # check that the user has the sf
        task_id = instance.id
        queue = instance.queue
        if queue == sf_consts.SALESFORCE_RESOURCE_SYNC_QUEUE:

            if instance.attempts >= 5:
                obj = dict(
                    id=str(task_id),
                    queue=queue,
                    name=instance.name,
                    params=instance.task_params,
                    attempts=instance.attempts,
                    error=instance.last_error,
                )
                # sf sync is second item
                sync_id = json.loads(instance.task_params)[0][1]
                operation = SFSyncOperation.objects.filter(id=sync_id).first()
                if operation:
                    operation.completed_operations.append(obj)
                    operation.save()
                    logger.info(
                        f"The operation in sync {str(operation.id)} failed it was removed after 5 attempts {str(task_id)}"
                    )
                    instance.delete()
                else:
                    logger.info(
                        f"The SfSync Object was deleted before the sync operation completed, sync: {sync_id}, task: {task_id}"
                    )

        # emit send task call type meeting - {meeting type}

