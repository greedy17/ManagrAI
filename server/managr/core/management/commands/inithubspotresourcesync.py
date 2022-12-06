from datetime import datetime, timedelta
import pytz
import logging

from django.core.management.base import BaseCommand, CommandError
from managr.hubspot.cron import queue_users_hs_resource
from managr.hubspot.tasks import emit_gen_next_hubspot_sync
from managr.core.models import User

logger = logging.getLogger("managr")


class Command(BaseCommand):
    help = "Helper for restarting the hs sync"

    def add_arguments(self, parser):
        parser.add_argument("-u", "--users", nargs="+", type=str)
        parser.add_argument(
            "--force", action="store_true", help="Delete poll instead of closing it",
        )

    def handle(self, *args, **options):
        if options["users"]:
            for t in options["users"]:
                user = User.objects.filter(email=t).first()
                if not hasattr(user, "hubspot_account"):
                    self.stdout.write(
                        self.style.ERROR("User does not have an hs account {}".format(user.email,))
                    )
                    continue
                operations = user.hubspot_account.resource_sync_opts
                scheduled_time = datetime.now(pytz.utc)
                formatted_time = scheduled_time.strftime("%Y-%m-%dT%H:%M%Z")
                emit_gen_next_hubspot_sync(str(user.id), operations, formatted_time)
            return logger.info("Starting hubspot resource sync for {}".format(options["users"]))
        else:
            # Temp HACK: currently disabling resource sync during field sync
            now = datetime.now(pytz.utc)
            noon = datetime(day=now.day, month=now.month, year=now.year, hour=12, tzinfo=pytz.utc)
            noon_plus_10_mins = noon + timedelta(minutes=10)
            midnight = datetime(day=now.day, month=now.month, year=now.year, tzinfo=pytz.utc)
            midnight_plus_10_mins = midnight + timedelta(minutes=10)
            if now >= noon and now <= noon_plus_10_mins:
                return logger.info("Skipping sync between noon utc time and 10 mins after")
            elif now >= noon and now <= midnight_plus_10_mins:
                return logger.info("Skipping sync between midnight utc time and 10 mins after")
            else:
                queue_users_hs_resource(force_all=options.get("force", None))
                return logger.info("Starting hubspot resource sync for all users")
