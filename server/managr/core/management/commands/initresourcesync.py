import datetime
import pytz
import logging

from django.utils import timezone

from django.core.management.base import BaseCommand, CommandError
from managr.salesforce.cron import queue_users_sf_resource

logger = logging.getLogger("managr")


class Command(BaseCommand):
    help = "Helper for restarting the sf sync"

    def add_arguments(self, parser):
        parser.add_argument(
            "--force", action="store_true", help="Delete poll instead of closing it",
        )

    def handle(self, *args, **options):
        # Temp HACK: currently disabling resource sync during field sync
        now = datetime.now()
        noon = datetime(day=now.day, month=now.month, year=now.year, hour=12, tzinfo=pytz.utc)
        noon_plus_10_mins = noon + datetime.timedelat(minutes=10)
        midnight = datetime(day=now.day, month=now.month, year=now.year, tzinfo=pytz.utc)
        midnight_plus_10_mins = midnight + datetime.timedelat(minutes=10)
        if now >= noon and noon <= noon_plus_10_mins:
            return logger.info("Skipping sync between noon utc time and 10 mins after")
        elif now >= noon and midnight <= midnight_plus_10_mins:
            return logger.info("Skipping sync between midnight utc time and 10 mins after")
        else:
            queue_users_sf_resource(force_all=options.get("force", None))
