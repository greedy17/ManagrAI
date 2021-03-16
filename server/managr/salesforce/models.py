import jwt
import pytz
import math
import logging

from functools import reduce

from datetime import datetime
from django.db import models
from django.utils import timezone

from django.contrib.postgres.fields import JSONField, ArrayField
from django.db.models import Q

from managr.core import constants as core_consts
from managr.core.models import TimeStampModel, IntegrationModel
from managr.slack.helpers import block_builders
from managr.slack import constants as slack_consts


from .adapter.models import SalesforceAuthAccountAdapter, OpportunityAdapter
from .adapter.exceptions import TokenExpired
from . import constants as sf_consts

logger = logging.getLogger("managr")


class ArrayLength(models.Func):
    function = "CARDINALITY"


class SObjectFieldQuerySet(models.QuerySet):
    def for_user(self, user):
        if user.organization and user.is_active:
            return self.filter(
                salesforce_account__user__organization__id=user.organization_id, is_public=False
            )
        else:
            return self.none()

    def for_form_template(self, user, form_id=None):
        if form_id:
            # get the type and resource
            # get the fields
            return self.for_user(user)

        return self.none()


class SObjectValidationQuerySet(models.QuerySet):
    def for_user(self, user):
        if user.organization and user.is_active:
            return self.filter(salesforce_account__user__organization__id=user.organization_id)
        else:
            return self.none()

    def for_sf_object(self, user, form_id=None):
        if form_id:
            # get the form
            # get the type and resource
            # get the fields
            return self.for_user(user)

        return self.none()


class SObjectPicklistQuerySet(models.QuerySet):
    def for_user(self, user):
        if user.organization and user.is_active:
            return self.filter(salesforce_account__user__organization__id=user.organization_id)
        else:
            return self.none()


class SObjectField(TimeStampModel, IntegrationModel):
    salesforce_account = models.ForeignKey(
        "salesforce.SalesforceAuthAccount",
        on_delete=models.CASCADE,
        related_name="object_fields",
        null=True,
    )
    salesforce_object = models.CharField(max_length=255, null=True)
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
    reference = models.BooleanField(default=False)
    relationship_name = models.CharField(max_length=255, null=True)
    reference_to_infos = ArrayField(
        JSONField(max_length=128, default=dict),
        default=list,
        blank=True,
        help_text="An of objects containing the API Name references",
    )
    options = ArrayField(
        JSONField(max_length=255, blank=True, null=True, default=dict),
        default=list,
        blank=True,
        help_text="if this is a custom managr field pass a dict of label, value, if this is not a custom managr field then construct the values dynamically",
    )
    is_public = models.BooleanField(
        default=False,
        help_text="Indicates whether or not this is a managr_created field that is not part of the user's object fields",
    )
    objects = SObjectFieldQuerySet.as_manager()

    def __str__(self):
        return f"{self.label} {self.salesforce_account} {self.salesforce_object}"

    @property
    def reference_display_label(self):
        """ returns the reference object's name as a display label """
        if self.data_type == "Reference" and self.reference:
            return self.relationship_name
        return self.label

    def to_slack_field(self, value=None, **kwargs):
        if self.data_type == "Picklist":
            # stage has a special function so we add the action param
            action_id = None
            if self.api_name == "StageName":
                action_id = (
                    slack_consts.ZOOM_MEETING__STAGE_SELECTED
                    + f"?w={str(kwargs.get('workflow').id)}"
                )

            block = block_builders.static_select(
                f"*{self.reference_display_label}*",
                self.get_slack_options,
                action_id=action_id,
                initial_option=dict(
                    *map(
                        lambda value: block_builders.option(value["text"]["text"], value["value"]),
                        filter(
                            lambda opt: opt.get("value", None) == value, self.get_slack_options,
                        ),
                    ),
                ),
                block_id=self.api_name,
            )
            return block

        elif self.data_type == "Reference":
            # temporarily using id as display value need to sync display value as part of data
            initial_option = block_builders.option(value, value) if value else None
            if self.is_public:
                user_id = str(kwargs.get("user").id)
                resource = self.relationship_name
                action_query = (
                    f"{slack_consts.GET_LOCAL_RESOURCE_OPTIONS}?u={user_id}&resource={resource}"
                )

            else:
                user_id = str(self.salesforce_account.user.id)
                action_query = f"{slack_consts.GET_EXTERNAL_RELATIONSHIP_OPTIONS}?u={user_id}&relationship={self.display_value_keys['api_name']}&fields={','.join(self.display_value_keys['name_fields'])}"
            return block_builders.external_select(
                f"*{self.reference_display_label}*",
                action_query,
                block_id=self.api_name,
                initial_option=initial_option,
            )

        elif self.data_type == "Date":
            return block_builders.datepicker(
                label=f"*{self.reference_display_label}*",
                initial_date=value,
                block_id=self.api_name,
            )

        elif self.data_type == "MultiPicklist":
            return block_builders.multi_static_select(
                f"*{self.reference_display_label}*",
                list(
                    map(
                        lambda value: block_builders.option(value["label"], value["value"]),
                        filter(
                            lambda opt: opt.get("value", None) == value, self.get_slack_options,
                        ),
                    ),
                ),
                initial_options=self.picklist_options.as_slack_options,
                block_id=self.api_name,
            )

        elif self.data_type == "Boolean":
            return block_builders.checkbox_block(
                " ",
                [block_builders.option(self.reference_display_label, "true")],
                action_id=self.api_name,
                block_id=self.api_name,
            )
        else:
            if self.data_type == "String" and self.length >= 250:
                # set these fields to be multiline

                return block_builders.input_block(
                    self.reference_display_label,
                    multiline=True,
                    optional=not self.required,
                    initial_value=value,
                    block_id=self.api_name,
                )

            return block_builders.input_block(
                self.reference_display_label,
                optional=not self.required,
                initial_value=value,
                block_id=self.api_name,
            )

    @property
    def display_value_keys(self):
        """ helper getter to retrieve related name display keys """
        if self.reference and len(self.reference_to_infos):
            # some fields are referenced to completely different objects (as in ReportsTo)
            items = dict(
                *filter(
                    lambda details: details["api_name"] == self.relationship_name,
                    self.reference_to_infos,
                ),
            )
            if not len(items):

                # arbitrarily chosing first option avaliable
                items = self.reference_to_infos[0]
            return items

        elif self.reference and not len(self.reference_to_infos):
            raise ValueError()

        return None

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
        elif not self.is_public and hasattr(self, "picklist_options"):
            return self.picklist_options.as_slack_options
        else:
            return None


class SObjectValidation(TimeStampModel, IntegrationModel):
    message = models.TextField(blank=True)
    description = models.TextField(blank=True)
    salesforce_object = models.CharField(max_length=255)
    salesforce_account = models.ForeignKey(
        "salesforce.SalesforceAuthAccount",
        on_delete=models.CASCADE,
        related_name="object_validations",
    )
    objects = SObjectValidationQuerySet.as_manager()

    def __str__(self):
        return f"{self.salesforce_account}-{self.salesforce_object}"


class SObjectPicklist(TimeStampModel, IntegrationModel):
    # label = models.CharField(blank=True, max_length=255)
    # attributes = JSONField(default=dict, max_length=255)

    # valid_for = models.CharField(blank=True, max_length=255)
    picklist_for = models.CharField(
        blank=True,
        max_length=255,
        help_text="the name of the field this picklist is for, serializer will translate to actual field",
    )
    # value = models.CharField(blank=True, max_length=255)
    values = ArrayField(
        JSONField(max_length=128, default=dict),
        default=list,
        blank=True,
        help_text="An array of objects containing the values",
    )
    salesforce_object = models.CharField(max_length=255)
    field = models.OneToOneField(
        "salesforce.SObjectField", on_delete=models.CASCADE, related_name="picklist_options"
    )

    salesforce_account = models.ForeignKey(
        "salesforce.SalesforceAuthAccount", on_delete=models.CASCADE, related_name="picklist_values"
    )
    objects = SObjectPicklistQuerySet.as_manager()

    def __str__(self):
        return f"{self.salesforce_account}-{self.picklist_for}"

    @property
    def as_slack_options(self):
        return list(
            map(lambda option: block_builders.option(option["label"], option["value"]), self.values)
        )


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
        models.CharField(max_length=255, blank=True),
        default=list,
        blank=True,
        help_text="List of failed tasks as that failed from task runner for uncaught exceptions after 5 tries",
    )

    @property
    def status(self):
        if not len(self.operations_list):
            return "No Operations"
        if len(self.operations_list) and not len(self.operations):
            return "Not Started"
        else:
            return "In Progress"

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

        return 0

    @property
    def in_progress(self):
        """ disable actions while in progress """
        return self.progress != 100

    def __str__(self):
        return f"{self.user.email} status: {self.status} tasks {self.progress}% complete"

    def remove_from_operations_list(self, operations=[]):
        """ This method is used to remove operations (array) from the NEXT sync """
        self.operations_list = list(filter(lambda opp: opp not in operations, self.operations_list))
        self.save()

    def begin_tasks(self, attempts=1):
        from managr.salesforce.background import emit_sf_sync

        sf_account = self.user.salesforce_account
        adapter = self.user.salesforce_account.adapter_class
        for key in self.operations_list:
            while True:
                try:
                    count = adapter.get_resource_count(key)["totalSize"]
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
            count = min(count, 10000)
            logger.info(f"{count} {key} {self.user.email}")
            for i in range(math.ceil(count / sf_consts.SALESFORCE_QUERY_LIMIT)):
                offset = sf_consts.SALESFORCE_QUERY_LIMIT * i
                limit = sf_consts.SALESFORCE_QUERY_LIMIT
                if offset > 2000:
                    # sf limit on offset for 2000 if it is greater than 2k
                    # we need to get the rest of the records
                    # log a warning this may fail
                    logger.warning(
                        f"offset for sync for user {self.user.email} with id {self.user.id} was over 2000"
                    )
                    offset = 2000
                    limit = count - offset

                t = emit_sf_sync(str(self.user.id), str(self.id), key, limit, offset)
                if self.operations:
                    self.operations.append(str(t.task_hash))
                else:
                    self.operations = [str(t.task_hash)]
                self.save()
                break

    def save(self, *args, **kwargs):
        from managr.salesforce.background import (
            emit_sf_sync,
            emit_gen_next_sync,
        )

        if self.progress == 100 and self.__class__.__name__ == "SFSyncOperation":
            logger.info("starting new process")
            scheduled_time = timezone.now() + timezone.timedelta(minutes=2.5)
            formatted_time = scheduled_time.strftime("%Y-%m-%dT%H:%M%Z")
            emit_gen_next_sync(str(self.user.id), self.operations_list, formatted_time)
        return super(SFSyncOperation, self).save(*args, **kwargs)


class SFObjectFieldsOperation(SFSyncOperation):
    """ May no Longer need to use this """

    @property
    def operations_map(self):
        from managr.salesforce.background import (
            emit_sync_sobject_fields,
            emit_sync_sobject_validations,
            emit_generate_form_template,
            emit_sync_sobject_picklist,
        )

        return {
            sf_consts.SALESFORCE_OBJECT_FIELDS: emit_sync_sobject_fields,
            sf_consts.SALESFORCE_VALIDATIONS: emit_sync_sobject_validations,
            sf_consts.SALESFORCE_PICKLIST_VALUES: emit_sync_sobject_picklist,
        }

    def begin_tasks(self, attempts=1):

        for op in self.operations_list:
            # split the operation to get opp and params
            operation_name, param = op.split(".")
            operation = self.operations_map.get(operation_name)

            # determine the operation and its param and get event emitter
            t = operation(str(self.user.id), str(self.id), param)
            if self.operations:
                self.operations.append(str(t.task_hash))
            else:
                self.operations = [str(t.task_hash)]
            self.save()

    def save(self, *args, **kwargs):
        # overriding to make sure super does not call parent

        logger.info(f"{self.progress}")
        if self.progress == 100 and self.__class__.__name__ == "SFObjectFieldsOperation":
            from managr.salesforce.background import emit_gen_next_object_field_sync

            logger.info("starting new process")
            scheduled_time = timezone.now() + timezone.timedelta(minutes=720)
            formatted_time = scheduled_time.strftime("%Y-%m-%dT%H:%M%Z")
            emit_gen_next_object_field_sync(str(self.user.id), self.operations_list, formatted_time)
        return super(SFObjectFieldsOperation, self).save(*args, **kwargs)


class MeetingWorkflow(SFSyncOperation):

    meeting = models.OneToOneField("zoom.ZoomMeeting", models.CASCADE, related_name="workflow")

    resource_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="The id of the related resource unopinionated",
    )
    resource_type = models.CharField(
        max_length=255, null=True, blank=True, help_text="The class name of the resource"
    )
    slack_view = models.CharField(
        blank=True,
        max_length=255,
        help_text="Id of slack view/modal, we will use this id to delete/update the form when using an async flow",
    )
    slack_interaction = models.CharField(
        blank=True,
        max_length=255,
        help_text="Id of current slack message interaction, we will use this id to delete/update the interaction with its status",
    )
    failed_task_description = ArrayField(
        models.CharField(max_length=255, blank=True),
        default=list,
        blank=True,
        help_text="list of dict failures",
    )

    class Meta:
        ordering = ["-datetime_created"]

    def __str__(self):
        meeting_name = self.meeting.topic if self.meeting else "No Meeting Topic"
        return f"{self.user.email}, {meeting_name}, for resource {self.resource_type} at progress {self.progress}"

    @property
    def resource(self):
        from managr.salesforce.routes import routes

        model_route = routes.get(self.resource_type, None)
        if model_route and self.resource_id:
            return model_route["model"].objects.get(id=self.resource_id)
        return None

    @property
    def operations_map(self):
        from managr.salesforce.background import (
            emit_add_call_to_sf,
            emit_update_contacts,
            emit_create_new_contacts,
            emit_sf_update_resource_from_meeting,
        )

        return {
            sf_consts.MEETING_REVIEW__UPDATE_RESOURCE: emit_sf_update_resource_from_meeting,
            sf_consts.MEETING_REVIEW__UPDATE_CONTACTS: emit_update_contacts,
            sf_consts.MEETING_REVIEW__CREATE_CONTACTS: emit_create_new_contacts,
            sf_consts.MEETING_REVIEW__SAVE_CALL_LOG: emit_add_call_to_sf,
        }

    def begin_tasks(self, attempts=1):

        for op in self.operations_list:
            # split the operation to get opp and params
            operation_name, param = op.split(".")
            operation = self.operations_map.get(operation_name)
            params = param.split(",")

            # determine the operation and its param and get event emitter
            t = operation(params[0], params[1:])
            if self.operations:
                self.operations.append(str(t.task_hash))
            else:
                self.operations = [str(t.task_hash)]
            self.save()

    def begin_communication(self, now=False):
        from managr.zoom.background import (
            emit_kick_off_slack_interaction,
            _kick_off_slack_interaction,
        )

        if self.resource and self.resource != slack_consts.FORM_RESOURCE_LEAD:
            self.add_form(self.resource_type, slack_consts.FORM_TYPE_MEETING_REVIEW)
        if not now:
            return emit_kick_off_slack_interaction(str(self.user.id), str(self.id))
            # used for testing a fake meeting
        return _kick_off_slack_interaction.now(str(self.user.id), str(self.id))

    def add_form(self, resource, form_type, **kwargs):
        """ 
            helper method to add form for the review 
            E.g Create form if creating new resource, stage gating form 
        """
        from managr.slack.models import OrgCustomSlackForm, OrgCustomSlackFormInstance

        template = (
            OrgCustomSlackForm.objects.for_user(self.user)
            .filter(
                Q(resource=resource, form_type=form_type,)
                & Q(Q(stage=kwargs.get("stage", None)) | Q(stage=kwargs.get("stage", "")))
            )
            .first()
        )
        if template:

            # check if a form with that template already exists and remove it
            self.forms.filter(template__id=template.id).delete()
            kwargs = dict(user=self.user, template=template, workflow=self,)
            if self.resource:
                kwargs["resource_id"] = str(self.resource.id)

            return OrgCustomSlackFormInstance.objects.create(**kwargs)
        return None

    def remove_form(self):
        """ helper method to remove for the review """
        return

    def save(self, *args, **kwargs):
        """ sets the loading to done """
        if self.progress == 100 and self.slack_interaction:
            from managr.slack.helpers import requests as slack_requests
            from managr.slack.helpers.block_sets import get_block_set

            block_set = [
                *get_block_set("final_meeting_interaction", {"w": str(self.id)}),
                get_block_set("create_meeting_task", {"w": str(self.id)}),
            ]

            if len(self.failed_task_description):
                for i, m in enumerate(self.failed_task_description):
                    block_set.insert(
                        i + 1, *get_block_set("error_message", {"message": f"{m}"}),
                    )

            slack_access_token = self.user.organization.slack_integration.access_token
            ts, channel = self.slack_interaction.split("|")
            res = slack_requests.update_channel_message(
                channel, ts, slack_access_token, block_set=block_set
            ).json()
            print(res)
            self.slack_interaction = f"{res['ts']}|{res['channel']}"
        return super(MeetingWorkflow, self).save(*args, **kwargs)


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
    sobjects = JSONField(
        default=dict, null=True, help_text="All resources we are retrieving", max_length=500,
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
        data["object_fields"] = dict(
            ## TODO: Use loop from sobjects
            Account=self.object_fields.filter(salesforce_object="Account").values_list(
                "api_name", flat=True
            ),
            Opportunity=self.object_fields.filter(salesforce_object="Opportunity").values_list(
                "api_name", flat=True
            ),
            Contact=self.object_fields.filter(salesforce_object="Contact").values_list(
                "api_name", flat=True
            ),
            Lead=self.object_fields.filter(salesforce_object="Lead").values_list(
                "api_name", flat=True
            ),
        )
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
        self.save()
        return fields

    def get_validations(self, resource):
        rules = self.adapter_class.list_validations(resource)
        return rules

    def get_picklist_values(self, resource):
        values = self.adapter_class.list_picklist_values(resource)
        return values

    def list_resource_data(self, resource, offset, *args, **kwargs):
        return self.adapter_class.list_resource_data(resource, offset, *args, **kwargs)

    def update_opportunity(self, data):
        return OpportunityAdapter.update_opportunity(data, self.access_token, self.instance_url)

    def save(self, *args, **kwargs):
        return super(SalesforceAuthAccount, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        return super().delete(*args, **kwargs)
