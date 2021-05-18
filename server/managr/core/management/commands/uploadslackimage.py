from django.utils import timezone

from django.core.management.base import BaseCommand, CommandError
from managr.salesforce.models import SalesforceAuthAccount
from managr.core.models import User

from managr.utils.misc import upload_to_bucket
from django.conf import settings
import os


class Command(BaseCommand):
    help = "Upload images for slack to aws takes in a path"

    def add_arguments(self, parser):
        parser.add_argument("files", nargs="+", type=str)

    def handle(self, *args, **options):
        for t in options["files"]:
            head_tail = os.path.split(t)
            if len(head_tail) == 2:
                self.stdout.write(self.style.SUCCESS(head_tail[1]))
                try:
                    upload_to_bucket(
                        t,
                        "production/slack/" + head_tail[1],
                        settings.AWS_STORAGE_BUCKET_NAME,
                        settings.AWS_ACCESS_KEY_ID,
                        settings.AWS_SECRET_ACCESS_KEY,
                    )
                except Exception as e:
                    self.stdout.write(self.style.ERROR(e))

            self.stdout.write(self.style.SUCCESS(t))
