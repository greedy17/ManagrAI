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
from ..exceptions import TokenExpired, InvalidRequest
from ..models import OutreachAccount, Sequence, Account, Prospect, ProspectAdapter
from ..helpers.class_functions import (
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
        except Exception as e:
            if attempts >= 5:
                return logger.exception(
                    f"Failed to sync outreach sequences for account {outreach_account.user.email}, error: {e}"
                )
            else:
                attempts += 1
    return logger.info(
        f"Synced {success}/{success+failed} outreach sequences for {outreach_account.user.email}"
    )


@background()
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
                    f"Failed to sync outreach accounts for account {outreach_account.user.email}"
                )
            else:
                outreach_account.regenerate_token()
                attempts += 1
        except Exception as e:
            if attempts >= 5:
                return logger.exception(
                    f"Failed to sync outreach accounts for account {outreach_account.user.email}, error: {e}"
                )
            else:
                attempts += 1
    return logger.info(
        f"Synced {success}/{success+failed} accounts for {outreach_account.user.email}"
    )


@background()
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
        except Exception as e:
            if attempts >= 5:
                return logger.exception(
                    f"Failed to sync outreach prospects for account {outreach_account.user.email}, error: {e}"
                )
            else:
                attempts += 1
    return logger.info(f"Synced {success}/{success+failed} prospects for {outreach_account}")


# def add_cadence_membership(person_id, cadence_id):
#     cadence = Sequence.objects.get(id=cadence_id)
#     auth_account = OutreachAccount.objects.get(id=cadence.owner.auth_account.id)
#     contact = Contact.objects.get(id=person_id)
#     person = Prospect.objects.filter(email=contact.email).first()
#     slaccount = Account.objects.get(name=contact.account.name)
#     owner = slaccount.owner.salesloft_id
#     people_id = person.people_id if person else None
#     created = False
#     while True:
#         attempts = 1
#         try:
#             if not person:
#                 data = {
#                     "first_name": contact.secondary_data["FirstName"],
#                     "last_name": contact.secondary_data["LastName"],
#                     "email_address": contact.email,
#                     "owner_id": owner,
#                     "account_id": slaccount.account_id,
#                 }
#                 create_res = ProspectAdapter.create_in_salesloft(auth_account.access_token, data)
#                 process_prospect(create_res["data"])
#                 people_id = create_res["data"]["id"]
#                 created = True

#             res = cadence.helper_class.add_membership(people_id, auth_account.access_token)
#             break
#         except TokenExpired:
#             if attempts >= 5:
#                 return logger.exception(
#                     f"Failed to add Person with id {people_id} to Sequence {cadence.name}, could not regenerate token"
#                 )
#             else:
#                 auth_account.regenerate_token()
#                 attempts += 1
#         except InvalidRequest:
#             return {"status": "Failed"}
#         except ValidationError as e:
#             logger.exception(f"Error adding cadence: {e}")
#             return {"status": "Failed"}
#     logger.info(f"Person with id {people_id} added to cadence {cadence.id}")
#     if created:
#         return {"status": "Created"}
#     return {"status": "Success"}
