import os
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from managr.core.change_lead_ashton import run_fn
from managr.core.models import User


class Command(BaseCommand):

    help = "Create Service account for different uses"

    def add_arguments(self, parser):
        parser.add_argument("email", type=str)

    def handle(self, *args, **kwargs):
        """ will throw error if  emailis not provided """
        env = os.environ.get("ENVIRONMENT")

        if env == "development" or env == "staging":
            self.stdout.write(self.style.ERROR(f"{kwargs}"))
            user = User.objects.filter(email=kwargs["email"]).first()
            if not user:
                self.stdout.write(
                    self.style.ERROR("Can only run this in staging or dev")
                )
                return
            run_fn(user)

            self.stdout.write(self.style.SUCCESS("Successfully sent notifications"))
        else:
            self.stdout.write(self.style.ERROR(f"Can only run this in staging or dev"))
