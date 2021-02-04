import logging
import json
from datetime import datetime
from background_task import background

from django.utils import timezone

from managr.api.decorators import log_all_exceptions

from managr.core.models import User
from managr.organization.models import Account, Stage
from managr.organization.serializers import AccountSerializer, StageSerializer
from managr.opportunity.models import Opportunity
from managr.opportunity.serializers import OpportunitySerializer

from ..models import SFSyncOperation
from ..adapter.models import AccountAdapter, StageAdapter, OpportunityAdapter, ActivityAdapter
from ..adapter.exceptions import TokenExpired

from .. import constants as sf_consts

logger = logging.getLogger("managr")


def emit_sf_sync(user_id, sync_id, resource, offset):
    user_id = str(user_id)
    sync_id = str(sync_id)

    if resource == sf_consts.RESOURCE_SYNC_ACCOUNT:
        return _process_account_sync(user_id, sync_id, offset, priority=3)
    elif resource == sf_consts.RESOURCE_SYNC_STAGE:
        return _process_stage_sync(user_id, sync_id, offset, priority=3)
    elif resource == sf_consts.RESOURCE_SYNC_OPPORTUNITY:
        return _process_opportunity_sync(user_id, sync_id, offset)


def emit_gen_next_sync(user_id, ops_list, schedule_time=timezone.now()):
    schedule = datetime.strptime(schedule_time, "%Y-%m-%dT%H:%M%Z")
    return _process_gen_next_sync(user_id, ops_list, schedule=schedule)


def emit_sf_add_call_to_sf(user_id, data):
    return _process_add_call_to_sf(user_id, data)


def emit_sf_update_opportunity(user_id, meeting_review_id):

    return _process_update_opportunity(user_id, meeting_review_id)


def emit_add_c_role_to_opp(user_id, opp_id, sf_contact_id):
    return _process_add_c_role_to_opp(user_id, opp_id, sf_contact_id)


@background(schedule=0)
@log_all_exceptions
def _process_add_call_to_sf(user_id, data, attempts=1):
    user = User.objects.filter(id=user_id).first()
    if not user:
        return logger.exception(f"User not found unable to log call {user_id}")
    if not hasattr(user, "salesforce_account"):
        return logger.exception("User does not have a salesforce account cannot push to sf")

    sf = user.salesforce_account
    try:
        return ActivityAdapter.save_zoom_meeting_to_salesforce(
            data, sf.access_token, sf.instance_url
        )
    except TokenExpired:
        if attempts >= 5:
            return logger.exception(
                f"Failed to refresh user token for Salesforce operation add contact as contact role to opportunity"
            )
        else:
            sf.regenerate_token()
            attempts += 1
            return _process_add_call_to_sf(user_id, data, attempts=attempts)


@background(schedule=0)
@log_all_exceptions
def _process_add_c_role_to_opp(user_id, opp_id, sf_contact_id, attempts=1):
    user = User.objects.filter(id=user_id).first()
    if not user:
        return logger.exception(
            f"User not found add contact role not initiated {user_id}, {str(opp_id)}, {sf_contact_id}"
        )
    opp = user.owned_opportunities.filter(id=opp_id).first()
    if not opp:
        return logger.exception(
            f"Opportunity not found add contact role not initiated {user_id}, {str(opp_id)}, {sf_contact_id}"
        )
    sf = user.salesforce_account
    try:
        opp.add_contact_role(sf.access_token, sf.instance_url, sf_contact_id)
    except TokenExpired:
        if attempts >= 5:
            return logger.exception(
                f"Failed to refresh user token for Salesforce operation add contact as contact role to opportunity"
            )
        else:
            sf.regenerate_token()
            attempts += 1
            return _process_add_c_role_to_opp(user_id, opp_id, sf_contact_id, attempts=attempts)


@background(schedule=0)
@log_all_exceptions
def _process_gen_next_sync(user_id, operations_list):
    user = User.objects.filter(id=user_id).first()
    if not user:
        return logger.exception(f"User not found sync operation not created {user_id}")

    return SFSyncOperation.objects.create(user=user, operations_list=operations_list).begin_tasks()


@background(schedule=0, queue=sf_consts.SALESFORCE_RESOURCE_SYNC_QUEUE)
def _process_account_sync(user_id, sync_id, offset, attempts=1):
    user = User.objects.filter(id=user_id).select_related("salesforce_account").first()
    if not hasattr(user, "salesforce_account"):
        return
    sf = user.salesforce_account
    try:
        res = sf.list_accounts(offset)
    except TokenExpired:
        if attempts >= 5:
            return logger.exception(
                f"Failed to sync ACCOUNT data for user {user_id} after {attempts} tries"
            )
        else:
            sf.regenerate_token()
            attempts += 1
            return _process_account_sync(user_id, sync_id, offset, attempts)
    accts = map(
        lambda data: AccountAdapter.from_api(data, user.organization.id, user.id, []).as_dict,
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
def _process_stage_sync(user_id, sync_id, offset, attempts=1):
    user = User.objects.filter(id=user_id).select_related("salesforce_account").first()
    if not hasattr(user, "salesforce_account"):
        return
    sf = user.salesforce_account
    try:
        res = sf.list_stages(offset)
    except TokenExpired:
        if attempts >= 5:
            return logger.exception(
                f"Failed to sync STAGE data for user {user_id} after {attempts} tries"
            )
        else:
            sf.regenerate_token()
            attempts += 1
            return _process_stage_sync(user_id, sync_id, offset, attempts)

    stages = map(
        lambda data: StageAdapter.from_api(data, user.organization.id, user.id, []).as_dict,
        res["records"],
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
@log_all_exceptions
def _process_opportunity_sync(user_id, sync_id, offset, attempts=1):
    user = User.objects.filter(id=user_id).select_related("salesforce_account").first()
    if not hasattr(user, "salesforce_account"):
        return
    sf = user.salesforce_account
    try:
        res = sf.list_opportunities(offset)
    except TokenExpired:
        if attempts >= 5:
            return logger.exception(
                f"Failed to sync OPPORTUNITY data for user {user_id} after {attempts} tries"
            )
        else:
            sf.regenerate_token()
            attempts += 1
            return _process_opportunity_sync(user_id, sync_id, offset, attempts)

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
            print(e)
            logger.exception(
                f"failed to import {opp['title']} with integration id of {opp['integration_id']} from {opp['integration_source']} for user {str(user.id)} {e}"
            )
            pass
    return


@background(schedule=0, queue=sf_consts.SALESFORCE_RESOURCE_SYNC_QUEUE)
def _process_update_opportunity(user_id, meeting_review_id, attempts=1):
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
            sf = user.salesforce_account
            try:
                meeting.opportunity.update_in_salesforce(formatted_data)
            except TokenExpired:
                if attempts >= 5:
                    return logger.exception(
                        f"Failed to sync STAGE data for user {user_id} after {attempts} tries"
                    )
                else:
                    sf.regenerate_token()
                    attempts += 1
                    return _process_update_opportunity(user_id, meeting_review_id, attempts)

            # push to sf
    return

