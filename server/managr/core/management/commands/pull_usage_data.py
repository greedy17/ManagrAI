from django.utils import timezone
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from datetime import datetime, timedelta, date
from managr.core.models import User
from managr.zoom.models import ZoomMeeting
from managr.organization.models import Organization
from managr.salesforce.models import SObjectField
from managr.slack.models import OrgCustomSlackFormInstance
from managr.alerts.models import AlertInstance, AlertTemplate


class Command(BaseCommand):
    """
    Usage:
        ./manage.py pull_usage_data

    Description: pulls high-level usage statistics from the database.
    Currently limited to the number of users, the number of meetings,
    and the number of SalesForce fields.

    By default, this pulls the usage statistics for the month 
    or range if args passed in 
    """

    help = "Pull usage statistics for the application"

    def add_arguments(self, parser):
        parser.add_argument(
            "--start", dest="start_date", type=str, help="Custom start format 'Month Day Year'"
        )
        parser.add_argument(
            "--end", dest="end_date", type=str, help="Custom end date format 'Month Day Year'"
        )

    def handle(self, *args, **options):
        start = options["start_date"]
        end = options["end_date"]
        # Get date range for range
        if not start and not end:
            end = date.today()
            start = end - timedelta(end.day - 1)
        else:
            create_date = datetime.strptime(start, "%b %d %Y")
            end = create_date.date()
            start = end - timedelta(end.day - 1)

        # Base queries
        total_users = User.objects.all()
        user_count_in_range = User.objects.filter(datetime_created__range=(start, end))
        slack_form_instances = (
            OrgCustomSlackFormInstance.objects.filter(datetime_created__range=(start, end))
            .filter(is_submitted=True)
            .filter(template__form_type="UPDATE")
        )
        alerts_sent = AlertInstance.objects.filter(datetime_created__range=(start, end)).filter(
            sent_at__range=(start, end)
        )
        alert_templates = AlertTemplate.objects.filter(datetime_created__range=(start, end))
        zoom_meetings = ZoomMeeting.objects.filter(datetime_created__range=(start, end))
        orgs = Organization.objects.all()

        totals = {
            "user_total": total_users.count(),
            "new_users": user_count_in_range.count(),
            "updates": {
                "total": slack_form_instances.count(),
                "alert": slack_form_instances.filter(update_source="alert").count(),
                "meeting": slack_form_instances.filter(update_source="meeting").count(),
                "command": slack_form_instances.filter(update_source="command").count(),
            },
            "alerts_sent": alerts_sent.count(),
            "alert_templates": alert_templates.count(),
            "zoom_meetings": zoom_meetings.count(),
        }
        org_data = {}
        for org in orgs:
            data = {}
            data["total_users"] = total_users.filter(organization=org).count()
            data["new_users"] = user_count_in_range.filter(organization=org).count()
            update_obj = {}
            update_total = slack_form_instances.filter(user__organization=org)
            update_obj["total"] = update_total.count()
            update_obj["alert"] = update_total.filter(update_source="alert").count()
            update_obj["meeting"] = update_total.filter(update_source="meeting").count()
            update_obj["command"] = update_total.filter(update_source="command").count()
            data["updates"] = update_obj
            data["alerts_sent"] = alerts_sent.filter(user__organization=org).count()
            data["alerts_templates"] = alert_templates.filter(user__organization=org).count()
            data["zoom_meeting"] = zoom_meetings.filter(
                zoom_account__user__organization=org
            ).count()
            org_data[org] = data

        self.stdout.write(
            self.style.SUCCESS("Totals between {start} and {end}:".format(start=start, end=end))
        )
        self.stdout.write(self.style.HTTP_INFO("{}").format(totals))
        self.stdout.write(self.style.HTTP_NOT_MODIFIED("-----------------------------"))
        self.stdout.write(
            self.style.SUCCESS("Org data between {start} and {end}:".format(start=start, end=end))
        )
        self.stdout.write(self.style.HTTP_INFO("{}").format(org_data))


# type of update made
# meetings = instances.filter(update_source="meeting")
# alerts = instances.filter(update_source="alert")
# command = instances.filter(update_source="command")
# alerts sent

# alert templates made

# zoom meetings


# instances.filter(user__organization=org)
