from django.db import models
from managr.core.models import TimeStampModel, IntegrationModel
from django.contrib.postgres.fields import JSONField, ArrayField

# Create your models here.


class BaseOpportunityQuerySet(models.QuerySet):
    def for_user(self, user):
        if user.organization and user.is_active:
            if user.user_level in ["SDR", "MANAGER"]:
                return self.filter(organization=user.organization)
            else:
                return self.filter(organization=user.organization, owner=user)
        else:
            return None


class BaseOpportunity(TimeStampModel, IntegrationModel):
    name = models.CharField(max_length=255, blank=True, null=False)
    amount = models.DecimalField(max_digits=30, decimal_places=15, default=0.00, null=True,)
    forecast_category = models.CharField(max_length=255, null=True)
    close_date = models.DateField(null=True)
    account = models.CharField(max_length=255, blank=True, help_text="Retrieved from Integration")
    contacts = models.ManyToManyField("HubspotContact", related_name="contacts", blank=True)
    external_company = models.CharField(
        max_length=255, blank=True, help_text="value from the integration"
    )

    external_owner = models.CharField(
        max_length=255, blank=True, help_text="value from the integration"
    )

    owner = models.ForeignKey(
        "core.User", related_name="owned_deals", on_delete=models.SET_NULL, blank=True, null=True,
    )
    stage = models.CharField(max_length=255, null=True)
    company = models.ForeignKey(
        "Company", related_name="companies", on_delete=models.SET_NULL, blank=True, null=True,
    )
    is_stale = models.BooleanField(default=False)
    secondary_data = JSONField(
        default=dict,
        null=True,
        help_text="All non primary fields that are on the model each org may have its own",
        max_length=500,
    )
    objects = BaseOpportunityQuerySet.as_manager()

    class Meta:
        ordering = ["-datetime_created"]
