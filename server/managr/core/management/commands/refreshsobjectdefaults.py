from django.utils import timezone

from django.core.management.base import BaseCommand, CommandError
from managr.core.models import User
from managr.salesforce.models import getSobjectDefaults


class Command(BaseCommand):
    help = "Check each user for reminders"

    def add_arguments(self, parser):
        parser.add_argument("-u", "--users", nargs="+", type=str)

    def handle(self, *args, **options):
        if options["users"]:
            for t in options["users"]:
                user = User.objects.filter(email=t).first()
                self.stdout.write(
                    self.style.SUCCESS("Checking reminders for: {}".format(user.email,)),
                )
        else:
            users = User.objects.filter(is_active=True)
            sobjects = getSobjectDefaults()
            for user in users:
                if hasattr(user, "salesforce_account"):
                    print(sobjects)
                    for key in sobjects.keys():
                        if key in user.salesforce_account.sobjects.keys():
                            continue
                        else:
                            user.salesforce_account.sobjects[key] = True
                    user.salesforce_account.save()
            self.stdout.write(self.style.SUCCESS("Refreshing sobjects for all users"),)
