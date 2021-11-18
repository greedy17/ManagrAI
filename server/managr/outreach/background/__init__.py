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

from ..exceptions import TokenExpired, InvalidRequest
from ..models import OutreachAccount
from ..helpers.class_functions import sync_all_sequences
from managr.organization.models import Contact

logger = logging.getLogger("managr")


def emit_sync_user_accounts(auth_account_id, verbose_name):
    return sync_accounts(auth_account_id, verbose_name=verbose_name)


def emit_sync_sequences(auth_account_id):
    return sync_sequences(auth_account_id)


def emit_sync_accounts(auth_account_id, verbose_name):
    return sync_slaccounts(auth_account_id, verbose_name=verbose_name)


def emit_sync_prospects(auth_account_id, verbose_name):
    return sync_people(auth_account_id, verbose_name=verbose_name)


@background()
def sync_accounts(auth_account_id):
    auth_account = SalesloftAuthAccount.objects.get(id=auth_account_id)
    while True:
        attempts = 1
        try:
            success = 0
            failed = 0
            res = auth_account.helper_class.get_users()
            initial_page = sync_current_account_page(res["data"], auth_account.id)
            success += initial_page["success"]
            failed += initial_page["failed"]
            if res["metadata"]["paging"]["total_pages"] > 1:
                count = 2
                while count <= res["metadata"]["paging"]["total_pages"] and count <= 20:
                    page_res = auth_account.helper_class.get_users(count)
                    curr_page = sync_current_account_page(page_res["data"], auth_account.id)
                    success += curr_page["success"]
                    failed += curr_page["failed"]
                    count += 1
            break
        except TokenExpired:
            if attempts >= 5:
                return logger.exception(
                    f"Failed to sync salesloft users for account {auth_account.id}"
                )
            else:
                auth_account.regenerate_token()
                attempts += 1
    return logger.info(f"Synced {success}/{success+failed} users for {auth_account}")


# @background()
def sync_sequences(outreach_account_id):
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


@background()
def sync_slaccounts(auth_account_id):
    auth_account = SalesloftAuthAccount.objects.get(id=auth_account_id)
    while True:
        attempts = 1
        try:
            success = 0
            failed = 0
            res = auth_account.helper_class.get_accounts()
            initial_page = sync_current_slaccount_page(res["data"])
            success += initial_page["success"]
            failed += initial_page["failed"]
            if res["metadata"]["paging"]["total_pages"] > 1:
                count = 2
                while count <= res["metadata"]["paging"]["total_pages"] and count <= 20:
                    page_res = auth_account.helper_class.get_accounts(count)
                    curr_page = sync_current_slaccount_page(page_res["data"])
                    success += curr_page["success"]
                    failed += curr_page["failed"]
                    count += 1
            break
        except TokenExpired:
            if attempts >= 5:
                return logger.exception(
                    f"Failed to sync salesloft accounts for account {auth_account}"
                )
            else:
                auth_account.regenerate_token()
                attempts += 1
    return logger.info(f"Synced {success}/{success+failed} accounts for {auth_account}")


@background()
def sync_people(auth_account_id):
    auth_account = SalesloftAuthAccount.objects.get(id=auth_account_id)
    while True:
        attempts = 1
        try:
            success = 0
            failed = 0
            res = auth_account.helper_class.get_people()
            initial_page = sync_current_person_page(res["data"])
            success += initial_page["success"]
            failed += initial_page["failed"]
            if res["metadata"]["paging"]["total_pages"] > 1:
                count = 2
                while count <= res["metadata"]["paging"]["total_pages"] and count <= 20:
                    page_res = auth_account.helper_class.get_people(count)
                    curr_page = sync_current_person_page(page_res["data"])
                    success += curr_page["success"]
                    failed += curr_page["failed"]
                    count += 1
            break
        except TokenExpired:
            if attempts >= 5:
                return logger.exception(
                    f"Failed to sync salesloft accounts for account {auth_account}"
                )
            else:
                auth_account.regenerate_token()
                attempts += 1
    return logger.info(f"Synced {success}/{success+failed} people for {auth_account}")


def add_cadence_membership(person_id, cadence_id):
    cadence = Cadence.objects.get(id=cadence_id)
    auth_account = SalesloftAuthAccount.objects.get(id=cadence.owner.auth_account.id)
    contact = Contact.objects.get(id=person_id)
    person = People.objects.filter(email=contact.email).first()
    slaccount = SLAccount.objects.get(name=contact.account.name)
    owner = slaccount.owner.salesloft_id
    people_id = person.people_id if person else None
    created = False
    while True:
        attempts = 1
        try:
            if not person:
                data = {
                    "first_name": contact.secondary_data["FirstName"],
                    "last_name": contact.secondary_data["LastName"],
                    "email_address": contact.email,
                    "owner_id": owner,
                    "account_id": slaccount.account_id,
                }
                create_res = PeopleAdapter.create_in_salesloft(auth_account.access_token, data)
                process_person(create_res["data"])
                people_id = create_res["data"]["id"]
                created = True

            res = cadence.helper_class.add_membership(people_id, auth_account.access_token)
            break
        except TokenExpired:
            if attempts >= 5:
                return logger.exception(
                    f"Failed to add Person with id {people_id} to Cadence {cadence.name}, could not regenerate token"
                )
            else:
                auth_account.regenerate_token()
                attempts += 1
        except InvalidRequest:
            return {"status": "Failed"}
        except ValidationError as e:
            logger.exception(f"Error adding cadence: {e}")
            return {"status": "Failed"}
    logger.info(f"Person with id {people_id} added to cadence {cadence.id}")
    if created:
        return {"status": "Created"}
    return {"status": "Success"}
