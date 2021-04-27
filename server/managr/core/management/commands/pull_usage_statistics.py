from django.utils import timezone
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from datetime import datetime, timedelta
from managr.core.models import User
from managr.zoom.models import ZoomMeeting
from managr.salesforce.models import SObjectField
from managr.api.emails import send_html_email


class Command(BaseCommand):
    """
    Usage:
        ./manage.py pull_usage_statistics

    Description: pulls high-level usage statistics from the database.
    Currently limited to the number of users, the number of meetings,
    and the number of SalesForce fields.

    By default, this pulls the usage statistics for the previous week
    """

    help = "Pull usage statistics for the application"

    def handle(self, *args, **options):

        # Get date range for previous week
        today = timezone.make_aware(datetime.today())
        start = today - timedelta(days=today.weekday(), weeks=1)
        end = start + timedelta(days=6)

        # Users
        past_week_user_count = User.objects.filter(datetime_created__range=(start, end)).count()
        total_user_count = User.objects.count()

        # Meetings
        past_week_meeting_count = ZoomMeeting.objects.filter(
            datetime_created__range=(start, end)
        ).count()
        total_meeting_count = ZoomMeeting.objects.count()

        # SF Field Objects
        past_week_sf_field_count = SObjectField.objects.filter(
            datetime_created__range=(start, end)
        ).count()
        total_sf_field_count = SObjectField.objects.count()

        # Email Settings
        email_subject = f"Managr: Usage statistics for week of {start.strftime('%B %d, %Y')}"
        superusers = User.objects.filter(is_superuser=True)
        recipients = [user.email for user in superusers] + [
            "mike@mymanagr.com",
            "pari@thinknimble.com",
            "zakk@thinknimble.com",
        ]
        context = {
            "start_date": start.strftime("%B %d, %Y"),
            "end_date": end.strftime("%B %d, %Y"),
            "users": {"total": total_user_count, "past_week": past_week_user_count},
            "meetings": {"total": total_meeting_count, "past_week": past_week_meeting_count},
            "fields": {"total": total_sf_field_count, "past_week": past_week_sf_field_count},
            "meetings_per_rep": past_week_meeting_count / total_user_count,
            "fields_per_rep": past_week_sf_field_count / total_user_count,
        }

        send_html_email(
            email_subject,
            "core/email-templates/usage-statistics.html",
            settings.SERVER_EMAIL,
            recipients,
            context=context,
        )
