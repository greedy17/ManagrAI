from django.dispatch import receiver
from django.db.models.signals import post_save

from .models import Organization


@receiver(post_save, sender=Organization)
def check_state(sender, instance, created, **kwargs):
    """Check if org was set to inactive"""
    if instance.state == "INACTIVE":
        users = instance.users.all()
        for user in users:
            user.access_token.revoke()
            user.is_active = False
            user.save()
    return
