from django.utils import timezone

from django.core.management.base import BaseCommand, CommandError
from managr.salesforce.models import SalesforceAuthAccount
from managr.core.models import User
from managr.salesforce.background import (
    emit_sf_sync,
    emit_gen_next_sync,
    emit_gen_next_object_field_opp_sync,
    emit_generate_form_template,
)
from managr.salesforce import constants as sf_consts


class Command(BaseCommand):
    help = "Helper for restarting the sf sync"

    def add_arguments(self, parser):
        parser.add_argument("users", nargs="+", type=str)

    def handle(self, *args, **options):
        for t in options["users"]:
            user = User.objects.filter(email=t).first()

        if user.is_admin:

            emit_generate_form_template(str(user.id))
            self.stdout.write(
                self.style.SUCCESS(
                    "Successfully initiated the object field sync for the user {}".format(
                        user.email,
                    )
                )
            )
        else:
            self.stdout.write(self.style.ERROR("User is not admin {}".format(user.email,)))
