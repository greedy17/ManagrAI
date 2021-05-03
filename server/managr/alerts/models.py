from django.db import models
from django.contrib.postgres.fields import ArrayField

from managr.core.models import TimeStampModel

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
    objects = AlertTemplateQuerySet()

    def __str__(self):
        return f"{self.title} created by {self.user.email}"

    class Meta:
        ordering = ["-datetime_created"]


class AlertGroupQuerySet(models.QuerySet):
    def for_user(self, user):
        if user.is_superuser:
            return self.all()
        if user.organization and user.is_active:
            return self.filter(user__organization=user.organization)
        else:
            return self.none()


class AlertGroup(TimeStampModel):
    operator = models.CharField(choices=(("AND", "AND"), ("OR", "OR"),), max_length=255)
    template = models.ForeignKey(
        "alerts.AlertTemplate", on_delete=models.CASCADE, related_name="groups"
    )

    def __str__(self):
        return f"Alert group with operator {self.operator}, for template {self.template.title}"

    class Meta:
        ordering = ["-datetime_created"]


class AlertOperand(TimeStampModel):
    group = models.ForeignKey(
        "alerts.AlertGroup", on_delete=models.CASCADE, related_name="operands"
    )
    operand_type = models.CharField(
        max_length=255,
        help_text="Type of operand aka if it is a 'field' ('close_date') or a 'managr' aka local to managr (last_stage_update)",
    )
    operand_type_identifier = models.CharField(max_length=255)
    operator = models.CharField(max_length=255)
    value = models.CharField(max_length=255)
    recipients = ArrayField(models.CharField(max_length=255), default=list)

    def __str__(self):
        return f"{self.operand_type_identifier} {self.operator}"

    class Meta:
        ordering = ["-datetime_created"]

