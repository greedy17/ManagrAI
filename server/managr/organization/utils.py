from .models import Organization
from django.utils import timezone
from datetime import timedelta


def check_trial_status():
    orgs = Organization.objects.filter(is_paid=False)
    now = timezone.now()
    for org in orgs:
        is_expired = now - org.datetime_created > timedelta(days=7)
        if is_expired:
            org.state = "INACTIVE"
            org.save()
    return
