import jwt
import pytz
import math
import logging
import json

from datetime import datetime
from django.db import models
from django.utils import timezone

from django.contrib.postgres.fields import JSONField, ArrayField
from django.db.models import Q
from django.db.models.constraints import UniqueConstraint
from background_task.models import CompletedTask, Task
from managr.crm.models import BaseOpportunity
from managr.core.models import TimeStampModel, IntegrationModel
from managr.slack.helpers.exceptions import (
    UnHandeledBlocksException,
    InvalidBlocksFormatException,
    InvalidBlocksException,
    InvalidAccessToken,
)
from managr.slack import constants as slack_consts
from .adapter.models import HubspotAuthAccountAdapter, DealAdapter
from .adapter.exceptions import (
    TokenExpired,
    InvalidFieldError,
    UnhandledCRMError,
    InvalidRefreshToken,
    CannotRetreiveObjectType,
)
from . import constants as hs_consts
from managr.slack.helpers import block_builders

logger = logging.getLogger("managr")


def getHobjectDefaults():
    return {
        hs_consts.RESOURCE_SYNC_COMPANY: True,
        hs_consts.RESOURCE_SYNC_CONTACT: True,
        hs_consts.RESOURCE_SYNC_DEAL: True,
    }


class HSSyncOperation(TimeStampModel):
    operation_type = models.CharField(max_length=255, blank=True)
    user = models.ForeignKey("core.User", on_delete=models.CASCADE, related_name="hs_sync")
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
        models.CharField(max_length=255, blank=True),
        default=list,
        blank=True,
        help_text="List of failed tasks as that failed from task runner for uncaught exceptions after 5 tries",
    )

    class Meta:
        ordering = ["-datetime_created"]

    @property
    def status(self):
        if not len(self.operations_list):
            return "No Operations"
        elif len(self.operations_list) and not len(self.operations):
            return "Not Started"
        elif len(self.operations_list) and not self.progress == 100:
            return "In Progress"
        elif len(self.operations_list) and self.progress == 100:
            return "Completed"
        else:
            return "Can't determine progress"

    @property
    def failed_count(self):
        return len(self.failed_operations)

    @property
    def completed_count(self):
        """Number of all operations success/failed completed"""
        return len(self.completed_operations)

    @property
    def total_count(self):
        """Number of all operations success/failed"""
        return len(self.operations)

    @property
    def progress(self):
        """percentage of all operations"""
        if len(self.operations):
            return int(((self.completed_count + self.failed_count) / self.total_count) * 100)

        return 0

    @property
    def in_progress(self):
        """disable actions while in progress"""
        return self.progress != 100

    def __str__(self):
        return f"{self.user.email} status: {self.status} tasks {self.progress}% complete"

    def remove_from_operations_list(self, operations=[]):
        """This method is used to remove operations (array) from the NEXT sync"""
        self.operations_list = list(filter(lambda opp: opp not in operations, self.operations_list))
        self.save()

    def reconcile(self):
        if len(self.operations) and (len(self.completed_operations) or len(self.failed_operations)):
            completed_tasks = set(self.completed_operations)
            all_tasks = set(self.operations)
            if self.progress > 100:
                tasks_diff = list(completed_tasks - all_tasks)
                for task_hash in tasks_diff:
                    # check to see if there was a problem completing the flow but all tasks are ready
                    task = CompletedTask.objects.filter(task_hash=task_hash).first()
                    if task and str(self.id) in task.task_params:
                        self.operations.append(task_hash)

                return self.save()

                return
            elif self.progress < 100:

                tasks_diff = list(all_tasks - completed_tasks)
                for task_hash in tasks_diff:
                    # check to see if there was a problem completing the flow but all tasks are ready
                    task = CompletedTask.objects.filter(task_hash=task_hash).count()
                    if task:
                        self.completed_operations.append(task_hash)

                return self.save()

        return

    def save(self, *args, **kwargs):
        return super(HSSyncOperation, self).save(*args, **kwargs)


class HSObjectFieldsOperation(HSSyncOperation):
    @property
    def operations_map(self):
        from managr.hubspot.tasks import emit_sync_hobject_fields

        return {
            hs_consts.HUBSPOT_OBJECT_FIELDS: emit_sync_hobject_fields,
        }

    def begin_tasks(self, attempts=1):
        for op in self.operations_list:
            # split the operation to get opp and params
            operation_name, param = op.split(".")
            operation = self.operations_map.get(operation_name)
            scheduled_for = datetime.now(pytz.utc)
            t = operation(str(self.user.id), str(self.id), param, scheduled_for)

            self.operations.append(str(t.task_hash))

            self.save()

    def save(self, *args, **kwargs):
        return super(HSObjectFieldsOperation, self).save(*args, **kwargs)


class HSResourceSync(HSSyncOperation):
    def begin_tasks(self, attempts=1):
        from managr.hubspot.tasks import emit_hs_sync

        for key in self.operations_list:
            while True:
                hs_account = self.user.hubspot_account
                try:
                    t = emit_hs_sync(str(self.user.id), str(self.id), key)
                    self.operations.append(str(t.task_hash))
                    self.save()
                    break
                except TokenExpired:
                    if attempts >= 5:
                        return logger.exception(
                            f"Failed to sync {key} data for user {str(self.user.id)} after {attempts} tries"
                        )
                    else:
                        try:
                            hs_account.regenerate_token()
                            attempts += 1
                        except InvalidRefreshToken:
                            return logger.exception(
                                f"Failed to sync {key} data for user {str(self.user.id)} after not being able to refresh their token"
                            )
                except CannotRetreiveObjectType:
                    hs_account.hobjects[key] = False
                    hs_account.save()

    def save(self, *args, **kwargs):
        return super(HSResourceSync, self).save(*args, **kwargs)


class HubspotAuthAccount(TimeStampModel):
    user = models.OneToOneField(
        "core.User", on_delete=models.CASCADE, related_name="hubspot_account"
    )
    access_token = models.CharField(max_length=255, blank=True)
    refresh_token = models.CharField(max_length=255, blank=True)
    hubspot_id = models.CharField(max_length=255, blank=True)
    hobjects = JSONField(
        default=getHobjectDefaults, help_text="All resources we are retrieving", max_length=500,
    )
    extra_pipeline_fields = ArrayField(models.CharField(max_length=255), default=list, blank=True)

    class Meta:
        ordering = ["-datetime_created"]
        constraints = [UniqueConstraint(fields=["hubspot_id"], name="unique_hubspot_id")]

    def __str__(self):
        return f"Hubspot-{self.user.email} {self.hubspot_id}"

    @property
    def adapter_class(self):
        data = self.__dict__
        data["id"] = str(data["id"])
        data["user"] = str(self.user.id)
        data["object_fields"] = {
            key: self.user.object_fields.filter(crm_object=key).values_list("api_name", flat=True)
            for key in self.hobjects.keys()
        }
        return HubspotAuthAccountAdapter(**data)

    @property
    def resource_sync_opts(self):
        return list(
            filter(
                lambda resource: f"{resource}"
                if self.hobjects.get(resource, None) not in ["", None, False]
                else False,
                self.hobjects,
            )
        )

    @property
    def crm_id(self):
        return self.hubspot_id

    @property
    def instance_url(self):
        return hs_consts.HUBSPOT_INSTANCE_URL

    @property
    def field_sync_opts(self):
        return list(
            map(
                lambda resource: f"{hs_consts.HUBSPOT_OBJECT_FIELDS}.{resource}",
                filter(
                    lambda resource: resource
                    if self.hobjects.get(resource, None) not in ["", None, False]
                    else False,
                    self.hobjects,
                ),
            )
        )

    @property
    def picklist_sync_opts(self):
        return list(
            map(
                lambda resource: f"{hs_consts.hubspot_PICKLIST_VALUES}.{resource}",
                filter(
                    lambda resource: resource
                    if self.hobjects.get(resource, None) not in ["", None, False]
                    else False,
                    self.hobjects,
                ),
            )
        )

    @property
    def validation_sync_opts(self):
        if self.user.is_admin:
            return list(
                map(
                    lambda resource: f"{hs_consts.hubspot_VALIDATIONS}.{resource}",
                    filter(
                        lambda resource: resource
                        if self.hobjects.get(resource, None) not in ["", None, False]
                        else False,
                        self.hobjects,
                    ),
                )
            )
        return []

    def regenerate_token(self):
        res = self.adapter_class.refresh()
        self.access_token = res.get("access_token", None)
        self.refresh_token = res.get("refresh_token", None)
        self.save()

    def revoke(self):
        adapter = self.adapter_class
        adapter.revoke()
        self.delete()

    def get_fields(self, resource):

        fields, record_type_id = [*self.adapter_class.list_fields(resource).values()]
        if fields and record_type_id:
            self.default_record_id = record_type_id
            current_record_ids = self.default_record_ids if self.default_record_ids else {}
            current_record_ids[resource] = record_type_id
            self.default_record_ids = current_record_ids
            self.save()
        return fields

    def get_validations(self, resource):
        rules = self.adapter_class.list_validations(resource)
        return rules

    def get_picklist_values(self, resource):
        values = self.adapter_class.list_picklist_values(resource)
        return values

    def get_deal_stages(self, resource):
        values = self.adapter_class.list_deal_stages(resource)
        return values["results"]

    def list_resource_data(self, resource, *args, **kwargs):
        attempts = 1
        while True:
            try:
                return self.adapter_class.list_resource_data(resource, *args, **kwargs)

            except InvalidFieldError as e:
                # catch all invalid fields on sync remove them from self and retry up to 20 times
                # this is done here rather than on the bg task to make it task agnostic
                # re raise the error for the decorator on the bg tasks to catch as well
                if attempts < 20:
                    attempts += 1
                    # remove the field from self
                    # get the field and make it into a string
                    try:
                        field_str = e.args[0].replace("'", "")
                        fields = self.object_fields.filter(hubspot_object=resource, name=field_str)
                        if fields.count():
                            fields.delete()
                        exclude_fields = self.exclude_fields if not None else {}
                        # add field to exclude fields for next sync
                        exclude_fields[resource] = [*exclude_fields.get(resource, []), field_str]
                        self.exclude_fields = exclude_fields
                        self.save()

                    except IndexError:
                        logger.exception(f"failed to parse invalid field {e}")
                        raise e
                else:
                    logger.exception(
                        f"Too many invalid fields for query, retry was ended at {attempts} for user {self.user.email} with id {self.user.id} current field {e}"
                    )
                    # re raise error for bg task to also handle
                    raise e
            except TokenExpired:
                if attempts >= 5:
                    return logger.exception(
                        f"Failed to retrieve resource data for user {str(self.user.id)}-{self.user.email} after {attempts} tries"
                    )
                else:
                    self.regenerate_token()
                    attempts += 1
        return

    def get_stage_picklist_values(self, resource):
        values = self.adapter_class.get_stage_picklist_values(resource)
        return values

    def get_individual_picklist_values(self, resource, field=None):
        attempts = 1
        while True:
            try:
                values = self.adapter_class.get_individual_picklist_values(
                    resource, field_name=field
                )
                break
            except TokenExpired:
                if attempts >= 5:
                    return logger.exception(
                        f"Failed to retrieve picklist values data for user {str(self.user.id)}-{self.user.email} after {attempts} tries"
                    )
                else:
                    self.regenerate_token()
                    attempts += 1

        return values

    def save(self, *args, **kwargs):
        return super(HubspotAuthAccount, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        from managr.crm.models import BaseOpportunity, ObjectField, BaseAccount, BaseContact

        self.user.crm = None
        self.user.save()
        fields = ObjectField.objects.filter(user=self.user)
        fields.delete()
        opps = BaseOpportunity.objects.filter(owner=self.user)
        opps.delete()
        accounts = BaseAccount.objects.filter(owner=self.user)
        accounts.delete()
        contacts = BaseContact.objects.filter(owner=self.user)
        contacts.delete()
        if self.user.is_team_lead:
            self.user.team.team_forms.all().delete()
        return super().delete(*args, **kwargs)


class CompanyQuerySet(models.QuerySet):
    def for_user(self, user):
        if user.organization and user.is_active:
            if user.user_level in ["SDR", "MANAGER"]:
                return self.filter(organization=user.organization)
            else:
                return self.filter(organization=user.organization, owner=user)
        else:
            return None


class Company(TimeStampModel, IntegrationModel):
    """
    Accounts are potential and exisiting clients that
    can be made into leads and added to lists

    """

    name = models.CharField(max_length=255)
    organization = models.ForeignKey(
        "organization.Organization", related_name="companies", on_delete=models.CASCADE,
    )
    owner = models.ForeignKey(
        "core.User", on_delete=models.CASCADE, related_name="companies", blank=True, null=True
    )
    external_owner = models.CharField(max_length=255, blank=True)
    secondary_data = JSONField(
        default=dict,
        null=True,
        help_text="All non primary fields that are on the model each org may have its own",
        max_length=500,
    )
    objects = CompanyQuerySet.as_manager()

    def __str__(self):
        return f"{self.name} {self.organization}"

    class Meta:
        ordering = ["-datetime_created"]


class DealQuerySet(models.QuerySet):
    def for_user(self, user):
        if user.organization and user.is_active:
            if user.user_level in ["SDR", "MANAGER"]:
                return self.filter(organization=user.organization)
            else:
                return self.filter(organization=user.organization, owner=user)
        else:
            return None


class Deal(TimeStampModel, IntegrationModel):
    name = models.CharField(max_length=255, blank=True, null=False)
    amount = models.DecimalField(max_digits=30, decimal_places=15, default=0.00, null=True,)
    forecast_category = models.CharField(max_length=255, null=True)

    close_date = models.DateField(null=True)

    company = models.CharField(max_length=255, blank=True, help_text="Retrieved from Integration")
    contacts = models.ManyToManyField("HubspotContact", related_name="contacts", blank=True)
    external_company = models.CharField(
        max_length=255, blank=True, help_text="value from the integration"
    )

    external_owner = models.CharField(
        max_length=255, blank=True, help_text="value from the integration"
    )

    owner = models.ForeignKey(
        "core.User", related_name="owned_deals", on_delete=models.SET_NULL, blank=True, null=True,
    )
    stage = models.CharField(max_length=255, null=True)
    company = models.ForeignKey(
        "Company", related_name="companies", on_delete=models.SET_NULL, blank=True, null=True,
    )
    is_stale = models.BooleanField(default=False)
    secondary_data = JSONField(
        default=dict,
        null=True,
        help_text="All non primary fields that are on the model each org may have its own",
        max_length=500,
    )
    reference_data = ArrayField(
        JSONField(max_length=128, default=dict),
        default=list,
        blank=True,
        help_text="An array of objects containing the API Name references and values for displaying",
    )
    objects = DealQuerySet.as_manager()

    class Meta:
        ordering = ["-datetime_created"]

    @property
    def adapter_class(self):
        data = self.__dict__
        data["id"] = str(data.get("id"))
        return DealAdapter(**data)

    @property
    def as_slack_option(self):
        return block_builders.option(self.name, str(self.id))

    def get_current_values(self):
        return self

    def get_deal_stage_options(self, access_token):
        res = self.adapter_class.get_deal_stage_options(access_token)
        stages = [{"label": stage["label"], "value": stage["label"]} for stage in res["stages"]]
        return stages


class HubspotContactQuerySet(models.QuerySet):
    def for_user(self, user):
        if user.organization and user.is_active:
            if user.user_level in ["SDR", "MANAGER"]:
                return self.filter(organization=user.organization)
            else:
                return self.filter(organization=user.organization, owner=user)
        else:
            return None


class HubspotContact(TimeStampModel, IntegrationModel):

    email = models.CharField(max_length=255, blank=True)
    owner = models.ForeignKey(
        "core.User",
        on_delete=models.CASCADE,
        related_name="hubspot_contacts",
        blank=True,
        null=True,
    )
    company = models.ForeignKey(
        "Company", on_delete=models.SET_NULL, related_name="contacts", null=True, blank=True,
    )
    external_owner = models.CharField(max_length=255, blank=True)
    external_company = models.CharField(max_length=255, blank=True)
    secondary_data = JSONField(
        default=dict,
        null=True,
        help_text="All non primary fields that are on the model each org may have its own",
        max_length=500,
    )
    objects = HubspotContactQuerySet.as_manager()

    class Meta:
        ordering = ["-datetime_created"]


class HObjectFieldQuerySet(models.QuerySet):
    def for_user(self, user):
        if user.organization and user.is_active:
            return self.filter(hubspot_account__user__id=user.id, is_public=False)
        else:
            return self.none()

    def for_form_template(self, user, form_id=None):
        if form_id:
            # get the type and resource
            # get the fields
            return self.for_user(user)

        return self.none()


class HObjectField(TimeStampModel, IntegrationModel):
    hubspot_account = models.ForeignKey(
        "HubspotAuthAccount", on_delete=models.CASCADE, related_name="hubspot_fields", null=True,
    )
    hubspot_object = models.CharField(max_length=255, null=True)
    name = models.CharField(max_length=255)
    label = models.CharField(max_length=255)
    type = models.CharField(max_length=255)
    field_type = models.CharField(max_length=255)
    calculated = models.BooleanField(default=False)
    external_options = models.BooleanField(default=False)
    has_unique_value = models.BooleanField(default=False)
    hidden = models.BooleanField(default=False)
    archived = models.BooleanField(default=False)
    display_value = models.TextField(blank=True, null=True)
    group_name = models.CharField(max_length=255, null=True, blank=True)
    options = ArrayField(
        JSONField(max_length=255, blank=True, null=True, default=dict), default=list, blank=True,
    )
    display_order = models.IntegerField(default=0)
    hubspot_defined = models.BooleanField(default=False, null=True)
    modification_metadata = JSONField(blank=True, null=True, default=dict)
    form_field = models.BooleanField(default=False)
    is_public = models.BooleanField(
        default=False,
        help_text="Indicates whether or not this is a managr_created field that is not part of the user's object fields",
    )
    objects = HObjectFieldQuerySet.as_manager()

    def __str__(self):
        return f"{self.label} {self.hubspot_account} {self.hubspot_object}"

    @property
    def get_slack_options(self):
        # non sf fields are created with is_public = True and may take options directly
        if self.is_public and len(self.options):

            return list(
                map(
                    lambda option: block_builders.option(option["label"], option["value"]),
                    self.options,
                )
            )
        elif not self.is_public and len(self.options):
            return list(
                map(
                    lambda option: block_builders.option(option["label"], option["value"]),
                    self.options,
                )
            )
        else:
            return [block_builders.option("No Options", "None")]

    def to_slack_field(self, value=None, *args, **kwargs):
        if self.field_type == "radio":
            # stage has a special function so we add the action param can only use one action_id so serving this statically for now
            action_id = None
            if self.name == "dealstage":
                initial_option = None
                if value:
                    initial_option = dict(
                        *map(
                            lambda value: block_builders.option(
                                value["text"]["text"], value["value"]
                            ),
                            filter(
                                lambda opt: opt.get("value", None) == value, self.get_slack_options,
                            ),
                        )
                    )
                user_id = str(self.hubspot_account.user.id)
                action_query = f"{slack_consts.GET_DEAL_STAGE_OPTIONS}?u={user_id}&field={str(self.id)}&resource_id={kwargs.get('resource_id')}"
                block = block_builders.external_select(
                    f"*{self.label}*",
                    action_query,
                    block_id=self.name,
                    initial_option=initial_option,
                )
            elif self.is_public:
                block = block_builders.static_select(
                    f"*{self.label}*",
                    self.get_slack_options,
                    initial_option=dict(
                        *map(
                            lambda value: block_builders.option(
                                value["text"]["text"], value["value"]
                            ),
                            filter(
                                lambda opt: opt.get("value", None) == value, self.get_slack_options,
                            ),
                        ),
                    ),
                    block_id=self.name,
                )

            else:
                initial_option = None
                if value:
                    initial_option = dict(
                        *map(
                            lambda value: block_builders.option(
                                value["text"]["text"], value["value"]
                            ),
                            filter(
                                lambda opt: opt.get("value", None) == value, self.get_slack_options,
                            ),
                        )
                    )
                user_id = str(self.salesforce_account.user.id)
                action_query = (
                    f"{slack_consts.GET_PICKLIST_OPTIONS}?u={user_id}&field={str(self.id)}"
                )
                block = block_builders.external_select(
                    f"*{self.label}*",
                    action_query,
                    block_id=self.name,
                    initial_option=initial_option,
                )

            return block

        elif self.field_type == "Reference":
            # temporarily using id as display value need to sync display value as part of data
            display_name = self.label
            initial_option = block_builders.option(value, value) if value else None
            if self.is_public and not self.allow_multiple:
                user_id = str(kwargs.get("user").id)
                resource = self.relationship_name
                action_query = (
                    f"{slack_consts.GET_LOCAL_RESOURCE_OPTIONS}?u={user_id}&resource={resource}"
                )
            elif self.is_public and self.allow_multiple:
                user_id = str(kwargs.get("user").id)
                resource = self.relationship_name
                action_query = f"{slack_consts.GET_LOCAL_RESOURCE_OPTIONS}?u={user_id}&resource={resource}&field_id={self.id}"
                return block_builders.multi_external_select(
                    f"_{self.label}_", action_query, block_id=self.name, initial_options=None,
                )
            else:
                user_id = str(self.salesforce_account.user.id)
                action_query = f"{slack_consts.GET_EXTERNAL_RELATIONSHIP_OPTIONS}?u={user_id}&relationship={self.display_value_keys['name']}&fields={','.join(self.display_value_keys['name_fields'])}"
            return block_builders.external_select(
                f"*{display_name}*",
                action_query,
                block_id=self.name,
                initial_option=initial_option,
            )

        elif self.field_type == "date":
            return block_builders.datepicker(
                label=f"*{self.label}*", initial_date=value, block_id=self.name,
            )

        elif self.field_type == "select":
            initial_options = None
            if value:
                initial_options = list(
                    filter(
                        lambda opt: opt.get("value", None) in value.split(";"),
                        self.get_slack_options,
                    )
                )
            user_id = str(self.hubspot_account.user.id)
            action_query = f"{slack_consts.GET_PICKLIST_OPTIONS}?u={user_id}&field={str(self.id)}"
            return block_builders.multi_external_select(
                f"*{self.label}*",
                action_query,
                initial_options=initial_options,
                block_id=self.name,
            )

        elif self.field_type == "checkbox":
            return block_builders.checkbox_block(
                " ",
                [block_builders.option(self.label, "true")],
                action_id=self.name,
                block_id=self.name,
            )
        elif self.field_type == "MultiChannelsSelect":
            return [
                block_builders.multi_channels_select_block(
                    section_text=f"_{self.label}_", initial_channels=value, block_id=self.name
                ),
                block_builders.context_block("Please add @managr to channel for access"),
            ]
        elif self.field_type == "MultiConversationsSelect":
            return [
                block_builders.multi_conversations_select_block(
                    section_text=f"_{self.label}_",
                    initial_conversations=value,
                    filter_opts={"include": ["private", "public"]},
                    block_id=self.name,
                ),
                block_builders.context_block("Please add @managr to channel for access"),
            ]
        else:
            if self.field_type == "DateTime":
                # currently we do not support date time instead make it into text field with format as placeholder
                return block_builders.input_block(
                    self.label,
                    multiline=False,
                    optional=True,
                    initial_value=value,
                    block_id=self.name,
                    placeholder="MM-DD-YYYY HH:MM AM/PM",
                )

            if self.field_type == "String" and self.length >= 250 or self.field_type == "TextArea":
                # set these fields to be multiline

                return block_builders.input_block(
                    self.label,
                    multiline=True,
                    optional=True,
                    initial_value=value,
                    block_id=self.name,
                )

            return block_builders.input_block(
                self.label, optional=True, initial_value=value, block_id=self.name,
            )

