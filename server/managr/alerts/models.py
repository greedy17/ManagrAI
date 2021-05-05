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
    user = models.ForeignKey("core.User", on_delete=models.CASCADE, related_name="alert_template")
    resource_type = models.CharField(max_length=255)

    occurences = models.PositiveIntegerField(
        default=1,
        help_text="How many instances of the same alert should we send out (always 1 max per day)",
    )
    recipients = ArrayField(models.CharField(max_length=255), default=list)
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
        help_text="Type of operand aka if it is a 'sf_only' ('close_date') or a 'managr' aka saved to the model directly (last_stage_update, stage, amount,close_date)",
    )
    operand_identifier = models.CharField(
        max_length=255, help_text="Name of the field or managr constraint"
    )
    operator = models.CharField(max_length=255)
    value = models.CharField(max_length=255)

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
    bindings = ArrayField(models.CharField(max_length=255), default=list)
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

    def __str__(self):
        return f"notification for {self.user.email} from template {self.template.title} for {self.template.resource_type}, {self.resource_id}"

    @property
    def resource(self):
        return model_routes[self.template_resource_type]["model"].objects.filter(
            id=self.resource_id
        )

    class Meta:
        ordering = ["-datetime_created"]

