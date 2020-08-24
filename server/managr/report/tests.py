from django.test import TestCase

from managr.organization.models import Organization
from managr.lead.models import Lead, LeadActivityLog, Action
from managr.lead import constants as lead_constants

from .models import StoryReport
from .story_report_generation import (
    LeadDataGenerator,
    RepresentativeDataGenerator,
    OrganizationDataGenerator
)


class StoryReportTestCase(TestCase):
    fixtures = ["fixture.json", "report_meta.json", "report_lead_one.json"]

    def setUp(self):
        self.org = Organization.objects.first()
        self.user = self.org.users.first()
        self.account = self.org.accounts.first()

    def test_story_report_lead_data_generator(self):
        # should be loaded from the fixture, else should error
        lead = Lead.objects.get(pk="99b5e01e-4c8a-4ba5-be09-5407848aa87a")
        # no need to create story-report since LeadDataGenerator
        # is decoupled from that model
        instance = LeadDataGenerator(lead)
        data = instance.as_dict

        # from fixture:
        ready_date = "2020-07-01"
        booked_date = "2020-07-11"
        demo_date = "2020-07-21"
        close_date = "2020-08-05"
        # NOTE: if there is no claiming-event logged, then the LeadDataGenerator uses
        # the lead's datetime_created property.
        # This is because upon lead creation a claiming-event is not logged.
        # This test happens to test the case where the lead is never released and claimed,
        # but rather is closed by the same person that created it.
        claim_date = "2020-06-20"

        # assert timestamps:
        self.assertEqual(str(instance.ready_timestamp.date()), ready_date)
        self.assertEqual(str(instance.booked_timestamp.date()), booked_date)
        self.assertEqual(str(instance.demo_timestamp.date()), demo_date)
        self.assertEqual(str(instance.closed_timestamp.date()), close_date)
        self.assertEqual(str(instance.claimed_timestamp.date()), claim_date)

        # date ranges derived from fixture-sourced dates above
        days_ready_to_booked = 10
        days_booked_to_demo = 10
        days_to_demo = 20
        days_demo_to_closed = 15
        # NOTE: if a lead has gone through status of READY, then
        # days_to_closed calculates from that day forward,
        # else it calculates from claim-event through close-date
        days_to_closed = 35

        # assert date ranges:
        self.assertEqual(instance.days_ready_to_booked, days_ready_to_booked)
        self.assertEqual(instance.days_booked_to_demo, days_booked_to_demo)
        self.assertEqual(instance.days_to_demo, days_to_demo)
        self.assertEqual(instance.days_to_closed, days_to_closed)

        # communications-counts derived from fixture sources
        call_count = 1
        text_count = 2
        email_count = 2
        reminder_count = 2
        note_count = 1
        custom_action_count = 1
        # aggregage below
        action_count = 9

        # assert call/text/email/actions counts
        self.assertEqual(instance.call_count, call_count)
        self.assertEqual(instance.text_count, text_count)
        self.assertEqual(instance.email_count, email_count)
        self.assertEqual(instance.action_count, action_count)
