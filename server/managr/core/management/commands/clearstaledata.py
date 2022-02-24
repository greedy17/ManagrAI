from django.utils import timezone

from django.core.management.base import BaseCommand, CommandError
from managr.salesloft.cron import queue_stale_salesloft_data_for_delete


class Command(BaseCommand):
    help = "Clear Stale Data for selected resource"

    def add_arguments(self, parser):
        parser.add_argument("cutoff", nargs="+", type=int)

    def handle(self, *args, **options):
        cutoff = options["cutoff"][0]
        return queue_stale_salesloft_data_for_delete(cutoff)
