import logging
import kronos
import datetime

from django.utils import timezone

from managr.salesforce import constants as sf_consts
from managr.salesforce.background import emit_gen_next_sync, emit_gen_next_object_field_sync
from managr.salesforce.models import SFObjectFieldSync, SFSyncOperation, SalesforceAuthAccount


def queue_users_sf_resource():
    """ runs every five mins and initiates user sf syncs if their prev workflow is done """
    sf_accounts = SalesforceAuthAccount.objects.filter(user__is_active=True)
    for account in sf_accounts:
        # get latest workflow
        latest_flow = SFSyncOperation.objects.filter(user=account.user).latest("datetime_created")
        if latest_flow and latest_flow.progress == 100:
            queue_users_sf_resource(latest_flow.user.id)
            continue
        # if latest workflow is at 100 emit sf resource sync
    return


def queue_users_sf_fields():
    """ runs every 12 hours and initiates user sf syncs if their prev workflow is done """
    sf_accounts = SalesforceAuthAccount.objects.filter(user__is_active=True)
    for account in sf_accounts:
        # get latest workflow
        latest_flow = SFObjectFieldSync.objects.filter(user=account.user).latest("datetime_created")
        if latest_flow and latest_flow.progress == 100:
            queue_users_sf_resource(latest_flow.user.id)
            continue
        # if latest workflow is at 100 emit sf resource sync
    return


def init_sf_resource_sync(user_id):
    operations = [
        sf_consts.RESOURCE_SYNC_ACCOUNT,
        sf_consts.RESOURCE_SYNC_CONTACT,
        sf_consts.RESOURCE_SYNC_OPPORTUNITY,
        sf_consts.RESOURCE_SYNC_LEAD,
    ]
    scheduled_time = timezone.now()
    formatted_time = scheduled_time.strftime("%Y-%m-%dT%H:%M%Z")
    return emit_gen_next_sync(str(user_id), operations, formatted_time)


def init_sf_field_sync(user):
    operations = [
        f"{sf_consts.SALESFORCE_OBJECT_FIELDS}.{sf_consts.RESOURCE_SYNC_ACCOUNT}",
        f"{sf_consts.SALESFORCE_PICKLIST_VALUES}.{sf_consts.RESOURCE_SYNC_ACCOUNT}",
        f"{sf_consts.SALESFORCE_OBJECT_FIELDS}.{sf_consts.RESOURCE_SYNC_CONTACT}",
        f"{sf_consts.SALESFORCE_PICKLIST_VALUES}.{sf_consts.RESOURCE_SYNC_CONTACT}",
        f"{sf_consts.SALESFORCE_OBJECT_FIELDS}.{sf_consts.RESOURCE_SYNC_LEAD}",
        f"{sf_consts.SALESFORCE_PICKLIST_VALUES}.{sf_consts.RESOURCE_SYNC_LEAD}",
        f"{sf_consts.SALESFORCE_OBJECT_FIELDS}.{sf_consts.RESOURCE_SYNC_OPPORTUNITY}",
        f"{sf_consts.SALESFORCE_PICKLIST_VALUES}.{sf_consts.RESOURCE_SYNC_OPPORTUNITY}",
    ]
    if user.instance.user.is_admin:
        # we only need validations to show the user who is creating the forms

        operations.extend(
            [
                f"{sf_consts.SALESFORCE_VALIDATIONS}.{sf_consts.RESOURCE_SYNC_ACCOUNT}",
                f"{sf_consts.SALESFORCE_VALIDATIONS}.{sf_consts.RESOURCE_SYNC_CONTACT}",
                f"{sf_consts.SALESFORCE_VALIDATIONS}.{sf_consts.RESOURCE_SYNC_OPPORTUNITY}",
                f"{sf_consts.SALESFORCE_VALIDATIONS}.{sf_consts.RESOURCE_SYNC_LEAD}",
            ]
        )

    scheduled_time = timezone.now()
    formatted_time = scheduled_time.strftime("%Y-%m-%dT%H:%M%Z")
    emit_gen_next_object_field_sync(str(user.id), operations, formatted_time)
    return

