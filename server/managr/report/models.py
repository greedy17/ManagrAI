import uuid

from django.db import models
from django.contrib.postgres.fields import JSONField

from managr.utils.sites import get_site_url
from managr.core.models import TimeStampModel
from managr.report import constants as report_const


class StoryReportQuerySet(models.QuerySet):
    def for_user(self, user):
        if user.is_superuser:
            return self.all()
        elif user.organization and user.is_active:
            return self.filter(generated_by__organization=user.organization_id)
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

    @property
    def client_side_url(self):
        base_app_url = get_site_url()
        return f"{base_app_url}/story-reports/{self.id}"

    class Meta:
        ordering = ["-datetime_created"]

    def __str__(self):
        return f"StoryReport ({self.id}): LEAD => '{self.lead.title}' ({self.lead_id}). GENERATED => {self.datetime_generated or 'Pending...'}"


class PerformanceReportQuerySet(models.QuerySet):
    def for_user(self, user):
        if user.is_superuser:
            return self.all()
        elif user.organization and user.is_active:
            return self.filter(generated_by__organization=user.organization_id)
        else:
            return None


class PerformanceReport(TimeStampModel):
    """
    This type of report can be focused on a Representative
    or can be Organization-wide and focus on all Representatives/.
    This report shows metrics around a Representative's/Organizaiton's
    performance within a specified date-range.
    """

    representative = models.ForeignKey(
        "core.User",
        related_name="performance_reports",
        on_delete=models.PROTECT,
        null=True,
        help_text="If populated, refers to the representative that is the focus of the report. "
                  "If it is NULL, it means that this is an organization-wide (all representatives) report.",
    )
    date_range_preset = models.CharField(
        choices=report_const.DATE_RANGES,
        max_length=255,
    )
    date_range_from = models.DateTimeField()
    date_range_to = models.DateTimeField()
    data = JSONField(help_text="Content of the PerformanceReport", default=dict)
    datetime_generated = models.DateTimeField(
        null=True, help_text="date time when the report was populated with computed data"
    )
    generated_by = models.ForeignKey(
        "core.User",
        related_name="generated_performance_reports",
        null=True,
        on_delete=models.SET_NULL,
        help_text="Email notifying of report generation is to be sent to this user",
    )

    objects = PerformanceReportQuerySet.as_manager()

    @property
    def is_representative_report(self):
        # True if the report is representative-specific
        return bool(self.representative)

    @property
    def is_organization_report(self):
        # True if the report is organization-wide
        return not bool(self.representative)

    @property
    def client_side_url(self):
        base_app_url = get_site_url()
        return f"{base_app_url}/performance-reports/{self.id}"

    class Meta:
        ordering = ["-datetime_created"]

    def __str__(self):
        if self.representative:
            return f"PerformanceReport ({self.id}): REPRESENTATIVE => '{self.representative.full_name}'. ({self.representative_id}). GENERATED => {self.datetime_generated or 'Pending...'}"
        else:
            return f"PerformanceReport ({self.id}): REPRESENTATIVE => 'ALL'. GENERATED => {self.datetime_generated or 'Pending...'}"
