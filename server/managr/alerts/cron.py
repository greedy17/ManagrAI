import logging
import kronos
import math

from datetime import datetime
from django.conf import settings
from django.template.loader import render_to_string
from django.utils import timezone
from django.db.models import Q, F, Func, IntegerField, DateField, Sum
from django.db.models.functions import Cast

from managr.alerts.models import AlertTemplate
from managr.alerts.background import emit_init_alert


@kronos.register("*/10  * * * *")
def init_alert_check():
    alerts = AlertTemplate.objects.filter(user__is_active=True, is_active=True)
    for alert in alerts:
        emit_init_alert(str(alert.id))
    return

