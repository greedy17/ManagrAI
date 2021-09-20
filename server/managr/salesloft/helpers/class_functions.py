import jwt
import pytz
import math
import logging
import json
import dateutil.parser

from ..models import Cadence, CadenceAdapter, People, PeopleAdapter, SLAccount, SLAccountAdapter
from ..serializers import CadenceSerializer, PeopleSerializer, SLAccountSerializer

logger = logging.getLogger("managr")


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
    for resource in data:
        res = process_cadence(resource)
        if "failed" in res:
            logger.error(f"Could not create cadence {resource['name']}")
            return
    return {"success": True}


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
    for resource in data:
        res = process_slaccount(resource)
        if "failed" in res:
            logger.error(f"Could not create salesloft account {resource['name']}")
            return
    return {"success": True}


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
    for resource in data:
        res = process_person(resource)
        if "failed" in res:
            logger.error(f"Could not create person {resource['display_name']}")
            return
    return {"success": True}

