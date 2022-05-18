import re
import pytz
import logging
import datetime
import operator as _operator
from dateutil.relativedelta import relativedelta
from calendar import monthrange

from django.db import models
from django.db.models import Q
from django.contrib.postgres.fields import ArrayField, JSONField
from django.utils import timezone

from managr.alerts.utils.utils import convertToSlackFormat
from managr.core.models import TimeStampModel
from managr.core import constants as core_consts
from managr.salesforce.routes import routes as model_routes
from managr.salesforce.adapter.routes import routes as adapter_routes
from managr.salesforce import constants as sf_consts
from managr.salesforce.adapter.exceptions import TokenExpired

# Create your models here.

logger = logging.getLogger("managr")


def default_days():
    return [0]


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
    invocation = models.PositiveIntegerField(
        default=0,
        help_text="Keeps track of the number of times this alert has been triggered, this is used to inform the workspace and paginate slack views",
    )
    last_invocation_datetime = models.DateTimeField(null=True)

    def __str__(self):
        return f"{self.title} created by {self.user.email}"

    class Meta:
        ordering = ["-datetime_created"]

    @property
    def adapter_class(self):
        return adapter_routes.get(self.resource_type, None)

    def url_str(self, user, config_id):
        """Generates Url Str for request when executing alert"""
        user_sf = user.salesforce_account if hasattr(user, "salesforce_account") else None
        operand_groups = [group.query_str(config_id) for group in self.groups.all()]

        operand_groups = f"AND ({' '.join(operand_groups)})"
        q = sf_consts.SALESFORCE_RESOURCE_QUERY_URI(
            user_sf.salesforce_id,
            self.resource_type,
            ["Id"],
            additional_filters=[
                *self.adapter_class.additional_filters(),
                operand_groups,
            ],
        )
        print(f"{user_sf.instance_url}{q}")
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
            recipient_type="USER_LEVEL",
            alert_targets=["SELF"],
        )

        if hasattr(user, "salesforce_account"):
            try:
                _process_check_alert.now(
                    str(c.id), str(user.id), self.invocation, datetime.datetime.now(pytz.utc)
                )
            except Exception as e:
                logger.info(f"Failed to send test alert for user {user.email} {e}")
                return c.delete()
        # delete after test is over
        c.delete()

    def config_user_group(self, config_id):
        """returns the users who will be receiving the messages based on the config"""
        config = self.configs.filter(id=config_id).first()
        if config:
            return config.recipient_users

    def config_run_against_date(self, config_id):
        """returns the date against which the query is executed"""
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
        choices=(
            ("AND", "AND"),
            ("OR", "OR"),
        ),
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
        """returns a grouped qs of operand rows (in ())"""
        q_s = f"({' '.join([operand.query_str(config_id) for operand in self.operands.all()])})"
        if self.group_order != 0:
            q_s = f"{self.group_condition} {q_s}"
        return q_s

    def delete(self, *args, **kwargs):
        current_item_order = self.group_order
        items_in_template = (
            self.template.groups.exclude(id=self.id)
            .filter(group_order__gte=current_item_order)
            .order_by("group_order")
        )
        for index, operand in enumerate(items_in_template):
            operand.group_order = current_item_order + index
            if operand.group_order == 0:
                operand.group_condition = "OR"
            operand.save()

        return super(AlertGroup, self).delete(*args, **kwargs)


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
        choices=(
            ("AND", "AND"),
            ("OR", "OR"),
        ),
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
        """gathers different parts of operand and constructs query"""
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
        elif self.data_type == "STRING" and self.operand_value != "null":

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

    @property
    def operand_identifier_ref(self):
        if self.operand_identifier:
            return self.group.template.user.imported_sobjectfield.filter(
                api_name=self.operand_identifier,
                salesforce_object=self.group.template.resource_type,
            ).first()
        return None

    def save(self, *args, **kwargs):

        return super(AlertOperand, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        current_item_order = self.operand_order
        items_in_template = (
            self.group.operands.exclude(id=self.id)
            .filter(operand_order__gte=current_item_order)
            .order_by("operand_order")
        )
        for index, operand in enumerate(items_in_template):
            operand.operand_order = current_item_order + index
            if operand.operand_order == 0:
                operand.operand_condition = "OR"
            operand.save()

        return super(AlertOperand, self).delete(*args, **kwargs)


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
    recurrence_day = models.SmallIntegerField(help_text="day of week/ month", null=True, blank=True)
    recurrence_days = ArrayField(models.SmallIntegerField(), default=default_days)
    recipients = ArrayField(
        models.CharField(max_length=255),
        default=list,
        help_text="Currently UI will only send one recipient will change in the future",
    )
    template = models.ForeignKey(
        "alerts.AlertTemplate", on_delete=models.CASCADE, related_name="configs"
    )
    recipient_type = models.CharField(max_length=255, default="USER_LEVEL")
    alert_targets = ArrayField(models.CharField(max_length=255), default=list)

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
            if today_weekday in self.recurrence_days:
                # calculate the specific date wanted based on day of week
                # day_diff = int(self.recurrence_day) - today_weekday
                return timezone.now()
            return timezone.now()
        elif self.recurrence_frequency == "MONTHLY":
            d = timezone.now()
            d_range = monthrange(d.year, d.month)
            if self.recurrence_day > d_range[1]:
                # aka if the month does not have 31 or is 28 and is greater than 28 days
                diff = self.recurrence_day - d_range[1]

                return timezone() + relativedelta(days=diff)
            else:
                return datetime.datetime(year=d.year, month=d.month, day=self.recurrence_day)

        return timezone.now()

    def add_to_recurrence_days(self):
        if self.recurrence_frequency == "WEEKLY":
            self.recurrence_days = [self.recurrence_day]
        return self.save()

    @property
    def target_users(self):
        query = Q()
        user_ids_to_include = []
        for target in self.alert_targets:
            if target == "SELF":
                user_ids_to_include.append(self.template.user.id)
            elif target == "MANAGERS":
                query |= Q(user_level=core_consts.USER_LEVEL_MANAGER, is_active=True)
            elif target == "REPS":
                query |= Q(user_level=core_consts.USER_LEVEL_REP, is_active=True)
            elif target == "ALL":
                query |= Q(is_active=True)
            elif target == "SDR":
                query |= Q(user_level=core_consts.USER_LEVEL_SDR, is_active=True)
            else:
                user_ids_to_include.append(target)
        if len(user_ids_to_include):
            query |= Q(id__in=user_ids_to_include, is_active=True)
        return self.template.user.organization.users.filter(query).distinct()

    def calculate_scheduled_time_for_alert(self, user):
        user_tz = user.timezone
        user_7am_naive = timezone.now().replace(
            hour=7, minute=0, second=0, microsecond=0, tzinfo=None
        )
        user_7am = timezone.make_aware(user_7am_naive, timezone=pytz.timezone(user_tz))
        utc_time_from_user_7_am = user_7am.astimezone(pytz.timezone("UTC"))
        return utc_time_from_user_7_am


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
        "alerts.AlertTemplate",
        on_delete=models.CASCADE,
        related_name="instances",
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
    channel = models.CharField(
        null=True, max_length=255, help_text="Channel the alert should be sent to added 06/30/21"
    )
    config = models.ForeignKey(
        "alerts.AlertConfig",
        on_delete=models.SET_NULL,
        related_name="instances",
        help_text="Config was set on 06/30/21 and will only have data for that date",
        null=True,
    )
    invocation = models.PositiveIntegerField(
        default=0,
        help_text="Keeps track of the number of times this alert has been triggered, this is used to inform the workspace and paginate slack views",
    )
    completed = models.BooleanField(default=False)

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
        """takes the message template body and renders"""

        body = self.template.message_template.body

        body = convertToSlackFormat(body)
        for k, v in self.var_binding_map.items():
            str_rep = "{ " + k + " }"
            str_rep = r"{}".format(str_rep)

            body = body.replace(str_rep, str(v))
        return body

    @property
    def var_binding_map(self):
        """takes set of variable bindings and replaces them with the value"""
        binding_map = dict()
        attempts = 1
        while True:
            try:
                current_values = self.resource.get_current_values()
                for binding in self.template.message_template.bindings:
                    ## collect all valid bindings
                    try:
                        k, v = binding.split(".")
                        if k != self.template.resource_type and k != "__Recipient":
                            continue
                        if k == self.template.resource_type and hasattr(
                            self.user, "salesforce_account"
                        ):
                            # if field does not exist set to strike through field with N/A
                            # binding_map[binding] = self.resource.secondary_data.get(v, "~None~")
                            binding_map[binding] = current_values.secondary_data.get(v, "~None~")
                            # if field value is None or blank set to empty or no value
                            if binding_map[binding] in ["", None]:
                                binding_map[binding] = "~None~"
                            # HACK pb for datetime fields Mike wants just the date
                            user = self.user
                            if self.resource.secondary_data.get(v):
                                field = user.salesforce_account.object_fields.filter(
                                    api_name=v
                                ).first()
                                if field and field.data_type == "DateTime":
                                    binding_map[binding] = binding_map[binding][0:10]

                        elif k == "__Recipient":
                            binding_map[binding] = getattr(self.user, v)
                            if binding_map[binding] in ["", None]:
                                binding_map[binding] = f" ~{k} {v} N/A~ "

                    except ValueError:
                        continue
                break

            except TokenExpired:
                if attempts >= 5:
                    logger.exception(
                        f"Failed to retrieve alerts current data for user {str(user.id)} after {attempts} tries"
                    )
                    break
                else:
                    self.user.salesforce_account.regenerate_token()
                    attempts += 1
            except Exception as e:
                return logger.warning(
                    f"Exception occured when pulling current data for render text in alert {self.id} because of {e}"
                )
        return binding_map
