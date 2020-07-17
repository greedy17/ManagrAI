from django.core.management.base import BaseCommand, CommandError
from managr.core.cron import revoke_extra_access_tokens


class Command(BaseCommand):
    """ manage.py service to create service accounts """
    help = 'Create Service account for different uses'

    def handle(self, *args, **kwargs):
        """ will throw error if service_email is not provided """

        revoke_extra_access_tokens()

        self.stdout.write(self.style.SUCCESS('Successfully cleared tokens'))
