from rest_framework.exceptions import ValidationError
from django.utils import timezone
from django.test import TestCase
from django.core.management import call_command

from django.test import RequestFactory
from django.test import Client

from rest_framework.authtoken.models import Token

from managr.core.factories import UserFactory
from managr.lead.factories import LeadFactory, LeadActivityLogFactory
from managr.organization.models import Organization, Stage
from managr.organization.factories import (
    AccountFactory,
    ContactFactory,
    OrganizationFactory,
)

from managr.lead.models import Notification, LeadActivityLog
from managr.lead import constants as lead_consts
from managr.organization import constants as org_consts
from .models import NotificationOption, NotificationSelection
from .serializers import EmailSerializer
from . import constants as core_consts
from .cron import _check_days_lead_expected_close_lapsed


class MockRequest:
    def __init__(self, user):
        self.user = user


class EmailSerializerTestCase(TestCase):
    # The fixture provides a test user and org
    fixtures = ["dev.json"]

    def setUp(self):
        self.org = Organization.objects.first()
        self.user = self.org.users.first()

        # Create some lead-related data
        self.account = AccountFactory(organization=self.org)
        self.contact_1 = ContactFactory(account=self.account)
        self.contact_2 = ContactFactory(account=self.account)
        self.contact_3 = ContactFactory(account=self.account)
        self.lead = LeadFactory(account=self.account)

        # This is the minimum valid data
        self.valid_data = {
            "subject": "Hello World",
            "body": "Hello World - Body of Email",
            "to": [{"name": "Foo Bar", "email": "foo@test.com",}],
            "lead": str(self.lead.id),
        }

        # We also need a mock Request object
        self.request = MockRequest(self.user)

    def test_validation(self):
        """Valid data should pass validation."""
        serializer = EmailSerializer(
            data=self.valid_data, context={"request": self.request}
        )
        self.assertEqual(serializer.is_valid(raise_exception=True), True)

    def test_validate_to_contact_dict(self):
        self.valid_data["to"] = ["foo@test.com"]
        serializer = EmailSerializer(
            data=self.valid_data, context={"request": self.request}
        )
        with self.assertRaises(ValidationError) as error:
            serializer.is_valid(raise_exception=True)
        self.assertEqual(
            str(error.exception),
            "{'to': {0: [ErrorDetail(string='Expected a dictionary of items but got type \"str\".', code='not_a_dict')]}}",
        )


class AlertsTestCase(TestCase):
    fixtures = ["notification_options_fixture.json", "dev.json"]

    def setUp(self):
        self.org = OrganizationFactory()
        self.manager = UserFactory(organization=self.org, type="MANAGER")
        self.rep = UserFactory(organization=self.org, type="REP")
        self.account = AccountFactory(organization=self.org)
        self.lead_1 = LeadFactory(account=self.account, claimed_by=self.rep)
        self.lead_2 = LeadFactory(account=self.account)

    # test the functions that drive some of the notification creations ####

    def test_returns_correct_late_lapse(self):
        expected_close_date = timezone.now() - timezone.timedelta(days=2)
        self.lead_1.expected_close_date = expected_close_date
        self.lead_1.save()
        self.assertEqual(_check_days_lead_expected_close_lapsed(expected_close_date), 2)
        expected_close_date = timezone.now() + timezone.timedelta(days=2)
        self.lead_1.expected_close_date = expected_close_date
        self.lead_1.save()
        self.assertEqual(_check_days_lead_expected_close_lapsed(expected_close_date), 0)
        expected_close_date = timezone.now() - timezone.timedelta(days=14)
        self.lead_1.expected_close_date = expected_close_date
        self.lead_1.save()
        self.assertEqual(
            _check_days_lead_expected_close_lapsed(expected_close_date), 14
        )

    def test_returns_correct_late_laps_group(self):
        # >=1x<14 1
        # >=14x<30 14
        # >=30 30
        expected_close_date = timezone.now() - timezone.timedelta(days=2)
        is_lapsed = _check_days_lead_expected_close_lapsed(expected_close_date)
        late = 0
        if is_lapsed >= 1 and is_lapsed < 14:
            late = 1
        elif is_lapsed >= 14 and is_lapsed < 30:
            late = 14
        elif is_lapsed >= 30:
            late = 30
        self.assertEqual(late, 1)
        expected_close_date = timezone.now() - timezone.timedelta(days=14)
        is_lapsed = _check_days_lead_expected_close_lapsed(expected_close_date)

        late = 0
        if is_lapsed >= 1 and is_lapsed < 14:
            late = 1
        elif is_lapsed >= 14 and is_lapsed < 30:
            late = 14
        elif is_lapsed >= 30:
            late = 30
        self.assertEqual(late, 14)
        expected_close_date = timezone.now() - timezone.timedelta(days=30)
        is_lapsed = _check_days_lead_expected_close_lapsed(expected_close_date)
        late = 0
        if is_lapsed >= 1 and is_lapsed < 14:
            late = 1
        elif is_lapsed >= 14 and is_lapsed < 30:
            late = 14
        elif is_lapsed >= 30:
            late = 30
        self.assertEqual(late, 30)

    def test_no_alerts_for_users(self):
        """ no alerts should be triggered concerning leads """
        call_command("createleadnotifications")
        self.assertEqual(Notification.objects.count(), 0)

    def test_all_alert_inactive(self):
        """ sets the latest activity to -100 to trigger the 90 day inactivity 
        this should create two new notifications for the rep and the manager (one each)
        """
        time_occured = timezone.now() - timezone.timedelta(days=100)
        activity = LeadActivityLogFactory(
            action_timestamp=time_occured, action_taken_by=self.rep
        )
        self.lead_1.activity_logs.add(activity)
        self.assertEqual(
            LeadActivityLog.objects.latest("action_timestamp").id, activity.id
        )
        call_command("createleadnotifications")
        self.assertEqual(Notification.objects.count(), 2)
        self.assertEqual(Notification.objects.filter(user=self.rep).count(), 1)
        self.assertEqual(Notification.objects.filter(user=self.manager).count(), 1)

    def test_rep_alert_inactive(self):
        """ sets the latest activity to -100 to trigger the 90 day inactivity 
        also sets manager user's notification settings to not alert on this trigger
        this should create one new notification for the rep only
        """
        time_occured = timezone.now() - timezone.timedelta(days=100)
        activity = LeadActivityLogFactory(
            action_timestamp=time_occured, action_taken_by=self.rep
        )
        self.lead_1.activity_logs.add(activity)
        self.assertEqual(
            LeadActivityLog.objects.latest("action_timestamp").id, activity.id
        )
        opt = NotificationOption.objects.get(
            pk=core_consts.NOTIFICATION_OPTION_INACTIVE_ID
        )

        selection = NotificationSelection.objects.create(
            option=opt, user=self.manager, value=False
        )

        self.manager.notification_settings.add(selection)
        call_command("createleadnotifications")
        self.assertEqual(Notification.objects.count(), 1)
        self.assertEqual(Notification.objects.filter(user=self.rep).count(), 1)
        self.assertEqual(Notification.objects.filter(user=self.manager).count(), 0)

    def test_rep_no_alert_inactive_unclaimed_lead(self):
        """ sets the latest activity to -100 to trigger the 90 day inactivity 
        also sets manager user's notification settings to not alert on this trigger
        this should create one new notification for the rep only
        """
        time_occured = timezone.now() - timezone.timedelta(days=100)
        activity = LeadActivityLogFactory(
            action_timestamp=time_occured, action_taken_by=self.rep
        )
        self.lead_2.activity_logs.add(activity)
        self.assertEqual(
            LeadActivityLog.objects.latest("action_timestamp").id, activity.id
        )
        opt = NotificationOption.objects.get(
            pk=core_consts.NOTIFICATION_OPTION_INACTIVE_ID
        )

        selection = NotificationSelection.objects.create(
            option=opt, user=self.manager, value=False
        )

        self.manager.notification_settings.add(selection)
        call_command("createleadnotifications")
        self.assertEqual(Notification.objects.count(), 0)

    def test_all_alert_stalled_in_stage(self):
        """ sets the latest status update to trigger the 60 day stalled 
        this should create two new notifications for the rep and the manager (one each)
        """
        stalled_date = timezone.now() - timezone.timedelta(days=65)
        self.lead_1.status_last_update = stalled_date
        self.lead_1.save()
        call_command("createleadnotifications")
        self.assertEqual(Notification.objects.count(), 2)
        self.assertEqual(Notification.objects.filter(user=self.rep).count(), 1)
        self.assertEqual(Notification.objects.filter(user=self.manager).count(), 1)

    def test_rep_alert_stalled_in_stage(self):
        """ sets the latest status update to trigger the 60 day stalled 
         also sets manager user's notification settings to not alert on this trigger
        this should create one new notification for the rep only
        """
        stalled_date = timezone.now() - timezone.timedelta(days=65)
        self.lead_1.status_last_update = stalled_date
        self.lead_1.save()
        opt = NotificationOption.objects.get(
            pk=core_consts.NOTIFICATION_OPTION_STALLED_IN_STAGE_ID
        )

        selection = NotificationSelection.objects.create(
            option=opt, user=self.manager, value=False
        )

        self.manager.notification_settings.add(selection)
        call_command("createleadnotifications")
        self.assertEqual(Notification.objects.count(), 1)
        self.assertEqual(Notification.objects.filter(user=self.rep).count(), 1)
        self.assertEqual(Notification.objects.filter(user=self.manager).count(), 0)

    def test_all_alert_days_1(self):
        """ sets the expected close date to be 1 day late
        this should create two new notifications for the rep and the manager (one each)
        """
        expected_close_date = timezone.now() - timezone.timedelta(days=2)

        self.lead_1.expected_close_date = expected_close_date
        self.lead_1.save()
        call_command("createleadnotifications")
        self.assertEqual(Notification.objects.count(), 2)
        self.assertEqual(Notification.objects.filter(user=self.rep).count(), 1)
        self.assertEqual(Notification.objects.filter(user=self.manager).count(), 1)

    def test_rep_alert_days_1(self):
        """ sets the expected close date to be 1 day late 
        also sets manager user's notification settings to not alert on this trigger
        this should create one new notification for the rep only
        """
        expected_close_date = timezone.now() - timezone.timedelta(days=2)

        self.lead_1.expected_close_date = expected_close_date
        self.lead_1.save()
        opt = NotificationOption.objects.get(
            pk=core_consts.NOTIFICATION_OPTION_LAPSED_1_DAY_ID
        )

        selection = NotificationSelection.objects.create(
            option=opt, user=self.manager, value=False
        )

        self.manager.notification_settings.add(selection)
        call_command("createleadnotifications")
        self.assertEqual(Notification.objects.count(), 1)
        self.assertEqual(Notification.objects.filter(user=self.rep).count(), 1)
        self.assertEqual(Notification.objects.filter(user=self.manager).count(), 0)

    def test_rep_no_alert_days_1_unclaimed_lead(self):
        """ sets the expected close date to be 1 day late 
        also sets manager user's notification settings to not alert on this trigger
        this should create one new notification for the rep only
        """
        expected_close_date = timezone.now() - timezone.timedelta(days=2)

        self.lead_2.expected_close_date = expected_close_date
        self.lead_2.save()
        opt = NotificationOption.objects.get(
            pk=core_consts.NOTIFICATION_OPTION_LAPSED_1_DAY_ID
        )

        selection = NotificationSelection.objects.create(
            option=opt, user=self.manager, value=False
        )

        self.manager.notification_settings.add(selection)
        call_command("createleadnotifications")
        self.assertEqual(Notification.objects.count(), 0)

    def test_all_alert_days_14(self):
        """ sets the expected close date to be 14+ days late
        this should create two new notifications for the rep and the manager (one each)
        """
        expected_close_date = timezone.now() - timezone.timedelta(days=16)

        self.lead_1.expected_close_date = expected_close_date
        self.lead_1.save()
        call_command("createleadnotifications")
        self.assertEqual(Notification.objects.count(), 2)
        self.assertEqual(Notification.objects.filter(user=self.rep).count(), 1)
        self.assertEqual(Notification.objects.filter(user=self.manager).count(), 1)
        self.assertEqual(
            Notification.objects.filter(user=self.manager).first().notification_type,
            lead_consts.NOTIFICATION_TYPE_OPPORTUNITY_LAPSED_EXPECTED_CLOSE_DATE_14,
            3,
        )

    def test_rep_alert_days_14(self):
        """ sets the expected close date to be 14+ days late 
        also sets manager user's notification settings to not alert on this trigger
        this should create one new notification for the rep only
        """
        expected_close_date = timezone.now() - timezone.timedelta(days=16)

        self.lead_1.expected_close_date = expected_close_date
        self.lead_1.save()
        opt = NotificationOption.objects.get(
            pk=core_consts.NOTIFICATION_OPTION_LAPSED_14_DAYS_ID
        )

        selection = NotificationSelection.objects.create(
            option=opt, user=self.manager, value=False
        )

        self.manager.notification_settings.add(selection)
        call_command("createleadnotifications")
        self.assertEqual(Notification.objects.count(), 1)
        self.assertEqual(Notification.objects.filter(user=self.rep).count(), 1)
        self.assertEqual(Notification.objects.filter(user=self.manager).count(), 0)

    def test_rep_no_alert_days_14_unclaimed_lead(self):
        """ sets the expected close date to be 14+ days late 
        also sets manager user's notification settings to not alert on this trigger
        this should create one new notification for the rep only
        """
        expected_close_date = timezone.now() - timezone.timedelta(days=16)

        self.lead_2.expected_close_date = expected_close_date
        self.lead_2.save()
        opt = NotificationOption.objects.get(
            pk=core_consts.NOTIFICATION_OPTION_LAPSED_14_DAYS_ID
        )

        selection = NotificationSelection.objects.create(
            option=opt, user=self.manager, value=False
        )

        self.manager.notification_settings.add(selection)
        call_command("createleadnotifications")
        self.assertEqual(Notification.objects.count(), 0)

    def test_all_alert_days_30(self):
        """ sets the expected close date to be 30+ days late
        this should create two new notifications for the rep and the manager (one each)
        """
        expected_close_date = timezone.now() - timezone.timedelta(days=31)

        self.lead_1.expected_close_date = expected_close_date
        self.lead_1.save()
        call_command("createleadnotifications")
        self.assertEqual(Notification.objects.count(), 2)
        self.assertEqual(Notification.objects.filter(user=self.rep).count(), 1)
        self.assertEqual(Notification.objects.filter(user=self.manager).count(), 1)
        self.assertEqual(
            Notification.objects.filter(user=self.manager).first().notification_type,
            lead_consts.NOTIFICATION_TYPE_OPPORTUNITY_LAPSED_EXPECTED_CLOSE_DATE_30,
            3,
        )

    def test_rep_alert_days_30(self):
        """ sets the expected close date to be 30+ days late 
        also sets manager user's notification settings to not alert on this trigger
        this should create one new notification for the rep only
        """
        expected_close_date = timezone.now() - timezone.timedelta(days=31)

        self.lead_1.expected_close_date = expected_close_date
        self.lead_1.save()
        opt = NotificationOption.objects.get(
            pk=core_consts.NOTIFICATION_OPTION_LAPSED_30_DAYS_ID
        )

        selection = NotificationSelection.objects.create(
            option=opt, user=self.manager, value=False
        )

        self.manager.notification_settings.add(selection)
        call_command("createleadnotifications")
        self.assertEqual(Notification.objects.count(), 1)
        self.assertEqual(Notification.objects.filter(user=self.rep).count(), 1)
        self.assertEqual(Notification.objects.filter(user=self.manager).count(), 0)

    def test_rep_no_alert_days_30_unclaimed_lead(self):
        """ sets the expected close date to be 30+ days late 
        also sets manager user's notification settings to not alert on this trigger
        this should create one new notification for the rep only
        """
        expected_close_date = timezone.now() - timezone.timedelta(days=31)

        self.lead_2.expected_close_date = expected_close_date
        self.lead_2.save()
        opt = NotificationOption.objects.get(
            pk=core_consts.NOTIFICATION_OPTION_LAPSED_30_DAYS_ID
        )

        selection = NotificationSelection.objects.create(
            option=opt, user=self.manager, value=False
        )

        self.manager.notification_settings.add(selection)
        call_command("createleadnotifications")
        self.assertEqual(Notification.objects.count(), 0)

    def test_notification_stage_update(self):
        """ should yield a notification created for user both users"""
        Stage.objects.create(
            title="test random stage",
            type=org_consts.STAGE_TYPE_PRIVATE,
            organization=self.org,
        )
        self.assertEqual(Notification.objects.count(), 2)

    def test_one_notification_stage_update(self):
        """ should yield a notification created for user """
        opt = NotificationOption.objects.get(
            pk=core_consts.NOTIFICATION_OPTION_STAGE_UPDATE_ID
        )
        NotificationSelection.objects.create(option=opt, user=self.rep, value=False)

        Stage.objects.create(
            title="test random stage",
            type=org_consts.STAGE_TYPE_PRIVATE,
            organization=self.org,
        )
        self.assertEqual(Notification.objects.count(), 1)
        self.assertEqual(Notification.objects.filter(user=self.manager).count(), 1)

