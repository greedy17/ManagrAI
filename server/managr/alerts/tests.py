import json

from django.utils import timezone
from django.test import TestCase
from django.db.models import Q, F, Func, IntegerField, DateField, Sum

from rest_framework.exceptions import ValidationError
from rest_framework.test import APIClient


from managr.core import factories as core_factories
from managr.salesforce.models import SalesforceAuthAccount
from managr.salesforce.adapter.routes import routes as adapter_routes
from managr.salesforce import constants as sf_consts

from . import models as alert_models

TestCase.maxDiff = None


class UserTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = core_factories.UserFactory(is_admin=True)
        temp = {
            "user_id": str(self.admin_user.id),
            "title": "test",
            "is_active": True,
            "resource_type": "Opportunity",
            "alert_level": "ORGANIZATION",
        }
        self.template = alert_models.AlertTemplate.objects.create(**temp)
        grp = {"template_id": str(self.template.id), "group_condition": "AND", "group_order": 0}
        self.group = alert_models.AlertGroup.objects.create(**grp)
        op = {
            "group_id": str(self.group.id),
            "operand_type": "FIELD",
            "operand_order": 0,
            "operand_identifier": "Amount",
            "operand_value": 20,
            "operand_condition": "OR",
            "operand_operator": "=",
            "data_type": "INTEGER",
        }
        self.row = alert_models.AlertOperand.objects.create(**op)
        sf = {
            "user_id": str(self.admin_user.id),
            "access_token": "tewrwerwer",
            "refresh_token": "ewrwerwer",
            "instance_url": "https://testing.com",
            "salesforce_id": "123456",
        }
        self.sf_account = SalesforceAuthAccount.objects.create(**sf)
        self.config = alert_models.AlertConfig.objects.create(
            recurrence_day=timezone.now().weekday(),
            recurrence_frequency="WEEKLY",
            recipients=["SELF"],
            template=self.template,
        )

    def test_operand_row_generates_query_string_wo_cond(self):
        """ 
            Tests that the appropriate qs was built for the row 
            NOTE if row is top group order it will not append operator
        """

        expected = (
            f"{self.row.operand_identifier} {self.row.operand_operator} {self.row.operand_value}"
        )
        self.assertEqual(self.row.query_str(self.config.id), expected)

    def test_operand_row_generates_query_string_w_str_cond(self):
        """ 
            Tests that the appropriate qs was built for the row 
            If data type is string it MUST append ' ' 
            NOTE if row is top group order it will not append operator
        """

        self.row.data_type = "STRING"
        self.row.save()
        expected = (
            f"{self.row.operand_identifier} {self.row.operand_operator} '{self.row.operand_value}'"
        )
        self.assertEqual(self.row.query_str(self.config.id), expected)

    def test_operand_row_generates_query_string_w_cond(self):
        """ 
            Tests that the appropriate qs was built for the row 
            NOTE if row is top group order it will not append operator
        """
        row = alert_models.AlertOperand.objects.create(
            **{
                "group_id": str(self.group.id),
                "operand_type": "FIELD",
                "operand_order": 1,
                "operand_identifier": "Amount",
                "operand_value": "Test",
                "operand_condition": "OR",
                "operand_operator": "=",
            }
        )
        expected = f"{row.operand_condition} {row.operand_identifier} {row.operand_operator} {row.operand_value}"
        self.assertEqual(row.query_str(self.config.id), expected)

    def test_operand_row_generates_date_query_string_w_cond(self):
        """ 
            Tests that the appropriate qs was built for the row 
            NOTE if row is top group order it will not append operator
        """
        row = alert_models.AlertOperand.objects.create(
            **{
                "group_id": str(self.group.id),
                "operand_type": "FIELD",
                "operand_order": 1,
                "operand_identifier": "CloseDate",
                "operand_value": 30,
                "operand_condition": "OR",
                "operand_operator": "=",
                "data_type": "DATE",
            }
        )
        value = (timezone.now() + timezone.timedelta(days=row.operand_value)).strftime("%Y-%m-%d")
        expected = (
            f"{row.operand_condition} {row.operand_identifier} {row.operand_operator} {value}"
        )
        self.assertEqual(row.query_str(self.config.id), expected)

    def test_operand_row_generates_date_query_string_w_cond_negative(self):
        """ 
            Tests that the appropriate qs was built for the row 
            NOTE if row is top group order it will not append operator
        """
        row = alert_models.AlertOperand.objects.create(
            **{
                "group_id": str(self.group.id),
                "operand_type": "FIELD",
                "operand_order": 1,
                "operand_identifier": "CloseDate",
                "operand_value": -30,
                "operand_condition": "OR",
                "operand_operator": "=",
                "data_type": "DATE",
            }
        )
        value = (timezone.now() + timezone.timedelta(days=row.operand_value)).strftime("%Y-%m-%d")
        expected = (
            f"{row.operand_condition} {row.operand_identifier} {row.operand_operator} {value}"
        )
        self.assertEqual(row.query_str(self.config.id), expected)

    def test_operand_row_generates_datetime_query_string_w_cond(self):
        """ 
            Tests that the appropriate qs was built for the row 
            NOTE if row is top group order it will not append operator
        """
        row = alert_models.AlertOperand.objects.create(
            **{
                "group_id": str(self.group.id),
                "operand_type": "FIELD",
                "operand_order": 1,
                "operand_identifier": "CloseDate",
                "operand_value": 30,
                "operand_condition": "OR",
                "operand_operator": "=",
                "data_type": "DATETIME",
            }
        )
        value = (timezone.now() + timezone.timedelta(days=row.operand_value)).strftime(
            "%Y-%m-%dT00:00:00Z"
        )
        end_value = (timezone.now() + timezone.timedelta(days=row.operand_value)).strftime(
            "%Y-%m-%dT11:59:00Z"
        )
        expected = (
            f"{row.operand_identifier} >= {value} AND {row.operand_identifier} <= {end_value}"
        )

        self.assertEqual(row.query_str(self.config.id), expected)

    def test_group_generates_query_string_w_and_cond(self):
        """ 
            Tests that the appropriate qs was built for the row 
            NOTE if row is top group order it will not append operator
        """

        expected = f"AND ({self.row.query_str(self.config.id)})"
        self.assertEqual(self.group.query_str(self.config.id), expected)

    def test_group_generates_url_string(self):
        """ 
            Tests that the appropriate qs was built for the row 
            NOTE if row is top group order it will not append operator
        """
        adapter_class = adapter_routes.get(self.template.resource_type, None)
        additional_filters = [
            *adapter_class.additional_filters(),
            *[group.query_str(self.config.id) for group in self.template.groups.all()],
        ]
        expected = f"{self.sf_account.instance_url}{sf_consts.CUSTOM_BASE_URI}/query/?q=SELECT Id FROM Opportunity WHERE OwnerId = '{self.sf_account.salesforce_id}' {' '.join(additional_filters)} order by LastModifiedDate DESC limit {sf_consts.SALESFORCE_QUERY_LIMIT}"
        self.assertEqual(self.template.url_str(self.admin_user, (self.config.id)), expected)

    def test_cron_config_filter_1(self):
        f = alert_models.AlertConfig.objects.filter(
            Q(template__user__is_active=True, template__is_active=True)
            & Q(
                Q(recurrence_frequency="WEEKLY", recurrence_day=timezone.now().weekday())
                | Q(recurrence_frequency="MONTHLY", recurrence_day=timezone.now().day)
            )
        ).count()
        self.assertEqual(f, 1)

    def test_cron_config_filter_3(self):

        for i in range(2):
            alert_models.AlertConfig.objects.create(
                recurrence_day=timezone.now().weekday(),
                recurrence_frequency="WEEKLY",
                recipients=["SELF"],
                template=self.template,
            )
        f = alert_models.AlertConfig.objects.filter(
            Q(template__user__is_active=True, template__is_active=True)
            & Q(
                Q(recurrence_frequency="WEEKLY", recurrence_day=timezone.now().weekday())
                | Q(recurrence_frequency="MONTHLY", recurrence_day=timezone.now().day)
            )
        ).count()

        self.assertEqual(f, 3)

    def test_cron_config_filter_5(self):

        for i in range(2):
            alert_models.AlertConfig.objects.create(
                recurrence_day=timezone.now().weekday(),
                recurrence_frequency="WEEKLY",
                recipients=["SELF"],
                template=self.template,
            )
        for i in range(2):
            alert_models.AlertConfig.objects.create(
                recurrence_day=timezone.now().day,
                recurrence_frequency="MONTHLY",
                recipients=["SELF"],
                template=self.template,
            )
        f = alert_models.AlertConfig.objects.filter(
            Q(template__user__is_active=True, template__is_active=True)
            & Q(
                Q(recurrence_frequency="WEEKLY", recurrence_day=timezone.now().weekday())
                | Q(recurrence_frequency="MONTHLY", recurrence_day=timezone.now().day)
            )
        ).count()

        self.assertEqual(f, 5)

    def test_cron_config_filter_4(self):

        for i in range(2):
            alert_models.AlertConfig.objects.create(
                recurrence_day=timezone.now().weekday(),
                recurrence_frequency="WEEKLY",
                recipients=["SELF"],
                template=self.template,
            )
        for i in range(2):
            alert_models.AlertConfig.objects.create(
                recurrence_day=timezone.now().day,
                recurrence_frequency="MONTHLY",
                recipients=["SELF"],
                template=self.template,
            )
        conf = self.config
        conf.recurrence_day = (timezone.now() + timezone.timedelta(days=1)).day
        conf.save()
        f = alert_models.AlertConfig.objects.filter(
            Q(template__user__is_active=True, template__is_active=True)
            & Q(
                Q(recurrence_frequency="WEEKLY", recurrence_day=timezone.now().weekday())
                | Q(recurrence_frequency="MONTHLY", recurrence_day=timezone.now().day)
            )
        ).count()

        self.assertEqual(f, 4)
