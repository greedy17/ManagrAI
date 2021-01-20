import logging
import json
from datetime import datetime
from background_task import background

from managr.core.models import User
from ..models import SFSyncOperation
from ..adapter.models import AccountAdapter

from .. import constants as sf_consts


def emit_sf_sync(user_id, resource, sync_id):
    user_id = str(user_id)
    sync_id = str(sync_id)
    if resource == sf_consts.RESOURCE_SYNC_ACCOUNT:
        return _process_account_sync(user_id, sync_id)
    elif resource == sf_consts.RESOURCE_SYNC_STAGE:
        return _process_stage_sync(user_id, sync_id)
    elif resource == sf_consts.RESOURCE_SYNC_OPPORTUNITY:
        return _process_opportunity_sync(user_id, sync_id)


# @background(schedule=0)
def _process_account_sync(user_id, sync_id):

    user = User.objects.filter(id=user_id).select_related("salesforce_account").first()

    if not hasattr(user, "salesforce_account"):
        return
    sf = user.salesforce_account

    res = sf.adapter_class.list_accounts()

    accts = map(
        lambda data: AccountAdapter.from_api(data, user.organization.id, []), res["records"],
    )
    for acct in list(accts):
        print(acct.as_dict)
    # remember to update failed or not
    return res


# from managr.salesforce.background import _process_account_sync
# user = User.objects.get(email="pari@thinknimble.com")
# _process_account_sync(str(user.id),'test')


@background(schedule=0)
def _process_stage_sync(user_id, sync_id):
    user = User.objects.filter(id=user_id).select_related("salesforce_account")
    if not hasattr(user, "salesforce_account"):
        return
    sf = user.salesforce_account
    res = sf.list_stages()
    return res


@background(schedule=0)
def _process_opportunity_sync():
    return

