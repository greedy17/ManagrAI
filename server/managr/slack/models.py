import logging
from re import template
from django.conf import settings
from datetime import datetime
from django.db import models
from django.db.models.constraints import UniqueConstraint
from django.contrib.postgres.fields import JSONField, ArrayField
from django.db.models import Q
from django.forms import UUIDField

from managr.slack.helpers import block_builders

from managr.crm.exceptions import TokenExpired, InvalidRefreshToken
from managr.core import constants as core_consts
from . import constants as slack_consts

from managr.core.models import TimeStampModel

logger = logging.getLogger("managr")


class OrganizationSlackIntegrationQuerySet(models.QuerySet):
    def for_user(self, user):
        if user.is_superuser or user.is_serviceaccount:
            return self.all()
        elif user.organization and user.is_active:
            return self.filter(organization=user.organization_id)
        else:
            return self.none()


class OrganizationSlackIntegration(TimeStampModel):
    scope = models.CharField(
        max_length=255,
        null=False,
        help_text="permissions that the Managr Slack App has in the Organization's Slack Workspace",
    )
    organization = models.OneToOneField(
        "organization.Organization",
        related_name="slack_integration",
        blank=False,
        null=False,
        on_delete=models.CASCADE,
    )
    team_name = models.CharField(
        max_length=255, null=False, help_text="name of the Organization's Slack Team"
    )
    team_id = models.CharField(
        max_length=255, null=False, help_text="ID of the Organization's Slack Team"
    )
    bot_user_id = models.CharField(max_length=255, null=False, help_text="ID of the Managr Bot")
    access_token = models.CharField(
        max_length=255, null=True, blank=True, help_text="Slack API access token"
    )
    incoming_webhook = JSONField(
        default=dict,
        null=True,
        blank=True,
        help_text="data leveraged to post messages from external sources into Slack",
    )
    enterprise = JSONField(
        default=dict,
        null=True,
        blank=True,
        help_text="data on the Organization's Enterprise Slack Team, if any",
    )
    is_revoked = models.BooleanField(default=True)

    objects = OrganizationSlackIntegrationQuerySet.as_manager()

    def __str__(self):
        return f"{self.organization.name} - slack integration"

    class Meta:
        ordering = ["organization"]
        constraints = [UniqueConstraint(fields=["team_id"], name="unique_team_id")]

    def delete(self, *args, **kwargs):
        return super(OrganizationSlackIntegration, self).delete(*args, **kwargs)


class UserSlackIntegrationQuerySet(models.QuerySet):
    def for_user(self, user):
        if user.is_superuser or user.is_serviceaccount:
            return self.all()
        elif user.organization and user.is_active:
            return self.filter(user=user.id)
        else:
            return self.none()


class UserSlackIntegration(TimeStampModel):
    user = models.OneToOneField(
        "core.User",
        related_name="slack_integration",
        blank=False,
        null=False,
        on_delete=models.CASCADE,
    )
    slack_id = models.CharField(
        max_length=255, null=False, help_text="Slack ID of the User, for this workspace"
    )
    channel = models.CharField(
        max_length=255,
        null=True,
        help_text="Channel ID for the DM conversation between user and Managr bot",
    )
    organization_slack = models.ForeignKey(
        OrganizationSlackIntegration,
        on_delete=models.CASCADE,
        related_name="user_slack_integrations",
    )
    is_revoked = models.BooleanField(default=True)
    is_onboarded = models.BooleanField(
        default=False,
        help_text="When a user opens the home tab it will notifiy us (or messages tab) slack requires an 'onboarding' interaction to be sent, since this event is recurring we only do it once",
    )

    zoom_channel = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Channel for zoom automation, defaults to channel",
    )

    recap_channel = models.CharField(
        max_length=255, null=True, blank=True, help_text="Channel for recaps to be sent",
    )
    recap_receivers = ArrayField(
        models.CharField(max_length=255),
        default=list,
        blank=True,
        help_text="Manager's slack id's who want a recap from this user",
    )
    realtime_alert_configs = JSONField(
        default=dict, help_text="Object for all real time alert settings", blank=True,
    )

    objects = UserSlackIntegrationQuerySet.as_manager()

    def __str__(self):
        return f"{self.user.email} slack integration"

    class Meta:
        ordering = ["user"]

    def add_to_recap_receivers(self, id):
        self.recap_receivers.append(id)
        self.save()
        return

    def change_recap_channel(self, channel):
        self.recap_channel = channel
        self.save()
        return


class OrgCustomSlackFormQuerySet(models.QuerySet):
    def for_user(self, user):
        if user.organization and user.is_active:
            return self.filter(team=user.team)
        else:
            return self.none()

    def for_staff(self, org=None):
        if org:
            return self.filter(organization=org)
        else:
            return self


class OrgCustomSlackForm(TimeStampModel):
    """Model to store the organizations JSON-based custom Slack form config - these are templates"""

    organization = models.ForeignKey(
        "organization.Organization", related_name="custom_slack_forms", on_delete=models.CASCADE,
    )
    team = models.ForeignKey(
        "organization.Team", related_name="team_forms", on_delete=models.CASCADE, null=True
    )
    form_type = models.CharField(
        max_length=255,
        choices=slack_consts.FORM_TYPES,
        help_text="Type of forms created, can only have one of each type",
    )
    resource = models.CharField(
        max_length=255,
        choices=slack_consts.FORM_RESOURCES,
        help_text="Resources we currently support custom forms for",
    )
    config = JSONField(
        default=dict,
        help_text="The configuration object for this organization's custom Slack form.",
        blank=True,
    )
    stage = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="if this is a special stage form the stage will appear here",
    )
    custom_fields = models.ManyToManyField("crm.ObjectField", through="slack.CustomFormField")
    custom_object = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="if this has a custom object attached this will show",
    )
    fields = models.ManyToManyField("salesforce.SObjectField", through="slack.FormField")

    objects = OrgCustomSlackFormQuerySet.as_manager()

    def __str__(self):
        return f"{self.organization.name}-{self.resource} {self.form_type} - ({self.team})"

    class Meta:
        ordering = [
            "resource",
        ]
        unique_together = ["resource", "form_type", "team", "stage"]

    def generate_form_state(self):
        form_fields = CustomFormField.objects.filter(form=self)
        state_object = {}
        for i, field in enumerate(form_fields):
            state_object[field.order] = field.field.api_name
        self.config = state_object
        self.save()

    def recreate_form(self):
        from managr.crm.models import ObjectField

        team_lead = self.team.team_lead
        fields = ObjectField.objects.filter(
            Q(api_name__in=self.config.values(), crm_object=self.resource, user=team_lead,)
            | Q(is_public=True)
        )
        self.custom_fields.clear()
        for i, field in enumerate(self.config.items()):
            current_field = fields.filter(api_name=field[1]).first()
            if current_field:
                self.custom_fields.add(
                    current_field.id,
                    through_defaults={"order": field[0], "include_in_recap": True,},
                )
        return self.save()

    def to_slack_options(self):
        filtered_fields = self.custom_fields.filter(is_public=False)
        options = [block_builders.option(field.label, field.api_name) for field in filtered_fields]
        return options


class OrgCustomSlackFormInstanceQuerySet(models.QuerySet):
    def for_user(self, user):
        if user.organization and user.is_active:
            return self.filter(user=user.id)
        else:
            return self.none()


class OrgCustomSlackFormInstance(TimeStampModel):
    """Model to store the instances created when a form is submitted from slack"""

    user = models.ForeignKey(
        "core.User", related_name="custom_slack_form_instances", on_delete=models.CASCADE,
    )
    template = models.ForeignKey(
        "slack.OrgCustomSlackForm", on_delete=models.SET_NULL, related_name="instances", null=True
    )
    saved_data = JSONField(default=dict, help_text="The data submitted on the form", blank=True,)
    previous_data = JSONField(
        default=dict, help_text="This will hold previous data for updated forms", blank=True,
    )
    resource_id = models.CharField(
        max_length=255, blank=True, help_text="The resource for this form (if not create"
    )
    workflow = models.ForeignKey("salesforce.MeetingWorkflow", models.CASCADE, "forms", null=True)
    is_submitted = models.BooleanField(
        help_text="If sf returned a success this will be true, this was set up on 06/25/2021 and will only be valid for forms therafter",
        default=False,
    )
    submission_date = models.DateTimeField(null=True, help_text="Date form was submitted")
    update_source = models.CharField(
        max_length=30,
        blank=True,
        null=True,
        help_text="On update forms, sets the source of the update",
    )
    alert_instance_id = models.ForeignKey(
        "alerts.AlertInstance", models.SET_NULL, related_name="form_instance", null=True, blank=True
    )
    objects = OrgCustomSlackFormInstanceQuerySet.as_manager()

    def __str__(self):
        return f"Slack Form {self.resource_type}, {self.user.email}"

    class Meta:
        ordering = ["-datetime_created"]

    @property
    def resource_type(self):
        if self.template:
            return self.template.resource
        else:
            return None

    @property
    def resource_object(self):
        from managr.salesforce.routes import routes as sf_routes
        from managr.hubspot.routes import routes as hs_routes

        routes = sf_routes if self.user.crm == "SALESFORCE" else hs_routes
        route = routes[self.resource_type]
        model_class = route["model"]

        model_object = model_class.objects.filter(id=self.resource_id).first()
        return model_object

    def get_user_fields(self):
        from managr.crm.models import ObjectField

        # template_fields = (
        #     self.template.formfield_set.all()
        #     .values_list("field__api_name", "field__salesforce_object",)
        #     .order_by("order")
        # )
        template_fields = (
            self.template.customformfield_set.all()
            .values_list("field__api_name", "field__crm_object",)
            .order_by("order")
        )
        user_fields = []
        # hack to maintain order
        for field in template_fields:
            try:
                # f = SObjectField.objects.get(
                #     Q(api_name=field[0])
                #     & Q(Q(salesforce_object=field[1]) | Q(salesforce_object__isnull=True))
                #     & (Q(is_public=True) | Q(salesforce_account=self.user.salesforce_account))
                # )
                f = ObjectField.objects.get(
                    Q(api_name=field[0])
                    & Q(Q(crm_object=field[1]) | Q(crm_object__isnull=True))
                    & (Q(is_public=True) | Q(user=self.user))
                )
            except ObjectField.DoesNotExist:
                logger.exception(f"GET USER FIELDS EXCEPTION DOES NOT EXIST: {field}")
            user_fields.append(f)
        if not template_fields:
            # user has not created form use all fields
            user_fields = ObjectField.objects.filter(user=self.user, crm_object=self.resource_type,)
        return user_fields

    def generate_form_values(self, data=None):
        form_values = {}
        if data:
            form_values = data
        else:
            if self.template.form_type != slack_consts.FORM_TYPE_CREATE:
                if self.resource_id:
                    if not self.resource_object:
                        return logger.exception(
                            f"Failed to find the resource with id {self.resource_id} of model {self.resource_type}, to generate form for the user, the resource was most likely removed"
                        )
                    attempts = 1
                    while True:
                        try:
                            current = self.resource_object.get_current_values()
                            form_values = current.secondary_data
                            break
                        except TokenExpired:
                            if attempts >= 5:
                                logger.exception("Failed pull current data")
                                form_values = self.resource_object.secondary_data
                                break
                            else:
                                try:
                                    if self.resource_object.owner == self.user:
                                        self.user.crm_account.regenerate_token()
                                    else:
                                        self.resource_object.owner.crm_account.regenerate_token()
                                    attempts += 1
                                except InvalidRefreshToken:
                                    logger.exception(
                                        f"Failed pull current data for user {str(self.user.id)} after not being able to refresh their token"
                                    )
                                    form_values = self.resource_object.secondary_data
                                    break
                        except Exception as e:
                            logger.exception(f"Failed pull current data from {e}")
                            form_values = {}
                            break
                else:
                    form_values = {}
        return form_values

    def generate_form(self, data=None, *args, **kwargs):
        """
        Collects all the fields
        and creates them into an object
        that has all the necessary fields as
        slack blocks
        If a resource is available it's current values
        will be passed in as values
        ## Optionally pass in data to override instance data
        """
        # get all fields that belong to the user based on the template fields
        user_fields = self.get_user_fields()
        form_values = self.generate_form_values(data)
        form_blocks = []
        for field in user_fields:
            val = form_values.get(field.api_name, None)
            if field.is_public:
                # pass in user as a kwarg
                generated_field = field.to_slack_field(
                    val, user=self.user, resource=self.resource_type,
                )
                if isinstance(generated_field, list):
                    form_blocks.extend(generated_field)
                else:
                    form_blocks.append(generated_field)
                if str(field.id) == "0bb152b5-aac1-4ee0-9c25-51ae98d55af1":
                    form_blocks.append(
                        block_builders.section_with_button_block(
                            "Insert",
                            "note_templates",
                            "*Note Templates*",
                            block_id="note_templates",
                            action_id=slack_consts.INSERT_NOTE_TEMPLATE_DROPDOWN,
                        )
                    )
                    form_blocks.append({"type": "divider"})
            else:
                generated_field = field.to_slack_field(
                    val,
                    user=self.user,
                    resource=self.resource_type,
                    **{**kwargs, "resource_id": self.resource_id},
                )
                if isinstance(generated_field, list):
                    form_blocks.extend(generated_field)
                else:
                    form_blocks.append(generated_field)
        return form_blocks

    def get_values(self, state):
        vals = dict()
        for field, data in state.items():
            for value in data.values():
                current_value = None
                if value["type"] == "external_select" or value["type"] == "static_select":
                    current_value = (
                        value.get("selected_option").get("value", None)
                        if value.get("selected_option", {})
                        else None
                    )
                elif value["type"] == "multi_channels_select":
                    current_value = (
                        ";".join(list(map(lambda val: val, value.get("selected_channels", []))))
                        if value.get("selected_channels", None)
                        else None
                    )
                elif value["type"] == "multi_conversations_select":
                    current_value = (
                        ";".join(
                            list(map(lambda val: val, value.get("selected_conversations", [])))
                        )
                        if value.get("selected_conversations", None)
                        else None
                    )
                elif (
                    value["type"] == "multi_static_select"
                    or value["type"] == "multi_external_select"
                ):
                    current_value = (
                        ";".join(
                            list(map(lambda val: val["value"], value.get("selected_options", [])))
                        )
                        if value.get("selected_options", None)
                        else None
                    )
                elif value["type"] == "plain_text_input":
                    current_value = value["value"]
                elif value["type"] == "checkboxes":
                    current_value = bool(len(value.get("selected_options", [])))
                elif value["type"] == "datepicker":
                    date = value.get("selected_date", None)
                    if self.user.crm == "HUBSPOT" and field == "closedate" and date is not None:
                        current_value = date + "T18:00:00.000Z"
                    else:
                        current_value = date
                vals[field] = current_value
        return vals

    def save_form(self, state, from_slack_object=True):
        """gets all form values but only saves values for fields"""
        values = self.get_values(state) if from_slack_object else state
        fields = [field.api_name for field in self.get_user_fields()]
        old_values = self.generate_form_values()
        new_data = dict()
        old_data = dict()
        for k, v in values.items():
            if k in fields:
                new_data[k] = v
                pass
        for o_k, o_v in old_values.items():
            if o_k in fields:
                old_data[o_k] = o_v
                pass

        self.saved_data = new_data
        self.previous_data = old_data
        self.save()


class FormField(TimeStampModel):
    field = models.ForeignKey(
        "salesforce.SObjectField",
        on_delete=models.CASCADE,
        related_name="forms",
        null=True,
        blank=True,
    )
    form = models.ForeignKey("slack.OrgCustomSlackForm", on_delete=models.CASCADE,)
    order = models.IntegerField(default=0)
    include_in_recap = models.BooleanField(default=True)


class CustomFormField(TimeStampModel):
    field = models.ForeignKey(
        "crm.ObjectField", on_delete=models.CASCADE, related_name="forms", null=True, blank=True,
    )
    form = models.ForeignKey("slack.OrgCustomSlackForm", on_delete=models.CASCADE,)
    order = models.IntegerField(default=0)
    include_in_recap = models.BooleanField(default=True)
