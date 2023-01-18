import logging
import kronos
from managr.outreach.models import OutreachAccount
from managr.outreach.background import sync_helper

logger = logging.getLogger("managr")


@kronos.register("0 * * * *")
def queue_outreach_sync(account_id=None):
    if account_id:
        logger.info(f"Started outreach sync for {account_id}")
        sync_helper(account_id)
    else:
        outreach_accounts = OutreachAccount.objects.all()
        for account in outreach_accounts:
            logger.info(f"Started outreach sync for {account.user.email}")
            sync_helper(account.id)
            continue
    return
