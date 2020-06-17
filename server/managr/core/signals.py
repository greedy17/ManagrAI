from rest_framework.authtoken.models import Token

from django.dispatch import receiver
from django.db.models.signals import post_save

from .models import User


@receiver(post_save, sender=User)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    """When a new user is created, automatically generate an auth token for them."""
    if created:
        Token.objects.create(user=instance)
