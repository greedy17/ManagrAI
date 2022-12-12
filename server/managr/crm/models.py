import pytz
from datetime import datetime
from django.db import models
from managr.core.models import TimeStampModel, IntegrationModel
from django.contrib.postgres.fields import JSONField, ArrayField
from managr.slack.helpers import block_builders
from managr.core.models import User
from managr.crm.routes import adapter_routes as adapters
from managr.crm.routes import model_routes
from managr.crm import constants as crm_consts
from managr.slack import constants as slack_consts

# Create your models here.
class BaseAccountQuerySet(models.QuerySet):
    def for_user(self, user):
        if user.organization and user.is_active:
            if user.user_level in ["SDR", "MANAGER"]:
                return self.filter(organization=user.organization, integration_source=user.crm)
            else:
                return self.filter(
                    organization=user.organization, owner=user, integration_source=user.crm
                )
        else:
            return None


class BaseAccount(TimeStampModel, IntegrationModel):
    name = models.CharField(max_length=255)
    organization = models.ForeignKey(
        "organization.Organization", related_name="base_accounts", on_delete=models.CASCADE,
    )
    owner = models.ForeignKey(
        "core.User", on_delete=models.CASCADE, related_name="base_accounts", blank=True, null=True
    )
    external_owner = models.CharField(max_length=255, blank=True)
    secondary_data = JSONField(
        default=dict,
        null=True,
        help_text="All non primary fields that are on the model each org may have its own",
        max_length=500,
    )
    objects = BaseAccountQuerySet.as_manager()

    def __str__(self):
        return f"{self.name} {self.organization}"

    class Meta:
        ordering = ["-datetime_created"]

    @property
    def as_slack_option(self):
        return block_builders.option(self.name, str(self.id))

    @property
    def object_type(self):
        if self.owner.crm == "SALESFORCE":
            return "Account"
        else:
            return "Company"

    @property
    def adapter_class(self):
        data = self.__dict__
        data["id"] = str(data["id"])
        data["owner"] = str(self.owner.id) if self.owner else None
        resource = "Account" if self.integration_source == "SALESFORCE" else "Company"
        return adapters[self.integration_source][resource](**data)

    def get_current_values(self):
        if self.owner.crm == "SALESFORCE":
            return self.adapter_class.get_current_values(
                self.integration_id,
                self.owner.crm_account.access_token,
                self.owner.crm_account.instance_url,
                str(self.owner.id),
            )
        return self.adapter_class.get_current_values()

    def update(self, data):
        token = self.owner.crm_account.access_token
        custom_base = (
            self.owner.salesforce_account.instance_url if self.owner.crm == "SALESFORCE" else None
        )
        object_fields = self.owner.object_fields.filter(crm_object=self.object_type).values_list(
            "api_name", flat=True
        )
        res = self.adapter_class.update(
            data, token, self.integration_id, object_fields, custom_base
        )
        self.is_stale = True
        self.save()
        return res

    @staticmethod
    def create(data, user_id, resource_type):
        user = User.objects.get(id=user_id)
        token = user.crm_account.access_token
        object_fields = user.object_fields.filter(crm_object=resource_type).values_list(
            "api_name", flat=True
        )
        res = adapters[user.crm][resource_type].create(data, token, object_fields)
        serializer = model_routes(user.crm)[resource_type]["serializer"](data=res.as_dict)
        serializer.is_valid()
        serializer.save()
        return serializer.instance

    def update_database_values(self, data):
        data.pop("meeting_comments", None)
        data.pop("meeting_type", None)
        self.secondary_data.update(data)
        return self.save()


class BaseOpportunityQuerySet(models.QuerySet):
    def for_user(self, user):
        if user.organization and user.is_active:
            if user.user_level in ["SDR", "MANAGER"]:
                return self.filter(
                    owner__organization=user.organization, integration_source=user.crm
                )
            else:
                return self.filter(
                    owner__organization=user.organization, owner=user, integration_source=user.crm
                )
        else:
            return None


class BaseOpportunity(TimeStampModel, IntegrationModel):
    name = models.CharField(max_length=255, blank=True, null=False)
    amount = models.DecimalField(max_digits=30, decimal_places=15, default=0.00, null=True,)
    forecast_category = models.CharField(max_length=255, null=True)
    close_date = models.DateField(null=True)
    account = models.ForeignKey(
        "BaseAccount",
        related_name="opportunities",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    contacts = models.ManyToManyField("BaseContact", related_name="opportunities", blank=True)
    external_account = models.CharField(
        max_length=255, blank=True, help_text="value from the integration"
    )
    external_owner = models.CharField(
        max_length=255, blank=True, help_text="value from the integration"
    )

    owner = models.ForeignKey(
        "core.User",
        related_name="base_opportunities",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    stage = models.CharField(max_length=255, null=True)
    is_stale = models.BooleanField(default=False)
    secondary_data = JSONField(
        default=dict,
        null=True,
        help_text="All non primary fields that are on the model each org may have its own",
        max_length=500,
    )
    objects = BaseOpportunityQuerySet.as_manager()

    def __str__(self):
        return f"{self.name} {self.stage}"

    class Meta:
        ordering = ["-datetime_created"]

    @property
    def object_type(self):
        if self.owner is None:
            return None
        if self.owner.crm == "SALESFORCE":
            return "Opportunity"
        else:
            return "Deal"

    @property
    def adapter_class(self):
        data = self.__dict__
        data["id"] = str(data["id"])
        data["owner"] = str(self.owner.id)
        resource = "Opportunity" if self.owner.crm == "SALESFORCE" else "Deal"
        return adapters[self.integration_source][resource](**data)

    @property
    def as_slack_option(self):
        return block_builders.option(self.name, str(self.id))

    def get_current_values(self):
        if self.owner.crm == "SALESFORCE":
            return self.adapter_class.get_current_values(
                self.integration_id,
                self.owner.crm_account.access_token,
                self.owner.crm_account.instance_url,
                str(self.owner.id),
            )
        return self.adapter_class.get_current_values()

    def update(self, data):
        token = self.owner.crm_account.access_token
        custom_base = (
            self.owner.salesforce_account.instance_url if self.owner.crm == "SALESFORCE" else None
        )
        object_fields = self.owner.object_fields.filter(crm_object=self.object_type).values_list(
            "api_name", flat=True
        )
        res = self.adapter_class.update(
            data, token, self.integration_id, object_fields, custom_base
        )
        self.is_stale = True
        self.save()
        return res

    @staticmethod
    def create(data, user_id, resource_type):
        user = User.objects.get(id=user_id)
        token = user.crm_account.access_token
        object_fields = user.object_fields.filter(crm_object=resource_type).values_list(
            "api_name", flat=True
        )
        res = adapters[user.crm][resource_type].create(
            data, token, object_fields, user_id, user.crm_account.instance_url
        )
        serializer = model_routes(user.crm)[resource_type]["serializer"](data=res.as_dict)
        serializer.is_valid()
        serializer.save()
        return serializer.instance

    def update_database_values(self, data):
        data.pop("meeting_comments", None)
        data.pop("meeting_type", None)
        self.secondary_data.update(data)
        return self.save()

    def add_contact_role(self, access_token, base_url, contact_integration_id):

        return self.adapter_class.add_contact_role(
            access_token, base_url, contact_integration_id, self.integration_id
        )


class BaseContactQuerySet(models.QuerySet):
    def for_user(self, user):
        if user.organization and user.is_active:
            if user.user_level in ["SDR", "MANAGER"]:
                return self.filter(owner__organization=user.organization)
            else:
                return self.filter(owner=user)
        else:
            return None


class BaseContact(TimeStampModel, IntegrationModel):
    email = models.CharField(max_length=255, blank=True)
    owner = models.ForeignKey(
        "core.User", on_delete=models.CASCADE, related_name="base_contacts", blank=True, null=True
    )
    account = models.ForeignKey(
        "BaseAccount", on_delete=models.SET_NULL, related_name="contacts", null=True, blank=True,
    )
    external_owner = models.CharField(max_length=255, blank=True)
    external_account = models.CharField(max_length=255, blank=True)
    secondary_data = JSONField(
        default=dict,
        null=True,
        help_text="All non primary fields that are on the model each org may have its own",
        max_length=500,
    )
    objects = BaseContactQuerySet.as_manager()

    class Meta:
        ordering = ["-datetime_created"]

    @property
    def object_type(self):
        return "Contact"

    @property
    def name(self):
        """returns full name for use with blocksets"""
        email = self.email if self.email else "N/A"
        return email

    @property
    def adapter_class(self):
        data = self.__dict__
        data["id"] = str(data["id"])
        data["owner"] = str(self.owner.id)
        return adapters[self.integration_source]["Contact"](**data)

    @property
    def as_slack_option(self):
        return block_builders.option(self.email, str(self.id))

    def get_current_values(self):
        if self.owner.crm == "SALESFORCE":
            return self.adapter_class.get_current_values(
                self.integration_id,
                self.owner.crm_account.access_token,
                self.owner.crm_account.instance_url,
                str(self.owner.id),
            )
        return self.adapter_class.get_current_values()

    def update(self, data):
        token = self.owner.crm_account.access_token
        custom_base = (
            self.owner.salesforce_account.instance_url if self.owner.crm == "SALESFORCE" else None
        )
        object_fields = self.owner.object_fields.filter(crm_object=self.object_type).values_list(
            "api_name", flat=True
        )
        res = self.adapter_class.update(
            data, token, self.integration_id, object_fields, custom_base
        )
        self.is_stale = True
        self.save()
        return res

    @staticmethod
    def create(data, user_id, resource_type):
        user = User.objects.get(id=user_id)
        token = user.crm_account.access_token
        object_fields = user.object_fields.filter(crm_object=resource_type).values_list(
            "api_name", flat=True
        )
        res = adapters[user.crm][resource_type].create(data, token, object_fields)
        serializer = model_routes(user.crm)[resource_type]["serializer"](data=res.as_dict)
        serializer.is_valid()
        serializer.save()
        return serializer.instance

    def update_database_values(self, data):
        data.pop("meeting_comments", None)
        data.pop("meeting_type", None)
        self.secondary_data.update(data)
        return self.save()


class ObjectFieldQuerySet(models.QuerySet):
    def for_user(self, user):
        if user.organization and user.is_active:
            if user.user_level in ["SDR", "MANAGER"]:
                return self.filter(user=user)
            else:
                return self.filter(user=user)
        else:
            return None


class ObjectField(TimeStampModel, IntegrationModel):
    user = models.ForeignKey(
        "core.User", on_delete=models.CASCADE, related_name="object_fields", null=True
    )
    crm_object = models.CharField(max_length=255, null=True)
    api_name = models.CharField(max_length=255)
    createable = models.BooleanField(default=False)
    updateable = models.BooleanField(default=False)
    required = models.BooleanField(default=False)
    data_type = models.CharField(max_length=255)
    display_value = models.CharField(
        max_length=255,
        blank=True,
        help_text="if this is a reference field we save the display value as well",
    )
    label = models.CharField(max_length=255)
    reference = models.BooleanField(default=False)
    relationship_name = models.CharField(max_length=255, null=True)
    length = models.PositiveIntegerField(default=0)
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
    filterable = models.BooleanField(
        default=False, help_text="Indicates if we can filter queries against this field"
    )
    objects = ObjectFieldQuerySet.as_manager()

    def __str__(self):
        return f"{self.label} {self.api_name}"

    @property
    def display_value_keys(self):
        """helper getter to retrieve related name display keys"""
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
    def reference_display_label(self):
        """returns the reference object's name as a display label"""

        if (
            self.data_type == "Reference"
            and self.reference
            and self.relationship_name
            and not self.is_public
        ):
            return self.relationship_name
        return self.label

    def to_slack_field(self, value=None, *args, **kwargs):
        print(self.data_type)
        print(value)
        if self.data_type == "Picklist":
            # stage has a special function so we add the action param can only use one action_id so serving this statically for now
            action_id = None
            if self.api_name in ["StageName", "dealstage"]:
                if self.api_name == "dealstage":
                    resource_id = kwargs.get("resource_id", None)
                    pipeline_id = kwargs.get("pipeline_id", None)
                    if resource_id or pipeline_id:
                        pipeline = pipeline_id
                        if resource_id:
                            resource = BaseOpportunity.objects.get(id=resource_id)
                            pipeline = resource.secondary_data["pipeline"]
                        stages = self.options[0].get(pipeline)["stages"]
                        stage_options = list(
                            map(
                                lambda option: block_builders.option(option["label"], option["id"]),
                                stages,
                            )
                        )
                        options = stage_options
                    else:
                        options = [block_builders.option("None", "None")]
                else:
                    options = self.get_slack_options
                initial_option = dict(
                    *map(
                        lambda value: block_builders.option(value["text"]["text"], value["value"]),
                        filter(lambda opt: opt.get("value", None) == value, options,),
                    ),
                )

                block = block_builders.static_select(
                    f"*{self.reference_display_label}*",
                    options,
                    action_id=action_id,
                    initial_option=initial_option,
                    block_id=self.api_name,
                )
            elif self.is_public:
                block = block_builders.static_select(
                    f"*{self.reference_display_label}*",
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
                    block_id=self.api_name,
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
                user_id = str(self.user.id)
                action_query = (
                    f"{slack_consts.GET_PICKLIST_OPTIONS}?u={user_id}&field={str(self.id)}"
                )
                block = block_builders.external_select(
                    f"*{self.reference_display_label}*",
                    action_query,
                    block_id=self.api_name,
                    initial_option=initial_option,
                )
            return block

        elif self.data_type == "Reference":
            # temporarily using id as display value need to sync display value as part of data
            display_name = (
                self.reference_display_label
                if self.integration_source == "SALESFORCE"
                else self.label
            )
            initial_option = block_builders.option(value, value) if value else None
            if self.is_public and not self.allow_multiple:
                user_id = str(kwargs.get("user").id)
                resource = self.relationship_name
                action_query = f"{slack_consts.GET_LOCAL_RESOURCE_OPTIONS}?u={user_id}&resource_type={resource}"
            elif self.is_public and self.allow_multiple:
                user_id = str(kwargs.get("user").id)
                resource = self.relationship_name
                action_query = f"{slack_consts.GET_LOCAL_RESOURCE_OPTIONS}?u={user_id}&resource_type={resource}&field_id={self.id}"
                return block_builders.multi_external_select(
                    f"_{self.reference_display_label}_",
                    action_query,
                    block_id=self.api_name,
                    initial_options=None,
                )
            # elif (
            #     self.api_name == "PricebookEntryId"
            #     and self.salesforce_object == "OpportunityLineItem"
            # ):
            #     user_id = str(kwargs.get("user").id)
            #     resource = self.relationship_name
            #     action_query = f"{slack_consts.GET_LOCAL_RESOURCE_OPTIONS}?u={user_id}&resource_type={resource}&field_id={self.id}&pricebook={kwargs.get('Pricebook2Id')}"
            #     return block_builders.external_select(
            #         "*Products*", action_query, block_id=self.api_name, initial_option=None,
            #     )
            else:
                if self.api_name == "PricebookEntryId":
                    display_name = "Products"
                additional_fields = kwargs.get("fields", "")
                user_id = str(self.user.id)
                action_query = f"{slack_consts.GET_EXTERNAL_RELATIONSHIP_OPTIONS}?u={user_id}&relationship={self.display_value_keys['api_name']}&fields={','.join(self.display_value_keys['name_fields'])}&resource={self.crm_object}&add={additional_fields}"
            return block_builders.external_select(
                f"*{display_name}*",
                action_query,
                block_id=self.api_name,
                initial_option=initial_option,
            )

        elif self.data_type == "Date":
            if self.user.crm == "HUBSPOT" and value is not None:
                try:
                    date_value = str(datetime.strptime(value, "%Y-%m-%dT%H:%M:%S%z").date())
                except ValueError:
                    try:
                        date_value = str(datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%f%z").date())
                    except ValueError:
                        date_value = value
            else:
                date_value = value
            return block_builders.datepicker(
                label=f"*{self.reference_display_label}*",
                initial_date=date_value,
                block_id=self.api_name,
            )

        elif self.data_type == "MultiPicklist":
            initial_options = None
            if value:
                initial_options = list(
                    filter(
                        lambda opt: opt.get("value", None) in value.split(";"),
                        self.get_slack_options,
                    )
                )
            user_id = str(self.user.id)
            action_query = f"{slack_consts.GET_PICKLIST_OPTIONS}?u={user_id}&field={str(self.id)}"
            return block_builders.multi_external_select(
                f"*{self.reference_display_label}*",
                action_query,
                initial_options=initial_options,
                block_id=self.api_name,
            )

        elif self.data_type == "Boolean":
            initial_value = (
                [block_builders.option(self.reference_display_label, "true")]
                if value is True
                else None
            )
            return block_builders.checkbox_block(
                " ",
                [block_builders.option(self.reference_display_label, "true")],
                action_id=self.api_name,
                block_id=self.api_name,
                initial_options=initial_value,
            )
        elif self.data_type == "MultiChannelsSelect":
            return [
                block_builders.multi_channels_select_block(
                    section_text=f"_{self.label}_", initial_channels=value, block_id=self.api_name
                ),
                block_builders.context_block("Please add @managr to channel for access"),
            ]
        elif self.data_type == "MultiConversationsSelect":
            return [
                block_builders.multi_conversations_select_block(
                    section_text=f"_{self.label}_",
                    initial_conversations=value,
                    filter_opts={"include": ["private", "public"]},
                    block_id=self.api_name,
                ),
                block_builders.context_block("Please add @managr to channel for access"),
            ]
        else:
            if self.data_type == "DateTime":
                # currently we do not support date time instead make it into text field with format as placeholder
                return block_builders.input_block(
                    self.reference_display_label,
                    multiline=False,
                    optional=not self.required,
                    initial_value=value,
                    block_id=self.api_name,
                    placeholder="MM-DD-YYYY HH:MM AM/PM",
                )

            if self.data_type == "String" and self.length >= 250 or self.data_type == "TextArea":
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

            # use this one.

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
        elif not self.is_public and hasattr(self, "crm_picklist_options"):
            return self.crm_picklist_options.as_slack_options
        elif self.user.crm == "HUBSPOT":
            if self.api_name == "dealstage":
                return list(
                    map(
                        lambda option: block_builders.option(option["label"], option["id"]),
                        self.options,
                    )
                )
            return list(
                map(
                    lambda option: block_builders.option(option["label"], option["value"]),
                    self.options,
                )
            )
        else:
            return [block_builders.option("No Options", "None")]

