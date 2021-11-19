import logging
import kronos
import uuid

from background_task.models import CompletedTask

from managr.outreach.background import (
    emit_sync_accounts,
    emit_sync_prospects,
    emit_sync_sequences,
)
from managr.outreach.models import OutreachAccount

logger = logging.getLogger("managr")


@kronos.register("0 * * * *")
def queue_outreach_sync(account_id=None):
    if account_id:
        sync_helper(account_id)
    else:
        outreach_accounts = OutreachAccount.objects.all()
        for account in outreach_accounts:
            emit_sync_accounts(str(account.id))
            emit_sync_prospects(str(account.id))
            emit_sync_sequences(str(account.id))
            logger.info(f"Started outreach sync for {account.user.email}")
            continue
    return


def sync_helper(auth_id):
    sync_steps = [emit_sync_sequences, emit_sync_accounts, emit_sync_prospects]
    outreach_account = OutreachAccount.objects.get(id=auth_id)
    v_name = uuid.uuid4()
    for step in sync_steps:
        attempts = 1
        step(str(outreach_account.id))
        # while True:
        #     if attempts >= 20:
        #         break
        #     try:
        #         task = CompletedTask.objects.filter(verbose_name=f"{step.__name__}_{v_name}")
        #         if task:
        #             break
        #     except Exception:
        #         attempts += 1
        #         continue
    return
