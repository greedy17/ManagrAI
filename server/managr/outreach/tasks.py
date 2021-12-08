import logging
import json
import re
import pytz
import uuid
import random
from datetime import datetime
from urllib.parse import urlencode

from django.conf import settings
from django.db.models import Q

from background_task import background
from rest_framework.exceptions import ValidationError

from managr.outreach.helpers.class_functions import process_prospect
from managr.api.decorators import log_all_exceptions
from .exceptions import TokenExpired, InvalidRequest
from .models import OutreachAccount, Sequence, Account, Prospect, ProspectAdapter
from managr.organization.models import Contact
from managr.outreach.helpers.class_functions import (
    sync_all_sequences,
    sync_all_prospects,
    sync_all_accounts,
)

logger = logging.getLogger("managr")


def emit_sync_outreach_sequences(outreach_account_id, verbose_name):
    return sync_outreach_sequences(outreach_account_id, verbose_name=verbose_name)


def emit_sync_outreach_accounts(outreach_account_id, verbose_name):
    return sync_outreach_accounts(outreach_account_id, verbose_name=verbose_name)


def emit_sync_outreach_prospects(outreach_account_id, verbose_name):
    return sync_outreach_prospects(outreach_account_id, verbose_name=verbose_name)


def emit_add_sequence_state(contact_id, sequence_id):
    return add_sequence_state(contact_id, sequence_id)


@background()
def sync_outreach_sequences(outreach_account_id):
    outreach_account = OutreachAccount.objects.get(id=outreach_account_id)
    while True:
        attempts = 1
        try:
            success = 0
            failed = 0
            res = outreach_account.helper_class.get_sequences()
            sync_count = sync_all_sequences(res["data"])
            success += sync_count["success"]
            failed += sync_count["failed"]
            break
        except TokenExpired:
            if attempts >= 5:
                return logger.exception(
                    f"Failed to sync outreach sequences for account {outreach_account.user.email}"
                )
            else:
                outreach_account.regenerate_token()
                attempts += 1
    return logger.info(
        f"Synced {success}/{success+failed} outreach sequences for {outreach_account.user.email}"
    )


@background(schedule=0)
@log_all_exceptions
def sync_outreach_accounts(outreach_account_id):
    outreach_account = OutreachAccount.objects.get(id=outreach_account_id)
    while True:
        attempts = 1
        try:
            success = 0
            failed = 0
            res = outreach_account.helper_class.get_accounts()
            sync_count = sync_all_accounts(res["data"])
            success += sync_count["success"]
            failed += sync_count["failed"]
            break
        except TokenExpired:
            if attempts >= 5:
                return logger.exception(
                    f"Failed to sync outreach sequences for account {outreach_account.user.email}"
                )
            else:
                outreach_account.regenerate_token()
                attempts += 1
    return logger.info(
        f"Synced {success}/{success+failed} accounts for {outreach_account.user.email}"
    )


@background(schedule=0)
@log_all_exceptions
def sync_outreach_prospects(outreach_account_id):
    outreach_account = OutreachAccount.objects.get(id=outreach_account_id)
    while True:
        attempts = 1
        try:
            success = 0
            failed = 0
            res = outreach_account.helper_class.get_prospects()
            sync_count = sync_all_prospects(res["data"])
            success += sync_count["success"]
            failed += sync_count["failed"]
            break
        except TokenExpired:
            if attempts >= 5:
                return logger.exception(
                    f"Failed to sync outreach prospects for account {outreach_account.user.email}"
                )
            else:
                outreach_account.regenerate_token()
                attempts += 1
    return logger.info(f"Synced {success}/{success+failed} prospects for {outreach_account}")


def add_sequence_state(contact_id, sequence_id):
    sequence = Sequence.objects.get(id=sequence_id)
    outreach_account = OutreachAccount.objects.get(id=sequence.owner.id)
    contact = Contact.objects.get(id=contact_id)
    prospect = Prospect.objects.filter(email=contact.email).first()
    prospect_id = prospect.prospect_id if prospect else None
    created = False
    while True:
        attempts = 1
        try:
            if not prospect:
                data = {
                    "data": {
                        "type": "prospect",
                        "attributes": {
                            "firstName": contact.secondary_data["FirstName"],
                            "lastName": contact.secondary_data["LastName"],
                            "emails": [contact.email],
                        },
                        "relationships": {
                            "owner": {"data": {"type": "user", "id": outreach_account.outreach_id}}
                        },
                    }
                }
                print(data)
                create_res = ProspectAdapter.create_in_outreach(outreach_account.access_token, data)
                process_prospect(create_res["data"])
                prospect_id = create_res["data"]["id"]
                created = True

            res = sequence.helper_class.add_sequence_state(
                outreach_account.access_token, prospect_id, outreach_account.mailbox,
            )
            break
        except TokenExpired:
            if attempts >= 5:
                return logger.exception(
                    f"Failed to add Person with id {prospect_id} to Sequence {sequence.name}, could not regenerate token"
                )
            else:
                outreach_account.regenerate_token()
                attempts += 1
        except InvalidRequest:
            return {"status": "Failed"}
        except ValidationError as e:
            logger.exception(f"Error adding sequence: {e}")
            return {"status": "Failed"}
    logger.info(f"Person with id {prospect_id} added to sequence {sequence.id}")
    if created:
        return {"status": "Created"}
    return {"status": "Success"}
