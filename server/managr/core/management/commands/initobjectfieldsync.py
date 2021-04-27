from django.utils import timezone

from django.core.management.base import BaseCommand, CommandError
from managr.salesforce.cron import queue_users_sf_fields


class Command(BaseCommand):
    help = "Helper for restarting the sf sync"

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Force all items to resync despite previous failure",
        )

    def handle(self, *args, **options):

        queue_users_sf_fields(force_all=options.get("force", None))
