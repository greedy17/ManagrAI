import logging
import json
import re
import pytz
import uuid
import random
from datetime import datetime, timedelta
from urllib.parse import urlencode

from django.conf import settings
from django.db.models import Q

from background_task import background
from rest_framework.exceptions import ValidationError

from ..exceptions import TokenExpired, InvalidRequest
from ..models import GongAuthAccount, GongCall, GongCallAdapter, GongAccount, GongAccountAdapter
from ..serializers import GongCallSerializer, GongAuthSerializer, GongAccountSerializer

logger = logging.getLogger("managr")


def emit_sync_gong_calls(auth_account_id):
    return sync_gong_calls(auth_account_id)


def emit_sync_gong_accounts(auth_account_id):
    return sync_gong_accounts(auth_account_id)


@background()
def sync_gong_calls(auth_account_id):
    curr_date = datetime.now()
    thirty = (curr_date - timedelta(30)).replace(microsecond=0).isoformat() + "Z"
    curr_date_str = curr_date.replace(microsecond=0).isoformat() + "Z"
    auth_account = GongAuthAccount.objects.get(id=auth_account_id)
    call_data = auth_account.helper_class.get_calls(thirty, curr_date_str)
    for call in call_data.get("calls"):
        call_id = call.get("metaData").get("id")
        call_res = GongCallAdapter.create_call(call, auth_account.id)
        call_existing = GongCall.objects.filter(gong_id=call_id).first()
        if call_existing:
            call_serializer = GongCallSerializer(data=call_res.as_dict, instance=call_existing)
        else:
            call_serializer = GongCallSerializer(data=call_res.as_dict)
        call_serializer.is_valid(raise_exception=True)
        call_serializer.save()
    return logger.info(f"Synced calls for account {auth_account_id}")


@background()
def sync_gong_accounts(auth_account_id):
    auth_account = GongAuthAccount.objects.get(id=auth_account_id)
    cursor = None
    while True:
        users = auth_account.helper_class.get_users(cursor)
        cursor = users["records"]["cursor"] if "cursor" in users["records"] else None
        user_data = users.get("users")
        for user in user_data:
            user_res = GongAccountAdapter.create_account(user, auth_account.id)
            if user_res is None:
                logger.error(f"Could not create gong account for {user['emailAddress']}")
                continue
            else:
                user_existing = GongAccount.objects.filter(email=user.get("emailAddress")).first()
                if user_existing:
                    user_serializer = GongAccountSerializer(
                        data=user_res.as_dict, instance=user_existing
                    )
                else:
                    user_serializer = GongAccountSerializer(data=user_res.as_dict)
                user_serializer.is_valid(raise_exception=True)
                user_serializer.save()
        if not cursor:
            break
    logger.info(f"Synced gong accounts for account {auth_account_id}")
    return {"success": True}
