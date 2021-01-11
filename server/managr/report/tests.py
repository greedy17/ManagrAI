from django.test import TestCase
from django.utils.dateparse import parse_datetime

from managr.core.models import User
from managr.organization.models import Organization, Account, Stage
from managr.lead.models import Lead, LeadActivityLog, Action, ActionChoice
from managr.lead import constants as lead_constants

from .models import (
    StoryReport,
    PerformanceReport,
)
from .story_report_generation import (
    LeadDataGenerator,
    RepresentativeDataGenerator,
    OrganizationDataGenerator,
)
from .performance_report_generation import (
    RepFocusData,
    RepTypicalData,
    OrgFocusData,
    OrgTypicalData,
)
from managr.report import constants as report_const
from pdb import set_trace


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
        self.assertEqual(str(self.instance.start_timestamp.date()), claim_date)

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
        closed_lead = 1
        # action_count = aggregage of above counts
        action_count = 10

        self.assertEqual(self.instance.call_count, call_count)
        self.assertEqual(self.instance.text_count, text_count)
        self.assertEqual(self.instance.email_count, email_count)
        self.assertEqual(self.instance.action_count, action_count)


class StoryReportRepresentativeDataGeneratorTestCase(TestCase):
    fixtures = [
        "fixture.json",
        "report_meta.json",
        "report_lead_one.json",
        "report_lead_two.json",
    ]

    def setUp(self):
        # should be loaded from the fixture, else should error
        self.lead_one = Lead.objects.get(pk="99b5e01e-4c8a-4ba5-be09-5407848aa87a")
        self.lead_two = Lead.objects.get(pk="77d63cfd-dd2d-40a8-9dfb-3c7d6865fd6d")
        # no need to create story-report since LeadDataGenerator
        # is decoupled from that model
        self.lead_one_data = LeadDataGenerator(self.lead_one)
        self.lead_two_data = LeadDataGenerator(self.lead_two)
        self.instance = RepresentativeDataGenerator(self.lead_one)
        self.rep_data_dict = self.instance.as_dict

    def test_averages(self):
        # all averages, except custom-action-counts, use same method within RepresentativeDataGenerator
        # Therefore, below we just test one metric
        total = (
            self.lead_one_data.days_ready_to_booked
            + self.lead_two_data.days_ready_to_booked
        )
        # rounded to zero decimal places, as does RepresentativeDataGenerator
        average_days_ready_to_booked = round(total / 2, 0)
        self.assertEqual(
            self.rep_data_dict["average_days_ready_to_booked"],
            average_days_ready_to_booked,
        )


class PerformanceReportRepFocusDataTestCase(TestCase):
    fixtures = [
        "fixture.json",
        "report_meta.json",
        "report_lead_one.json",
        "report_lead_two.json",
    ]

    def setUp(self):
        # should be loaded from the fixture, else should error
        self.representative = User.objects.get(
            pk="3dddd261-93b1-46fe-a83e-bc164551362a"
        )
        self.organization = self.representative.organization
        # Both leads closed in 2020
        self.closed_lead_one = Lead.objects.get(
            pk="99b5e01e-4c8a-4ba5-be09-5407848aa87a"
        )
        self.closed_lead_two = Lead.objects.get(
            pk="77d63cfd-dd2d-40a8-9dfb-3c7d6865fd6d"
        )
        self.performance_report = PerformanceReport.objects.create(
            representative=self.representative,
            generated_by=self.representative,
            date_range_preset=report_const.THIS_YEAR,
            date_range_from="2020-01-01T05:00:00Z",
            date_range_to="2022-01-01T04:59:59.999000Z",
        )

    def generate_report_data(self):
        return RepFocusData(self.performance_report).as_dict

    def test_actions_count(self):
        data = self.generate_report_data()
        # there should already be an action due to fixtures:
        # pk 7aa287d3-4ce6-4823-a236-b18e260729b7
        self.assertEqual(data["actions_count"], 1)

        # an org-level action for Test Org
        action_choice = self.organization.action_choices.first()
        Action.objects.create(
            action_type=action_choice,
            created_by=self.representative,
            datetime_created="2021-03-01T05:00:00Z",
        )
        data = self.generate_report_data()
        self.assertEqual(data["actions_count"], 2)

    def test_incoming_messages_count(self):
        data = self.generate_report_data()
        self.assertEqual(data["incoming_messages_count"], 0)
        for n in range(3):
            LeadActivityLog.objects.create(
                activity=lead_constants.EMAIL_RECEIVED,
                lead=self.closed_lead_one,
                action_taken_by=self.representative,
                action_timestamp="2020-04-01T05:00:00Z",
                datetime_created="2020-04-01T05:00:00Z",
            )
        data = self.generate_report_data()
        self.assertEqual(data["incoming_messages_count"], 3)

    def test_amount_closed(self):
        data = self.generate_report_data()
        aggregate = (
            self.closed_lead_one.closing_amount + self.closed_lead_two.closing_amount
        )
        self.assertEqual(data["amount_closed"], aggregate)

    def test_ACV(self):
        data = self.generate_report_data()
        aggregate = (
            self.closed_lead_one.closing_amount + self.closed_lead_two.closing_amount
        )
        average = round(aggregate / 2)
        self.assertEqual(data["ACV"], average)

    def test_activities_count(self):
        # Fixture for lead one includes 13 total activities,
        # 3 of which are Lead.UPDATED and therefore not counted.
        # fixture for lead two includes 4 total activities,
        # 3 of which are Lead.UPDATED and therefore not counted.
        data = self.generate_report_data()
        self.assertEqual(data["activities_count"], 11)
        LeadActivityLog.objects.create(
            activity=lead_constants.LEAD_UPDATED,
            lead=self.closed_lead_two,
            action_taken_by=self.representative,
            action_timestamp="2020-04-01T05:00:00Z",
            datetime_created="2020-04-01T05:00:00Z",
        )
        data = self.generate_report_data()
        self.assertEqual(data["activities_count"], 11)
        LeadActivityLog.objects.create(
            activity=lead_constants.NOTE_CREATED,
            lead=self.closed_lead_two,
            action_taken_by=self.representative,
            action_timestamp="2020-04-01T05:00:00Z",
            datetime_created="2020-04-01T05:00:00Z",
        )
        data = self.generate_report_data()
        self.assertEqual(data["activities_count"], 12)

    def test_actions_to_close_opportunity(self):
        # Fixture data includes one action for lead one,
        # zero actions for lead two,
        # and a total of two leads.
        data = self.generate_report_data()
        average = data["actions_to_close_opportunity"]["average"]
        most_performed = data["actions_to_close_opportunity"]["most_performed"]

        # lead one has 1 action
        # lead two has 0 actions
        # there are 2 leads
        # so 1/2 => 0.5
        self.assertEqual(average, 0.5)
        self.assertEqual(most_performed, "TEST ACTION ONE")

        action_type = ActionChoice.objects.create(
            title="test-choice", organization=self.organization,
        )
        for n in range(10):
            action = Action.objects.create(
                action_type=action_type,
                created_by=self.representative,
                lead=self.closed_lead_one,
            )
            # datetime_created must be between:
            # lead created && lead closed
            action.datetime_created = "2020-06-25 11:39:23.632256Z"
            action.save()
        data = self.generate_report_data()
        average = data["actions_to_close_opportunity"]["average"]
        most_performed = data["actions_to_close_opportunity"]["most_performed"]

        # lead one has 11 action
        # lead two has 0 actions
        # there are two leads
        # so 11/2 => 5.5
        self.assertEqual(average, 5.5)
        self.assertEqual(most_performed, action_type.title)

    def test_sales_cycle(self):
        num_1 = LeadDataGenerator(self.closed_lead_one).as_dict["days_to_closed"]
        num_2 = LeadDataGenerator(self.closed_lead_two).as_dict["days_to_closed"]
        average = (num_1 + num_2) / 2
        data = self.generate_report_data()
        self.assertEqual(data["sales_cycle"], average)

    def test_forecast_table_additions(self):
        # Originally, given fixture:
        data = self.generate_report_data()
        self.assertEqual(data["forecast_table_additions"], 0)

        for x in range(2):
            LeadActivityLog.objects.create(
                activity=lead_constants.LEAD_UPDATED,
                lead=self.closed_lead_one,
                action_taken_by=self.representative,
                action_timestamp=f"2020-04-0{x + 1}T05:00:00Z",
                datetime_created=f"2020-04-0{x + 1}T05:00:00Z",
                meta={
                    "extra": {"forecast_table_addition": True, "forecast_amount": 200,}
                },
            )

        data = self.generate_report_data()
        self.assertEqual(data["forecast_table_additions"], 1)

        LeadActivityLog.objects.create(
            activity=lead_constants.LEAD_UPDATED,
            lead=self.closed_lead_two,
            action_taken_by=self.representative,
            action_timestamp="2020-04-01T05:00:00Z",
            datetime_created="2020-04-01T05:00:00Z",
            meta={"extra": {"forecast_table_addition": True, "forecast_amount": 200,}},
        )
        data = self.generate_report_data()
        self.assertEqual(data["forecast_table_additions"], 2)

    def test_forecast_amount(self):
        # Originally, given fixture:
        data = self.generate_report_data()
        self.assertEqual(data["forecast_amount"], 0)

        # Adding a log with proper meta should increase
        # the output in the report by corresponding amount:
        LeadActivityLog.objects.create(
            activity=lead_constants.LEAD_UPDATED,
            lead=self.closed_lead_one,
            action_taken_by=self.representative,
            action_timestamp="2020-04-02T05:00:00Z",
            datetime_created="2020-04-02T05:00:00Z",
            meta={"extra": {"forecast_table_addition": True, "forecast_amount": 200,}},
        )

        data = self.generate_report_data()
        self.assertEqual(data["forecast_amount"], 200)

        # Adding a log with proper meta for the same lead
        # should change output in report by only
        # including the top amount per lead:
        LeadActivityLog.objects.create(
            activity=lead_constants.LEAD_UPDATED,
            lead=self.closed_lead_one,
            action_taken_by=self.representative,
            action_timestamp="2020-04-02T05:00:00Z",
            datetime_created="2020-04-02T05:00:00Z",
            meta={"extra": {"forecast_table_addition": True, "forecast_amount": 500,}},
        )
        data = self.generate_report_data()
        self.assertEqual(data["forecast_amount"], 500)

        # Adding a log with proper meta for another lead
        # should change output in report by including
        # this new lead's log, plus other lead's highest log.
        LeadActivityLog.objects.create(
            activity=lead_constants.LEAD_UPDATED,
            lead=self.closed_lead_two,
            action_taken_by=self.representative,
            action_timestamp="2020-04-02T05:00:00Z",
            datetime_created="2020-04-02T05:00:00Z",
            meta={"extra": {"forecast_table_addition": True, "forecast_amount": 200,}},
        )
        data = self.generate_report_data()
        self.assertEqual(data["forecast_amount"], 700)

    def test_deals_closed_count(self):
        data = self.generate_report_data()
        self.assertEqual(data["deals_closed_count"], 2)

    def test_deal_analysis(self):
        self.maxDiff = None
        # Originally, given fixture:
        expected = {
            "company_size": {"value": None, "percentage": None,},
            "industry": {"value": None, "percentage": None,},
            "type": {"value": None, "percentage": None,},
            "competitor": {"value": None, "percentage": None,},
            "geography": {"value": None, "percentage": None,},
        }
        data = self.generate_report_data()
        self.assertDictEqual(data["deal_analysis"], expected)

        # Adding lead-custom-fields to only closed_lead_one
        self.closed_lead_one.company_size = lead_constants.FIFTYONE_TO_TWOHUNDRED
        self.closed_lead_one.industry = lead_constants.AGRICULTURE
        self.closed_lead_one.type = lead_constants.MQL
        self.closed_lead_one.competitor = lead_constants.YES
        self.closed_lead_one.geography_address = (
            "8830 Castlebury Ct, Laurel, MD 20723, USA"
        )
        self.closed_lead_one.geography_address_components = {
            "streetNumber": {"long_name": "8830", "short_name": "8830"},
            "route": {"long_name": "Castlebury Court", "short_name": "Castlebury Ct"},
            "locality": {"long_name": "Laurel", "short_name": "Laurel"},
            "administrative_area_level_3": {
                "long_name": "Savage",
                "short_name": "Savage",
            },
            "administrative_area_level_2": {
                "long_name": "Howard County",
                "short_name": "Howard County",
            },
            "administrative_area_level_1": {
                "long_name": "Maryland",
                "short_name": "MD",
            },
            "country": {"long_name": "United States", "short_name": "US"},
            "postalCode": {"long_name": "20723", "short_name": "20723"},
            "latitude": 39.124847,
            "longitude": -76.860657,
        }
        self.closed_lead_one.save()
        expected = {
            "company_size": {
                "value": lead_constants.FIFTYONE_TO_TWOHUNDRED,
                "percentage": 50,
            },
            "industry": {"value": lead_constants.AGRICULTURE, "percentage": 50},
            "type": {"value": lead_constants.MQL, "percentage": 50},
            "competitor": {"value": lead_constants.YES, "percentage": 50},
            "geography": {"value": "Maryland", "percentage": 50},
        }
        data = self.generate_report_data()
        self.assertDictEqual(data["deal_analysis"], expected)

        # Also adding lead-custom-fields to closed_lead_two
        self.closed_lead_two.company_size = lead_constants.FIFTYONE_TO_TWOHUNDRED
        self.closed_lead_two.industry = lead_constants.AGRICULTURE
        self.closed_lead_two.type = lead_constants.MQL
        self.closed_lead_two.competitor = lead_constants.YES
        self.closed_lead_two.geography_address = (
            "8830 Castlebury Ct, Laurel, MD 20723, USA"
        )
        self.closed_lead_two.geography_address_components = {
            "streetNumber": {"long_name": "8830", "short_name": "8830"},
            "route": {"long_name": "Castlebury Court", "short_name": "Castlebury Ct"},
            "locality": {"long_name": "Laurel", "short_name": "Laurel"},
            "administrative_area_level_3": {
                "long_name": "Savage",
                "short_name": "Savage",
            },
            "administrative_area_level_2": {
                "long_name": "Howard County",
                "short_name": "Howard County",
            },
            "administrative_area_level_1": {
                "long_name": "Maryland",
                "short_name": "MD",
            },
            "country": {"long_name": "United States", "short_name": "US"},
            "postalCode": {"long_name": "20723", "short_name": "20723"},
            "latitude": 39.124847,
            "longitude": -76.860657,
        }
        self.closed_lead_two.save()
        expected = {
            "company_size": {
                "value": lead_constants.FIFTYONE_TO_TWOHUNDRED,
                "percentage": 100,
            },
            "industry": {"value": lead_constants.AGRICULTURE, "percentage": 100,},
            "type": {"value": lead_constants.MQL, "percentage": 100,},
            "competitor": {"value": lead_constants.YES, "percentage": 100,},
            "geography": {"value": "Maryland", "percentage": 100,},
        }
        data = self.generate_report_data()
        self.assertDictEqual(data["deal_analysis"], expected)

    def test_top_opportunities(self):
        # Originally, given fixture:
        data = self.generate_report_data()
        top_closed = data["top_opportunities"][lead_constants.FORECAST_CLOSED]
        top_verbal = data["top_opportunities"][lead_constants.FORECAST_VERBAL]
        top_strong = data["top_opportunities"][lead_constants.FORECAST_STRONG]
        top_50_50 = data["top_opportunities"][lead_constants.FORECAST_FIFTY_FIFTY]
        self.assertEqual(len(top_closed), 2)
        self.assertEqual(len(top_verbal), 0)
        self.assertEqual(len(top_strong), 0)
        self.assertEqual(len(top_50_50), 0)

        # Add one lead that is currenty forecasted as STRONG
        lead_three = Lead.objects.create(
            title="third lead",
            created_by=self.representative,
            claimed_by=self.representative,
            amount=100,
            expected_close_date="2020-10-01T05:00:00Z",
            account=Account.objects.first(),
        )
        LeadActivityLog.objects.create(
            activity=lead_constants.LEAD_UPDATED,
            lead=lead_three,
            action_taken_by=self.representative,
            action_timestamp="2020-04-01T05:00:00Z",
            datetime_created="2020-04-01T05:00:00Z",
            meta={
                "extra": {
                    "forecast_update": True,
                    "forecast_amount": 100,
                    "new_forecast": lead_constants.FORECAST_STRONG,
                    "previous_forecast": lead_constants.FORECAST_NA,
                }
            },
        )
        data = self.generate_report_data()
        top_closed = data["top_opportunities"][lead_constants.FORECAST_CLOSED]
        top_verbal = data["top_opportunities"][lead_constants.FORECAST_VERBAL]
        top_strong = data["top_opportunities"][lead_constants.FORECAST_STRONG]
        top_50_50 = data["top_opportunities"][lead_constants.FORECAST_FIFTY_FIFTY]
        self.assertEqual(len(top_closed), 2)
        self.assertEqual(len(top_verbal), 0)
        self.assertEqual(len(top_strong), 1)
        self.assertEqual(len(top_50_50), 0)

        # Add another lead with forecast of STRONG, yet should be same output
        # as last data generated
        lead_four = Lead.objects.create(
            title="fourth lead",
            created_by=self.representative,
            claimed_by=self.representative,
            amount=100,
            expected_close_date="2020-10-01T05:00:00Z",
            account=Account.objects.first(),
        )
        LeadActivityLog.objects.create(
            activity=lead_constants.LEAD_UPDATED,
            lead=lead_four,
            action_taken_by=self.representative,
            action_timestamp="2020-04-01T05:00:00Z",
            datetime_created="2020-04-01T05:00:00Z",
            meta={
                "extra": {
                    "forecast_update": True,
                    "forecast_amount": 100,
                    "new_forecast": lead_constants.FORECAST_STRONG,
                    "previous_forecast": lead_constants.FORECAST_NA,
                }
            },
        )
        data = self.generate_report_data()
        top_closed = data["top_opportunities"][lead_constants.FORECAST_CLOSED]
        top_verbal = data["top_opportunities"][lead_constants.FORECAST_VERBAL]
        top_strong = data["top_opportunities"][lead_constants.FORECAST_STRONG]
        top_50_50 = data["top_opportunities"][lead_constants.FORECAST_FIFTY_FIFTY]
        self.assertEqual(len(top_closed), 2)
        self.assertEqual(len(top_verbal), 0)
        self.assertEqual(len(top_strong), 1)
        self.assertEqual(len(top_50_50), 0)

        # Add lead with forecast of VERBAL,
        # should be included as third lead alongside two original CLOSED,
        # and therefore there should be no STRONG leads in top_opportunities.
        lead_five = Lead.objects.create(
            title="fifth lead",
            created_by=self.representative,
            claimed_by=self.representative,
            amount=100,
            expected_close_date="2020-10-01T05:00:00Z",
            account=Account.objects.first(),
        )
        LeadActivityLog.objects.create(
            activity=lead_constants.LEAD_UPDATED,
            lead=lead_five,
            action_taken_by=self.representative,
            action_timestamp="2020-04-01T05:00:00Z",
            datetime_created="2020-04-01T05:00:00Z",
            meta={
                "extra": {
                    "forecast_update": True,
                    "forecast_amount": 100,
                    "new_forecast": lead_constants.FORECAST_VERBAL,
                    "previous_forecast": lead_constants.FORECAST_NA,
                }
            },
        )
        data = self.generate_report_data()
        top_closed = data["top_opportunities"][lead_constants.FORECAST_CLOSED]
        top_verbal = data["top_opportunities"][lead_constants.FORECAST_VERBAL]
        top_strong = data["top_opportunities"][lead_constants.FORECAST_STRONG]
        top_50_50 = data["top_opportunities"][lead_constants.FORECAST_FIFTY_FIFTY]
        self.assertEqual(len(top_closed), 2)
        self.assertEqual(len(top_verbal), 1)
        self.assertEqual(len(top_strong), 0)
        self.assertEqual(len(top_50_50), 0)


class PerformanceReportRepTypicalDataTestCase(TestCase):
    fixtures = [
        "fixture.json",
        "report_meta.json",
        "report_lead_one.json",
        "report_lead_two.json",
    ]

    def setUp(self):
        # should be loaded from the fixture, else should error
        self.representative = User.objects.get(
            pk="3dddd261-93b1-46fe-a83e-bc164551362a"
        )
        self.organization = self.representative.organization
        # Both leads closed in 2020
        self.closed_lead_one = Lead.objects.get(
            pk="99b5e01e-4c8a-4ba5-be09-5407848aa87a"
        )
        self.closed_lead_two = Lead.objects.get(
            pk="77d63cfd-dd2d-40a8-9dfb-3c7d6865fd6d"
        )
        self.performance_report = PerformanceReport.objects.create(
            representative=self.representative,
            generated_by=self.representative,
            date_range_preset=report_const.THIS_MONTH,
            date_range_from="2020-09-01T04:00:00Z",
            date_range_to="2020-10-01T03:59:59.999000Z",
        )

    def test_average_for_field(self):
        # all statistics for this aspect of PerformanceReports are generated
        # via average_for_field().
        lead_one_data = LeadDataGenerator(self.closed_lead_one).as_dict
        lead_two_data = LeadDataGenerator(self.closed_lead_two).as_dict
        rep_data = RepTypicalData(self.performance_report).as_dict

        # test activities_count
        numerator = lead_one_data["action_count"] + lead_two_data["action_count"]
        denominator = 2
        activities_average = numerator / denominator
        self.assertEqual(rep_data["activities_count"], activities_average)

        # test sales_cycle
        numerator = lead_one_data["days_to_closed"] + lead_two_data["days_to_closed"]
        denominator = 2
        sales_cycle_average = numerator / denominator
        self.assertEqual(rep_data["sales_cycle"], sales_cycle_average)


class PerformanceReportOrgTypicalDataTestCase(TestCase):
    fixtures = [
        "fixture.json",
        "report_meta.json",
        "report_lead_one.json",
        "report_lead_two.json",
    ]

    def setUp(self):
        # should be loaded from the fixture, else should error
        self.representative = User.objects.get(
            pk="3dddd261-93b1-46fe-a83e-bc164551362a"
        )
        self.organization = self.representative.organization
        self.closed_lead_one = Lead.objects.get(
            pk="99b5e01e-4c8a-4ba5-be09-5407848aa87a"
        )
        self.closed_lead_two = Lead.objects.get(
            pk="77d63cfd-dd2d-40a8-9dfb-3c7d6865fd6d"
        )
        self.performance_report = PerformanceReport.objects.create(
            representative=self.representative,
            generated_by=self.representative,
            date_range_preset=report_const.THIS_MONTH,
            date_range_from="2020-09-01T04:00:00Z",
            date_range_to="2020-10-01T03:59:59.999000Z",
        )

    def generate_rep_one_data(self):
        return RepTypicalData(self.performance_report).as_dict

    def generate_rep_two_data(self):
        # generate rep
        representative = User.objects.create(
            email="second_report_tester@reports.com",
            is_invited=True,
            is_active=True,
            organization=self.organization,
        )
        # generate closed lead
        lead_one = Lead.objects.create(
            title="first lead",
            created_by=representative,
            claimed_by=representative,
            status=Stage.objects.get(pk="fe89a6fd-f049-4b23-a059-86d45c12b14b"),
            amount=1000,
            closing_amount=1000,
            expected_close_date="2020-08-05T05:00:00Z",
            account=Account.objects.first(),
        )
        log_one = LeadActivityLog.objects.create(
            activity=lead_constants.LEAD_CLOSED,
            lead=lead_one,
            action_taken_by=representative,
            action_timestamp="2020-08-05T05:00:00Z",
            datetime_created="2020-08-05T05:00:00Z",
        )

        # make sure that leads dates are static regardless of
        # whenever these tests are run
        # All of the dates have to take place before the report's
        # date_range_from, because that is part of the protocol for
        # leads/data to be included in the data generation.
        representative.datetime_created = "2020-06-25T05:00:00Z"
        representative.save()
        lead_one.datetime_created = "2020-07-05T05:00:00Z"
        lead_one.save()
        log_one.datetime_created = "2020-08-05T05:00:00Z"
        log_one.action_timestamp = "2020-08-05T05:00:00Z"
        log_one.save()

        # generate performance report
        performance_report = PerformanceReport.objects.create(
            representative=representative,
            generated_by=representative,
            date_range_preset=self.performance_report.date_range_preset,
            date_range_from=self.performance_report.date_range_from,
            date_range_to=self.performance_report.date_range_to,
        )
        return RepTypicalData(performance_report).as_dict

    def generate_org_data(self):
        org_data_generator = OrgTypicalData(self.performance_report)
        return org_data_generator.as_dict_for_representative_report

    def test_average_for_field(self):
        # Originally, given fixture:
        # Only one rep with two leads.
        # Therefore, averages of OrgTypicalData
        # should be same as the one rep's RepTypicalData.
        rep_one_averages = self.generate_rep_one_data()
        org_averages = self.generate_org_data()

        self.assertEqual(
            org_averages["activities_count"], rep_one_averages["activities_count"],
        )
        self.assertEqual(
            org_averages["actions_count"], rep_one_averages["actions_count"],
        )
        self.assertEqual(
            org_averages["incoming_messages_count"],
            rep_one_averages["incoming_messages_count"],
        )
        self.assertEqual(
            org_averages["forecast_amount"], rep_one_averages["forecast_amount"],
        )
        self.assertEqual(
            org_averages["deals_closed_count"], rep_one_averages["deals_closed_count"],
        )
        self.assertEqual(
            org_averages["amount_closed"], rep_one_averages["amount_closed"],
        )

        # Add new rep and confirm org_averages
        rep_two_averages = self.generate_rep_two_data()
        org_averages = self.generate_org_data()
        activities_count = (
            rep_one_averages["activities_count"] + rep_two_averages["activities_count"]
        ) / 2
        actions_count = (
            rep_one_averages["actions_count"] + rep_two_averages["actions_count"]
        ) / 2
        deals_closed_count = (
            rep_one_averages["deals_closed_count"]
            + rep_two_averages["deals_closed_count"]
        ) / 2
        amount_closed = (
            rep_one_averages["amount_closed"] + rep_two_averages["amount_closed"]
        ) / 2

        self.assertEqual(
            org_averages["activities_count"], activities_count,
        )
        self.assertEqual(
            org_averages["actions_count"], actions_count,
        )
        self.assertEqual(
            org_averages["deals_closed_count"], deals_closed_count,
        )
        self.assertEqual(
            org_averages["amount_closed"], amount_closed,
        )


class PerformanceReportOrgFocusDataTestCase(TestCase):
    fixtures = [
        "fixture.json",
        "report_meta.json",
        "report_lead_one.json",
        "report_lead_two.json",
    ]

    def setUp(self):
        # should be loaded from the fixture, else should error
        self.representative = User.objects.get(
            pk="3dddd261-93b1-46fe-a83e-bc164551362a"
        )
        self.organization = self.representative.organization
        self.closed_lead_one = Lead.objects.get(
            pk="99b5e01e-4c8a-4ba5-be09-5407848aa87a"
        )
        self.closed_lead_two = Lead.objects.get(
            pk="77d63cfd-dd2d-40a8-9dfb-3c7d6865fd6d"
        )
        self.rep_performance_report = PerformanceReport.objects.create(
            representative=self.representative,
            generated_by=self.representative,
            date_range_preset=report_const.THIS_YEAR,
            date_range_from=parse_datetime("2020-01-01T04:00:00Z"),
            date_range_to=parse_datetime("2020-12-29T03:59:59.999000Z"),
        )
        self.org_performance_report = PerformanceReport.objects.create(
            representative=None,
            generated_by=self.representative,
            date_range_preset=report_const.THIS_YEAR,
            date_range_from=parse_datetime("2020-01-01T04:00:00Z"),
            date_range_to=parse_datetime("2020-12-29T03:59:59.999000Z"),
        )

    def generate_rep_one_focus_data(self):
        return RepFocusData(self.rep_performance_report).as_dict

    def generate_rep_two_focus_data(self, skip_lead_generation=False):
        # generate rep
        representative = User.objects.create(
            email="second_report_tester@reports.com",
            is_invited=True,
            is_active=True,
            organization=self.organization,
        )
        self.rep_two = representative
        # generate closed lead
        if not skip_lead_generation:
            lead_one = Lead.objects.create(
                title="first lead",
                created_by=representative,
                claimed_by=representative,
                status=Stage.objects.get(pk="fe89a6fd-f049-4b23-a059-86d45c12b14b"),
                amount=1000,
                closing_amount=1000,
                expected_close_date=parse_datetime("2020-08-05T05:00:00Z"),
                account=Account.objects.first(),
            )
            self.rep_two_closed_lead_one = lead_one
            log_one = LeadActivityLog.objects.create(
                activity=lead_constants.LEAD_CLOSED,
                lead=lead_one,
                action_taken_by=representative,
                action_timestamp=parse_datetime("2020-08-05T05:00:00Z"),
                datetime_created=parse_datetime("2020-08-05T05:00:00Z"),
            )

        # make sure that leads dates are static regardless of
        # whenever these tests are run
        # All of the dates have to take place before the report's
        # date_range_from, because that is part of the protocol for
        # leads/data to be included in the data generation.
        representative.datetime_created = parse_datetime("2020-06-25T05:00:00Z")
        representative.save()
        if not skip_lead_generation:
            lead_one.datetime_created = parse_datetime("2020-07-05T05:00:00Z")
            lead_one.save()
            log_one.datetime_created = parse_datetime("2020-08-05T05:00:00Z")
            log_one.action_timestamp = parse_datetime("2020-08-05T05:00:00Z")
            log_one.save()

        # generate performance report
        performance_report = PerformanceReport.objects.create(
            representative=representative,
            generated_by=representative,
            date_range_preset=self.rep_performance_report.date_range_preset,
            date_range_from=self.rep_performance_report.date_range_from,
            date_range_to=self.rep_performance_report.date_range_to,
        )
        return RepFocusData(performance_report).as_dict

    def generate_org_focus_data(self):
        self.org_data_generator = OrgFocusData(self.org_performance_report)
        return self.org_data_generator.as_dict_for_organization_report

    def test_sum_for_field(self):
        """
        fields that utilize OrgFocusData.sum_for_field:
        -- activities_count
        -- actions_count
        -- incoming_messages_count
        -- forecast_amount
        -- deals_closed_count
        -- amount_closed
        -- forecast_table_additions.value
        """
        # Originally, given fixture:
        # Only one rep with two leads.
        # Therefore, averages of OrgFocusData
        # should be same as the one rep's RepFocusData.
        rep_one_data = self.generate_rep_one_focus_data()
        org_data = self.generate_org_focus_data()

        self.assertEqual(
            org_data["activities_count"], rep_one_data["activities_count"],
        )
        self.assertEqual(
            org_data["actions_count"], rep_one_data["actions_count"],
        )
        self.assertEqual(
            org_data["incoming_messages_count"],
            rep_one_data["incoming_messages_count"],
        )
        self.assertEqual(
            org_data["forecast_amount"], rep_one_data["forecast_amount"],
        )
        self.assertEqual(
            org_data["deals_closed_count"], rep_one_data["deals_closed_count"],
        )
        self.assertEqual(
            org_data["amount_closed"], rep_one_data["amount_closed"],
        )
        self.assertEqual(
            org_data["forecast_table_additions"]["value"],
            rep_one_data["forecast_table_additions"],
        )

        # Add new rep and confirm org_data
        rep_two_data = self.generate_rep_two_focus_data()
        org_data = self.generate_org_focus_data()

        activities_count = (
            rep_one_data["activities_count"] + rep_two_data["activities_count"]
        )
        actions_count = rep_one_data["actions_count"] + rep_two_data["actions_count"]
        incoming_messages_count = (
            rep_one_data["incoming_messages_count"]
            + rep_two_data["incoming_messages_count"]
        )
        forecast_amount = (
            rep_one_data["forecast_amount"] + rep_two_data["forecast_amount"]
        )
        deals_closed_count = (
            rep_one_data["deals_closed_count"] + rep_two_data["deals_closed_count"]
        )
        amount_closed = rep_one_data["amount_closed"] + rep_two_data["amount_closed"]
        forecast_table_additions = (
            rep_one_data["forecast_table_additions"]
            + rep_two_data["forecast_table_additions"]
        )

        self.assertEqual(
            org_data["activities_count"], activities_count,
        )
        self.assertEqual(
            org_data["actions_count"], actions_count,
        )
        self.assertEqual(
            org_data["incoming_messages_count"], incoming_messages_count,
        )
        self.assertEqual(
            org_data["forecast_amount"], forecast_amount,
        )
        self.assertEqual(
            org_data["deals_closed_count"], deals_closed_count,
        )
        self.assertEqual(
            org_data["amount_closed"], amount_closed,
        )
        self.assertEqual(
            org_data["forecast_table_additions"]["value"], forecast_table_additions,
        )

    def test_average_for_field(self):
        """
        fields that utilize OrgFocusData.average_for_field:
        -- sales_cycle.average
        -- actions_to_close_opportunity.average
        -- ACV.average
        """
        # Originally, given fixture:
        # Only one rep with two leads.
        # Therefore, averages of OrgFocusData
        # should be same as the one rep's RepFocusData.
        rep_one_data = self.generate_rep_one_focus_data()
        org_data = self.generate_org_focus_data()

        self.assertEqual(
            org_data["sales_cycle"]["average"], rep_one_data["sales_cycle"],
        )
        self.assertEqual(
            org_data["actions_to_close_opportunity"]["average"],
            rep_one_data["actions_to_close_opportunity"]["average"],
        )
        self.assertEqual(
            org_data["ACV"]["average"], rep_one_data["ACV"],
        )

        # Add new rep and confirm org_data
        rep_two_data = self.generate_rep_two_focus_data()
        org_data = self.generate_org_focus_data()
        sales_cycle = (rep_one_data["sales_cycle"] + rep_two_data["sales_cycle"]) / 2
        actions_to_close_opportunity = (
            rep_one_data["actions_to_close_opportunity"]["average"]
            + rep_two_data["actions_to_close_opportunity"]["average"]
        ) / 2
        ACV = (rep_one_data["ACV"] + rep_two_data["ACV"]) / 2

        self.assertEqual(
            org_data["sales_cycle"]["average"], sales_cycle,
        )
        self.assertEqual(
            org_data["actions_to_close_opportunity"]["average"],
            actions_to_close_opportunity,
        )
        self.assertEqual(
            org_data["ACV"]["average"], ACV,
        )

    def test_deal_analysis(self):
        self.maxDiff = None
        # Originally, given fixture:
        expected = {
            "company_size": {"value": None, "percentage": None,},
            "industry": {"value": None, "percentage": None,},
            "type": {"value": None, "percentage": None,},
            "competitor": {"value": None, "percentage": None,},
            "geography": {"value": None, "percentage": None,},
        }
        data = self.generate_org_focus_data()
        self.assertDictEqual(data["deal_analysis"], expected)

        # Adding lead-custom-fields to only closed_lead_one
        self.closed_lead_one.company_size = lead_constants.FIFTYONE_TO_TWOHUNDRED
        self.closed_lead_one.industry = lead_constants.AGRICULTURE
        self.closed_lead_one.type = lead_constants.MQL
        self.closed_lead_one.competitor = lead_constants.YES
        self.closed_lead_one.geography_address = (
            "8830 Castlebury Ct, Laurel, MD 20723, USA"
        )
        self.closed_lead_one.geography_address_components = {
            "streetNumber": {"long_name": "8830", "short_name": "8830"},
            "route": {"long_name": "Castlebury Court", "short_name": "Castlebury Ct"},
            "locality": {"long_name": "Laurel", "short_name": "Laurel"},
            "administrative_area_level_3": {
                "long_name": "Savage",
                "short_name": "Savage",
            },
            "administrative_area_level_2": {
                "long_name": "Howard County",
                "short_name": "Howard County",
            },
            "administrative_area_level_1": {
                "long_name": "Maryland",
                "short_name": "MD",
            },
            "country": {"long_name": "United States", "short_name": "US"},
            "postalCode": {"long_name": "20723", "short_name": "20723"},
            "latitude": 39.124847,
            "longitude": -76.860657,
        }
        self.closed_lead_one.save()
        expected = {
            "company_size": {
                "value": lead_constants.FIFTYONE_TO_TWOHUNDRED,
                "percentage": 50,
            },
            "industry": {"value": lead_constants.AGRICULTURE, "percentage": 50},
            "type": {"value": lead_constants.MQL, "percentage": 50},
            "competitor": {"value": lead_constants.YES, "percentage": 50},
            "geography": {"value": "Maryland", "percentage": 50},
        }
        data = self.generate_org_focus_data()
        self.assertDictEqual(data["deal_analysis"], expected)

        # Also adding lead-custom-fields to closed_lead_two
        self.closed_lead_two.company_size = lead_constants.FIFTYONE_TO_TWOHUNDRED
        self.closed_lead_two.industry = lead_constants.AGRICULTURE
        self.closed_lead_two.type = lead_constants.MQL
        self.closed_lead_two.competitor = lead_constants.YES
        self.closed_lead_two.geography_address = (
            "8830 Castlebury Ct, Laurel, MD 20723, USA"
        )
        self.closed_lead_two.geography_address_components = {
            "streetNumber": {"long_name": "8830", "short_name": "8830"},
            "route": {"long_name": "Castlebury Court", "short_name": "Castlebury Ct"},
            "locality": {"long_name": "Laurel", "short_name": "Laurel"},
            "administrative_area_level_3": {
                "long_name": "Savage",
                "short_name": "Savage",
            },
            "administrative_area_level_2": {
                "long_name": "Howard County",
                "short_name": "Howard County",
            },
            "administrative_area_level_1": {
                "long_name": "Maryland",
                "short_name": "MD",
            },
            "country": {"long_name": "United States", "short_name": "US"},
            "postalCode": {"long_name": "20723", "short_name": "20723"},
            "latitude": 39.124847,
            "longitude": -76.860657,
        }
        self.closed_lead_two.save()
        expected = {
            "company_size": {
                "value": lead_constants.FIFTYONE_TO_TWOHUNDRED,
                "percentage": 100,
            },
            "industry": {"value": lead_constants.AGRICULTURE, "percentage": 100,},
            "type": {"value": lead_constants.MQL, "percentage": 100,},
            "competitor": {"value": lead_constants.YES, "percentage": 100,},
            "geography": {"value": "Maryland", "percentage": 100,},
        }
        data = self.generate_org_focus_data()
        self.assertDictEqual(data["deal_analysis"], expected)

        # Adding self.rep_two_closed_lead_one, which lacks custom-lead-fields
        self.generate_rep_two_focus_data()

        expected = {
            "company_size": {
                "value": lead_constants.FIFTYONE_TO_TWOHUNDRED,
                "percentage": 67,
            },
            "industry": {"value": lead_constants.AGRICULTURE, "percentage": 67},
            "type": {"value": lead_constants.MQL, "percentage": 67},
            "competitor": {"value": lead_constants.YES, "percentage": 67},
            "geography": {"value": "Maryland", "percentage": 67},
        }
        data = self.generate_org_focus_data()
        self.assertDictEqual(data["deal_analysis"], expected)

    def test_actions_to_close_opportunity_most_performed(self):
        # Fixture data includes one action for lead one,
        # zero actions for lead two,
        # and a total of two leads.
        data = self.generate_org_focus_data()
        most_performed = data["actions_to_close_opportunity"]["most_performed"]
        self.assertEqual(most_performed, "TEST ACTION ONE")

        # add enough actions for closed_lead_one of rep_one that this new action
        # is most-performed for organization
        action_type = ActionChoice.objects.create(
            title="test-choice-one", organization=self.organization,
        )
        for n in range(10):
            action = Action.objects.create(
                action_type=action_type,
                created_by=self.representative,
                lead=self.closed_lead_one,
            )
            # datetime_created must be between:
            # lead created && lead closed
            action.datetime_created = parse_datetime("2020-06-25 11:39:23.632256Z")
            action.save()
        data = self.generate_org_focus_data()
        most_performed = data["actions_to_close_opportunity"]["most_performed"]
        self.assertEqual(most_performed, action_type.title)

        # add enough actions for closed_lead_one of rep_two that this new action
        # is most-performed for organization
        self.generate_rep_two_focus_data()
        action_type = ActionChoice.objects.create(
            title="test-choice-two", organization=self.organization,
        )
        for n in range(15):
            action = Action.objects.create(
                action_type=action_type,
                created_by=self.rep_two,
                lead=self.rep_two_closed_lead_one,
            )
            # datetime_created must be between:
            # lead created && lead closed
            action.datetime_created = parse_datetime("2020-06-25 11:39:23.632256Z")
            action.save()
        data = self.generate_org_focus_data()
        most_performed = data["actions_to_close_opportunity"]["most_performed"]
        self.assertEqual(most_performed, action_type.title)

    def test_top_opportunities(self):
        # Originally, given fixture:
        data = self.generate_org_focus_data()
        top_closed = data["top_opportunities"][lead_constants.FORECAST_CLOSED]
        top_verbal = data["top_opportunities"][lead_constants.FORECAST_VERBAL]
        top_strong = data["top_opportunities"][lead_constants.FORECAST_STRONG]
        top_50_50 = data["top_opportunities"][lead_constants.FORECAST_FIFTY_FIFTY]
        self.assertEqual(len(top_closed), 2)
        self.assertEqual(len(top_verbal), 0)
        self.assertEqual(len(top_strong), 0)
        self.assertEqual(len(top_50_50), 0)

        # Add one lead that is currenty forecasted as STRONG
        # This lead belogs to rep_two, and the above should still be the case,
        # since this is org-level top_opportunities
        self.generate_rep_two_focus_data(skip_lead_generation=True)
        lead_three = Lead.objects.create(
            title="third lead",
            created_by=self.rep_two,
            claimed_by=self.rep_two,
            amount=100,
            expected_close_date=parse_datetime("2020-10-01T05:00:00Z"),
            account=Account.objects.first(),
        )
        LeadActivityLog.objects.create(
            activity=lead_constants.LEAD_UPDATED,
            lead=lead_three,
            action_taken_by=self.rep_two,
            action_timestamp=parse_datetime("2020-04-01T05:00:00Z"),
            datetime_created=parse_datetime("2020-04-01T05:00:00Z"),
            meta={
                "extra": {
                    "forecast_update": True,
                    "forecast_amount": 100,
                    "new_forecast": lead_constants.FORECAST_STRONG,
                    "previous_forecast": lead_constants.FORECAST_NA,
                }
            },
        )
        data = self.generate_org_focus_data()
        top_closed = data["top_opportunities"][lead_constants.FORECAST_CLOSED]
        top_verbal = data["top_opportunities"][lead_constants.FORECAST_VERBAL]
        top_strong = data["top_opportunities"][lead_constants.FORECAST_STRONG]
        top_50_50 = data["top_opportunities"][lead_constants.FORECAST_FIFTY_FIFTY]
        self.assertEqual(len(top_closed), 2)
        self.assertEqual(len(top_verbal), 0)
        self.assertEqual(len(top_strong), 1)
        self.assertEqual(len(top_50_50), 0)

        # Add another lead with forecast of STRONG, yet should be same output
        # as last data generated
        lead_four = Lead.objects.create(
            title="fourth lead",
            created_by=self.representative,
            claimed_by=self.representative,
            amount=100,
            expected_close_date=parse_datetime("2020-10-01T05:00:00Z"),
            account=Account.objects.first(),
        )
        LeadActivityLog.objects.create(
            activity=lead_constants.LEAD_UPDATED,
            lead=lead_four,
            action_taken_by=self.representative,
            action_timestamp=parse_datetime("2020-04-01T05:00:00Z"),
            datetime_created=parse_datetime("2020-04-01T05:00:00Z"),
            meta={
                "extra": {
                    "forecast_update": True,
                    "forecast_amount": 100,
                    "new_forecast": lead_constants.FORECAST_STRONG,
                    "previous_forecast": lead_constants.FORECAST_NA,
                }
            },
        )
        data = self.generate_org_focus_data()
        top_closed = data["top_opportunities"][lead_constants.FORECAST_CLOSED]
        top_verbal = data["top_opportunities"][lead_constants.FORECAST_VERBAL]
        top_strong = data["top_opportunities"][lead_constants.FORECAST_STRONG]
        top_50_50 = data["top_opportunities"][lead_constants.FORECAST_FIFTY_FIFTY]
        self.assertEqual(len(top_closed), 2)
        self.assertEqual(len(top_verbal), 0)
        self.assertEqual(len(top_strong), 1)
        self.assertEqual(len(top_50_50), 0)

        # Add lead with forecast of VERBAL,
        # should be included as third lead alongside two original CLOSED,
        # and therefore there should be no STRONG leads in top_opportunities.
        # This lead belogs to rep_two, and the above should still be the case,
        # since this is org-level top_opportunities
        lead_five = Lead.objects.create(
            title="fifth lead",
            created_by=self.rep_two,
            claimed_by=self.rep_two,
            amount=100,
            expected_close_date=parse_datetime("2020-10-01T05:00:00Z"),
            account=Account.objects.first(),
        )
        LeadActivityLog.objects.create(
            activity=lead_constants.LEAD_UPDATED,
            lead=lead_five,
            action_taken_by=self.rep_two,
            action_timestamp=parse_datetime("2020-04-01T05:00:00Z"),
            datetime_created=parse_datetime("2020-04-01T05:00:00Z"),
            meta={
                "extra": {
                    "forecast_update": True,
                    "forecast_amount": 100,
                    "new_forecast": lead_constants.FORECAST_VERBAL,
                    "previous_forecast": lead_constants.FORECAST_NA,
                }
            },
        )
        data = self.generate_org_focus_data()
        top_closed = data["top_opportunities"][lead_constants.FORECAST_CLOSED]
        top_verbal = data["top_opportunities"][lead_constants.FORECAST_VERBAL]
        top_strong = data["top_opportunities"][lead_constants.FORECAST_STRONG]
        top_50_50 = data["top_opportunities"][lead_constants.FORECAST_FIFTY_FIFTY]
        self.assertEqual(len(top_closed), 2)
        self.assertEqual(len(top_verbal), 1)
        self.assertEqual(len(top_strong), 0)
        self.assertEqual(len(top_50_50), 0)

    def test_top_performers(self):
        """
        fields that utilize OrgFocusData.top_performers:
        -- top_performers_by_A_C_V
        -- top_performers_by_actions
        -- sales_cycle.top_performer
        -- actions_to_close_opportunity.top_performer
        -- ACV.top_performer
        -- forecast_table_additions.top_performer
        """
        # given fixture, there is only one rep, so they should
        # be the one and only top_performer
        data = self.generate_org_focus_data()

        self.assertEqual(len(data["top_performers_by_A_C_V"]), 1)
        self.assertEqual(len(data["top_performers_by_actions"]), 1)
        self.assertEqual(len(data["sales_cycle"]["top_performer"]), 1)
        self.assertEqual(len(data["actions_to_close_opportunity"]["top_performer"]), 1)
        self.assertEqual(len(data["ACV"]["top_performer"]), 1)
        self.assertEqual(len(data["forecast_table_additions"]["top_performer"]), 1)

        self.assertEqual(
            data["top_performers_by_A_C_V"][0]["id"], str(self.representative.id)
        )
        self.assertEqual(
            data["top_performers_by_actions"][0]["id"], str(self.representative.id)
        )
        self.assertEqual(
            data["sales_cycle"]["top_performer"][0]["id"], str(self.representative.id)
        )
        self.assertEqual(
            data["actions_to_close_opportunity"]["top_performer"][0]["id"],
            str(self.representative.id),
        )
        self.assertEqual(
            data["ACV"]["top_performer"][0]["id"], str(self.representative.id)
        )
        self.assertEqual(
            data["forecast_table_additions"]["top_performer"][0]["id"],
            str(self.representative.id),
        )

        # add the second rep, and length of top_performers should update
        self.generate_rep_two_focus_data()
        data = self.generate_org_focus_data()

        # increase:
        self.assertEqual(len(data["top_performers_by_A_C_V"]), 2)
        self.assertEqual(len(data["top_performers_by_actions"]), 2)
        # remain the same:
        self.assertEqual(len(data["sales_cycle"]["top_performer"]), 1)
        self.assertEqual(len(data["actions_to_close_opportunity"]["top_performer"]), 1)
        self.assertEqual(len(data["ACV"]["top_performer"]), 1)
        self.assertEqual(len(data["forecast_table_additions"]["top_performer"]), 1)

        # so far, self.representative has one action and a high ACV
        # self.rep_two has zero actions and a low ACV,
        # so self.representative should be top performer for the following fields:
        self.assertEqual(
            data["top_performers_by_A_C_V"][0]["id"], str(self.representative.id)
        )
        self.assertEqual(
            data["ACV"]["top_performer"][0]["id"], str(self.representative.id)
        )
        self.assertEqual(
            data["top_performers_by_actions"][0]["id"], str(self.representative.id)
        )

        # give self.rep_two a new lead with astronomical closing_amount, to be top_by_A_C_V
        # give self.rep_two a couple of actions, to be top_by_actions
        lead_one = Lead.objects.create(
            title="test-lead-one",
            created_by=self.rep_two,
            claimed_by=self.rep_two,
            status=Stage.objects.get(pk="fe89a6fd-f049-4b23-a059-86d45c12b14b"),
            amount=999999,
            closing_amount=999999,
            expected_close_date=parse_datetime("2020-10-05T05:00:00Z"),
            account=Account.objects.first(),
        )
        log_one = LeadActivityLog.objects.create(
            activity=lead_constants.LEAD_CLOSED,
            lead=lead_one,
            action_taken_by=self.rep_two,
            action_timestamp=parse_datetime("2020-10-06T05:00:00Z"),
            datetime_created=parse_datetime("2020-10-06T05:00:00Z"),
        )
        # force a high sales-cycle avg for rep_two
        lead_one.datetime_created = parse_datetime("2020-08-05T05:00:00Z")
        lead_one.save()
        log_one.datetime_created = parse_datetime("2020-10-06T05:00:00Z")
        log_one.action_timestamp = parse_datetime("2020-10-06T05:00:00Z")
        log_one.save()
        action_type = ActionChoice.objects.create(
            title="test-choice-one", organization=self.organization,
        )
        for n in range(10):
            action = Action.objects.create(
                action_type=action_type, created_by=self.rep_two, lead=lead_one,
            )
            action.datetime_created = parse_datetime("2020-08-05T05:00:00Z")
            action.save()

        data = self.generate_org_focus_data()

        self.assertEqual(data["top_performers_by_A_C_V"][0]["id"], str(self.rep_two.id))
        self.assertEqual(
            data["top_performers_by_actions"][0]["id"], str(self.rep_two.id)
        )
        self.assertEqual(data["ACV"]["top_performer"][0]["id"], str(self.rep_two.id))
        self.assertEqual(
            data["sales_cycle"]["top_performer"][0]["id"], str(self.representative.id)
        )

        # decrease sales-cycle avg for rep_two, by closing lead one in a day :)
        lead_one.expected_close_date = parse_datetime("2020-08-06T05:00:00Z")
        lead_one.save()
        log_one.datetime_created = parse_datetime("2020-08-06T05:00:00Z")
        log_one.action_timestamp = parse_datetime("2020-08-06T05:00:00Z")
        log_one.save()
        data = self.generate_org_focus_data()

        self.assertEqual(
            data["sales_cycle"]["top_performer"][0]["id"], str(self.rep_two.id)
        )

