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


class SalesloftAuthAccountQuerySet(models.QuerySet):
    def for_user(self, user):
        if user.is_superuser:
            return self.all()
        if user.organization and user.is_active:
            if user.type == core_consts.ACCOUNT_TYPE_MANAGER:
                return self.filter(user__organization=user.organization)
            elif user.type == core_consts.ACCOUNT_TYPE_REP:
                return self.filter(user=user)
            else:
                return self.none()


class SalesloftAuthAccount(TimeStampModel):
    user = models.OneToOneField(
        "core.User", on_delete=models.CASCADE, related_name="salesloft_account"
    )
    access_token = models.TextField(blank=True)
    refresh_token = models.TextField(blank=True)

    objects = SalesloftAuthAccountQuerySet.as_manager()

    class Meta:
        ordering = ["-datetime_created"]
