from django.utils import timezone

from django.core.management.base import BaseCommand, CommandError
from managr.salesforce.models import SalesforceAuthAccount
from managr.core.models import User
from managr.salesforce.cron import report_sf_data_sync
from managr.salesforce import constants as sf_consts


class Command(BaseCommand):
    help = "Helper for restarting the sf sync"

    def add_arguments(self, parser):
        parser.add_argument(
            "--user", action="store_true", help="Delete poll instead of closing it",
        )

    def handle(self, *args, **options):
        if options["user"]:

            for t in options["user"]:
                user = User.objects.filter(email=t).first()
                if hasattr(user, "salesforce_account"):
                    report_sf_data_sync(user.sf_account)
                    self.stdout.write(
                        self.style.SUCCESS(
                            "Successfully initiated the sync for the user {}".format(user.email,)
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR(
                            "Successfully initiated the sync for the user {}".format(user.email,)
                        )
                    )
        else:
            report_sf_data_sync()

