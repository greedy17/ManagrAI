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
from managr.slack.helpers import block_builders

from .adapter.models import SalesforceAuthAccountAdapter, OpportunityAdapter
from .adapter.exceptions import TokenExpired
from . import constants as sf_consts

logger = logging.getLogger("managr")


class ArrayLength(models.Func):
    function = "CARDINALITY"


class SObjectField(IntegrationModel):  # change this to the integration object
    salesforce_account = models.ForeignKey(
        "salesforce.SalesforceAuthAccount", on_delete=models.CASCADE, related_name="object_fields"
    )
    salesforce_object = models.CharField(max_length=255)
    api_name = models.CharField(max_length=255)
    custom = models.BooleanField(default=False)
    createable = models.BooleanField(default=False)
    updateable = models.BooleanField(default=False)
    unique = models.BooleanField(default=False)
    required = models.BooleanField(default=False)
    data_type = models.CharField(max_length=255)
    display_value = models.CharField(
        max_length=255,
        blank=True,
        help_text="if this is a reference field we save the display value as well",
    )
    value = models.CharField(max_length=255, null=True, blank=True)
    label = models.CharField(max_length=255)
    length = models.PositiveIntegerField(default=0)
    reference = models.CharField(max_length=255, null=True)
    reference_to_infos = ArrayField(
        models.CharField(max_length=255, blank=True),
        default=list,
        blank=True,
        help_text="An Array of operations to perform on",
    )
    options = ArrayField(
        models.CharField(max_length=255, blank=True),
        default=list,
        blank=True,
        help_text="An Array of operations to perform on",
    )

    def __str__(self):
        return f"{self.label} {self.salesforce_account__user}"

    def to_slack_field_type(self):
        if self.data_type == "Picklist":
            return block_builders.static_select
        elif self.data_type == "Reference":
            return block_builders.external_select

        elif self.data_type == "Date":
            return block_builders.datePicker

        elif self.data_type == "MultiPicklist":
            return block_builders.mulit_static_select

        elif self.data_type == "Boolean":
            return block_builders.checkbox_block
        else:
            return block_builders.input_block

    @property
    def display_value_keys(self):
        return

    @property
    def as_dict(self):
        return vars(self)

    @property
    def as_slack_block(self):
        return self


class SObjectValidation(IntegrationModel):
    message = models.TextField(blank=True)
    description = models.TextField(blank=True)
    salesforce_object = models.CharField(max_length=255)
    salesforce_account = models.ForeignKey(
        "salesforce.SalesforceAuthAccount", on_delete=models.CASCADE, related_name="object_fields"
    )

    def __str__(self):
        return f"{self.salesforce_account}-{self.salesforce_account__user}"


class SFSyncOperation(TimeStampModel):
    operation_type = models.CharField(max_length=255, blank=True)
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
        from managr.salesforce.background import (
            emit_sf_sync,
            emit_gen_next_sync,
            emit_generate_forms,
        )

        sf_account = self.user.salesforce_account
        adapter = self.user.salesforce_account.adapter_class
        for key in self.operations_list:
            while True:
                try:
                    count = adapter.get_resource_count(key)["totalSize"]
                    # populate the sf account resource fields (unique to each user)
                    sf_account.get_fields(key)
                    # populate the sf account resource validators (may be unique to each user)
                    sf_account.get_validations(key)
                    # populate the sf account picklist values (may be unique to each user)
                    sf_account.get_picklist_values(key)
                    # emit event to create forms
                    if self.user.is_admin:
                        emit_generate_forms(str(self.user.id))
                    break
                except TokenExpired:
                    if attempts >= 5:
                        return logger.exception(
                            f"Failed to sync {key} data for user {str(self.user.id)} after {attempts} tries"
                        )
                    else:
                        sf_account.regenerate_token()
                        attempts += 1
                # get counts to set offsets
            count = min(count, 1000)
            for i in range(math.ceil(count / sf_consts.SALESFORCE_QUERY_LIMIT)):
                offset = sf_consts.SALESFORCE_QUERY_LIMIT * i

                t = emit_sf_sync(str(self.user.id), str(self.id), key, offset)
                if self.operations:
                    self.operations.append(str(t.task_hash))
                else:
                    self.operations = [str(t.task_hash)]
                self.save()

        scheduled_time = timezone.now() + timezone.timedelta(minutes=2.5)
        formatted_time = scheduled_time.strftime("%Y-%m-%dT%H:%M%Z")
        emit_gen_next_sync(str(self.user.id), self.operations_list, formatted_time)

        def delete(*args, **kwargs):
            return super().delete(*args, **kwargs)


class SFObjectFieldsOperation(SFSyncOperation):
    def begin_tasks(self, attempts=1):
        return super().begin_tasks(attempts=attempts)


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
    object_fields = JSONField(
        default=dict,
        null=True,
        help_text="All non primary fields that are on the model each org may have its own",
        max_length=500,
    )
    default_record_id = models.CharField(
        max_length=255,
        blank=True,
        help_text="The default record id should be the same for all objects and is used for picklist values",
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
        data["user"] = str(self.user.id)
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

    def get_fields(self, resource):
        fields, record_type_id = [*self.adapter_class.list_fields(resource).values()]
        self.default_record_id = record_type_id

    def get_validations(self, resource):
        rules = self.adapter_class.list_validations(resource)
        if self.object_fields and self.object_fields.get(resource, None):
            self.object_fields[resource]["validations"] = rules
        self.save()

    def get_picklist_values(self, resource):
        values = self.adapter_class.list_picklist_values(resource)

        if self.object_fields and self.object_fields.get(resource, None):
            fields = self.object_fields.get(resource).get("fields", [])
            for k, v in values.items():
                if k in fields:
                    fields[k]["options"] = v
                    continue

        self.save()

    def list_resource_data(self, resource, offset, *args, **kwargs):
        return self.adapter_class.list_resource_data(resource, offset, *args, **kwargs)

    def update_opportunity(self, data):
        return OpportunityAdapter.update_opportunity(data, self.access_token, self.instance_url)

    def save(self, *args, **kwargs):
        return super(SalesforceAuthAccount, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        return super().delete(*args, **kwargs)
