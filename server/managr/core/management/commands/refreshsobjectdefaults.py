from django.utils import timezone

from django.core.management.base import BaseCommand, CommandError
from managr.core.models import User
from managr.salesforce.models import getSobjectDefaults


class Command(BaseCommand):
    help = "Check each user for reminders"

    def add_arguments(self, parser):
        parser.add_argument("-u", "--users", nargs="+", type=str)
        parser.add_argument("-t", "--total", action="store_true")

    def handle(self, *args, **options):
        if options["users"]:
            sobjects = getSobjectDefaults()
            for t in options["users"]:
                user = User.objects.filter(email=t)
                if hasattr(user, "salesforce_account"):
                    if options["total"]:
                        user.salesforce_account.sobjects = sobjects
                        user.salesforce_account.save()
                        self.stdout.write(
                            self.style.SUCCESS("Resetting sobjects for user {}".format(t))
                        )
                    else:
                        for key in sobjects.keys():
                            if key in user.salesforce_account.sobjects.keys():
                                continue
                            else:
                                user.salesforce_account.sobjects[key] = True
                        user.salesforce_account.save()
                        self.stdout.write(
                            self.style.SUCCESS("Refreshing sobjects for user {}".format(t))
                        )
        else:
            users = User.objects.filter(is_active=True)
            sobjects = getSobjectDefaults()
            for user in users:
                if hasattr(user, "salesforce_account"):
                    if options["total"]:
                        user.salesforce_account.sobjects = sobjects
                        user.salesforce_account.save()
                    else:
                        for key in sobjects.keys():
                            if key in user.salesforce_account.sobjects.keys():
                                continue
                            else:
                                user.salesforce_account.sobjects[key] = True
                        user.salesforce_account.save()
            if options["total"]:
                self.stdout.write(self.style.SUCCESS("Resetting sobjects for users"))
            else:
                self.stdout.write(self.style.SUCCESS("Refreshing sobjects for all users"),)
