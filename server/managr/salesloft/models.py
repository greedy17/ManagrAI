import jwt
import pytz
import math
import logging

from datetime import datetime
from django.db import models
from django.utils import timezone

from django.contrib.postgres.fields import JSONField, ArrayField

from managr.core.models import TimeStampModel

from managr.salesforce.adapter.models import ActivityAdapter

from . import constants as salesloft_consts

logger = logging.getLogger("managr")


class SalesloftAuthAccount(TimeStampModel):
    user = models.OneToOneField(
        "core.User", on_delete=models.CASCADE, related_name="salesloft_account"
    )
