import logging
import kronos
from django.utils import timezone


from managr.hubspot.models import HubspotAuthAccount, HSObjectFieldsOperation
from managr.hubspot.tasks import emit_gen_next_hubspot_field_sync

logger = logging.getLogger("managr")


@kronos.register("0 */12 * * *")
def queue_users_hs_fields(force_all=False):
    """
    runs every 12 hours and initiates user sf syncs if their prev workflow is done
    force_all will attempt all failed and not faild
    """
    hs_accounts = HubspotAuthAccount.objects.filter(user__is_active=True)
    for account in hs_accounts:
        # get latest workflow
        # if not force_all:
        # flows = HSObjectFieldsOperation.objects.filter(user=account.user)
        # should_run = check_last_object_sync(flows)
        # if should_run:
        init_hs_field_sync(account.user)
        #         continue
        #     else:
        #         continue
        # else:
        #     init_hs_field_sync(account.user)
        #     continue
        # if latest workflow is at 100 emit sf resource sync
    return


def init_hs_field_sync(user):
    logger.info(f"Initiating HS Object Field Sync for User {str(user.id)} with email {user.email}")
    if not hasattr(user, "hubspot_account"):
        return
    operations = [
        *user.hubspot_account.field_sync_opts,
    ]
    scheduled_time = timezone.now()
    formatted_time = scheduled_time.strftime("%Y-%m-%dT%H:%M%Z")
    emit_gen_next_hubspot_field_sync(str(user.id), operations, formatted_time)
    return
