from rest_framework.authtoken.models import Token

from django.dispatch import receiver
from django.db.models.signals import post_save

from .models import User
from background_task.models import CompletedTask
from managr.hubspot import constants as hs_consts
from managr.salesforce import constants as sf_consts


@receiver(post_save, sender=User)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    """When a new user is created, automatically generate an auth token for them."""
    if created:
        Token.objects.create(user=instance)


@receiver(post_save, sender=CompletedTask)
def update_succesful_task_operations(sender, instance=None, created=False, **kwargs):
    from managr.hubspot.signals import update_succesful_hubspot_operations
    from managr.salesforce.signals import update_succesful_operations

    if created:
        # check that the user has the sf
        queue = instance.queue

        if queue in [
            sf_consts.SALESFORCE_RESOURCE_SYNC_QUEUE,
            sf_consts.SALESFORCE_FIELD_SYNC_QUEUE,
            sf_consts.SALESFORCE_MEETING_REVIEW_WORKFLOW_QUEUE,
        ]:
            update_succesful_operations(sender, instance, created, **kwargs)
        elif queue in [
            hs_consts.HUBSPOT_RESOURCE_SYNC_QUEUE,
            hs_consts.HUBSPOT_FIELD_SYNC_QUEUE,
        ]:
            update_succesful_hubspot_operations(sender, instance, created, **kwargs)
        else:
            return
