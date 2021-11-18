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

from managr.outreach.background import (
    emit_sync_accounts,
    emit_sync_prospects,
    emit_sync_sequences,
    emit_sync_user_accounts,
)
from managr.outreach.models import OutreachAccount
from managr.core.models import User

from managr.api.decorators import log_all_exceptions
from managr.outreach.exceptions import TokenExpired

logger = logging.getLogger("managr")


# @kronos.register("0 * * * *")
def queue_outreach_sync(account_id=None):
    if account_id:
        sync_helper(account_id)
    else:
        outreach_accounts = OutreachAccount.objects.all()
        for account in outreach_accounts:
            sync_helper(account.id)
            logger.info("Started outreach sync for {account.user}")
            continue
    return


def sync_helper(auth_id):
    sync_steps = [emit_sync_sequences]
    outreach_account = OutreachAccount.objects.get(id=auth_id)
    v_name = uuid.uuid4()
    for step in sync_steps:
        attempts = 1
        # sync_step = step(str(outreach_account.id), f"{step.__name__}_{v_name}")
        sync_step = step(str(outreach_account.id))
        # while True:
        #     if attempts >= 20:
        #         break
        #     try:
        #         task = CompletedTask.objects.filter(verbose_name=f"{step.__name__}_{v_name}")
        #         if task:
        #             break
        #     except Exception as e:
        #         attempts += 1
        #         continue
    return
