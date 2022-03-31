from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from managr.core.utils import get_totals_for_year


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
        totals = get_totals_for_year()
        self.stdout.write(self.style.HTTP_INFO("{}").format(totals))

