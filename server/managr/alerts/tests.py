import json
import datetime
import pytz
import random
from dateutil.relativedelta import relativedelta
from calendar import monthrange


from django.utils import timezone
from django.test import TestCase
from django.db.models import Q, F, Func, IntegerField, DateField, Sum

from rest_framework.exceptions import ValidationError
from rest_framework.test import APIClient

from managr.core import factories as core_factories
from managr.alerts.utils.utils import convertToSlackFormat
from managr.organization import factories as org_factories
from managr.opportunity import factories as opp_factories
from managr.salesforce.models import SalesforceAuthAccount
from managr.salesforce.adapter.routes import routes as adapter_routes
from managr.salesforce import constants as sf_consts

from . import models as alert_models

TestCase.maxDiff = None


class UserTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = core_factories.UserFactory(
            is_admin=True, user_level="MANAGER", organization=org_factories.OrganizationFactory()
        )

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

    def test_group_generates_query_string_wo_and_cond(self):
        """
        Tests that the appropriate qs was built for the row
        NOTE if row is top group order it will not append operator
        """

        expected = f"({self.row.query_str(self.config.id)})"
        self.assertEqual(self.group.query_str(self.config.id), expected)

    def test_group_generates_url_string(self):
        """
        Tests that the appropriate qs was built for the row
        NOTE if row is top group order it will not append operator
        """
        adapter_class = adapter_routes.get(self.template.resource_type, None)
        query_items = [group.query_str(self.config.id) for group in self.template.groups.all()]
        query_items = f"AND ({' '.join(query_items)})"
        additional_filters = [*adapter_class.additional_filters(), query_items]
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

    def test_sends_to_self_and_owner_only(self):
        """Expects four instances to be created since both matched but the admin and rep users get the alert the admin user gets 3 and the owner only 1"""
        rep = core_factories.UserFactory(
            is_admin=False, user_level="REP", organization=self.admin_user.organization
        )
        self.assertEqual(rep.organization.id, self.admin_user.organization.id)
        opp_1 = opp_factories.OpportunityFactory(owner=rep)
        opp_2 = opp_factories.OpportunityFactory(owner=self.admin_user)

        conf_1 = alert_models.AlertConfig.objects.create(
            recurrence_day=timezone.now().day,
            recurrence_frequency="MONTHLY",
            recipients=["SELF"],
            template=self.template,
        )
        conf_2 = alert_models.AlertConfig.objects.create(
            recurrence_day=timezone.now().day,
            recurrence_frequency="MONTHLY",
            recipients=["OWNER"],
            template=self.template,
        )

        # we pretend that our query found both opps
        query = Q()
        for opp in [opp_1, opp_2]:
            for setting in [conf_1, conf_2]:
                for user_group in setting.recipients:
                    # if self expects two instances one for each opp matched (2 matched here)
                    if user_group == "SELF":
                        alert_models.AlertInstance.objects.create(
                            template_id=self.template.id,
                            user_id=self.template.user.id,
                            resource_id=str(opp.id),
                            instance_meta={},
                        )
                    # expects 2 since each owner will get 1
                    elif user_group == "OWNER":
                        alert_models.AlertInstance.objects.create(
                            template_id=self.template.id,
                            user_id=opp.owner.id,
                            resource_id=str(opp.id),
                            instance_meta={},
                        )

                    else:
                        ## expects 0
                        if user_group == "MANAGERS":
                            query |= Q(Q(user_level="MANAGER", is_active=True))

                        elif user_group == "REPS":
                            query |= Q(user_level="REP", is_active=True)
                        elif user_group == "ALL":

                            query = Q(is_active=True) & Q(
                                Q(user_level="MANAGER") | Q(user_level="REP")
                            )

                        users = (
                            self.template.user.organization.users.filter(query)
                            .filter(is_active=True)
                            .distinct()
                        )
                        for u in users:
                            alert_models.AlertInstance.objects.create(
                                template_id=self.template.id,
                                user_id=u.id,
                                resource_id=str(opp.id),
                                instance_meta={},
                            )
        self.assertEquals(alert_models.AlertInstance.objects.count(), 4)

    def test_sends_to_self_only(self):
        """Expects two instances to be created since both matched but only the admin user gets the alert"""
        rep = core_factories.UserFactory(
            is_admin=False, user_level="REP", organization=self.admin_user.organization
        )
        self.assertEqual(rep.organization.id, self.admin_user.organization.id)
        opp_1 = opp_factories.OpportunityFactory(owner=rep)
        opp_2 = opp_factories.OpportunityFactory(owner=self.admin_user)

        conf_1 = alert_models.AlertConfig.objects.create(
            recurrence_day=timezone.now().day,
            recurrence_frequency="MONTHLY",
            recipients=["SELF"],
            template=self.template,
        )

        # we pretend that our query found both opps

        for opp in [opp_1, opp_2]:
            for setting in [conf_1]:
                for user_group in setting.recipients:
                    # if self expects two instances one for each opp matched (2 matched here)
                    if user_group == "SELF":
                        alert_models.AlertInstance.objects.create(
                            template_id=self.template.id,
                            user_id=self.template.user.id,
                            resource_id=str(opp.id),
                            instance_meta={},
                        )
                    # expects 2 since each owner will get 1
                    elif user_group == "OWNER":
                        alert_models.AlertInstance.objects.create(
                            template_id=self.template.id,
                            user_id=opp.owner.id,
                            resource_id=str(opp.id),
                            instance_meta={},
                        )

        self.assertEquals(alert_models.AlertInstance.objects.count(), 2)

    def test_sends_to_owner_only(self):
        """Expects two instances to be created since both matched but only the owning user gets the alert"""
        rep = core_factories.UserFactory(
            is_admin=False, user_level="REP", organization=self.admin_user.organization
        )
        self.assertEqual(rep.organization.id, self.admin_user.organization.id)
        opp_1 = opp_factories.OpportunityFactory(owner=rep)
        opp_2 = opp_factories.OpportunityFactory(owner=self.admin_user)

        conf_1 = alert_models.AlertConfig.objects.create(
            recurrence_day=timezone.now().day,
            recurrence_frequency="MONTHLY",
            recipients=["OWNER"],
            template=self.template,
        )

        # we pretend that our query found both opps
        query = Q()
        for opp in [opp_1, opp_2]:
            for setting in [conf_1]:
                for user_group in setting.recipients:
                    # if self expects two instances one for each opp matched (2 matched here)
                    if user_group == "SELF":
                        alert_models.AlertInstance.objects.create(
                            template_id=self.template.id,
                            user_id=self.template.user.id,
                            resource_id=str(opp.id),
                            instance_meta={},
                        )
                    # expects 2 since each owner will get 1
                    elif user_group == "OWNER":
                        alert_models.AlertInstance.objects.create(
                            template_id=self.template.id,
                            user_id=opp.owner.id,
                            resource_id=str(opp.id),
                            instance_meta={},
                        )

                    else:
                        ## expects 0
                        if user_group == "MANAGERS":
                            query |= Q(Q(user_level="MANAGER", is_active=True))

                        elif user_group == "REPS":
                            query |= Q(user_level="REP", is_active=True)
                        elif user_group == "ALL":

                            query = Q(is_active=True) & Q(
                                Q(user_level="MANAGER") | Q(user_level="REP")
                            )

                        users = (
                            self.template.user.organization.users.filter(query)
                            .filter(is_active=True)
                            .distinct()
                        )
                        for u in users:
                            alert_models.AlertInstance.objects.create(
                                template_id=self.template.id,
                                user_id=u.id,
                                resource_id=str(opp.id),
                                instance_meta={},
                            )
        self.assertEquals(alert_models.AlertInstance.objects.count(), 2)

    def test_sends_to_is_admin_user_only(self):
        """Expects 1 instance to be created from the rep's opp"""
        rep = core_factories.UserFactory(
            is_admin=False, user_level="REP", organization=self.admin_user.organization
        )
        self.assertEqual(rep.organization.id, self.admin_user.organization.id)
        opp_1 = opp_factories.OpportunityFactory(owner=rep)

        conf_1 = alert_models.AlertConfig.objects.create(
            recurrence_day=timezone.now().day,
            recurrence_frequency="MONTHLY",
            recipients=["SELF"],
            template=self.template,
        )

        # we pretend that our query found both opps
        for opp in [opp_1]:
            for setting in [conf_1]:
                for user_group in setting.recipients:
                    # if self expects two instances one for each opp matched (2 matched here)
                    if user_group == "SELF":
                        alert_models.AlertInstance.objects.create(
                            template_id=self.template.id,
                            user_id=self.template.user.id,
                            resource_id=str(opp.id),
                            instance_meta={},
                        )
                    # expects 2 since each owner will get 1
                    elif user_group == "OWNER":
                        alert_models.AlertInstance.objects.create(
                            template_id=self.template.id,
                            user_id=opp.owner.id,
                            resource_id=str(opp.id),
                            instance_meta={},
                        )

        self.assertEquals(alert_models.AlertInstance.objects.count(), 1)
        self.assertEquals(alert_models.AlertInstance.objects.first().user.id, self.template.user.id)

    def test_sends_to_managers_only(self):
        """Expects 4 instances to be created since both matched but there are only 3 managers and 1 is inactive"""
        rep = core_factories.UserFactory(
            is_admin=False, user_level="REP", organization=self.admin_user.organization
        )
        core_factories.UserFactory(
            is_admin=False, user_level="MANAGER", organization=self.admin_user.organization
        )
        core_factories.UserFactory(
            is_admin=False,
            user_level="MANAGER",
            organization=self.admin_user.organization,
            is_active=False,
        )

        self.assertEqual(rep.organization.id, self.admin_user.organization.id)
        opp_1 = opp_factories.OpportunityFactory(owner=rep)
        opp_2 = opp_factories.OpportunityFactory(owner=self.admin_user)

        conf_1 = alert_models.AlertConfig.objects.create(
            recurrence_day=timezone.now().day,
            recurrence_frequency="MONTHLY",
            recipients=["MANAGERS"],
            template=self.template,
        )

        # we pretend that our query found both opps
        query = Q()
        for opp in [opp_1, opp_2]:
            for setting in [conf_1]:
                for user_group in setting.recipients:
                    # if self expects two instances one for each opp matched (2 matched here)
                    if user_group == "SELF":
                        alert_models.AlertInstance.objects.create(
                            template_id=self.template.id,
                            user_id=self.template.user.id,
                            resource_id=str(opp.id),
                            instance_meta={},
                        )
                    # expects 2 since each owner will get 1
                    elif user_group == "OWNER":
                        alert_models.AlertInstance.objects.create(
                            template_id=self.template.id,
                            user_id=opp.owner.id,
                            resource_id=str(opp.id),
                            instance_meta={},
                        )

                    else:
                        ## expects 0
                        if user_group == "MANAGERS":
                            query |= Q(Q(user_level="MANAGER", is_active=True))

                        elif user_group == "REPS":
                            query |= Q(user_level="REP", is_active=True)
                        elif user_group == "ALL":

                            query = Q(is_active=True) & Q(
                                Q(user_level="MANAGER") | Q(user_level="REP")
                            )

                        users = self.template.user.organization.users.filter(query).distinct()
                        for u in users:
                            alert_models.AlertInstance.objects.create(
                                template_id=self.template.id,
                                user_id=u.id,
                                resource_id=str(opp.id),
                                instance_meta={},
                            )
        self.assertEquals(alert_models.AlertInstance.objects.count(), 4)

    def test_sends_to_SDR_only(self):
        """Expects there two be 2 alerts for the SDR since there are two opportunites"""
        sdr = core_factories.UserFactory(
            is_admin=False, user_level="SDR", organization=self.admin_user.organization
        )
        rep = core_factories.UserFactory(
            is_admin=False, user_level="REP", organization=self.admin_user.organization
        )

        self.assertEqual(sdr.organization.id, self.admin_user.organization.id)
        opp_1 = opp_factories.OpportunityFactory(owner=rep)
        opp_2 = opp_factories.OpportunityFactory(owner=self.admin_user)

        conf_1 = alert_models.AlertConfig.objects.create(
            recurrence_day=timezone.now().day,
            recurrence_frequency="MONTHLY",
            recipients=["SDR"],
            template=self.template,
        )

        # we pretend that our query found both opps
        query = Q()
        for opp in [opp_1, opp_2]:
            for setting in [conf_1]:
                for user_group in setting.recipients:
                    if user_group == "SELF":
                        alert_models.AlertInstance.objects.create(
                            template_id=self.template.id,
                            user_id=self.template.user.id,
                            resource_id=str(opp.id),
                            instance_meta={},
                        )
                    elif user_group == "OWNER":
                        alert_models.AlertInstance.objects.create(
                            template_id=self.template.id,
                            user_id=opp.owner.id,
                            resource_id=str(opp.id),
                            instance_meta={},
                        )

                    else:
                        ## expects 2 since both alerts are for the SDR
                        if user_group == "MANAGERS":
                            query |= Q(Q(user_level="MANAGER", is_active=True))

                        elif user_group == "REPS":
                            query |= Q(user_level="REP", is_active=True)

                        elif user_group == "SDR":
                            query |= Q(user_level="SDR", is_active=True)

                        elif user_group == "ALL":

                            query = Q(is_active=True) & Q(
                                Q(user_level="MANAGER") | Q(user_level="REP")
                            )

                        users = self.template.user.organization.users.filter(query).distinct()
                        for u in users:
                            alert_models.AlertInstance.objects.create(
                                template_id=self.template.id,
                                user_id=u.id,
                                resource_id=str(opp.id),
                                instance_meta={},
                            )
        self.assertEquals(alert_models.AlertInstance.objects.count(), 2)

    def test_group_generates_url_string_w_weekly(self):
        """
        Tests that the appropriate qs was built for the row
        NOTE if row is top group order it will not append operator
        """
        conf_1 = alert_models.AlertConfig.objects.create(
            recurrence_day=3,
            recurrence_frequency="WEEKLY",
            recipients=["MANAGERS"],
            template=self.template,
        )
        adapter_class = adapter_routes.get(self.template.resource_type, None)
        query_items = [group.query_str(self.config.id) for group in self.template.groups.all()]
        query_items = f"AND ({' '.join(query_items)})"
        additional_filters = [*adapter_class.additional_filters(), query_items]
        expected = f"{self.sf_account.instance_url}{sf_consts.CUSTOM_BASE_URI}/query/?q=SELECT Id FROM Opportunity WHERE OwnerId = '{self.sf_account.salesforce_id}' {' '.join(additional_filters)} order by LastModifiedDate DESC limit {sf_consts.SALESFORCE_QUERY_LIMIT}"
        self.assertEqual(self.template.url_str(self.admin_user, str(conf_1.id)), expected)

    def test_url_str_run_now_monthly(self):
        temp = {
            "user_id": str(self.admin_user.id),
            "title": "test",
            "is_active": True,
            "resource_type": "Opportunity",
            "alert_level": "ORGANIZATION",
        }
        template = alert_models.AlertTemplate.objects.create(**temp)
        grp = {"template_id": str(template.id), "group_condition": "AND", "group_order": 0}
        group = alert_models.AlertGroup.objects.create(**grp)
        op = {
            "group_id": str(group.id),
            "operand_type": "FIELD",
            "operand_order": 0,
            "operand_identifier": "CloseDate",
            "operand_value": 2,
            "operand_condition": "OR",
            "operand_operator": ">",
            "data_type": "DATE",
        }
        alert_models.AlertOperand.objects.create(**op)

        conf_1 = alert_models.AlertConfig.objects.create(
            recurrence_day=27,
            recurrence_frequency="MONTHLY",
            recipients=["SELF"],
            template=template,
        )
        adapter_class = adapter_routes.get(template.resource_type, None)
        additional_filters = adapter_class.additional_filters()
        current_date_filter = f"AND ((CloseDate > {datetime.datetime(day=29,month=timezone.now().month,year=timezone.now().year).strftime('%Y-%m-%d')}))"
        expected = f"{self.sf_account.instance_url}{sf_consts.CUSTOM_BASE_URI}/query/?q=SELECT Id FROM Opportunity WHERE OwnerId = '{self.sf_account.salesforce_id}' {' '.join(additional_filters)} {current_date_filter} order by LastModifiedDate DESC limit {sf_consts.SALESFORCE_QUERY_LIMIT}"
        self.assertEqual(template.url_str(template.user, conf_1.id), expected)

    def test_url_str_run_now_monthly_next_month_31(self):
        """test for month with 31 days should return 6th"""
        temp = {
            "user_id": str(self.admin_user.id),
            "title": "test",
            "is_active": True,
            "resource_type": "Opportunity",
            "alert_level": "ORGANIZATION",
        }
        template = alert_models.AlertTemplate.objects.create(**temp)
        grp = {"template_id": str(template.id), "group_condition": "AND", "group_order": 0}
        group = alert_models.AlertGroup.objects.create(**grp)
        op = {
            "group_id": str(group.id),
            "operand_type": "FIELD",
            "operand_order": 0,
            "operand_identifier": "CloseDate",
            "operand_value": 10,
            "operand_condition": "OR",
            "operand_operator": ">",
            "data_type": "DATE",
        }
        opp = alert_models.AlertOperand.objects.create(**op)

        conf_1 = alert_models.AlertConfig.objects.create(
            recurrence_day=27,
            recurrence_frequency="MONTHLY",
            recipients=["SELF"],
            template=template,
        )
        adapter_class = adapter_routes.get(template.resource_type, None)
        additional_filters = adapter_class.additional_filters()
        d = timezone.now()
        d_range = monthrange(d.year, d.month)
        if conf_1.recurrence_day > d_range[1]:
            # aka if the month does not have 31 or is 28 and is greater than 28 days
            diff = conf_1.recurrence_day - d_range[1]

            d = timezone() + relativedelta(days=diff)
        else:
            d = datetime.datetime(year=d.year, month=d.month, day=conf_1.recurrence_day)
        current_date_filter = f"AND ((CloseDate > {(d+timezone.timedelta(days=opp.operand_value)).strftime('%Y-%m-%d')}))"
        expected = f"{self.sf_account.instance_url}{sf_consts.CUSTOM_BASE_URI}/query/?q=SELECT Id FROM Opportunity WHERE OwnerId = '{self.sf_account.salesforce_id}' {' '.join(additional_filters)} {current_date_filter} order by LastModifiedDate DESC limit {sf_consts.SALESFORCE_QUERY_LIMIT}"
        self.assertEqual(template.url_str(template.user, conf_1.id), expected)

    def test_url_str_run_now_monthly_next_month_30(self):
        """test for month with 31 days should return 1st july taking into account 30 day month"""
        temp = {
            "user_id": str(self.admin_user.id),
            "title": "test",
            "is_active": True,
            "resource_type": "Opportunity",
            "alert_level": "ORGANIZATION",
        }
        template = alert_models.AlertTemplate.objects.create(**temp)
        grp = {"template_id": str(template.id), "group_condition": "AND", "group_order": 0}
        group = alert_models.AlertGroup.objects.create(**grp)
        op = {
            "group_id": str(group.id),
            "operand_type": "FIELD",
            "operand_order": 0,
            "operand_identifier": "CloseDate",
            "operand_value": 35,
            "operand_condition": "OR",
            "operand_operator": ">",
            "data_type": "DATE",
        }
        opp = alert_models.AlertOperand.objects.create(**op)

        conf_1 = alert_models.AlertConfig.objects.create(
            recurrence_day=27,
            recurrence_frequency="MONTHLY",
            recipients=["SELF"],
            template=template,
        )
        adapter_class = adapter_routes.get(template.resource_type, None)
        additional_filters = adapter_class.additional_filters()
        d = timezone.now()
        d_range = monthrange(d.year, d.month)
        if conf_1.recurrence_day > d_range[1]:
            # aka if the month does not have 31 or is 28 and is greater than 28 days
            diff = conf_1.recurrence_day - d_range[1]

            d = timezone() + relativedelta(days=diff)
        else:
            d = datetime.datetime(year=d.year, month=d.month, day=conf_1.recurrence_day)
        current_date_filter = f"AND ((CloseDate > {(d+timezone.timedelta(days=opp.operand_value)).strftime('%Y-%m-%d')}))"
        expected = f"{self.sf_account.instance_url}{sf_consts.CUSTOM_BASE_URI}/query/?q=SELECT Id FROM Opportunity WHERE OwnerId = '{self.sf_account.salesforce_id}' {' '.join(additional_filters)} {current_date_filter} order by LastModifiedDate DESC limit {sf_consts.SALESFORCE_QUERY_LIMIT}"
        self.assertEqual(template.url_str(template.user, conf_1.id), expected)

    def test_formatting_bindings(self):
        original_text = "This text should render like <strong>this</strong>"
        original_text_1 = "This text should render like <em>this</em>"
        original_text_2 = "This text should render like <s>this</s>"
        original_text_3 = "This text should render like<strong>this</strong>"
        original_text_4 = "This text should render like<em>this</em>"
        original_text_5 = "This text should render like<s>this</s>"
        original_text_6 = "This text should render like <em>this</em>"
        original_text_7 = "This text should render like <s>this</s>"
        original_text_8 = "This text should render like<strong>this</strong>"
        original_text_9 = "This text should render like<em> this</em>"
        original_text_10 = "This text should render like<s> this</s>"
        original_text_11 = "This text should render like<s>{ this }</s>"
        original_text_12 = "<s>This text should render like{ this }</s>"
        original_text_13 = "<strong>This</strong> <em>text</em> <strong><em>should render</em></strong> like{ this }"

        sample_text = "This text should render like *this*"
        sample_text_1 = "This text should render like _this_"
        sample_text_2 = "This text should render like ~this~"
        sample_text_3 = "This text should render like*this*"
        sample_text_4 = "This text should render like_this_"
        sample_text_5 = "This text should render like~this~"
        sample_text_6 = "This text should render like _this_"
        sample_text_7 = "This text should render like ~this~"
        sample_text_8 = "This text should render like*this*"
        sample_text_9 = "This text should render like_this_"
        sample_text_10 = "This text should render like~this~"
        sample_text_11 = "This text should render like ~{ this }~"
        sample_text_12 = "~This text should render like{ this }~"
        sample_text_13 = "*This* _text_ *_should render_* like{ this }"

        self.assertEqual(convertToSlackFormat(original_text), sample_text)
        self.assertEqual(convertToSlackFormat(original_text_1), sample_text_1)
        self.assertEqual(convertToSlackFormat(original_text_2), sample_text_2)
        self.assertEqual(convertToSlackFormat(original_text_3), sample_text_3)
        self.assertEqual(convertToSlackFormat(original_text_4), sample_text_4)
        self.assertEqual(convertToSlackFormat(original_text_5), sample_text_5)
        self.assertEqual(convertToSlackFormat(original_text_6), sample_text_6)
        self.assertEqual(convertToSlackFormat(original_text_7), sample_text_7)
        self.assertEqual(convertToSlackFormat(original_text_8), sample_text_8)
        self.assertEqual(convertToSlackFormat(original_text_9), sample_text_9)
        self.assertEqual(convertToSlackFormat(original_text_10), sample_text_10)
        self.assertEqual(convertToSlackFormat(original_text_11), sample_text_11)
        self.assertEqual(convertToSlackFormat(original_text_12), sample_text_12)
        self.assertEqual(convertToSlackFormat(original_text_13), sample_text_13)

    def test_field_bindings(self):

        opp_2 = opp_factories.OpportunityFactory(owner=self.admin_user)
        opp_2.secondary_data = {
            "Id": "0065w000025aEK6AAM",
            "Company": "T",
            "Name": "Amazon",
            "Type": None,
            "IsWon": False,
            "Amount": 480000.0,
            "CRM__c": None,
            "Fiscal": "2021 2",
            "OwnerId": "0055w00000BiLWwAAN",
            "IsClosed": False,
            "NextStep": None,
            "Video__c": None,
            "AccountId": "0015w00002TgeyYAAR",
            "CloseDate": "2021-06-02",
            "ContactId": None,
            "IsDeleted": False,
            "StageName": "Ready",
            "CampaignId": None,
            "FiscalYear": 2021,
            "Handoff__c": None,
            "LeadSource": None,
            "Package__c": None,
            "CreatedById": "0055w00000BiLWwAAN",
            "CreatedDate": "2021-05-27T13:50:24.000+0000",
            "Description": None,
            "Probability": 0.0,
            "Messanger__c": None,
            "Pricebook2Id": None,
            "RecordTypeId": "0125w000000GGd5AAG",
            "FiscalQuarter": 2,
            "Multi_Test__c": None,
            "SyncedQuoteId": None,
            "Competitors__c": None,
            "HasOverdueTask": False,
            "LastViewedDate": "2021-05-27T13:59:29.000+0000",
            "SystemModstamp": "2021-05-27T13:59:29.000+0000",
            "HasOpenActivity": False,
            "ForecastCategory": "Pipeline",
            "LastActivityDate": None,
            "LastModifiedById": "0055w00000BiLWwAAN",
            "LastModifiedDate": "2021-05-27T13:59:29.000+0000",
            "Next_Step_Date__c": None,
            "Agreement_Notes__c": None,
            "LastReferencedDate": "2021-05-27T13:59:29.000+0000",
            "ForecastCategoryName": "Pipeline",
            "OpportunityHistories": {
                "done": True,
                "records": [
                    {
                        "Id": "0085w000041qLB3AAM",
                        "attributes": {
                            "url": "/services/data/v50.0/sobjects/OpportunityHistory/0085w000041qLB3AAM",
                            "type": "OpportunityHistory",
                        },
                        "CreatedDate": "2021-05-27T13:59:29.000+0000",
                    }
                ],
                "totalSize": 1,
            },
            "managr__Heroku_id__c": None,
            "HasOpportunityLineItem": False,
            "Last_Correspondence__c": None,
            "OpportunityContactRoles": None,
            "managr__Managr_Amount__c": None,
            "LastAmountChangedHistoryId": None,
            "Last_Correspondence_Date__c": None,
            "managr__Heroku_id_formula__c": None,
            "LastCloseDateChangedHistoryId": "0085w000041qLB3AAM",
            "managr__Managr_Account_Id_Formula__c": None,
        }
        opp_2.save()
        message_templ = alert_models.AlertMessageTemplate.objects.create(
            template=self.template,
            bindings=[
                "__Recipient.first_name",
                "Opportunity.Company",
                "Opportunity.LastModifiedDate",
                "Opportunity.Competitors__c",
                "Opportunity.Last_Correspondence__c",
                "Opportunity.Last_Correspondence_Date__c",
                "Opportunity.Last_Correspondence_Date__c",
                "Opportunity.num_of_Outreach__c",
                "Opportunity.Outreach_Type__c",
                "Opportunity.Last_Outreach_Date__c",
            ],
            notification_text="POP UP",
            body="<p>Hey { __Recipient.first_name } <strong>{ Opportunity.Company }</strong> hasn't been worked in over 10 days, last touched on <strong>{ Opportunity.LastModifiedDate }</strong>. They are using <strong>{ Opportunity.Competitors__c } </strong>last correspondence was<em> { Opportunity.Last_Correspondence__c }</em>, which took place on { Opportunity.Last_Correspondence_Date__c }. You have reached out <strong>{ Opportunity.num_of_Outreach__c }</strong> times via <em>{ Opportunity.Outreach_Type__c },</em> last time was on <em>{ Opportunity.Last_Outreach_Date__c }</em></p>",
        )
        expected = f"Hey {self.admin_user.first_name} *T* hasn't been worked in over 10 days, last touched on *{opp_2.secondary_data.get('LastModifiedDate', '~None~')}* . They are using *~None~* last correspondence was _~None~_ , which took place on ~None~. You have reached out *~None~* times via _~None~,_ last time was on _~None~_\n"
        instance = alert_models.AlertInstance.objects.create(
            template_id=self.template.id,
            user_id=self.admin_user.id,
            resource_id=str(opp_2.id),
            instance_meta={},
        )
        self.assertEqual(expected, instance.render_text())
        return

    def test_config_returns_correct_send_time_7am_local(self):
        temp = {
            "user_id": str(self.admin_user.id),
            "title": "test",
            "is_active": True,
            "resource_type": "Opportunity",
            "alert_level": "ORGANIZATION",
        }
        template = alert_models.AlertTemplate.objects.create(**temp)
        grp = {"template_id": str(template.id), "group_condition": "AND", "group_order": 0}
        group = alert_models.AlertGroup.objects.create(**grp)
        op = {
            "group_id": str(group.id),
            "operand_type": "FIELD",
            "operand_order": 0,
            "operand_identifier": "CloseDate",
            "operand_value": 2,
            "operand_condition": "OR",
            "operand_operator": ">",
            "data_type": "DATE",
        }
        alert_models.AlertOperand.objects.create(**op)

        conf_1 = alert_models.AlertConfig.objects.create(
            recurrence_day=27,
            recurrence_frequency="MONTHLY",
            recipients=["SELF"],
            template=template,
        )
        for index in range(0, 6):
            tz = pytz.all_timezones[random.randint(0, 10)]
            self.admin_user.timezone = tz
            self.admin_user.save()
            today = datetime.datetime.now()
            self.assertEqual(
                datetime.datetime(
                    today.year, today.month, today.day, 7, 0, tzinfo=pytz.timezone(tz)
                ).astimezone(pytz.utc),
                conf_1.calculate_scheduled_time_for_alert(self.admin_user),
            )
