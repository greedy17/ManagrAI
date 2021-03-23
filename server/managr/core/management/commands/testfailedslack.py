from django.utils import timezone

from django.core.management.base import BaseCommand, CommandError
from managr.salesforce.models import SalesforceAuthAccount
from managr.core.models import User
from managr.salesforce.background import emit_sf_sync, emit_gen_next_sync
from managr.salesforce import constants as sf_consts
from managr.slack.helpers.slackerrorstest import send_failed_slack


class Command(BaseCommand):
    help = "Helper for restarting the sf sync"

    def handle(self, *args, **options):
        return send_failed_slack()

