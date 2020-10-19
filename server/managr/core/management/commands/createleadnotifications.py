from django.core.management.base import BaseCommand, CommandError
from managr.core.cron import create_lead_notifications


class Command(BaseCommand):
    """ manage.py service to create service accounts """

    help = "Create Service account for different uses"

    def handle(self, *args, **kwargs):
        """ will throw error if service_email is not provided """

        create_lead_notifications()

        self.stdout.write(self.style.SUCCESS("Successfully sent notifications"))
