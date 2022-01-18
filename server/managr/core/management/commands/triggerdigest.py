import uuid
from django.utils import timezone

from django.core.management.base import BaseCommand, CommandError
from managr.core.models import User
from managr.core.background import emit_generate_afternoon_digest, emit_generate_morning_digest


class Command(BaseCommand):
    help = "Check each user for reminders"

    def add_arguments(self, parser):
        parser.add_argument("-u", "--users", nargs="+", type=str)
        parser.add_argument("-t", "--time", nargs="+", type=str)

    def handle(self, *args, **options):
        time = options["time"][0]
        for t in options["users"]:
            user = User.objects.filter(email=t).first()
            if time == "morning":
                emit_generate_morning_digest(
                    str(user.id), f"morning-digest-{user.email}-{str(uuid.uuid4())}"
                )
            elif time == "afternoon":
                emit_generate_afternoon_digest(
                    str(user.id), f"afternoon-digest-{user.email}-{str(uuid.uuid4())}"
                )
            else:
                emit_generate_morning_digest(
                    str(user.id), f"morning-digest-{user.email}-{str(uuid.uuid4())}"
                )
            self.stdout.write(
                self.style.SUCCESS("Creating {} digest for {}".format(time, user.email,)),
            )

