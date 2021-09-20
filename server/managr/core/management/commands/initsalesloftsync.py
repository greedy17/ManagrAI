from django.utils import timezone

from django.core.management.base import BaseCommand, CommandError
from managr.salesforce.models import SalesforceAuthAccount
from managr.core.models import User
from managr.salesloft.background import emit_sync_cadences, emit_sync_slaccounts, emit_sync_people


class Command(BaseCommand):
    help = "Helper starting SL sync"

    def add_arguments(self, parser):
        parser.add_argument("users", nargs="+", type=str)

    def handle(self, *args, **options):
        for t in options["users"]:
            user = User.objects.filter(email=t).first()
            if not hasattr(user, "salesloft_account"):
                self.stdout.write(
                    self.style.ERROR("User does not have an sl account {}".format(user.email,))
                )
            auth_id = str(user.salesloft_account.auth_account.id)
            emit_sync_slaccounts(auth_id)
            emit_sync_people(auth_id)
            emit_sync_cadences(auth_id)
            self.stdout.write(
                self.style.SUCCESS(
                    "Successfully initiated the sync for the user {}".format(user.email,)
                )
            )
