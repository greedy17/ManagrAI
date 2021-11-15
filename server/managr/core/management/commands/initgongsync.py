from django.utils import timezone

from django.core.management.base import BaseCommand, CommandError
from managr.salesforce.models import SalesforceAuthAccount
from managr.core.models import User
from managr.gong.cron import queue_gong_sync


class Command(BaseCommand):
    help = "Helper starting gong call sync"

    def add_arguments(self, parser):
        parser.add_argument("-u", "--users", nargs="+", type=str)

    def handle(self, *args, **options):
        if options["users"]:
            for t in options["users"]:
                user = User.objects.filter(email=t).first()
                if not hasattr(user, "gong_account"):
                    self.stdout.write(
                        self.style.ERROR("User does not have a gong account {}".format(user.email,))
                    )
                auth_id = user.gong_account.auth_account.id
                queue_gong_sync(str(auth_id))
                self.stdout.write(
                    self.style.SUCCESS(
                        "Successfully initiated gong sync for the user {}".format(user.email,)
                    ),
                )
        else:
            queue_gong_sync()
            self.stdout.write(
                self.style.SUCCESS("Successfully initiated gong sync for all accounts"),
            )
