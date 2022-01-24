import logging
import time
import uuid
import random

from background_task.models import CompletedTask
from django.conf import settings

from background_task import background

from managr.outreach.helpers.class_functions import process_prospect
from managr.api.decorators import log_all_exceptions
from ..exceptions import TokenExpired, InvalidRequest
from ..models import OutreachAccount, Sequence, Account, Prospect, ProspectAdapter
from ..helpers.class_functions import (
    sync_all_sequences,
    sync_all_prospects,
    sync_all_accounts,
)

logger = logging.getLogger("managr")


def emit_sync_outreach_sequences(outreach_account_id, verbose_name):
    return sync_outreach_sequences(outreach_account_id, verbose_name=verbose_name)


def emit_sync_outreach_accounts(outreach_account_id, verbose_name):
    return sync_outreach_accounts(outreach_account_id, verbose_name=verbose_name)


def emit_sync_outreach_prospects(outreach_account_id, verbose_name):
    return sync_outreach_prospects(outreach_account_id, verbose_name=verbose_name)


@background()
def sync_outreach_sequences(outreach_account_id):
    outreach_account = OutreachAccount.objects.get(id=outreach_account_id)
    while True:
        attempts = 1
        try:
            success = 0
            failed = 0
            res = outreach_account.helper_class.get_sequences()
            sync_count = sync_all_sequences(res["data"])
            success += sync_count["success"]
            failed += sync_count["failed"]
            break
        except TokenExpired:
            if attempts >= 5:
                return logger.exception(
                    f"Failed to sync outreach sequences for account {outreach_account.user.email}"
                )
            else:
                outreach_account.regenerate_token()
                attempts += 1
        except Exception as e:
            if attempts >= 5:
                return logger.exception(
                    f"Failed to sync outreach sequences for account {outreach_account.user.email}, error: {e}"
                )
            else:
                attempts += 1
    return logger.info(
        f"Synced {success}/{success+failed} outreach sequences for {outreach_account.user.email}"
    )


@background()
@log_all_exceptions
def sync_outreach_accounts(outreach_account_id):
    outreach_account = OutreachAccount.objects.get(id=outreach_account_id)
    while True:
        attempts = 1
        try:
            success = 0
            failed = 0
            res = outreach_account.helper_class.get_accounts()
            sync_count = sync_all_accounts(res["data"])
            success += sync_count["success"]
            failed += sync_count["failed"]
            break
        except TokenExpired:
            if attempts >= 5:
                return logger.exception(
                    f"Failed to sync outreach accounts for account {outreach_account.user.email}"
                )
            else:
                outreach_account.regenerate_token()
                attempts += 1
        except Exception as e:
            if attempts >= 5:
                return logger.exception(
                    f"Failed to sync outreach accounts for account {outreach_account.user.email}, error: {e}"
                )
            else:
                attempts += 1
    return logger.info(
        f"Synced {success}/{success+failed} accounts for {outreach_account.user.email}"
    )


@background()
@log_all_exceptions
def sync_outreach_prospects(outreach_account_id):
    outreach_account = OutreachAccount.objects.get(id=outreach_account_id)
    while True:
        attempts = 1
        try:
            success = 0
            failed = 0
            res = outreach_account.helper_class.get_prospects()
            sync_count = sync_all_prospects(res["data"])
            success += sync_count["success"]
            failed += sync_count["failed"]
            break
        except TokenExpired:
            if attempts >= 5:
                return logger.exception(
                    f"Failed to sync outreach prospects for account {outreach_account.user.email}"
                )
            else:
                outreach_account.regenerate_token()
                attempts += 1
        except Exception as e:
            if attempts >= 5:
                return logger.exception(
                    f"Failed to sync outreach prospects for account {outreach_account.user.email}, error: {e}"
                )
            else:
                attempts += 1
    return logger.info(f"Synced {success}/{success+failed} prospects for {outreach_account}")


@background()
def sync_helper(auth_id):
    sync_steps = [
        emit_sync_outreach_sequences,
        emit_sync_outreach_accounts,
        emit_sync_outreach_prospects,
    ]
    outreach_account = OutreachAccount.objects.get(id=auth_id)
    v_name = str(uuid.uuid4())
    has_error = False
    current_task = None
    for step in sync_steps:
        if has_error:
            logger.exception(f"OUTREACH SYNC ERROR ON TASK: {current_task}")
            break
        logger.info(f"Scheduling task {step} for {outreach_account}")
        attempts = 1
        sync_step = step(str(outreach_account.id), f"{step.__name__}_{v_name}")
        current_task = sync_step.verbose_name
        while True:
            if attempts >= 10:
                has_error = True
                break
            try:
                task = (
                    CompletedTask.objects.filter(task_hash=sync_step.task_hash)
                    .order_by("-run_at")
                    .first()
                )
                if task and task.verbose_name == f"{step.__name__}_{v_name}":
                    logger.info(f"COMPLETED OUTREACH SYNC TASK:{task}")
                    break
                else:
                    attempts += 1
                    sleep = 1 * 2 ** attempts + random.uniform(0, 1)
                    time.sleep(sleep)
            except Exception as e:
                logger.exception(f"OUTREACH SYNC HELPER ERROR: {e}")
                attempts += 1
    return
