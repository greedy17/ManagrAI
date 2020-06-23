from django.test import TestCase
from django.utils import timezone

from managr.organization.models import Organization
from managr.organization.factories import AccountFactory, ContactFactory

from ..factories import LeadFactory, CallNoteFactory
from ..background.consumers import BaseActionConsumer, CallNoteActionConsumer
from ..background.exceptions import ConsumerConfigError
from ..models import Lead, CallNote, LeadActivityLog
from ..insights import LeadInsights
from .. import constants as lead_constants


class LeadInsightsTestCase(TestCase):
    def setUp(self):
        # Random lead for basic insight testing
        self.lead = LeadFactory(amount=25000, status=lead_constants.LEAD_STATUS_WAITING)

        # Open and closed leads for KPI testing
        self.open_lead_1 = LeadFactory(
            amount=25000, status=lead_constants.LEAD_STATUS_WAITING
        )
        self.open_lead_2 = LeadFactory(
            amount=25000, status=lead_constants.LEAD_STATUS_WAITING
        )
        self.closed_lead_1 = LeadFactory(
            amount=25000, closing_amount=30000, status=lead_constants.LEAD_STATUS_CLOSED
        )
        self.lost_lead_1 = LeadFactory(
            amount=25000, status=lead_constants.LEAD_STATUS_LOST
        )

    def test_call_count(self):
        LeadActivityLog.objects.create(
            lead=self.lead,
            activity=lead_constants.CALL_NOTE_CREATED,
            action_timestamp=timezone.now(),
        )
        insights = LeadInsights()
        self.assertEqual(insights.call_count, 1)

        LeadActivityLog.objects.create(
            lead=self.lead,
            activity=lead_constants.CALL_NOTE_CREATED,
            action_timestamp=timezone.now(),
        )
        insights = LeadInsights()
        self.assertEqual(insights.call_count, 2)

    def test_call_latest(self):
        older_timestamp = timezone.make_aware(timezone.datetime(2020, 4, 1))
        newer_timestamp = timezone.make_aware(timezone.datetime(2020, 5, 1))
        LeadActivityLog.objects.create(
            lead=self.lead,
            action_timestamp=older_timestamp,
            activity=lead_constants.CALL_NOTE_CREATED,
        )
        LeadActivityLog.objects.create(
            lead=self.lead,
            action_timestamp=newer_timestamp,
            activity=lead_constants.CALL_NOTE_CREATED,
        )
        insights = LeadInsights()

        self.assertEqual(insights.call_latest, newer_timestamp)

    def test_note_count(self):
        LeadActivityLog.objects.create(
            lead=self.lead,
            activity=lead_constants.NOTE_CREATED,
            action_timestamp=timezone.now(),
        )
        insights = LeadInsights()
        self.assertEqual(insights.note_count, 1)

        LeadActivityLog.objects.create(
            lead=self.lead,
            activity=lead_constants.NOTE_CREATED,
            action_timestamp=timezone.now(),
        )
        insights = LeadInsights()
        self.assertEqual(insights.note_count, 2)

    def test_note_latest(self):
        older_timestamp = timezone.make_aware(timezone.datetime(2020, 4, 1))
        newer_timestamp = timezone.make_aware(timezone.datetime(2020, 5, 1))
        LeadActivityLog.objects.create(
            lead=self.lead,
            action_timestamp=older_timestamp,
            activity=lead_constants.NOTE_CREATED,
        )
        LeadActivityLog.objects.create(
            lead=self.lead,
            action_timestamp=newer_timestamp,
            activity=lead_constants.NOTE_CREATED,
        )
        insights = LeadInsights()

        self.assertEqual(insights.note_latest, newer_timestamp)

    def test_action_count(self):
        LeadActivityLog.objects.create(
            lead=self.lead,
            activity=lead_constants.ACTION_CREATED,
            action_timestamp=timezone.now(),
        )
        insights = LeadInsights()
        self.assertEqual(insights.action_count, 1)

        LeadActivityLog.objects.create(
            lead=self.lead,
            activity=lead_constants.ACTION_CREATED,
            action_timestamp=timezone.now(),
        )
        insights = LeadInsights()
        self.assertEqual(insights.action_count, 2)

    def test_action_latest(self):
        older_timestamp = timezone.make_aware(timezone.datetime(2020, 4, 1))
        newer_timestamp = timezone.make_aware(timezone.datetime(2020, 5, 1))
        LeadActivityLog.objects.create(
            lead=self.lead,
            action_timestamp=older_timestamp,
            activity=lead_constants.ACTION_CREATED,
        )
        LeadActivityLog.objects.create(
            lead=self.lead,
            action_timestamp=newer_timestamp,
            activity=lead_constants.ACTION_CREATED,
        )
        insights = LeadInsights()

        self.assertEqual(insights.action_latest, newer_timestamp)

    def test_total_closed_value(self):
        insights = LeadInsights()
        self.assertEqual(insights.total_closed_value, 30000)

    def test_avg_contract_value(self):
        insights = LeadInsights()
        self.assertEqual(insights.average_contract_value, 26250)

    def test_avg_contract_value_empty_qs(self):
        insights = LeadInsights(Lead.objects.none())
        self.assertEqual(insights.average_contract_value, 0)

    def test_forecast(self):
        insights = LeadInsights()
        self.assertEqual(insights.forecast, 75000)

    def test_forecast_empty_qs(self):
        insights = LeadInsights(Lead.objects.none())
        self.assertEqual(insights.forecast, 0)
