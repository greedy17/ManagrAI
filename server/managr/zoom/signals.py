import logging

from django.dispatch import receiver
from django.db.models.signals import post_save

from managr.salesforce.background import emit_sf_update_opportunity

from .models import MeetingReview


logger = logging.getLogger("managr")


@receiver(post_save, sender=MeetingReview)
def save_to_salesforce(sender, instance=None, created=False, **kwargs):
    """When a new user is created, automatically generate an auth token for them."""
    if created:
        # check that the user has the sf
        user = instance.meeting.zoom_account.user
        if user.salesforce_account:
            emit_sf_update_opportunity(str(user.id), str(instance.id))
            res = instance.save_event_to_salesforce()
        else:
            logger.exception(
                f"{user.email} does not have an sf account this meeting was not logged to sf"
            )
        # emit send task call type meeting - {meeting type}

