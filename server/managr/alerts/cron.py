import logging
import kronos
import math

from datetime import datetime
from django.conf import settings
from django.template.loader import render_to_string
from django.utils import timezone
from django.db.models import Q, F, Func, IntegerField, DateField, Sum
from django.db.models.functions import Cast

from managr.alerts.models import AlertTemplate, AlertConfig
from managr.alerts.background import emit_init_alert


@kronos.register("*/10  * * * *")
def init_alert_check():
    configs = AlertConfig.objects.filter(
        Q(template__user__is_active=True, template__is_active=True)
        & Q(
            Q(recurrence_frequency="WEEKLY", recurrence_day=timezone.now().weekday())
            | Q(recurrence_frequency="MONTHLY", recurrence_day=timezone.now().day)
        )
    )
    for config in configs:
        emit_init_alert(str(config.id))
    return

