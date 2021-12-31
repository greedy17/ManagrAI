from datetime import datetime, timedelta
import pytz
import logging

from django.utils import timezone

from django.core.management.base import BaseCommand, CommandError
from managr.salesforce.cron import get_products

logger = logging.getLogger("managr")


class Command(BaseCommand):
    help = "Helper for restarting the sf sync"

    def add_arguments(self, parser):
        parser.add_argument(
            "--force", action="store_true", help="Delete poll instead of closing it",
        )

    def handle(self, *args, **options):

        get_products("286b825b-a58b-4166-a6a8-8309462dace2")
