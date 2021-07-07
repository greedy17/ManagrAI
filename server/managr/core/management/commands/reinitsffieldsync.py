from django.utils import timezone

from django.core.management.base import BaseCommand, CommandError
from managr.salesforce.models import SalesforceAuthAccount
from managr.core.models import User
from managr.salesforce.background import (
    emit_sf_sync,
    emit_gen_next_sync,
    emit_gen_next_object_field_sync,
)
from managr.salesforce import constants as sf_consts


class Command(BaseCommand):
    help = "Helper for restarting the sf sync"

    def add_arguments(self, parser):
        parser.add_argument("users", nargs="+", type=str)

    def handle(self, *args, **options):
        for t in options["users"]:
            user = User.objects.filter(email=t).first()

            if not hasattr(user, "salesforce_account"):
                self.stdout.write(
                    self.style.ERROR("User does not have an sf account {}".format(user.email,))
                )
            operations = [
                *user.salesforce_account.field_sync_opts,
                *user.salesforce_account.validation_sync_opts,
            ]
            scheduled_time = timezone.now()
            formatted_time = scheduled_time.strftime("%Y-%m-%dT%H:%M%Z")
            emit_gen_next_object_field_sync(str(user.id), operations, formatted_time)
            self.stdout.write(
                self.style.SUCCESS(
                    "Successfully initiated the object field sync for the user {}".format(
                        user.email,
                    )
                )
            )
