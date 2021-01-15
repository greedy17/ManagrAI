import jwt
import pytz
import math

from datetime import datetime
from django.db import models
from django.utils import timezone

from django.contrib.postgres.fields import JSONField, ArrayField
from django.contrib.postgres.fields import JSONField

from managr.core import constants as core_consts
from managr.core.models import TimeStampModel, IntegrationModel

from .adapter.models import SalesforceAuthAccountAdapter


class SalesforceAuthAccount(TimeStampModel):
    user = models.OneToOneField(
        "core.User", on_delete=models.CASCADE, related_name="salesforce_account"
    )
    access_token = models.CharField(max_length=255, blank=True)
    refresh_token = models.CharField(max_length=255, blank=True)
    signature = models.CharField(max_length=255, blank=True)
    scope = models.CharField(max_length=255, blank=True)
    id_token = models.TextField(blank=True)
    instance_url = models.CharField(max_length=255, blank=True)
    salesforce_id = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["-datetime_created"]

    def __str__(self):
        return f"SF-{self.user.email} {self.salesforce_id}"

    @property
    def adpater_class(self):
        data = self.__dict__
        data["id"] = str(data["id"])
        return SalesforceAuthAccountAdapter(**data)

    def revoke(self):
        adapter = self.adpater_class
        adapter.revoke()
        self.delete()
