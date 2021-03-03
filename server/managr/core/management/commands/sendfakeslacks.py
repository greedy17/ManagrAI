from django.core.management.base import BaseCommand, CommandError
from managr.slack.helpers.example_payloads import trigger_fake_slack


class Command(BaseCommand):
    help = "Helper for dev to send slack messages"

    def add_arguments(self, parser):
        parser.add_argument("types", nargs="+", type=int)

    def handle(self, *args, **options):
        for t in options["types"]:
            trigger_fake_slack(int(t))
            self.stdout.write(self.style.SUCCESS('Successfully closed poll "%s"' % t))
