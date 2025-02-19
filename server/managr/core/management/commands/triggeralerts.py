import datetime

import pytz
from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.timezone import make_aware

from managr.comms.models import AssistAlert
from managr.comms.tasks import (
    emit_send_news_summary,
    emit_send_omni_summary,
    emit_send_social_summary,
)


class Command(BaseCommand):
    help = "Add background tasks for sending email news summary"

    def add_arguments(self, parser):
        parser.add_argument("ids", nargs="?", type=str, help="The id/ids of alerts to send"),
        parser.add_argument(
            "--test",
            action="store_true",
            help="For testing in staging and dev",
        )
        parser.add_argument(
            "--user",
            type=str,
            help="Send alerts for a specific user, by email",
            required=False,
        )

    def handle(self, *args, **options):
        func_switcher = {
            "NEWS": emit_send_news_summary,
            "SOCIAL": emit_send_social_summary,
            "OMNI": emit_send_omni_summary,
        }
        ids = options.get("ids", False)
        user = options.get("user", False)
        if ids:
            ids = ids.split(",")
            alerts = AssistAlert.objects.filter(id__in=ids)
        elif user:
            alerts = AssistAlert.objects.filter(user__email=user)
        else:
            alerts = AssistAlert.objects.all()
        current_day = datetime.datetime.now()
        for alert in alerts:
            if settings.IN_DEV or options["test"]:
                run_at = str(datetime.datetime.now())
            else:
                user_tz = pytz.timezone(alert.user.timezone)
                run_at = make_aware(alert.run_at, timezone=user_tz)
                run_at = run_at.replace(
                    year=current_day.year, month=current_day.month, day=current_day.day
                )
                run_at = str(run_at)
            alert_func = func_switcher[alert.search_type]
            alert_func(str(alert.id), run_at)
        return
