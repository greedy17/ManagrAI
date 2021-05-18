import logging

from django.dispatch import receiver
from django.db.models.signals import post_save


from .models import MeetingReview


logger = logging.getLogger("managr")
