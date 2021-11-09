import logging
import kronos
import math
import uuid

from datetime import datetime
from django.conf import settings
from django.template.loader import render_to_string
from django.utils import timezone
from django.db.models import Q, F, Func, IntegerField, DateField, Sum
from django.db.models.functions import Cast

from background_task.models import CompletedTask

from rest_framework.response import Response

from managr.gong.background import emit_sync_gong_calls, emit_sync_gong_accounts
from managr.gong.models import GongAuthAccount
from managr.core.models import User

from managr.api.decorators import log_all_exceptions
from managr.gong.exceptions import TokenExpired

logger = logging.getLogger("managr")


@kronos.register("30 * * * *")
def queue_gong_sync(auth_account=None):
    if auth_account:
        emit_sync_gong_accounts(auth_account)
        emit_sync_gong_calls(auth_account)
    else:
        gong_accounts = GongAuthAccount.objects.all()
        for account in gong_accounts:
            emit_sync_gong_accounts(str(account.id))
            emit_sync_gong_calls(str(account.id))
            logger.info("Started Gong call sync for {account.organization.name}")
            continue
    return

