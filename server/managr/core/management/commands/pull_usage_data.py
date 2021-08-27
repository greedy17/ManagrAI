from django.utils import timezone
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from datetime import datetime, timedelta
from managr.core.models import User
from managr.zoom.models import ZoomMeeting
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
        parser.add_argument("start_date", type=str, help="Custom start format 'Month Day Year'")
        parser.add_argument("end_date", type=str, help="Custom end date format 'Month Day Year'")

    def handle(self, *args, **kwargs):
        start = kwargs["start_date"]
        end = kwargs["end_date"]
        # Get date range for range
        if not start and not end:
            end = datetime.date.today()
            start = end - datetime.timedelta(end.day - 1)
        else:
            create_date = datetime.datetime.strptime(start, "%b %d %Y")
            end = create_date.date()
            start = end - datetime.timedelta(end.day - 1)

        # Base queries
        total_users = User.objects.all().count()
        user_count_in_range = User.objects.filter(datetime_created__range=(start, end)).count()
        slack_form_instances = OrgCustomSlackFormInstance.objects.filter(
            datetime_created__range=(start, end)
        ).filter(is_submitted=True).filter(template__form_type="UPDATE")
        alerts_sent = AlertInstance.objects.filter(datetime_created__range=(start, end)).filter(
            sent_at__range=(start, end)
        )
        alert_templates = AlertTempalte.objects.filter(datetime_created__range=(start, end))
        zoom_meetings = ZoomMeeting.objects.filter(datetime_created__range=(start, end))
        orgs = Organization.objects.all()

        totals = {
            "user_total" : total_users,
            "new_users" : user_count_in_range,
            "updates" : slack_form_instances,

        }
        org_data = {

        }
        for org in orgs:



# type of update made
# meetings = instances.filter(update_source="meeting")
# alerts = instances.filter(update_source="alert")
# command = instances.filter(update_source="command")
# alerts sent

# alert templates made

# zoom meetings


# instances.filter(user__organization=org)
