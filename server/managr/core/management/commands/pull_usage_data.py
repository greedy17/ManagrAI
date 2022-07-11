from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from managr.core.utils import get_totals_for_year
from managr.api.emails import send_html_email


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

    def handle(self, *args, **options):
        # email_subject = "Managr Usage Data"
        # recipients = ["zach@mymanagr.com"]
        totals = get_totals_for_year()
        # send_html_email(
        #     email_subject,
        #     "core/email-templates/usage-data.html",
        #     settings.SERVER_EMAIL,
        #     recipients,
        #     context=totals,
        # )
        self.stdout.write(self.style.HTTP_INFO("{}").format(totals))

