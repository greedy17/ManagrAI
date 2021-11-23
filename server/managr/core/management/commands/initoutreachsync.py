from django.core.management.base import BaseCommand
from managr.core.models import User
from managr.outreach.cron import queue_outreach_sync


class Command(BaseCommand):
    help = "Helper starting Outreach sync"

    def add_arguments(self, parser):
        parser.add_argument("-u", "--users", nargs="+", type=str)

    def handle(self, *args, **options):
        if options["users"]:
            for t in options["users"]:
                user = User.objects.filter(email=t).first()
                if not hasattr(user, "outreach_account"):
                    self.stdout.write(
                        self.style.ERROR(
                            "User does not have an outreach account {}".format(user.email,)
                        )
                    )
                outreach_id = str(user.outreach_account.id)
                queue_outreach_sync(outreach_id)
                self.stdout.write(
                    self.style.SUCCESS(
                        "Successfully initiated the sync for the user {}".format(user.email,)
                    ),
                )
        else:
            queue_outreach_sync()
            self.stdout.write(
                self.style.SUCCESS("Successfully initiated outreach sync for all accounts"),
            )
