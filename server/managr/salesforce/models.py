import jwt
import pytz
import math
from functools import reduce

from datetime import datetime
from django.db import models
from django.utils import timezone

from django.contrib.postgres.fields import JSONField, ArrayField


from managr.core import constants as core_consts
from managr.core.models import TimeStampModel, IntegrationModel

from .adapter.models import SalesforceAuthAccountAdapter
from . import constants as sf_consts


class SFSyncOperation(TimeStampModel):
    user = models.ForeignKey("core.User", on_delete=models.CASCADE, related_name="sf_sync")
    operations = JSONField(
        default=dict, blank=True, help_text="A dict of operations by type {'accounts':[]}",
    )

    failed_operations = JSONField(
        default=dict,
        blank=True,
        help_text="A dict of failed operations (limit 5 tries) {'accounts':[]}",
    )
    successful_operations = JSONField(
        default=dict,
        blank=True,
        help_text="A dict of successful operations by type {'accounts':[]}",
    )

    completed_operations = JSONField(
        default=dict,
        blank=True,
        help_text="A dict of all completed operations by type {'accounts':[]}",
    )

    @property
    def successful_count(self):
        """ Number of total successful operations"""
        if len(self.successful_operations):
            return reduce(lambda x, y: int(x) + int(len(y)), self.successful_operations.values(), 0)

        return len(self.successful_operations)

    @property
    def failed_count(self):
        """ Number of total failed operations"""
        if len(self.failed_operations):
            return reduce(lambda x, y: int(x) + int(len(y)), self.failed_operations.values(), 0)

        return len(self.failed_operations)

    @property
    def completed_count(self):
        """ Number of all operations success/failed completed"""
        if len(self.completed_operations):
            return reduce(lambda x, y: int(x) + int(len(y)), self.completed_operations.values(), 0)

        return len(self.completed_operations)

    @property
    def total_count(self):
        """ Number of all operations success/failed """
        if len(self.operations):
            return reduce(lambda x, y: int(x) + int(len(y)), self.operations.values(), 0)

        return len(self.operations)

    @property
    def progress(self):
        """ percentage of all operations """
        if len(self.operations):
            return int((self.completed_count / self.total_count) * 100)

        return 100

    @property
    def in_progress(self):
        """ disable actions while in progress """

        return self.progress != 100

    @property
    def completed(self):
        self.progress == 100

    def __str__(self):
        return f"{self.user.email} tasks {self.progress}"

    def begin_tasks(self):
        from managr.salesforce.background import emit_sf_sync

        for opp in self.operations.values():
            for task in opp:
                emit_sf_sync(str(self.user.id), task, str(self.id))


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
    # TODO: need to split the value here as it returns a link
    salesforce_id = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["-datetime_created"]

    def __str__(self):
        return f"SF-{self.user.email} {self.salesforce_id}"

    @property
    def adapter_class(self):
        data = self.__dict__
        data["id"] = str(data["id"])
        return SalesforceAuthAccountAdapter(**data)

    def revoke(self):
        adapter = self.adapter_class
        adapter.revoke()
        self.delete()

    def save(self, *args, **kwargs):
        return super(SalesforceAuthAccount, self).save(*args, **kwargs)
