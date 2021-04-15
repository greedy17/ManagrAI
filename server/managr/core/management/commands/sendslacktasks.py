from django.utils import timezone

from django.core.management.base import BaseCommand, CommandError
from managr.salesforce.models import SalesforceAuthAccount
from managr.core.models import User
from managr.salesforce.cron import report_sf_data_sync
from managr.salesforce import constants as sf_consts

from managr.salesforce.cron import send_daily_tasks

class Command(BaseCommand):
    help = "Helper for sending task list to slack at 7am every morning"

    # def add_arguments(self, parser):
    #     parser.add_argument(
    #         "--user", action="store_true", help="Delete poll instead of closing it",
    #     )

    def handle(self, *args, **options):
        send_daily_tasks()
        # queue_users_sf_fields(force_all=options.get("force", None))