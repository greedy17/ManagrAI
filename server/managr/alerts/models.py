import re
import operator as _operator
from dateutil.relativedelta import relativedelta

from django.db import models
from django.contrib.postgres.fields import ArrayField, JSONField
from django.utils import timezone

from managr.alerts.utils.utils import convertToSlackFormat
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

    def url_str(self, user, config_id):
        """ Generates Url Str for request when executing alert """
        user_sf = user.salesforce_account if hasattr(user, "salesforce_account") else None
        operand_groups = [group.query_str(config_id) for group in self.groups.all()]

        operand_groups = f"AND ({' '.join(operand_groups)})"

        q = sf_consts.SALESFORCE_RESOURCE_QUERY_URI(
            user_sf.salesforce_id,
            self.resource_type,
            ["Id"],
            additional_filters=[*self.adapter_class.additional_filters(), operand_groups,],
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
        # create a temporary config
        c = AlertConfig.objects.create(
            recurrence_day=timezone.now().weekday(),
            recurrence_frequency="WEEKLY",
            recipients=["SELF"],
            template=self,
        )

        if hasattr(user, "salesforce_account"):
            try:
                _process_check_alert.now(str(c.id), str(user.id))
            except:
                return c.delete()
        # delete after test is over
        c.delete()

    def config_user_group(self, config_id):
        """ returns the users who will be receiving the messages based on the config """
        config = self.configs.filter(id=config_id).first()
        if config:
            return config.recipient_users

    def config_run_against_date(self, config_id):
        """ returns the date against which the query is executed """
        config = self.configs.filter(id=config_id).first()
        if config:
            return config.run_against_date


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

    def query_str(self, config_id):
        """ returns a grouped qs of operand rows (in ()) """
        q_s = f"({' '.join([operand.query_str(config_id) for operand in self.operands.all()])})"
        if self.group_order != 0:
            q_s = f"{self.group_condition} {q_s}"
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

    def query_str(self, config_id):
        """ gathers different parts of operand and constructs query """
        # if type is date or date time we need to create a strftime/date
        value = self.operand_value
        operator = self.operand_operator
        if self.data_type == "DATE":
            # try converting value to int
            value = (
                self.group.template.config_run_against_date(config_id)
                + timezone.timedelta(days=int(self.operand_value))
            ).strftime("%Y-%m-%d")
        elif self.data_type == "DATETIME":
            value = (
                self.group.template.config_run_against_date(config_id)
                + timezone.timedelta(days=int(self.operand_value))
            ).strftime("%Y-%m-%dT00:00:00Z")
        elif self.data_type == "STRING":
            # sf requires single quotes for strings only (aka not decimal or date)

            # zero conditional does not get added
            if self.operand_operator in ["CONTAINS", "STARTSWITH", "ENDSWITH"]:
                operator = "LIKE"
                if self.operand_operator == "CONTAINS":
                    value = f"'%{value}%'"
                elif self.operand_operator == "STARTSWITH":
                    value = f"'%{value}'"
                elif self.operand_operator == "ENDSWITH":
                    value = f"'{value}%'"
            else:
                value = f"'{value}'"
        q_s = f"{self.operand_identifier} {operator} {value}"
        ## TODO: there may be a reason to check id for match in group.operands.first() if there is an issue with order
        if self.operand_order != 0:
            q_s = f"{self.operand_condition} {q_s}"
        if self.data_type == "DATETIME" and (operator == "=" or operator == "!="):
            # calulate a boundary for same day
            end_value = (
                self.group.template.config_run_against_date(config_id)
                + timezone.timedelta(days=int(self.operand_value))
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

    @property
    def run_against_date(self):
        """ 
            returns the date based on the selected config to run against 
            normally this would be today's date but mike wants to allow 
            users to manually run this alert for the date provided
        """
        if self.recurrence_frequency == "WEEKLY":
            today_weekday = timezone.now().weekday()
            if today_weekday != int(self.recurrence_day):
                # calculate the specific date wanted based on day of week
                day_diff = int(self.recurrence_day) - today_weekday
                return timezone.now() + timezone.timedelta(days=day_diff)
            return timezone.now()
        elif self.recurrence_frequency == "MONTHLY":
            return timezone.now() + relativedelta(days=int(self.recurrence_day))

        return timezone.now()


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
    instance_meta = JSONField(
        default=dict,
        null=True,
        blank=True,
        help_text="an object holding some metadata results_count: # across alert, query_sent: copy of sql, errors: Array of any errors ",
    )
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

        body = self.template.message_template.body

        body = convertToSlackFormat(body)
        for k, v in self.var_binding_map.items():
            str_rep = "{ " + k + " }"
            str_rep = r"{}".format(str_rep)

            body = body.replace(str_rep, str(v))
        return body

    @property
    def var_binding_map(self):
        """ takes set of variable bindings and replaces them with the value """
        binding_map = dict()
        for binding in self.template.message_template.bindings:
            ## collect all valid bindings
            try:
                k, v = binding.split(".")
                if k != self.template.resource_type and k != "__Recipient":
                    continue
                if k == self.template.resource_type and hasattr(self.user, "salesforce_account"):
                    binding_map[binding] = self.resource.secondary_data.get(v, "*N/A*")
                    # HACK pb for datetime fields Mike wants just the date
                    user = self.user
                    if self.resource.secondary_data.get(v):
                        field = user.salesforce_account.object_fields.filter(api_name=v).first()
                        if field and field.data_type == "DateTime":
                            binding_map[binding] = binding_map[binding][0:10]

                elif k == "__Recipient":
                    binding_map[binding] = getattr(self.user, v)

            except ValueError:
                continue
        return binding_map
