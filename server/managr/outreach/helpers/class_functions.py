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
from managr.organization.models import Contact

logger = logging.getLogger("managr")


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


def process_account(account):
    account_res = AccountAdapter.create_account(account)
    if account_res is None:
        return {"failed": True}
    else:
        account_existing = Account.objects.filter(account_id=account["id"]).first()
        if account_existing:
            account_serializer = AccountSerializer(
                data=account_res.as_dict, instance=account_existing
            )
        else:
            account_serializer = AccountSerializer(data=account_res.as_dict)
        account_serializer.is_valid(raise_exception=True)
        account_serializer.save()
        return {"success": True}


def sync_all_accounts(data):
    failed = 0
    success = 0
    for resource in data:
        res = process_account(resource)
        if "failed" in res:
            failed += 1
        else:
            success += 1
    return {"success": success, "failed": failed}


def process_prospect(prospect, contact_id, email):
    if contact_id:
        prospect_res = ProspectAdapter.create_prospect(prospect, contact_id, email)
    else:
        prospect_res = None
    if prospect_res is None:
        return {"failed": True}
    else:
        prospect_existing = Prospect.objects.filter(prospect_id=prospect["id"]).first()
        if prospect_existing:
            prospect_serializer = ProspectSerializer(
                data=prospect_res.as_dict, instance=prospect_existing
            )
        else:
            prospect_serializer = ProspectSerializer(data=prospect_res.as_dict)
        prospect_serializer.is_valid(raise_exception=True)
        prospect_serializer.save()
    return {"success": True}


def sync_all_prospects(data):
    failed = 0
    success = 0
    for resource in data:
        contact = Contact.objects.filter(email__in=resource["attributes"]["emails"]).first()
        contact_id = contact.id if contact else None
        email = contact.email if contact else None
        res = process_prospect(resource, contact_id, email)
        if "failed" in res:
            failed += 1
        else:
            success += 1
    return {"success": success, "failed": failed}

