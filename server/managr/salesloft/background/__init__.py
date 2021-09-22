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
from ..models import (
    SalesloftAuthAccount,
    SLAccountAdapter,
    SLAccount,
    CadenceAdapter,
    Cadence,
    People,
    PeopleAdapter,
)
from managr.organization.models import Contact

from ..helpers.class_functions import (
    process_cadence,
    process_person,
    process_slaccount,
    sync_current_slaccount_page,
    sync_current_person_page,
    sync_current_cadence_page,
)

logger = logging.getLogger("managr")


def emit_sync_cadences(auth_account_id):
    return sync_cadences(auth_account_id)


def emit_sync_slaccounts(auth_account_id):
    return sync_slaccounts(auth_account_id)


def emit_sync_people(auth_account_id):
    return sync_people(auth_account_id)


def emit_add_cadence_membership(people_id, cadence_id):
    return add_cadence_membership(people_id, cadence_id)


@background()
def sync_cadences(auth_account_id):
    auth_account = SalesloftAuthAccount.objects.get(id=auth_account_id)
    while True:
        attempts = 1
        try:
            res = auth_account.helper_class.get_cadences()
            sync_current_cadence_page(res["data"])
            if res["metadata"]["paging"]["total_pages"] > 1:
                count = 2
                while count <= res["metadata"]["paging"]["total_pages"]:
                    page_res = auth_account.helper_class.get_cadences(count)
                    sync_current_cadence_page(page_res["data"])
                    count += 1
            break
        except TokenExpired:
            if attempts >= 5:
                return logger.exception(
                    f"Failed to sync salesloft cadences for account {auth_account.id}"
                )
            else:
                auth_account.regenerate_token()
                attempts += 1
    return logger.info(f"Synced all cadences for {auth_account}")


@background()
def sync_slaccounts(auth_account_id):
    auth_account = SalesloftAuthAccount.objects.get(id=auth_account_id)
    while True:
        attempts = 1
        try:
            res = auth_account.helper_class.get_accounts()
            sync_current_slaccount_page(res["data"])
            if res["metadata"]["paging"]["total_pages"] > 1:
                count = 2
                while count <= res["metadata"]["paging"]["total_pages"]:
                    page_res = auth_account.helper_class.get_accounts(count)
                    sync_current_slaccount_page(page_res["data"])
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
    return logger.info(f"Synced all accounts for {auth_account}")


@background()
def sync_people(auth_account_id):
    auth_account = SalesloftAuthAccount.objects.get(id=auth_account_id)
    while True:
        attempts = 1
        try:
            res = auth_account.helper_class.get_people()
            sync_current_person_page(res["data"])
            if res["metadata"]["paging"]["total_pages"] > 1:
                count = 2
                while count <= res["metadata"]["paging"]["total_pages"]:
                    page_res = auth_account.helper_class.get_people(count)
                    sync_current_person_page(page_res["data"])
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
    return logger.info(f"Synced all people for {auth_account}")


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
