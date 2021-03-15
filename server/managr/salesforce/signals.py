import logging
import json
import traceback
from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save

from background_task.models import CompletedTask, Task
from managr.opportunity.models import Opportunity

from .models import SFSyncOperation, MeetingWorkflow
from . import constants as sf_consts

logger = logging.getLogger("managr")


@receiver(post_save, sender=CompletedTask)
def update_succesful_operations(sender, instance=None, created=False, **kwargs):
    """When A background task is completed from the sf sync """
    if created:
        # check that the user has the sf
        task_id = instance.id
        queue = instance.queue

        if queue not in [
            sf_consts.SALESFORCE_RESOURCE_SYNC_QUEUE,
            sf_consts.SALESFORCE_MEETING_REVIEW_WORKFLOW_QUEUE,
        ]:
            return
        if queue == sf_consts.SALESFORCE_RESOURCE_SYNC_QUEUE:
            # sf sync is second item
            sync_id = json.loads(instance.task_params)[0][1]
            operation = SFSyncOperation.objects.filter(id=sync_id).first()
        elif queue == sf_consts.SALESFORCE_MEETING_REVIEW_WORKFLOW_QUEUE:
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
                f"The SfSync Object was deleted before the sync operation completed, sync: {sync_id}, task: {task_id}"
            )
