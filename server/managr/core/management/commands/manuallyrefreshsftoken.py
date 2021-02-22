from django.core.management.base import BaseCommand, CommandError
from managr.salesforce.models import SalesforceAuthAccount


class Command(BaseCommand):
    help = "Helper for dev to regen tokens"

    def add_arguments(self, parser):
        parser.add_argument("users", nargs="+", type=str)

    def handle(self, *args, **options):
        for t in options["users"]:
            sf = SalesforceAuthAccount.objects.filter(user__email=t).first()
            sf.regenerate_token()
            self.stdout.write(
                self.style.SUCCESS(
                    "Successfully closed refreshed token for user {} their token now is {}".format(
                        sf.user.email, sf.access_token
                    )
                )
            )
