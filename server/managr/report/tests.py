from django.test import TestCase

from managr.core.models import User
from managr.organization.models import Organization, Account
from managr.lead.models import Lead, LeadActivityLog, Action, ActionChoice
from managr.lead import constants as lead_constants

from .models import (
    StoryReport,
    PerformanceReport,
)
from .story_report_generation import (
    LeadDataGenerator,
    RepresentativeDataGenerator,
    OrganizationDataGenerator
)
from .performance_report_generation import (
    RepDataForSelectedDateRange
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
    fixtures = ["fixture.json", "report_meta.json", "report_lead_one.json", "report_lead_two.json"]

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
        total = self.lead_one_data.days_ready_to_booked + self.lead_two_data.days_ready_to_booked
        # rounded to zero decimal places, as does RepresentativeDataGenerator
        average_days_ready_to_booked = round(total / 2, 0)
        self.assertEqual(self.rep_data_dict["average_days_ready_to_booked"], average_days_ready_to_booked)


class PerformanceReportRepresentativeFocusedDateRangeTestCase(TestCase):
    fixtures = ["fixture.json", "report_meta.json", "report_lead_one.json", "report_lead_two.json"]

    def setUp(self):
        # should be loaded from the fixture, else should error
        self.representative = User.objects.get(pk="3dddd261-93b1-46fe-a83e-bc164551362a")
        self.organization = self.representative.organization
        # Both leads closed in 2020
        self.closed_lead_one = Lead.objects.get(pk="99b5e01e-4c8a-4ba5-be09-5407848aa87a")
        self.closed_lead_two = Lead.objects.get(pk="77d63cfd-dd2d-40a8-9dfb-3c7d6865fd6d")
        self.performance_report = PerformanceReport.objects.create(
            representative=self.representative,
            generated_by=self.representative,
            date_range_preset=report_const.THIS_YEAR,
            date_range_from="2020-01-01T05:00:00Z",
            date_range_to="2021-01-01T04:59:59.999000Z",
        )

    def generate_report_data(self):
        return RepDataForSelectedDateRange(self.performance_report).as_dict

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
            datetime_created="2020-03-01T05:00:00Z",
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
        aggregate = self.closed_lead_one.closing_amount + self.closed_lead_two.closing_amount
        self.assertEqual(data["amount_closed"], aggregate)

    def test_ACV(self):
        data = self.generate_report_data()
        aggregate = self.closed_lead_one.closing_amount + self.closed_lead_two.closing_amount
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
        # the rounding via Python's round() is down, hence zero
        self.assertEqual(average, 0)
        self.assertEqual(most_performed, 'TEST ACTION ONE')

        action_type = ActionChoice.objects.create(
            title="test-choice",
            organization=self.organization,
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
        # datetime_created not working, so they fall out of range since lead closed long ago
        data = self.generate_report_data()
        average = data["actions_to_close_opportunity"]["average"]
        most_performed = data["actions_to_close_opportunity"]["most_performed"]

        # lead one has 11 action
        # lead two has 0 actions
        # there are two leads
        # so 11/2 => 5.5
        # the rounding via Python's round() is up, hence 6
        self.assertEqual(average, 6)
        self.assertEqual(most_performed, action_type.title)

    def test_sales_cycle(self):
        num_1 = LeadDataGenerator(self.closed_lead_one).as_dict["days_to_closed"]
        num_2 = LeadDataGenerator(self.closed_lead_two).as_dict["days_to_closed"]
        average = round((num_1 + num_2) / 2)
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
                    "extra": {
                        "forecast_table_addition": True,
                        "forecast_amount": 200,
                    }
                }
            )

        data = self.generate_report_data()
        self.assertEqual(data["forecast_table_additions"], 1)

        LeadActivityLog.objects.create(
                activity=lead_constants.LEAD_UPDATED,
                lead=self.closed_lead_two,
                action_taken_by=self.representative,
                action_timestamp="2020-04-01T05:00:00Z",
                datetime_created="2020-04-01T05:00:00Z",
                meta={
                    "extra": {
                        "forecast_table_addition": True,
                        "forecast_amount": 200,
                    }
                }
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
            meta={
                "extra": {
                    "forecast_table_addition": True,
                    "forecast_amount": 200,
                }
            }
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
            meta={
                "extra": {
                    "forecast_table_addition": True,
                    "forecast_amount": 500,
                }
            }
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
            meta={
                "extra": {
                    "forecast_table_addition": True,
                    "forecast_amount": 200,
                }
            }
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
            'company_size': {
                'value': None,
                'percentage': None,
            },
            'industry': {
                'value': None,
                'percentage': None,
            },
            'type': {
                'value': None,
                'percentage': None,
            },
            'competitor': {
                'value': None,
                'percentage': None,
            },
            'geography': {
                'value': None,
                'percentage': None,
            },
        }
        data = self.generate_report_data()
        self.assertDictEqual(data["deal_analysis"], expected)

        # Adding lead-custom-fields to only closed_lead_one
        self.closed_lead_one.company_size = lead_constants.FIFTYONE_TO_TWOHUNDRED
        self.closed_lead_one.industry = lead_constants.AGRICULTURE
        self.closed_lead_one.type = lead_constants.MQL
        self.closed_lead_one.competitor = lead_constants.YES
        self.closed_lead_one.geography_address = "8830 Castlebury Ct, Laurel, MD 20723, USA"
        self.closed_lead_one.geography_address_components = {
                                                                "streetNumber": {
                                                                    "long_name": "8830",
                                                                    "short_name": "8830"
                                                                },
                                                                "route": {
                                                                    "long_name": "Castlebury Court",
                                                                    "short_name": "Castlebury Ct"
                                                                },
                                                                "locality": {
                                                                    "long_name": "Laurel",
                                                                    "short_name": "Laurel"
                                                                },
                                                                "administrative_area_level_3": {
                                                                    "long_name": "Savage",
                                                                    "short_name": "Savage"
                                                                },
                                                                "administrative_area_level_2": {
                                                                    "long_name": "Howard County",
                                                                    "short_name": "Howard County"
                                                                },
                                                                "administrative_area_level_1": {
                                                                    "long_name": "Maryland",
                                                                    "short_name": "MD"
                                                                },
                                                                "country": {
                                                                    "long_name": "United States",
                                                                    "short_name": "US"
                                                                },
                                                                "postalCode": {
                                                                    "long_name": "20723",
                                                                    "short_name": "20723"
                                                                },
                                                                "latitude": 39.124847,
                                                                "longitude": -76.860657
                                                            }
        self.closed_lead_one.save()
        expected = {
            'company_size': {
                'value': lead_constants.FIFTYONE_TO_TWOHUNDRED,
                'percentage': 50
            },
            'industry': {
                'value': lead_constants.AGRICULTURE,
                'percentage': 50
            },
            'type': {
                'value': lead_constants.MQL,
                'percentage': 50
            },
            'competitor': {
                'value': lead_constants.YES,
                'percentage': 50
            },
            'geography': {
                'value': "Maryland",
                'percentage': 50
            }
        }
        data = self.generate_report_data()
        self.assertDictEqual(data["deal_analysis"], expected)

        # Also adding lead-custom-fields to closed_lead_two
        self.closed_lead_two.company_size = lead_constants.FIFTYONE_TO_TWOHUNDRED
        self.closed_lead_two.industry = lead_constants.AGRICULTURE
        self.closed_lead_two.type = lead_constants.MQL
        self.closed_lead_two.competitor = lead_constants.YES
        self.closed_lead_two.geography_address = "8830 Castlebury Ct, Laurel, MD 20723, USA"
        self.closed_lead_two.geography_address_components = {
                                                                "streetNumber": {
                                                                    "long_name": "8830",
                                                                    "short_name": "8830"
                                                                },
                                                                "route": {
                                                                    "long_name": "Castlebury Court",
                                                                    "short_name": "Castlebury Ct"
                                                                },
                                                                "locality": {
                                                                    "long_name": "Laurel",
                                                                    "short_name": "Laurel"
                                                                },
                                                                "administrative_area_level_3": {
                                                                    "long_name": "Savage",
                                                                    "short_name": "Savage"
                                                                },
                                                                "administrative_area_level_2": {
                                                                    "long_name": "Howard County",
                                                                    "short_name": "Howard County"
                                                                },
                                                                "administrative_area_level_1": {
                                                                    "long_name": "Maryland",
                                                                    "short_name": "MD"
                                                                },
                                                                "country": {
                                                                    "long_name": "United States",
                                                                    "short_name": "US"
                                                                },
                                                                "postalCode": {
                                                                    "long_name": "20723",
                                                                    "short_name": "20723"
                                                                },
                                                                "latitude": 39.124847,
                                                                "longitude": -76.860657
                                                            }
        self.closed_lead_two.save()
        expected = {
            'company_size': {
                'value': lead_constants.FIFTYONE_TO_TWOHUNDRED,
                'percentage': 100,
            },
            'industry': {
                'value': lead_constants.AGRICULTURE,
                'percentage': 100,
            },
            'type': {
                'value': lead_constants.MQL,
                'percentage': 100,
            },
            'competitor': {
                'value': lead_constants.YES,
                'percentage': 100,
            },
            'geography': {
                'value': "Maryland",
                'percentage': 100,
            }
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
                }
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
                }
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
                }
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
