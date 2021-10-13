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

from managr.salesloft import constants as sl_consts
from managr.salesloft.background import emit_sync_slaccounts, emit_sync_people, emit_sync_cadences
from managr.salesloft.models import SalesloftAuthAccount
from managr.core.models import User

from managr.api.decorators import log_all_exceptions
from managr.salesloft.exceptions import TokenExpired

logger = logging.getLogger("managr")


@kronos.register("0 * * * *")
def queue_account_sl_syncs(auth_account=None):
    if auth_account:
        sync_helper(auth_account)
    else:
        sl_accounts = SalesloftAuthAccount.objects.all()
        for account in sl_accounts:
            sync_helper(account.id)
            logger.info("Started salesloft sync for {account.organization}")
            continue
    return


def sync_helper(auth_id):
    sync_steps = [emit_sync_slaccounts, emit_sync_people, emit_sync_cadences]
    sl_account = SalesloftAuthAccount.objects.get(id=auth_id)
    v_name = uuid.uuid4()
    for step in sync_steps:
        attempts = 1
        sync_step = step(str(sl_account.id), f"{step.__name__}_{v_name}")
        while True:
            if attempts >= 5:
                break
            try:
                task = CompletedTask.objects.filter(verbose_name=f"{step.__name__}_{v_name}")
                if task:
                    break
            except Exception as e:
                attempts += 1
                continue
    return
