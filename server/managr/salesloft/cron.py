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


from rest_framework.response import Response

from managr.salesloft import constants as sl_consts
from managr.salesloft.background import sync_helper
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
            logger.info("Started salesloft sync for {account.organization}")
            sync_helper(account.id)
            continue
    return

