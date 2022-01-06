from django.utils import timezone

from django.core.management.base import BaseCommand, CommandError
from managr.core.models import User
from managr.core import constants as core_consts


class Command(BaseCommand):
    help = "Check each user for reminders"

    def add_arguments(self, parser):
        parser.add_argument("-u", "--users", nargs="+", type=str)
        parser.add_argument("-t", "--total", action="store_true")

    def handle(self, *args, **options):
        if options["users"]:
            for t in options["users"]:
                user = User.objects.filter(email=t).first()
                self.stdout.write(
                    self.style.SUCCESS("Checking reminders for: {}".format(user.email,)),
                )
        else:
            users = User.objects.filter(is_active=True)
            reminder_config = core_consts.REMINDERS()
            for user in users:
                if user.reminders is None:
                    user.reminders = core_consts.REMINDERS()
                    user.save()
                elif options["total"]:
                    user.reminders = core_consts.REMINDERS()
                    user.save()
                else:
                    for key in reminder_config.keys():
                        if key in user.reminders.keys():
                            continue
                        else:
                            user.reminders[key] = True
                    user.save()
            self.stdout.write(self.style.SUCCESS("Refreshing reminders"),)
