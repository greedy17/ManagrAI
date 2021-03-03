import logging

from django.db import models
from django.contrib.postgres.fields import JSONField
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

    objects = UserSlackIntegrationQuerySet.as_manager()

    def __str__(self):
        return f"{self.user.email} slack integration"

    class Meta:
        ordering = ["user"]


class OrgCustomSlackFormQuerySet(models.QuerySet):
    def for_user(self, user):
        if user.organization and user.is_active:
            return self.filter(organization=user.organization_id)
        else:
            return self.none()


class OrgCustomSlackForm(TimeStampModel):
    """Model to store the organizations JSON-based custom Slack form config - these are templates """

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
    fields = models.ManyToManyField("salesforce.SObjectField", related_name="form_fields")

    objects = OrgCustomSlackFormQuerySet.as_manager()

    def __str__(self):
        return f"Slack Form {self.resource}, {self.form_type}"

    class Meta:
        ordering = ["resource", "-stage"]
        unique_together = ["resource", "form_type", "organization", "stage"]


class OrgCustomSlackFormInstanceQuerySet(models.QuerySet):
    def for_user(self, user):
        if user.organization and user.is_active:
            return self.filter(user=user.id)
        else:
            return self.none()


class OrgCustomSlackFormInstance(TimeStampModel):
    """Model to store the instances created when a form is submitted from slack """

    user = models.ForeignKey(
        "core.User", related_name="custom_slack_form_instances", on_delete=models.CASCADE,
    )
    template = models.ForeignKey(
        "slack.OrgCustomSlackForm", on_delete=models.SET_NULL, related_name="instances", null=True
    )
    saved_data = JSONField(
        default=dict,
        help_text="The Generated form with instances of its fields as a json object",
        blank=True,
    )
    resource_id = models.CharField(
        max_length=255, blank=True, help_text="The resource for this form (if not create"
    )
    review_workflow = models.ForeignKey(
        "salesforce.MeetingWorkflow", models.PROTECT, "forms", null=True
    )

    objects = OrgCustomSlackFormInstanceQuerySet.as_manager()

    def __str__(self):
        return f"Slack Form {self.resource_type}, {self.user.email}"

    class Meta:
        ordering = ["-datetime_created"]

    @property
    def resource_type(self):
        return self.template.resource

    @property
    def resource_object(self):
        from managr.salesforce.routes import routes

        route = routes[self.resource_type]
        model_class = route["model"]
        model_object = model_class.objects.filter(id=self.resource_id).first()
        return model_object

    def generate_form(self):
        """ 
        Collects all the fields 
        and creates them into an object 
        that has all the necessary fields as 
        slack blocks 
        If a resource is available it's current values
        will be passed in as values
        """
        # get all fields that belong to the user based on the template fields
        template_fields = self.template.fields.all().values_list("api_name", "salesforce_object",)
        user_fields = SObjectField.objects.filter(
            Q(api_name__in=list(map(lambda field: field[0], template_fields)),)
            & Q(
                Q(salesforce_object__in=list(map(lambda field: field[1], template_fields)),)
                | Q(salesforce_object__isnull=True)
            )
            & (Q(is_public=True) | Q(salesforce_account=self.user.salesforce_account))
        )
        if self.template.form_type != slack_consts.FORM_TYPE_CREATE and self.resource_id:
            if not self.resource_object:
                return logger.exception(
                    f"Failed to find the resource with id {self.template.resource_id} of model {self.resource_type}, to generate form for user"
                )
            model_data = self.resource_object.secondary_data

            form_blocks = []
            for field in user_fields:
                val = model_data.get(field.api_name)
                form_blocks.append(field.to_slack_field(val))

            print(form_blocks)
        else:
            return [field.to_slack_field() for field in user_fields]


# users can have a slack form for create,
# update resources and one form for reviewing a meeting

