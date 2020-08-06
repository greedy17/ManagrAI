import uuid

from django.db import models
from django.contrib.postgres.fields import JSONField

from managr.core.models import TimeStampModel


class StoryReportQuerySet(models.QuerySet):
    def for_user(self, user):
        if user.is_superuser:
            return self.all()
        elif user.organization and user.is_active:
            return self.filter(lead__account__organization=user.organization_id)
        else:
            return None


class StoryReport(TimeStampModel):
    """
    This type of report can be generated for a Closed Lead.
    This report shows what occurred on the lead.
    """

    lead = models.ForeignKey(
        "lead.Lead",
        related_name="story_reports",
        on_delete=models.PROTECT,
        null=False,
    )
    data = JSONField(help_text="Content of the StoryReport", default=dict)
    datetime_generated = models.DateTimeField(
        null=True, help_text="date time when the report was populated with computed data"
    )
    generated_by = models.ForeignKey(
        "core.User",
        related_name="generated_story_reports",
        null=True,
        on_delete=models.SET_NULL,
        help_text="Email notifying of report generation is to be sent to this user",
    )

    objects = StoryReportQuerySet.as_manager()

    class Meta:
        ordering = ["-datetime_created"]

    def __str__(self):
        return f"StoryReport for: '{self.lead.title}' ({self.lead.id}). Generated: {self.datetime_generated or 'Pending...'}"
