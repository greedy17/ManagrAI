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
from ..serializers import SLAccountSerializer, CadenceSerializer, PeopleSerializer


logger = logging.getLogger("managr")


def emit_sync_cadences(auth_account_id):
    return sync_cadences(auth_account_id)


def emit_sync_slaccounts(auth_account_id):
    return sync_slaccounts(auth_account_id)


def emit_sync_people(auth_account_id):
    return sync_people(auth_account_id)


def emit_add_cadence_membership(people_id, cadence_id):
    return add_cadence_membership(people_id, cadence_id)


def create_person(people):
    people_res = PeopleAdapter.create_people(people)
    if people_res is None:
        logger.error(f"Could not create people {people['display_name']}")
    else:
        people_existing = People.objects.filter(people_id=people["id"]).first()
        if people_existing:
            people_serializer = PeopleSerializer(data=people_res.as_dict, instance=people_existing)
        else:
            people_serializer = PeopleSerializer(data=people_res.as_dict)
        people_serializer.is_valid(raise_exception=True)
        people_serializer.save()
    return


@background()
def sync_cadences(auth_account_id):
    auth_account = SalesloftAuthAccount.objects.get(id=auth_account_id)
    while True:
        attempts = 1
        try:
            res = auth_account.helper_class.get_all_cadences()
            break
        except TokenExpired:
            if attempts >= 5:
                return logger.exception(
                    f"Failed to sync salesloft cadences for account {auth_account.id}"
                )
            else:
                auth_account.regenerate_token()
                attempts += 1

    for cadence in res["data"]:
        cadence_res = CadenceAdapter.create_cadence(cadence)
        if cadence_res is None:
            logger.error(f"Could not create cadence {cadence['name']}")
            continue
        else:
            cadence_existing = Cadence.objects.filter(cadence_id=cadence["id"]).first()
            if cadence_existing:
                cadence_serializer = CadenceSerializer(
                    data=cadence_res.as_dict, instance=cadence_existing
                )
            else:
                cadence_serializer = CadenceSerializer(data=cadence_res.as_dict)
            cadence_serializer.is_valid(raise_exception=True)
            cadence_serializer.save()
    return logger.info(f"Synced cadences for {auth_account.id}")


@background()
def sync_slaccounts(auth_account_id):
    auth_account = SalesloftAuthAccount.objects.get(id=auth_account_id)
    while True:
        attempts = 1
        try:
            res = auth_account.helper_class.get_all_accounts()
            break
        except TokenExpired:
            if attempts >= 5:
                return logger.exception(
                    f"Failed to sync salesloft accounts for account {auth_account}"
                )
            else:
                auth_account.regenerate_token()
                attempts += 1

    for account in res["data"]:
        account_res = SLAccountAdapter.create_slaccount(account)
        if account_res is None:
            logger.error(f"Could not create salesloft account {account['name']}")
            continue
        else:
            account_existing = SLAccount.objects.filter(account_id=account["id"]).first()
            if account_existing:
                account_serializer = SLAccountSerializer(
                    data=account_res.as_dict, instance=account_existing
                )
            else:
                account_serializer = SLAccountSerializer(data=account_res.as_dict)
            account_serializer.is_valid(raise_exception=True)
            account_serializer.save()
    return logger.info(f"Synced accounts for {auth_account}")


@background()
def sync_people(auth_account_id):
    auth_account = SalesloftAuthAccount.objects.get(id=auth_account_id)
    while True:
        attempts = 1
        try:
            res = auth_account.helper_class.get_all_people()
            break
        except TokenExpired:
            if attempts >= 5:
                return logger.exception(
                    f"Failed to sync salesloft accounts for account {auth_account}"
                )
            else:
                auth_account.regenerate_token()
                attempts += 1

    for people in res["data"]:
        create_person(people)
    return logger.info(f"Synced people for {auth_account}")


def add_cadence_membership(person_id, cadence_id):
    cadence = Cadence.objects.get(id=cadence_id)
    auth_account = SalesloftAuthAccount.objects.get(id=cadence.owner.auth_account.id)
    contact = Contact.objects.get(id=person_id)
    person = People.objects.filter(email=contact.email).first()
    slaccount = SLAccount.objects.get(name=contact.account.name)
    owner = slaccount.owner.salesloft_id
    people_id = person.id if person else None
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
                create_person(create_res["data"])
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
