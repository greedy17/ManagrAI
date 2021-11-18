import jwt
import pytz
import math
import logging
import json
import dateutil.parser

from ..models import (
    Sequence,
    SequenceAdapter,
    Prospect,
    ProspectAdapter,
    Account,
    AccountAdapter,
    OutreachAccountAdapter,
    OutreachAccount,
)
from ..serializers import (
    SequenceSerializer,
    ProspectSerializer,
    AccountSerializer,
    OutreachAccountSerializer,
)

logger = logging.getLogger("managr")


def process_account(account, outreach_account_id):
    user_res = OutreachAccountAdapter.create_account(account, outreach_account_id)
    if user_res is None:
        return {"failed": True}
    else:
        user_existing = OutreachAccount.objects.filter(email=account.get("email")).first()
        if user_existing:
            user_serializer = OutreachAccountSerializer(
                data=user_res.as_dict, instance=user_existing
            )
        else:
            user_serializer = OutreachAccountSerializer(data=user_res.as_dict)
        user_serializer.is_valid(raise_exception=True)
        user_serializer.save()
        return {"success": True}


def sync_all_sequences(data):
    failed = 0
    success = 0
    for resource in data:
        res = process_sequence(resource)
        if "failed" in res:
            failed += 1
        else:
            success += 1
    return {"success": success, "failed": failed}


def process_sequence(sequence):
    sequence_res = SequenceAdapter.create_sequence(sequence)
    if sequence_res is None:
        return {"failed": True}
    else:
        sequence_existing = Sequence.objects.filter(sequence_id=sequence["id"]).first()
        if sequence_existing:
            sequence_serializer = SequenceSerializer(
                data=sequence_res.as_dict, instance=sequence_existing
            )
        else:
            sequence_serializer = SequenceSerializer(data=sequence_res.as_dict)
        sequence_serializer.is_valid(raise_exception=True)
        sequence_serializer.save()
        return {"success": True}


def sync_sequences(data):
    failed = 0
    success = 0
    for resource in data:
        res = process_sequence(resource)
        if "failed" in res:
            failed += 1
        else:
            success += 1
    return {"success": success, "failed": failed}


def process_slaccount(slaccount):
    account_res = AccountAdapter.create_slaccount(slaccount)
    if account_res is None:
        return {"failed": True}
    else:
        account_existing = Account.objects.filter(account_id=slaccount["id"]).first()
        if account_existing:
            account_serializer = AccountSerializer(
                data=account_res.as_dict, instance=account_existing
            )
        else:
            account_serializer = AccountSerializer(data=account_res.as_dict)
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
    people_res = ProspectAdapter.create_people(people)
    if people_res is None:
        return {"failed": True}
    else:
        people_existing = Prospect.objects.filter(people_id=people["id"]).first()
        if people_existing:
            people_serializer = ProspectSerializer(
                data=people_res.as_dict, instance=people_existing
            )
        else:
            people_serializer = ProspectSerializer(data=people_res.as_dict)
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

