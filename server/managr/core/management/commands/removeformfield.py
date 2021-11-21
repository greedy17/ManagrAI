from django.utils import timezone
from django.db.models import Q
from django.core.management.base import BaseCommand, CommandError
from managr.core.models import User
from managr.slack.models import OrgCustomSlackForm
from managr.salesforce.background import remove_field
from managr.organization.models import Organization


class Command(BaseCommand):
    help = "Helper for restarting the sf sync"

    def add_arguments(self, parser):
        parser.add_argument("org_id", nargs="+", type=str)
        parser.add_argument("field_id", nargs="+", type=str)

    def handle(self, *args, **options):
        remove_field(options["org_id"][0], options["field_id"][0])
        self.stdout.write(
            self.style.SUCCESS(
                "Successfully removed field {} on form from org {}".format(
                    options["field_id"][0], options["org_id"][0]
                )
            )
        )
        # else:
        #     self.stdout.write(self.style.ERROR("User is not admin {}".format(user.email,)))
