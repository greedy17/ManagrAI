from django.utils import timezone
from django.test import TestCase
from django.core.management import call_command


from managr.lead.models import Lead, LeadActivityLog, Notification


def run_fn(user):
    time_occured = timezone.now() - timezone.timedelta(days=100)
    lead = Lead.objects.filter(claimed_by=user).first()
    la = lead.activity_logs.first()
    la.action_timestamp = time_occured
    lead.activity_logs.all().delete()
    la.save()
    call_command("createleadnotifications")
    stalled_date = timezone.now() - timezone.timedelta(days=65)
    lead.status_last_update = stalled_date
    lead.save()
    call_command("createleadnotifications")

    expected_close_date = timezone.now() - timezone.timedelta(days=2)
    lead.expected_close_date = expected_close_date
    lead.save()
    call_command("createleadnotifications")
    expected_close_date = timezone.now() - timezone.timedelta(days=16)
    lead.expected_close_date = expected_close_date
    lead.save()
    call_command("createleadnotifications")
    expected_close_date = timezone.now() - timezone.timedelta(days=31)
    lead.expected_close_date = expected_close_date
    lead.save()
    call_command("createleadnotifications")


if __name__ == "__main__":
    run_fn()
