from django.utils import timezone

from django.core.management.base import BaseCommand, CommandError
from managr.salesforce.models import SalesforceAuthAccount
from managr.core.models import User
from managr.salesforce.background import emit_generate_form_template
from managr.hubspot.tasks import emit_generate_hs_form_template
from managr.salesforce import constants as sf_consts


class Command(BaseCommand):
    help = "Helper for restarting the sf sync"

    def add_arguments(self, parser):
        parser.add_argument("users", nargs="+", type=str)

    def handle(self, *args, **options):
        for t in options["users"]:
            user = User.objects.filter(email=t).first()

        if user.is_admin:
            if user.crm == "SALESFORCE":
                emit_generate_form_template(str(user.id), True)
            else:
                emit_generate_hs_form_template(str(user.id), True)
            self.stdout.write(
                self.style.SUCCESS(
                    "Successfully initiated form recreation for  {}".format(user.email,)
                )
            )
        else:
            self.stdout.write(self.style.ERROR("User is not admin {}".format(user.email,)))
