from django.utils import timezone

from django.core.management.base import BaseCommand
from managr.core.models import User
from managr.hubspot.cron import queue_users_hs_fields
from managr.hubspot.tasks import emit_gen_next_hubspot_field_sync


class Command(BaseCommand):
    help = "Helper for restarting the sf sync"

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Force all items to resync despite previous failure",
        )
        parser.add_argument("-users", nargs="+", type=str, default=[])

    def handle(self, *args, **options):
        if len(options["users"]):
            for t in options["users"]:
                user = User.objects.filter(email=t).first()
                if not hasattr(user, "hubspot_account"):
                    self.stdout.write(
                        self.style.ERROR("User does not have an hs account {}".format(user.email,))
                    )

                operations = [
                    *user.huspot_account.field_sync_opts,
                ]
                scheduled_time = timezone.now()
                formatted_time = scheduled_time.strftime("%Y-%m-%dT%H:%M%Z")
                emit_gen_next_hubspot_field_sync(str(user.id), operations, formatted_time)
                self.stdout.write(
                    self.style.SUCCESS(
                        "Successfully initiated field sync for the user {}".format(user.email,)
                    )
                )
        else:
            queue_users_hs_fields(force_all=options.get("force", None))
            self.stdout.write(
                self.style.SUCCESS("Successfully initiated field sync for all hubspot users")
            )
