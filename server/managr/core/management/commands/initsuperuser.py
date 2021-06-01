import os
from django.utils import timezone

from django.core.management.base import BaseCommand, CommandError

from managr.core.models import User


class Command(BaseCommand):
    help = "Create's an initial super user if one does not exist"

    def handle(self, *args, **options):
        u = User.objects.filter(is_superuser=True).count()
        if not u:
            email = os.environ.get("SUPERUSER_EMAIL")
            password = os.environ.get("SUPERUSER_PASSWORD")
            # create a super user
            User.objects.create_superuser(email, password)
            self.stdout.write(self.style.SUCCESS("Created SU with email {}".format(email)))
