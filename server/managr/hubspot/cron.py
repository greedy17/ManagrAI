import logging
import kronos
from django.utils import timezone


from managr.hubspot.models import HubspotAuthAccount, HSObjectFieldsOperation, HSResourceSync
from managr.hubspot.tasks import emit_gen_next_hubspot_field_sync, emit_gen_next_hubspot_sync

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


@kronos.register("*/10  * * * *")
def queue_users_hs_resource(force_all=False):
    """
    runs every 12 hours and initiates user sf syncs if their prev workflow is done
    force_all will attempt all failed and not faild
    """
    hs_accounts = HubspotAuthAccount.objects.filter(user__is_active=True)
    for account in hs_accounts:
        # if not force_all:
        #     flows = HSResourceSync.objects.filter(user=account.user)
        #     has_completed_object_field_flow = check_last_object_sync(
        #         SFObjectFieldsOperation.objects.filter(user=account.user)
        #     )
        #     latest_flow = flows.latest("datetime_created") if flows.count() else None
        #     if not flows.count() and has_completed_object_field_flow:
        #         init_sf_resource_sync(account.user)

        #     else:
        #         if latest_flow and latest_flow.progress == 100:
        #             logger.info(
        #                 f"SF_LATEST_RESOURCE_SYNC --- Operation id {str(latest_flow.id)}, email {latest_flow.user.email}"
        #             )
        #             init_sf_resource_sync(latest_flow.user)
        #             continue
        #         elif latest_flow and latest_flow.progress != 100:
        #             # check to see if the tasks were completed but not recorded
        #             latest_flow.reconcile()
        #             if latest_flow.progress == 100:
        #                 init_sf_resource_sync(account.user)
        #                 continue

        #             else:
        #                 if settings.SLACK_ERROR_WEBHOOK:
        #                     try:
        #                         slack_requests.generic_request(
        #                             slack_const.SLACK_ERROR_WEBHOOK,
        #                             {
        #                                 "text": f"Unable to force complete resource workflow ({str(latest_flow.id)}) for user {account.user.email} with id {account.user.id} progress is {latest_flow.progress}"
        #                             },
        #                         )
        #                     except Exception as fail_safe_error:
        #                         logger.exception(
        #                             f"Failed to send slack error to error channel {fail_safe_error}"
        #                         )
        #                         continue

        # else:
        #     # only init if the last field sync is at 100%
        init_hubspot_resource_sync(account.user)
        continue

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


def init_hubspot_resource_sync(user):
    if not hasattr(user, "hubspot_account"):
        return
    # operations = [*user.hubspot_account.resource_sync_opts]
    operations = [
        *user.hubspot_account.field_sync_opts,
    ]
    scheduled_time = timezone.now()
    formatted_time = scheduled_time.strftime("%Y-%m-%dT%H:%M%Z")
    return emit_gen_next_hubspot_sync(str(user.id), operations, formatted_time)
