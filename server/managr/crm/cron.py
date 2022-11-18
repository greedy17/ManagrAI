import logging
import kronos
import math
from django.utils import timezone

from managr.core.models import User
from managr.crm.models import CrmObjectFieldsOperation, CrmResourceSync
from managr.crm.background import _process_stale_data_for_delete

logger = logging.getLogger("managr")


@kronos.register("0 */24 * * *")
def queue_stale_crm_data_for_delete(cutoff=1440):
    """
    This should queue stale data for delete, it should only do this for users who are active and who have an sf account
    In the future we will be having a flag for users who's salesforce token is soft revoked aka, they would like to pause the sync
    or for whom we are having issues and they would like to refresh their token, for these users we should not be deleting data
    """
    resource_items = []
    limit = 0
    pages = 1
    # get users who are active and have a salesforce_accounta
    qs = User.objects.filter(is_active=True, crm__isnull=False).distinct()
    # count them to paginate the response
    user_count = qs.count()
    logger.info(f"STARTING STALE DATE ClEAR FOR {user_count} users")
    # set limit of 100 or less
    limit = max(100, user_count)
    # divide into pages
    pages = math.ceil(user_count / limit)
    # cutoff of 1 day
    cutoff = timezone.now() - timezone.timedelta(minutes=cutoff)

    for i in range(0, pages):
        users = qs[i * limit : i + 1 * limit].select_related("salesforce_account")
        for user in users:
            # only run this for users with a successful latest flow

            flows = CrmResourceSync.objects.filter(user=user)
            latest_flow = not flows.latest("datetime_created").in_progress if flows else False
            field_flows = CrmObjectFieldsOperation.objects.filter(user=user)
            latest_field_flow = (
                not field_flows.latest("datetime_created").in_progress if field_flows else False
            )

            if not latest_flow and not latest_field_flow:
                logger.info(
                    f"skipping clear data for user {user.email} with id {str(user.id)} because the latest field and resource flow were not successful"
                )
                continue

            elif not latest_flow and latest_field_flow:

                logger.info(
                    f"skipping clear resource data (fields only) for user {user.email} with id {str(user.id)} because the latest resource flow was not successful"
                )
                resource_items = [
                    "objectfield",
                    "objectvalidation",
                    "objectpicklist",
                ]
            elif latest_flow and not latest_field_flow:
                logger.info(
                    f"skipping clear field data (resources only) for user {user.email} with id {str(user.id)} because the latest resource flow was not successful"
                )
                resource_items.extend(["base_opportunity", "base_account", "base_contact"])
            else:
                resource_items.extend(
                    [
                        "objectfield",
                        "objectvalidation",
                        "objectpicklist",
                        "base_opportunity",
                        "base_account",
                        "base_contact",
                    ]
                )

            for r in resource_items:
                try:
                    qs = getattr(user, f"imported_{r}").filter(last_edited__lt=cutoff)
                    resource_count = qs.count()

                    if resource_count and resource_count <= 500:
                        # emit current batch to delete queue and start new
                        # TODO - Eventually remove the .now to make async
                        _process_stale_data_for_delete.now(
                            [
                                {
                                    "user_id": str(user.id),
                                    "resource": {
                                        r: list(str(id) for id in qs.values_list("id", flat=True))
                                    },
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
                            _process_stale_data_for_delete.now(
                                [
                                    {
                                        "user_id": str(user.id),
                                        "resource": {
                                            r: list(
                                                str(id) for id in items.values_list("id", flat=True)
                                            )
                                        },
                                    }
                                ],
                            )

                except AttributeError as e:
                    logger.info(f"{user.email} does not have {r} to delete {e}")
                    continue
