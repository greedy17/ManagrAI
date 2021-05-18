from django.utils import timezone

from django.core.management.base import BaseCommand, CommandError
from managr.salesforce.models import SalesforceAuthAccount
from managr.core.models import User
from managr.salesforce.background import emit_sf_sync, emit_gen_next_sync
from managr.salesforce import constants as sf_consts


class Command(BaseCommand):
    help = "Helper for restarting the sf sync"

    def add_arguments(self, parser):
        parser.add_argument("users", nargs="+", type=str)

    def handle(self, *args, **options):
        for t in options["users"]:
            user = User.objects.filter(email=t).first()

            operations = [
                sf_consts.RESOURCE_SYNC_ACCOUNT,
                sf_consts.RESOURCE_SYNC_CONTACT,
                sf_consts.RESOURCE_SYNC_OPPORTUNITY,
                sf_consts.RESOURCE_SYNC_LEAD,
            ]
            scheduled_time = timezone.now()
            formatted_time = scheduled_time.strftime("%Y-%m-%dT%H:%M%Z")
            emit_gen_next_sync(str(user.id), operations, formatted_time)
            self.stdout.write(
                self.style.SUCCESS(
                    "Successfully initiated the sync for the user {}".format(
                        user.email,
                    )
                )
            )
