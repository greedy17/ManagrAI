import jwt
import pytz
import math
import logging

from functools import reduce

from datetime import datetime
from django.db import models
from django.utils import timezone

from django.contrib.postgres.fields import JSONField, ArrayField


from managr.core import constants as core_consts
from managr.core.models import TimeStampModel, IntegrationModel

from .adapter.models import SalesforceAuthAccountAdapter, OpportunityAdapter
from .adapter.exceptions import TokenExpired
from . import constants as sf_consts

logger = logging.getLogger("managr")


class ArrayLength(models.Func):
    function = "CARDINALITY"


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
        help_text="An Array of completed task id's",
    )
    failed_operations = ArrayField(
        JSONField(max_length=128, default=dict),
        default=list,
        blank=True,
        null=True,
        help_text="List of failed tasks as json since they are deleted",
    )

    @property
    def failed_count(self):
        return len(self.failed_operations)

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
            return int(((self.completed_count + self.failed_count) / self.total_count) * 100)

        return 100

    @property
    def in_progress(self):
        """ disable actions while in progress """
        return self.progress != 100

    def __str__(self):
        return f"{self.user.email} tasks {self.progress}% complete"

    def begin_tasks(self, attempts=1):
        from managr.salesforce.background import emit_sf_sync, emit_gen_next_sync

        sf_account = self.user.salesforce_account
        adapter = self.user.salesforce_account.adapter_class

        for key in self.operations_list:
            if key == sf_consts.RESOURCE_SYNC_ACCOUNT:
                try:
                    count = adapter.get_account_count()["totalSize"]
                except TokenExpired:
                    if attempts >= 5:
                        return logger.exception(
                            f"Failed to sync {key} data for user {str(self.user.id)} after {attempts} tries"
                        )
                    else:
                        sf_account.regenerate_token()
                        attempts += 1
                        return self.begin_tasks(attempts)
            elif key == sf_consts.RESOURCE_SYNC_STAGE:
                try:
                    count = adapter.get_stage_count()["totalSize"]
                except TokenExpired:
                    if attempts >= 5:
                        return logger.exception(
                            f"Failed to sync {key} data for user {str(self.user.id)} after {attempts} tries"
                        )
                    else:
                        sf_account.regenerate_token()
                        attempts += 1
                        return self.begin_tasks(attempts)
            elif key == sf_consts.RESOURCE_SYNC_OPPORTUNITY:
                try:
                    count = adapter.get_opportunity_count()["totalSize"]
                except TokenExpired:
                    if attempts >= 5:
                        return logger.exception(
                            f"Failed to sync {key} data for user {str(self.user.id)} after {attempts} tries"
                        )
                    else:
                        sf_account.regenerate_token()
                        attempts += 1
                        return self.begin_tasks(attempts)
                # get counts to set offsets
            for i in range(math.ceil(count / sf_consts.SALESFORCE_QUERY_LIMIT)):
                offset = sf_consts.SALESFORCE_QUERY_LIMIT * i
                t = emit_sf_sync(str(self.user.id), str(self.id), key, offset)
                if self.operations:
                    self.operations.append(str(t.id))
                else:
                    self.operations = [str(t.id)]
                self.save()

        scheduled_time = timezone.now() + timezone.timedelta(minutes=5)
        formatted_time = scheduled_time.strftime("%Y-%m-%dT%H:%M%Z")
        emit_gen_next_sync(str(self.user.id), self.operations_list, formatted_time)

        def delete(*args, **kwargs):
            return super().delete(*args, **kwargs)


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
    refresh_token_task = models.CharField(
        max_length=55,
        blank=True,
        help_text="Automatically Send a Refresh task to be executed 15 mins before expiry to reduce errors",
    )
    is_busy = models.BooleanField(default=False)

    class Meta:
        ordering = ["-datetime_created"]

    def __str__(self):
        return f"SF-{self.user.email} {self.salesforce_id}"

    @property
    def adapter_class(self):
        data = self.__dict__
        data["id"] = str(data["id"])
        return SalesforceAuthAccountAdapter(**data)

    def regenerate_token(self):
        data = self.__dict__
        data["id"] = str(data.get("id"))

        helper = SalesforceAuthAccountAdapter(**data)
        res = helper.refresh()
        self.token_generated_date = timezone.now()
        self.access_token = res.get("access_token", None)
        self.signature = res.get("signature", None)
        self.scope = res.get("scope", None)
        self.save()

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

    def update_opportunity(self, data):
        return OpportunityAdapter.update_opportunity(data, self.access_token, self.instance_url)

    def save(self, *args, **kwargs):
        return super(SalesforceAuthAccount, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        return super().delete(*args, **kwargs)
