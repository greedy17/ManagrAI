import logging
import kronos
import math
from django.utils import timezone
from django.db.models import Q

from managr.salesloft import constants as sl_consts
from managr.salesloft.background import sync_helper, _process_stale_salesloft_data_for_delete
from managr.salesloft.models import SalesloftAuthAccount
from managr.core.models import User
from managr.salesloft.routes import routes as sl_routes

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


@kronos.register("0 */24 * * *")
def queue_stale_salesloft_data_for_delete(cutoff=1440):
    resource_items = []
    limit = 0
    pages = 1
    # get users who are active and have a salesforce_account
    qs = User.objects.filter(is_active=True, salesloft_account__isnull=False).distinct()
    # count them to paginate the response
    user_count = qs.count()
    # set limit of 100 or less
    limit = max(100, user_count)
    # divide into pages
    pages = math.ceil(user_count / limit)
    # cutoff of 1 day
    cutoff = timezone.now() - timezone.timedelta(minutes=cutoff)

    for i in range(0, pages):
        users = qs[i * limit : i + 1 * limit].select_related("salesloft_account")
        for user in users:
            resource_items = [
                sl_consts.SALESLOFT_RESOURCE_PEOPLE,
                sl_consts.SALESLOFT_RESOURCE_SLACCOUNT,
            ]
            for r in resource_items:
                try:
                    qs = sl_routes[r]["model"].objects.filter(
                        Q(owner=user.salesloft_account, last_edited__lt=cutoff)
                    )
                    resource_count = qs.count()

                    if resource_count and resource_count <= 500:
                        _process_stale_salesloft_data_for_delete.now(
                            [
                                {
                                    "user_id": str(user.id),
                                    "resource": {r: qs.values_list("id", flat=True)},
                                }
                            ],
                        )
                    elif resource_count and resource_count > 500:
                        # create make into batches of 500 and send
                        resource_pages = 1
                        resource_pages = math.ceil(resource_count / 500)
                        for i in range(0, resource_pages):
                            items = qs[i * 500 : i + 1 * 500].values_list("id", flat=True)
                            # TODO - Eventually remove the .now to make async
                            _process_stale_salesloft_data_for_delete.now(
                                [
                                    {
                                        "user_id": str(user.id),
                                        "resource": {r: items.values_list("id", flat=True)},
                                    }
                                ],
                            )

                except AttributeError as e:
                    logger.info(f"{user.email} does not have {r} to delete {e}")
                    continue
