import datetime
from django.conf import settings
from django.core.management.base import BaseCommand
from managr.comms.models import EmailAlert
from managr.comms.tasks import emit_send_news_summary


class Command(BaseCommand):
    help = "Add background tasks for sending email news summary"

    def add_arguments(self, parser):
        parser.add_argument(
            "--test",
            action="store_true",
            help="For testing in staging and dev",
        )

    def handle(self, *args, **options):
        alerts = EmailAlert.objects.all()
        current_day = datetime.datetime.now()
        for alert in alerts:
            if settings.IN_DEV or options["test"]:
                run_at = str(datetime.datetime.now())
            else:
                run_at = alert.run_at.replace(
                    year=current_day.year, month=current_day.month, day=current_day.day
                )
                run_at = str(run_at)
            emit_send_news_summary(str(alert.id), run_at)
        return
