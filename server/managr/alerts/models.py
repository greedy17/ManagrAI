import operator as _operator

from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.utils import timezone

from managr.core.models import TimeStampModel
from managr.salesforce.routes import routes as model_routes
from managr.salesforce.adapter.routes import routes as adapter_routes
from managr.salesforce import constants as sf_consts

# Create your models here.


class AlertTemplateQuerySet(models.QuerySet):
    def for_user(self, user):
        if user.is_superuser:
            return self.all()
        if user.organization and user.is_active:
            return self.filter(user=user)
        else:
            return self.none()


class AlertTemplate(TimeStampModel):
    title = models.CharField(max_length=255)
    user = models.ForeignKey("core.User", on_delete=models.CASCADE, related_name="alert_templates")
    resource_type = models.CharField(max_length=255)
    alert_level = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    objects = AlertTemplateQuerySet.as_manager()

    def __str__(self):
        return f"{self.title} created by {self.user.email}"

    class Meta:
        ordering = ["-datetime_created"]

    @property
    def adapter_class(self):
        return adapter_routes.get(self.resource_type, None)

    def url_str(self, user):
        """ Generates Url Str for request when executing alert """
        user_sf = user.salesforce_account if hasattr(user, "salesforce_account") else None

        q = sf_consts.SALESFORCE_RESOURCE_QUERY_URI(
            user_sf.salesforce_id,
            self.resource_type,
            ["Id"],
            additional_filters=[
                *self.adapter_class.additional_filters(),
                *[group.query_str for group in self.groups.all()],
            ],
        )
        return f"{user_sf.instance_url}{q}"

    @property
    def get_users(self):
        # get user groups
        ## currently applies to all user groups
        return self.user.organization.users.filter(is_active=True)

    def test_alert(self):
        from managr.alerts.background import _process_check_alert

        user = self.user
        if hasattr(user, "salesforce_account"):
            _process_check_alert.now(str(self.id), str(user.id))


class AlertGroupQuerySet(models.QuerySet):
    def for_user(self, user):
        if user.is_superuser:
            return self.all()
        if user.organization and user.is_active:
            return self.filter(template__user__organization=user.organization)
        else:
            return self.none()


class AlertGroup(TimeStampModel):
    group_condition = models.CharField(
        choices=(("AND", "AND"), ("OR", "OR"),),
        max_length=255,
        help_text="Applied to itself for multiple groups AND/OR group1 AND/OR group 2",
    )
    group_order = models.SmallIntegerField()
    template = models.ForeignKey(
        "alerts.AlertTemplate", on_delete=models.CASCADE, related_name="groups"
    )
    objects = AlertGroupQuerySet.as_manager()

    def __str__(self):
        return f"Alert group, for template {self.template.title}"

    class Meta:
        ordering = ["group_order"]

    @property
    def query_str(self):
        """ returns a grouped qs of operand rows (in ()) """
        q_s = f"({' '.join([operand.query_str for operand in self.operands.all()])})"
        if self.group_order != 0:
            q_s = f"{self.operand_condition} {q_s}"
        else:
            ## the firest item always gets the AND since there are other additional filters already
            q_s = f"AND {q_s}"
        return q_s


class AlertOperandQuerySet(models.QuerySet):
    def for_user(self, user):
        if user.is_superuser:
            return self.all()
        if user.organization and user.is_active:
            return self.filter(group__template__user__organization=user.organization)
        else:
            return self.none()


class AlertOperand(TimeStampModel):
    group = models.ForeignKey(
        "alerts.AlertGroup", on_delete=models.CASCADE, related_name="operands"
    )
    operand_condition = models.CharField(
        choices=(("AND", "AND"), ("OR", "OR"),),
        max_length=255,
        help_text="Applied to itself for multiple groups AND/OR group1 AND/OR group 2",
    )
    operand_type = models.CharField(
        max_length=255,
        help_text="field indicates sobject field non_field indicates managr model fields",
    )
    operand_identifier = models.CharField(
        max_length=255, help_text="Name of the field or managr constraint"
    )
    operand_operator = models.CharField(max_length=255)
    operand_value = models.CharField(max_length=255)
    operand_order = models.SmallIntegerField()
    data_type = models.CharField(
        null=True,
        max_length=255,
        help_text="To what data type we are comparing to, all data types are converted to either string, date, decimal",
    )

    objects = AlertOperandQuerySet.as_manager()

    def __str__(self):
        return f"{self.group.template.title} {self.operand_identifier}"

    class Meta:
        ordering = ["operand_order"]

    @property
    def query_str(self):
        """ gathers different parts of operand and constructs query """
        # if type is date or date time we need to create a strftime/date
        value = self.operand_value
        if self.data_type == "DATE":
            # try converting value to int

            value = (timezone.now() + timezone.timedelta(days=int(self.operand_value))).strftime(
                "%Y-%m-%d"
            )
        elif self.data_type == "DATETIME":
            value = (timezone.now() + timezone.timedelta(days=int(self.operand_value))).strftime(
                "%Y-%m-%dT00:00:00Z"
            )
        elif self.data_type == "STRING":
            # sf requires single quotes for strings only (aka not decimal or date)
            value = f"'{value}'"
        # zero conditional does not get added
        q_s = f"{self.operand_identifier} {self.operand_operator} {value}"
        ## TODO: there may be a reason to check id for match in group.operands.first() if there is an issue with order
        if self.operand_order != 0:
            q_s = f"{self.operand_condition} {q_s}"
        if self.data_type == "DATETIME" and (
            self.operand_operator == "=" or self.operand_operator == "!="
        ):
            # calulate a boundary for same day
            end_value = (
                timezone.now() + timezone.timedelta(days=int(self.operand_value))
            ).strftime("%Y-%m-%dT11:59:00Z")
            q_s = (
                f"{self.operand_identifier} >= {value} AND {self.operand_identifier} <= {end_value}"
            )

        return q_s


class AlertMessageTemplateQuerySet(models.QuerySet):
    def for_user(self, user):
        if user.is_superuser:
            return self.all()
        if user.organization and user.is_active:
            return self.filter(template__user=user)
        else:
            return self.none()


class AlertMessageTemplate(TimeStampModel):
    template = models.OneToOneField(
        "alerts.AlertTemplate", on_delete=models.CASCADE, related_name="message_template"
    )
    bindings = ArrayField(models.CharField(max_length=255), default=list, blank=True)
    notification_text = models.TextField(
        blank=True,
        help_text="This is the message that appears in the slack notification when the app is closed/out of view",
    )
    body = models.TextField(
        help_text="This is the message the user will see in their notification message"
    )
    objects = AlertMessageTemplateQuerySet.as_manager()

    def __str__(self):
        return f"notification message for {self.template}"

    class Meta:
        ordering = ["-datetime_created"]


class AlertConfigQuerySet(models.QuerySet):
    def for_user(self, user):
        if user.is_superuser:
            return self.all()
        if user.organization and user.is_active:
            return self.filter(template__user__organization=user.organization)
        else:
            return self.none()


class AlertConfig(TimeStampModel):
    recurrence_frequency = models.CharField(
        max_length=255, default="WEEKLY", help_text="Weekly/Monthly will run on these days"
    )
    recurrence_day = models.SmallIntegerField(help_text="day of week/ month")
    recipients = ArrayField(
        models.CharField(max_length=255),
        default=list,
        help_text="Currently UI will only send one recipient will change in the future",
    )
    template = models.ForeignKey(
        "alerts.AlertTemplate", on_delete=models.CASCADE, related_name="configs"
    )
    objects = AlertConfigQuerySet.as_manager()

    def __str__(self):
        return f"Configuration for {self.template.title} for user {self.template.user}"

    class Meta:
        ordering = ["-datetime_created"]


class AlertInstanceQuerySet(models.QuerySet):
    def for_user(self, user):
        if user.is_superuser:
            return self.all()
        if user.organization and user.is_active:
            return self.filter(template__user=user)
        else:
            return self.none()


class AlertInstance(TimeStampModel):
    template = models.ForeignKey(
        "alerts.AlertTemplate", on_delete=models.CASCADE, related_name="instances",
    )
    user = models.ForeignKey("core.User", on_delete=models.CASCADE, related_name="alerts")
    rendered_text = models.TextField(
        help_text=(
            "This is the original text rendered at time of send,"
            "if for some reason an update has occured it will not show the new message but the original,"
            "use to_rendered_text for the updated message"
        )
    )
    sent_at = models.DateTimeField(null=True)
    resource_id = models.CharField(max_length=255)
    objects = AlertGroupQuerySet.as_manager()

    # TODO [MGR-1013]: add private errors here to keep track in case of errors

    # TODO: change resource_id to be a list of id's to apply to one instance

    def __str__(self):
        return f"notification for {self.user.email} from template {self.template.title} for {self.template.resource_type}, {self.resource_id}"

    @property
    def resource(self):
        return (
            model_routes[self.template.resource_type]["model"]
            .objects.filter(id=self.resource_id)
            .first()
        )

    class Meta:
        ordering = ["-datetime_created"]

    def render_text(self):
        """ takes the message template body and renders """
        return
