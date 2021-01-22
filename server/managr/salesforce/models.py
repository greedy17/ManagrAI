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
    operations_list = ArrayField(
        models.CharField(max_length=255, blank=True),
        default=list,
        blank=True,
        help_text="An Array of operations to perform on",
    )
    operations = ArrayField(
        models.CharField(max_length=255, blank=True),
        default=list,
        blank=True,
        help_text="An Array of task ids",
    )
    completed_operations = ArrayField(
        models.CharField(max_length=255, blank=True),
        default=list,
        blank=True,
        help_text="An Array of completed/faild task id's",
    )

    @property
    def completed_count(self):
        """ Number of all operations success/failed completed"""
        return len(self.completed_operations)

    @property
    def total_count(self):
        """ Number of all operations success/failed """
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

    def __str__(self):
        return f"{self.user.email} tasks {self.progress}"

    def begin_tasks(self):
        from managr.salesforce.background import emit_sf_sync

        for key in self.operations_list:
            if key == sf_consts.RESOURCE_SYNC_ACCOUNT:
                count = self.user.salesforce_account.adapter_class.get_account_count()["totalSize"]
            elif key == sf_consts.RESOURCE_SYNC_STAGE:
                count = self.user.salesforce_account.adapter_class.get_account_count()["totalSize"]
            elif key == sf_consts.RESOURCE_SYNC_OPPORTUNITY:
                count = self.user.salesforce_account.adapter_class.get_opportunity_count()[
                    "totalSize"
                ]
                # get counts to set offsets
            for i in range(math.ceil(count / sf_consts.SALESFORCE_QUERY_LIMIT)):
                offset = (sf_consts.SALESFORCE_QUERY_LIMIT * i) + 1 if i > 0 else None
                t = emit_sf_sync(str(self.user.id), str(self.id), key, offset)
                if self.operations:
                    self.operations.append(str(t.id))
                else:
                    self.operations = [str(t.id)]
                self.save()


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
    salesforce_account = models.CharField(max_length=255, blank=True)
    login_link = models.CharField(max_length=255, blank=True)

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

    def list_accounts(self, offset):
        return self.adapter_class.list_accounts(offset)

    def list_stages(self, offset):
        return self.adapter_class.list_stages(offset)

    def list_opportunities(self, offset):
        return self.adapter_class.list_opportunities(offset)

    def save(self, *args, **kwargs):
        return super(SalesforceAuthAccount, self).save(*args, **kwargs)
