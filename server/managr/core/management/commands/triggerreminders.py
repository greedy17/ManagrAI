from django.utils import timezone

from django.core.management.base import BaseCommand, CommandError
from managr.core.models import User
from managr.core.cron import check_reminders


class Command(BaseCommand):
    help = "Check each user for reminders"

    def add_arguments(self, parser):
        parser.add_argument("-u", "--users", nargs="+", type=str)

    def handle(self, *args, **options):
        if options["users"]:
            for t in options["users"]:
                user = User.objects.filter(email=t).first()
                check_reminders(user.id)
                self.stdout.write(
                    self.style.SUCCESS("Checking reminders for: {}".format(user.email,)),
                )
        else:
            users = User.objects.filter(is_active=True)
            for user in users:
                check_reminders(user.id)
            self.stdout.write(self.style.SUCCESS("Checking reminders for all users"),)
