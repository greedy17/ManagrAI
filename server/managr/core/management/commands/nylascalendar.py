from django.utils import timezone

from django.core.management.base import BaseCommand, CommandError
from managr.salesforce.models import SalesforceAuthAccount
from managr.core.models import User

from managr.core.cron  import _convert_nylas_calendar_details


class Command(BaseCommand):
    help = "Helper for restarting the sf sync"

    def add_arguments(self, parser):
        parser.add_argument("-u", "--users", nargs="+", type=str)

    def handle(self, *args, **options):
        if options["users"]:
            for t in options["users"]:
                user = User.objects.filter(email=t).first()
                if not hasattr(user, "nylas_account"):
                    self.stdout.write(
                        self.style.ERROR("User does not have a nylas account {}".format(user.email,))
                    )
                auth_id = str(user.nylas_account.auth_account.id)
                _convert_nylas_calendar_details(auth_id)
                self.stdout.write(
                    self.style.SUCCESS(
                        "Successfully initiated nylas sync for the user {}".format(user.email,)
                    ),
                )
        else:
            _convert_nylas_calendar_details()
            self.stdout.write(
                self.style.SUCCESS("Successfully initiated nylas sync for all accounts"),
            )
