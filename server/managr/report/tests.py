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


class StoryReportLeadDataGeneratorTestCase(TestCase):
    fixtures = ["fixture.json", "report_meta.json", "report_lead_one.json"]

    def setUp(self):
        # should be loaded from the fixture, else should error
        self.lead = Lead.objects.get(pk="99b5e01e-4c8a-4ba5-be09-5407848aa87a")
        # no need to create story-report since LeadDataGenerator
        # is decoupled from that model
        self.instance = LeadDataGenerator(self.lead)

    def test_timestamps(self):
        # derived from fixture:
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

        self.assertEqual(str(self.instance.ready_timestamp.date()), ready_date)
        self.assertEqual(str(self.instance.booked_timestamp.date()), booked_date)
        self.assertEqual(str(self.instance.demo_timestamp.date()), demo_date)
        self.assertEqual(str(self.instance.closed_timestamp.date()), close_date)
        self.assertEqual(str(self.instance.claimed_timestamp.date()), claim_date)

    def test_date_ranges(self):
        # derived from fixture-sourced dates
        days_ready_to_booked = 10
        days_booked_to_demo = 10
        days_to_demo = 20
        days_demo_to_closed = 15
        # NOTE: if a lead has gone through status of READY, then
        # days_to_closed calculates from that day forward,
        # else it calculates from claim-event through close-date
        days_to_closed = 35

        self.assertEqual(self.instance.days_ready_to_booked, days_ready_to_booked)
        self.assertEqual(self.instance.days_booked_to_demo, days_booked_to_demo)
        self.assertEqual(self.instance.days_to_demo, days_to_demo)
        self.assertEqual(self.instance.days_to_closed, days_to_closed)

    def test_counts(self):
        # communications-counts derived from fixture sources
        call_count = 1
        text_count = 2
        email_count = 2
        reminder_count = 2
        note_count = 1
        custom_action_count = 1
        # action_count = aggregage of above counts
        action_count = 9

        self.assertEqual(self.instance.call_count, call_count)
        self.assertEqual(self.instance.text_count, text_count)
        self.assertEqual(self.instance.email_count, email_count)
        self.assertEqual(self.instance.action_count, action_count)


class StoryReportRepresentativeDataGeneratorTestCase(TestCase):
    fixtures = ["fixture.json", "report_meta.json", "report_lead_one.json", "report_lead_two.json"]

    def setUp(self):
        # should be loaded from the fixture, else should error
        self.lead_one = Lead.objects.get(pk="99b5e01e-4c8a-4ba5-be09-5407848aa87a")
        self.lead_two = Lead.objects.get(pk="77d63cfd-dd2d-40a8-9dfb-3c7d6865fd6d")
        # no need to create story-report since LeadDataGenerator
        # is decoupled from that model
        self.lead_one_data = LeadDataGenerator(self.lead_one)
        self.lead_two_data = LeadDataGenerator(self.lead_two)
        self.rep_data_dict = RepresentativeDataGenerator(self.lead_one).as_dict

    def test_date_ranges(self):
        # all averages, except custom-action-counts, use same method within RepresentativeDataGenerator
        # Therefore, below we just test one metric
        total = self.lead_one_data.days_ready_to_booked + self.lead_two_data.days_ready_to_booked
        # rounded to zero decimal places, as does RepresentativeDataGenerator
        average_days_ready_to_booked = round(total / 2, 0)

        self.assertEqual(self.rep_data_dict["average_days_ready_to_booked"], average_days_ready_to_booked)
