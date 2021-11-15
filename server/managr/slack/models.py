import logging

from django.db import models
from django.db.models.constraints import UniqueConstraint
from django.contrib.postgres.fields import JSONField, ArrayField
from django.db.models import Q

from managr.salesforce.models import SObjectField


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
        max_length=255, null=True, help_text="Channel for zoom automation, defaults to channel",
    )

    recap_channel = models.CharField(
        max_length=255, null=True, help_text="Channel for recaps to be sent",
    )
    recap_receivers = ArrayField(models.CharField(max_length=255), default=list, blank=True)

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
            return self.filter(organization=user.organization_id)
        else:
            return self.none()


class OrgCustomSlackForm(TimeStampModel):
    """Model to store the organizations JSON-based custom Slack form config - these are templates"""

    organization = models.ForeignKey(
        "organization.Organization", related_name="custom_slack_forms", on_delete=models.CASCADE,
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
    )
    stage = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="if this is a special stage form the stage will appear here",
    )
    fields = models.ManyToManyField("salesforce.SObjectField", through="slack.FormField")

    objects = OrgCustomSlackFormQuerySet.as_manager()

    def __str__(self):
        return f"Slack Form {self.resource}, {self.form_type} for {self.organization.name}"

    class Meta:
        ordering = [
            "resource",
        ]
        unique_together = ["resource", "form_type", "organization", "stage"]


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
        max_length=30, blank=True, help_text="On update forms, sets the source of the update"
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
        from managr.salesforce.routes import routes

        route = routes[self.resource_type]
        model_class = route["model"]
        model_object = model_class.objects.filter(id=self.resource_id).first()
        return model_object

    def get_user_fields(self):
        template_fields = (
            self.template.formfield_set.all()
            .values_list("field__api_name", "field__salesforce_object",)
            .order_by("order")
        )
        user_fields = []
        print(template_fields)
        # hack to maintain order
        for field in template_fields:
            print(field)
            f = SObjectField.objects.get(
                Q(api_name=field[0])
                & Q(Q(salesforce_object=field[1]) | Q(salesforce_object__isnull=True))
                & (Q(is_public=True) | Q(salesforce_account=self.user.salesforce_account))
            )
            user_fields.append(f)
        if not template_fields:
            # user has not created form use all fields
            user_fields = SObjectField.objects.filter(
                salesforce_account=self.user.salesforce_account,
                salesforce_object=self.resource_type,
            )
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
                    form_values = self.resource_object.secondary_data
                else:
                    form_values = {}
        return form_values

    def generate_form(self, data=None):
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
            else:
                generated_field = field.to_slack_field(
                    val, user=self.user, resource=self.resource_type,
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
        "salesforce.SObjectField", on_delete=models.CASCADE, related_name="forms"
    )
    form = models.ForeignKey("slack.OrgCustomSlackForm", on_delete=models.CASCADE,)
    order = models.IntegerField(default=0)
    include_in_recap = models.BooleanField(default=True)
