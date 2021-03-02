from django.db import models
from django.contrib.postgres.fields import JSONField
from . import constants as slack_consts

from managr.core.models import TimeStampModel


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
        "organization.Organization",
        related_name="custom_slack_form_instances",
        on_delete=models.CASCADE,
    )
    template = models.ForeignKey(
        "slack.OrgCustomSlackForm", on_delete=models.SET_NULL, related_name="instances", null=True
    )

    form_data = JSONField(
        default=dict,
        help_text="The form data as a field object with a value inserted for this organization's custom Slack form.",
    )

    objects = OrgCustomSlackFormInstanceQuerySet.as_manager()

    def __str__(self):
        return f"Slack Form {self.resource}, {self.form_type}"

    class Meta:
        ordering = ["-datetime_created"]


# users can have a slack form for create,
# update resources and one form for reviewing a meeting
