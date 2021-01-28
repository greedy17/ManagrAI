from django.dispatch import receiver
from django.db.models.signals import post_save

from .models import MeetingReview


@receiver(post_save, sender=MeetingReview)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    """When a new user is created, automatically generate an auth token for them."""
    if created:
        print(instance.meeting_type)
        # emit send task call type meeting - {meeting type}

