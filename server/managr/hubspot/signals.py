import logging
import json
from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save

from background_task.models import CompletedTask, Task

from .models import HSSyncOperation, HSObjectFieldsOperation
from managr.salesforce.models import MeetingWorkflow
from . import constants as hs_consts

logger = logging.getLogger("managr")


@receiver(post_save, sender=CompletedTask)
def update_succesful_hubspot_operations(sender, instance=None, created=False, **kwargs):
    """When A background task is completed from the hs sync"""
    if created:
        # check that the user has the sf
        task_id = instance.id
        queue = instance.queue

        if queue not in [
            hs_consts.HUBSPOT_RESOURCE_SYNC_QUEUE,
            hs_consts.HUBSPOT_FIELD_SYNC_QUEUE,
            hs_consts.HUBSPOT_MEETING_REVIEW_WORKFLOW_QUEUE,
        ]:
            return
        if queue == hs_consts.HUBSPOT_RESOURCE_SYNC_QUEUE:
            # sf sync is second item
            sync_id = json.loads(instance.task_params)[0][1]
            operation = HSSyncOperation.objects.filter(id=sync_id).first()
        elif queue == hs_consts.HUBSPOT_FIELD_SYNC_QUEUE:
            # sf sync is second item
            sync_id = json.loads(instance.task_params)[0][1]
            operation = HSObjectFieldsOperation.objects.filter(id=sync_id).first()
        elif queue == hs_consts.HUBSPOT_MEETING_REVIEW_WORKFLOW_QUEUE:
            sync_id = json.loads(instance.task_params)[0][0]
            operation = MeetingWorkflow.objects.filter(id=sync_id).first()
        if operation and not instance.failed_at:
            operation.completed_operations.append(str(instance.task_hash))
            operation.save()
        elif operation and instance.failed_at:
            operation.failed_operations.append(str(instance.task_hash))
            operation.save()
        else:
            logger.info(
                f"The Hubspot Sync Object was deleted before the sync operation completed, sync: {sync_id}, task: {task_id}"
            )
