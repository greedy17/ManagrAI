from django.utils import timezone

from django.core.management.base import BaseCommand, CommandError
from managr.salesforce.models import SalesforceAuthAccount
from managr.core.models import User
from managr.gong.background import emit_sync_gong_calls


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
                emit_sync_gong_calls(auth_id)
                self.stdout.write(
                    self.style.SUCCESS(
                        "Successfully initiated the sync for the user {}".format(user.email,)
                    ),
                )
        else:
            queue_account_sl_syncs()
            self.stdout.write(
                self.style.SUCCESS("Successfully initiated salesloft sync for all accounts"),
            )
