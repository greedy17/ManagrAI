from django.utils import timezone

from django.core.management.base import BaseCommand, CommandError
from managr.core.models import User
from managr.core.cron import generate_morning_digest
from managr.core.cron import generate_afternoon_digest


class Command(BaseCommand):
    help = "Check each user for reminders"

    def add_arguments(self, parser):
        parser.add_argument("-u", "--users", nargs="+", type=str)
        parser.add_argument("-t", "--time", nargs="+", type=str)

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Time: {}".format(options["time"])))
        time = options["time"][0]
        users = options["users"]
        for t in options["users"]:
            user = User.objects.filter(email=t).first()
            if time == "morning":
                generate_morning_digest(str(user.id))
            elif time == "afternoon":
                generate_afternoon_digest(str(user.id))
            else:
                return
            self.stdout.write(self.style.SUCCESS("Checking reminders for: {}".format(user.email,)),)

