import logging
import json
from datetime import datetime
from background_task import background

from managr.core.models import User
from managr.organization.models import Account, Stage
from managr.organization.serializers import AccountSerializer, StageSerializer
from managr.opportunity.models import Opportunity
from managr.opportunity.serializers import OpportunitySerializer

from ..models import SFSyncOperation
from ..adapter.models import AccountAdapter, StageAdapter, OpportunityAdapter

from .. import constants as sf_consts

logging.getLogger("managr")


def emit_sf_sync(user_id, sync_id, resource, offset):
    user_id = str(user_id)
    sync_id = str(sync_id)
    if resource == sf_consts.RESOURCE_SYNC_ACCOUNT:
        return _process_account_sync(user_id, sync_id, offset, priority=3)
    elif resource == sf_consts.RESOURCE_SYNC_STAGE:
        return _process_stage_sync(user_id, sync_id, offset, priority=3)
    elif resource == sf_consts.RESOURCE_SYNC_OPPORTUNITY:
        return _process_opportunity_sync(user_id, sync_id, offset)


def emit_sf_update_opportunity(user_id, meeting_review_id):
    user_id = str(user_id)
    meeting_review_id = str(meeting_review_id)
    _process_update_opportunity(user_id, meeting_review_id)


@background(schedule=0, queue=sf_consts.SALESFORCE_RESOURCE_SYNC_QUEUE)
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

    for acct in list(accts):
        existing = Account.objects.filter(integration_id=acct["integration_id"]).first()
        if existing:
            serializer = AccountSerializer(data=acct, instance=existing)
        else:
            serializer = AccountSerializer(data=acct)
        # check if already exists and update

        serializer.is_valid(raise_exception=True)
        serializer.save()
    return


@background(schedule=0, queue=sf_consts.SALESFORCE_RESOURCE_SYNC_QUEUE)
def _process_stage_sync(user_id, sync_id, offset):
    user = User.objects.filter(id=user_id).select_related("salesforce_account").first()
    if not hasattr(user, "salesforce_account"):
        return
    sf = user.salesforce_account
    res = sf.list_stages(offset)
    stages = map(
        lambda data: StageAdapter.from_api(data, user.organization.id, []).as_dict, res["records"],
    )
    for stage in list(stages):
        existing = Stage.objects.filter(integration_id=stage["integration_id"]).first()
        if existing:
            serializer = StageSerializer(data=stage, instance=existing)
        else:
            serializer = StageSerializer(data=stage)
        # check if already exists and update

        serializer.is_valid(raise_exception=True)
        serializer.save()

    return


@background(schedule=0, queue=sf_consts.SALESFORCE_RESOURCE_SYNC_QUEUE)
def _process_opportunity_sync(user_id, sync_id, offset):
    user = User.objects.filter(id=user_id).select_related("salesforce_account").first()
    if not hasattr(user, "salesforce_account"):
        return
    sf = user.salesforce_account
    res = sf.list_opportunities(offset)
    opps = map(lambda data: OpportunityAdapter.from_api(data, user.id, []).as_dict, res["records"],)

    for opp in list(opps):
        existing = Opportunity.objects.filter(integration_id=opp["integration_id"]).first()
        if existing:
            serializer = OpportunitySerializer(data=opp, instance=existing)
        else:
            serializer = OpportunitySerializer(data=opp)
        # check if already exists and update

        try:
            serializer.is_valid(raise_exception=True)
            serializer.save()
        except Exception as e:
            logger.exception(
                f"failed to import {opp['title']} with integration id of {opp['integration_id']} from {opp['integration_source']} for user {str(user.id)} {e}"
            )
            pass
    return


@background(schedule=0, queue=sf_consts.SALESFORCE_RESOURCE_SYNC_QUEUE)
def _process_update_opportunity(user_id, meeting_review_id):
    user = (
        User.objects.filter(id=user_id)
        .select_related("zoom_account")
        .select_related("salesforce_account")
        .first()
    )
    if user and user.has_zoom_integration and user.has_slack_integration:
        meeting = user.zoom_account.meetings.filter(meeting_review__id=meeting_review_id).first()
        meeting_review = meeting.meeting_review
        if meeting_review:
            formatted_data = meeting_review.as_sf_update
            meeting.opportunity.update_in_salesforce(formatted_data)

            # push to sf
    return

