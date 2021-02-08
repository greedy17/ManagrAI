import logging

from django.dispatch import receiver
from django.db.models.signals import post_save

from managr.salesforce.background import emit_sf_update_opportunity, emit_sf_add_call_to_sf
from managr.zoom.background import emit_push_meeting_contacts

from .models import MeetingReview


logger = logging.getLogger("managr")


@receiver(post_save, sender=MeetingReview)
def save_to_salesforce(sender, instance=None, created=False, **kwargs):
    """When a new user is created, automatically generate an auth token for them."""
    if created:
        # check that the user has the sf
        meeting = instance.meeting
        user = meeting.zoom_account.user
        if user.salesforce_account:
            # emit_sf_update_opportunity(str(user.id), str(instance.id))
            data = instance.get_event_data_salesforce()
            emit_sf_add_call_to_sf(str(user.id), data)
            emit_push_meeting_contacts(str(meeting.id))

        else:
            logger.exception(
                f"{user.email} does not have an sf account this meeting was not logged to sf"
            )
        # emit send task call type meeting - {meeting type}

