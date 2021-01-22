import logging
import json
from datetime import datetime
from background_task import background

from managr.core.models import User
from managr.organization.serializers import AccountSerializer, StageSerializer
from managr.opportunity.serializers import OpportunitySerializer

from ..models import SFSyncOperation
from ..adapter.models import AccountAdapter, StageAdapter, OpportunityAdapter

from .. import constants as sf_consts


def emit_sf_sync(user_id, sync_id, resource, offset):
    user_id = str(user_id)
    sync_id = str(sync_id)
    if resource == sf_consts.RESOURCE_SYNC_ACCOUNT:
        return _process_account_sync(user_id, sync_id, offset)
    elif resource == sf_consts.RESOURCE_SYNC_STAGE:
        return _process_stage_sync(user_id, sync_id, offset)
    elif resource == sf_consts.RESOURCE_SYNC_OPPORTUNITY:
        return _process_opportunity_sync(user_id, sync_id, offset)


@background(schedule=0)
def _process_account_sync(user_id, sync_id, offset):
    user = User.objects.filter(id=user_id).select_related("salesforce_account").first()
    if not hasattr(user, "salesforce_account"):
        return
    sf = user.salesforce_account
    res = sf.list_accounts(offset)
    accts = map(
        lambda data: AccountAdapter.from_api(data, user.organization.id, []).as_dict,
        res["records"],
    )
    serializer = AccountSerializer(data=list(accts), many=True)
    serializer.is_valid(raise_exception=True)
    serializer.save()

    # remember to update failed or not
    return


# from managr.salesforce.background import _process_account_sync
# user = User.objects.get(email="pari@thinknimble.com")
# _process_account_sync(str(user.id),'test')


@background(schedule=0)
def _process_stage_sync(user_id, sync_id, offset):
    user = User.objects.filter(id=user_id).select_related("salesforce_account").first()
    if not hasattr(user, "salesforce_account"):
        return
    sf = user.salesforce_account
    res = sf.list_stages(offset)
    stages = map(
        lambda data: StageAdapter.from_api(data, user.organization.id, []).as_dict, res["records"],
    )
    serializer = StageSerializer(data=list(stages), many=True)
    serializer.is_valid(raise_exception=True)
    serializer.save()

    return


@background(schedule=0)
def _process_opportunity_sync(user_id, sync_id, offset):
    user = User.objects.filter(id=user_id).select_related("salesforce_account").first()
    if not hasattr(user, "salesforce_account"):
        return
    sf = user.salesforce_account
    res = sf.list_opportunities(offset)
    opps = map(lambda data: OpportunityAdapter.from_api(data, user.id, []).as_dict, res["records"],)
    for opp in list(opps):
        serializer = OpportunitySerializer(data=opp)
        serializer.is_valid(raise_exception=True)
        serializer.save()
    return
