from django.utils import timezone

from django.core.management.base import BaseCommand, CommandError
from managr.salesforce.cron import queue_stale_sf_data_for_delete


class Command(BaseCommand):
    help = "Clear Stale SF Data"

    def add_arguments(self, parser):
        parser.add_argument("cutoff", nargs="+", type=int)

    def handle(self, *args, **options):
        cutoff = options["cutoff"][0]
        return queue_stale_sf_data_for_delete(cutoff)
