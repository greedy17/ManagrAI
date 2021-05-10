import operator as _operator

from django.db import models
from django.contrib.postgres.fields import ArrayField

from managr.core.models import TimeStampModel
from managr.salesforce.routes import routes as model_routes
from managr.salesforce.adapter.routes import routes as adapter_routes

# Create your models here.


class AlertTemplateQuerySet(models.QuerySet):
    def for_user(self, user):
        if user.is_superuser:
            return self.all()
        if user.organization and user.is_active:
            return self.filter(user__organization=user.organization)
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
    template = models.ForeignKey(
        "alerts.AlertTemplate", on_delete=models.CASCADE, related_name="groups"
    )
    objects = AlertGroupQuerySet.as_manager()

    def __str__(self):
        return f"Alert group with operator {self.operator}, for template {self.template.title}"

    class Meta:
        ordering = ["-datetime_created"]


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

    objects = AlertOperandQuerySet.as_manager()

    def __str__(self):
        return f"{self.operand_type_identifier} {self.operator}"

    class Meta:
        ordering = ["-datetime_created"]


class AlertMessageTemplateQuerySet(models.QuerySet):
    def for_user(self, user):
        if user.is_superuser:
            return self.all()
        if user.organization and user.is_active:
            return self.filter(template__user__organization=user.organization)
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
        return f"notification message for {self.template.title}"

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
    resource_id = models.CharField(max_length=255)
    sent_at = models.DateTimeField()
    objects = AlertGroupQuerySet.as_manager()

    def __str__(self):
        return f"notification for {self.user.email} from template {self.template.title} for {self.template.resource_type}, {self.resource_id}"

    @property
    def resource(self):
        return model_routes[self.template_resource_type]["model"].objects.filter(
            id=self.resource_id
        )

    class Meta:
        ordering = ["-datetime_created"]

