import datetime
from django.conf import settings
from django.core.management.base import BaseCommand
from managr.comms.models import AssistAlert
from managr.comms.tasks import emit_send_news_summary, emit_send_social_summary
from managr.comms.utils import convert_to_server_time


class Command(BaseCommand):
    help = "Add background tasks for sending email news summary"

    def add_arguments(self, parser):
        parser.add_argument("ids", nargs="?", type=str, help="The id/ids of alerts to send"),
        parser.add_argument(
            "--test",
            action="store_true",
            help="For testing in staging and dev",
        )

    def handle(self, *args, **options):
        ids = options.get("ids", False)
        if ids:
            ids = ids.split(",")
            alerts = AssistAlert.objects.filter(id__in=ids)
        else:
            alerts = AssistAlert.objects.all()
        current_day = datetime.datetime.now()
        for alert in alerts:
            if settings.IN_DEV or options["test"]:
                run_at = str(datetime.datetime.now())
            else:
                run_at = convert_to_server_time(alert.run_at, alert.user.timezone)
                run_at = run_at.replace(
                    year=current_day.year, month=current_day.month, day=current_day.day
                )
            run_at = str(run_at)
            if alert.search.type == "NEWS":
                emit_send_news_summary(str(alert.id), run_at)
            else:
                emit_send_social_summary(str(alert.id), run_at)
        return
