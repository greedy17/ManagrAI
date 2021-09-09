import logging
import json
import re
import pytz
import uuid
import random
from datetime import datetime

from django.conf import settings
from django.db.models import Q

from background_task import background
from rest_framework.exceptions import ValidationError

from managr.salesloft.exceptions import TokenExpired
from managr.salesloft.models import SalesloftAuthAccount


logger = logging.getLogger("managr")


def emit_sync_cadences(auth_account_id):
    return sync_cadences(auth_account_id)


def emit_sync_slaccounts(auth_account_id):
    return sync_slaccounts(auth_account_id)


@background()
def sync_cadences(auth_account_id):
    auth_account = SalesloftAuthAccount.objects.get(id=auth_account_id)

    return


@background()
def sync_slaccounts(auth_account_id):
    auth_account = SalesloftAuthAccount.objects.get(id=auth_account_id)
    user_data = users.get("data")
    for user in user_data:
        user_res = SalesloftAccountAdapter.create_account(user, admin_account.id)
        if user_res is None:
            logger.error(f"Could not create salesloft account for {user['email']}")
            continue
        else:
            user_existing = SalesloftAccount.objects.filter(email=user.get("email")).first()
            if user_existing:
                user_serializer = SalesloftAccountSerializer(
                    data=user_res.as_dict, instance=user_existing
                )
            else:
                user_serializer = SalesloftAccountSerializer(data=user_res.as_dict)
            user_serializer.is_valid(raise_exception=True)
            user_serializer.save()
    return

