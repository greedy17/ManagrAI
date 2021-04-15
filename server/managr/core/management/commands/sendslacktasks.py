from django.core.management.base import BaseCommand, CommandError

from managr.salesforce.cron import send_daily_tasks

class Command(BaseCommand):
    help = "Helper for sending task list to slack at 7am every morning"

    

    def handle(self, *args, **options):
        send_daily_tasks()
       