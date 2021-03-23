from django.utils import timezone

from django.core.management.base import BaseCommand, CommandError
from managr.salesforce.cron import queue_users_sf_resource


class Command(BaseCommand):
    help = "Helper for restarting the sf sync"

    def handle(self, *args, **options):
        queue_users_sf_resource()
