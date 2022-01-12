from django.utils import timezone

from django.core.management.base import BaseCommand, CommandError
from managr.salesforce.models import SalesforceAuthAccount
from managr.core.models import User

from managr.core.cron import _send_calendar_details, _process_calendar_details


class Command(BaseCommand):
    help = "Helper for restarting the sf sync"

    def add_arguments(self, parser):
        parser.add_argument("-u", "--users", nargs="+", type=str)

    def handle(self, *args, **options):
        if options["users"]:
            for t in options["users"]:
                user = User.objects.filter(email=t).first()
                if not hasattr(user, "nylas"):
                    self.stdout.write(
                        self.style.ERROR(
                            "User does not have a nylas account {}".format(user.email,)
                        )
                    )
                _send_calendar_details(user.id)
                self.stdout.write(
                    self.style.SUCCESS(
                        "Successfully initiated nylas sync for the user {}".format(user.email,)
                    ),
                )
        else:
            users = User.objects.all()
            for user in users:
                if hasattr(user, "nylas"):
                    _send_calendar_details(user.id)
            self.stdout.write(
                self.style.SUCCESS("Successfully initiated nylas sync for all accounts"),
            )
