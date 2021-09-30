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
from ..models import GongAuthAccount, GongCall, GongCallAdapter, GongAccount
from ..serializers import GongCallSerializer

logger = logging.getLogger("managr")


def emit_sync_gong_calls(auth_account_id):
    return sync_gong_calls(auth_account_id)


def sync_gong_calls(auth_account_id):
    curr_date = datetime.now()
    thirty = (curr_date - timedelta(30)).replace(microsecond=0).isoformat() + "Z"
    curr_date_str = curr_date.replace(microsecond=0).isoformat() + "Z"
    auth_account = GongAuthAccount.objects.get(id=auth_account_id)
    call_data = auth_account.helper_class.get_calls(thirty, curr_date_str)
    for call in call_data.get("calls"):
        call_res = GongCallAdapter.create_call(call, auth_account.id)
        print(call_res)
        call_existing = GongAccount.objects.filter(gong_id=call.get("metaData").get("id")).first()
        if call_existing:
            call_serializer = GongCallSerializer(data=call_res.as_dict, instance=call_existing)
        else:
            call_serializer = GongCallSerializer(data=call_res.as_dict)
        print(call_serializer)
        call_serializer.is_valid(raise_exception=True)
        call_serializer.save()
    return logger.info(f"Synced calls for account {auth_account_id}")
