from django.core.management.base import BaseCommand, CommandError
from managr.core.models import User


class Command(BaseCommand):
    """ manage.py service to create service accounts """
    help = 'Create Service account for different uses'

    def add_arguments(self, parser):
        parser.add_argument('service_email', type=str)

    def handle(self, *args, **kwargs):
        """ will throw error if service_email is not provided """
        email = kwargs['service_email']

        password = input("password: ")
        print(self.style)
        user = User.objects.create_serviceaccount(
            email=email, password=password)

        self.stdout.write(self.style.SUCCESS(
            'Successfully created service email "%s"' % user.email))

        self.stdout.write(self.style.WARNING(
            'In order to use this account please authenticate with nylas using this link "%s"' % user.email_auth_link))
