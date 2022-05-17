from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model
from django.dispatch import receiver
from django.db.models.signals import post_save

from .models import User, UserActivity


@receiver(post_save, sender=User)
def create_auth_token(sender, instance, created, **kwargs):
    """When a new user is created, automatically generate an auth token for them."""
    if created:
        Token.objects.create(user=instance)


@receiver(post_save, sender=get_user_model())
def create_activity(sender, instance, created, **kwargs):
    if created:
        UserActivity.objects.create(user=instance)
