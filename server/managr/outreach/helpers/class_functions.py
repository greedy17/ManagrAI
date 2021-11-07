import jwt
import pytz
import math
import logging
import json
import dateutil.parser

from ..models import Cadence, CadenceAdapter, People, PeopleAdapter, SLAccount, SLAccountAdapter, SalesloftAccountAdapter,SalesloftAccount
from ..serializers import CadenceSerializer, PeopleSerializer, SLAccountSerializer, SalesloftAccountSerializer

logger = logging.getLogger("managr")

def process_account(account, auth_account_id):
    user_res = SalesloftAccountAdapter.create_account(account, auth_account_id)
    if user_res is None:
        return {"failed": True}
    else:
        user_existing = SalesloftAccount.objects.filter(email=account.get("email")).first()
        if user_existing:
            user_serializer = SalesloftAccountSerializer(
                data=user_res.as_dict, instance=user_existing
            )
        else:
            user_serializer = SalesloftAccountSerializer(data=user_res.as_dict)
        user_serializer.is_valid(raise_exception=True)
        user_serializer.save()
        return {"success": True}

def sync_current_account_page(data, auth_account_id):
    failed = 0
    success = 0
    for resource in data:
        res = process_account(resource, auth_account_id)
        if "failed" in res:
            failed += 1
        else:
            success += 1
    return {"success": success, "failed": failed}


def process_cadence(cadence):
    cadence_res = CadenceAdapter.create_cadence(cadence)
    if cadence_res is None:
        return {"failed": True}
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
        return {"success": True}


def sync_current_cadence_page(data):
    failed = 0
    success = 0
    for resource in data:
        res = process_cadence(resource)
        if "failed" in res:
            failed += 1
        else:
            success += 1
    return {"success": success, "failed": failed}


def process_slaccount(slaccount):
    account_res = SLAccountAdapter.create_slaccount(slaccount)
    if account_res is None:
        return {"failed": True}
    else:
        account_existing = SLAccount.objects.filter(account_id=slaccount["id"]).first()
        if account_existing:
            account_serializer = SLAccountSerializer(
                data=account_res.as_dict, instance=account_existing
            )
        else:
            account_serializer = SLAccountSerializer(data=account_res.as_dict)
        account_serializer.is_valid(raise_exception=True)
        account_serializer.save()
        return {"success": True}


def sync_current_slaccount_page(data):
    failed = 0
    success = 0
    for resource in data:
        res = process_slaccount(resource)
        if "failed" in res:
            failed += 1
        else:
            success += 1
    return {"success": success, "failed": failed}


def process_person(people):
    people_res = PeopleAdapter.create_people(people)
    if people_res is None:
        return {"failed": True}
    else:
        people_existing = People.objects.filter(people_id=people["id"]).first()
        if people_existing:
            people_serializer = PeopleSerializer(data=people_res.as_dict, instance=people_existing)
        else:
            people_serializer = PeopleSerializer(data=people_res.as_dict)
        people_serializer.is_valid(raise_exception=True)
        people_serializer.save()
    return {"success": True}


def sync_current_person_page(data):
    failed = 0
    success = 0
    for resource in data:
        res = process_person(resource)
        if "failed" in res:
            failed += 1
        else:
            success += 1
    return {"success": success, "failed": failed}

