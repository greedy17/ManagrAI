from django.utils import timezone

from django.core.management.base import BaseCommand, CommandError
from managr.salesforce.models import SalesforceAuthAccount
from managr.core.models import User
from managr.salesforce.cron import report_sf_data_sync
from managr.salesforce import constants as sf_consts

from managr.alerts.cron import init_alert_check


class Command(BaseCommand):
    help = "Helper for restarting the sf sync"

    def handle(self, *args, **options):

        return init_alert_check()
