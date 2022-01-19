import uuid
from django.core.management.base import BaseCommand, CommandError
from managr.core.models import User
from managr.core.background import emit_check_reminders


class Command(BaseCommand):
    help = "Check each user for reminders"

    def add_arguments(self, parser):
        parser.add_argument("-u", "--users", nargs="+", type=str)

    def handle(self, *args, **options):
        if options["users"]:
            for t in options["users"]:
                user = User.objects.filter(email=t).first()
                emit_check_reminders(user.id, f"reminders-{user.email}-{str(uuid.uuid4())}")
                self.stdout.write(
                    self.style.SUCCESS("Checking reminders for: {}".format(user.email,)),
                )
        else:
            users = User.objects.filter(is_active=True)
            for user in users:
                emit_check_reminders(user.id, f"reminders-{user.email}-{str(uuid.uuid4())}")
            self.stdout.write(self.style.SUCCESS("Checking reminders for all users"),)
