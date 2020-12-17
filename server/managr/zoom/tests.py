import math
import uuid
from datetime import datetime
import pytz

from django.test import TestCase
from django.utils import timezone

from managr.core.models import User
from managr.lead import constants as lead_consts
from managr.lead.models import Lead
from managr.organization.models import Organization, Stage
from managr.organization.factories import AccountFactory, ContactFactory
from managr.slack import constants as slack_consts

from .utils import score_meeting
from .models import ZoomAuthAccount, ZoomMeeting, MeetingReview
from . import constants as zoom_consts


class MeetingScoreTestCase(TestCase):
    # The fixture provides a test user and org
    fixtures = ["dev.json"]

    def setUp(self):
        self.user = User.objects.first()
        self.org = Organization.objects.first()

        self.account = AccountFactory(organization=self.org)
        self.lead = Lead.objects.create(account=self.account, claimed_by=self.user)

        self.ready_stage = Stage.objects.get(title="READY")
        self.booked_stage = Stage.objects.get(title="BOOKED")

        self.zoom_account = ZoomAuthAccount.objects.create(
            user=self.user,
            zoom_id="12345",
            email="test@user.com",
            type=0,
            personal_meeting_url="test.com",
            timezone="US/Eastern",
            verified=1,
            host_key="12345",
            jid="12345",
            account_id="12345",
            status="12345",
            access_token="12345",
            refresh_token="12345",
            token_generated_date=timezone.now(),
        )
        self.zoom_meeting = ZoomMeeting.objects.create(
            zoom_account=self.zoom_account,
            meeting_id="12345",
            meeting_uuid=uuid.uuid4(),
            type=1,
            lead=self.lead,
            #
            # Other fields available on this model...
            #
            # start_time
            # end_time
            # duration
            # status
            # participants   # Many-to-many to contacts - needed for score
            # participants_count
            # total_minutes
        )
        #
        # NOTE
        # This is here or documentation - this shows the fields available
        # on the MeetingReview model that impacts the meeting score.
        #
        # self.meeting_review = MeetingReview.objects.create(
        #     meeting=self.zoom_meeting,
        #     # Text that must match a Stage in the DB
        #     # update_stage="READY",
        #     sentiment=slack_consts.ZOOM_MEETING__GREAT,
        #     # forecast_strength=lead_consts.FORECAST_STRONG,
        #     # updated_close_date=datetime(2020, 12, 15)
        #     #
        #     # Other fields available on this model...
        #     #
        #     # description
        #     # next_steps
        #     # prev_forecast
        #     # prev_stage
        #     # prev_expected_close_date
        #     # prev_amount
        # )
        # END NOTE

    def test_meeting_review_sentiment_great(self):
        self.meeting_review = MeetingReview.objects.create(
            meeting=self.zoom_meeting, sentiment=slack_consts.ZOOM_MEETING__GREAT,
        )
        score, score_components = score_meeting(self.zoom_meeting)
        self.assertEqual(score, 50)

    def test_meeting_review_sentiment_cant_tell(self):
        self.meeting_review = MeetingReview.objects.create(
            meeting=self.zoom_meeting, sentiment=slack_consts.ZOOM_MEETING__CANT_TELL,
        )
        score, score_components = score_meeting(self.zoom_meeting)
        self.assertEqual(score, 20)

    def test_meeting_review_sentiment_not_well(self):
        self.meeting_review = MeetingReview.objects.create(
            meeting=self.zoom_meeting, sentiment=slack_consts.ZOOM_MEETING__NOT_WELL,
        )
        score, score_components = score_meeting(self.zoom_meeting)
        self.assertEqual(score, 0)

    def test_meeting_review_stage_progressed_from_none(self):
        # NOTE: 'READY' is a global `Stage` from the fixture data
        self.meeting_review = MeetingReview.objects.create(
            meeting=self.zoom_meeting, update_stage=self.ready_stage.id,
        )
        score, score_components = score_meeting(self.zoom_meeting)

        # Without a sentiment, the score is 20 (can't tell) + 10 (progress)
        self.assertEqual(score, 30)

    def test_meeting_review_stage_progressed_next_stage(self):
        self.meeting_review = MeetingReview.objects.create(
            meeting=self.zoom_meeting,
            prev_stage=self.ready_stage.id,
            update_stage=self.booked_stage.id,
        )
        score, score_components = score_meeting(self.zoom_meeting)

        # Without a sentiment, the score is 20 (can't tell) + 10 (progress)
        self.assertEqual(score, 30)

    def test_meeting_stage_progressed_render_message(self):
        self.meeting_review = MeetingReview.objects.create(
            meeting=self.zoom_meeting,
            prev_stage=self.ready_stage.id,
            update_stage=self.booked_stage.id,
        )
        score, score_components = score_meeting(self.zoom_meeting)

        stage_component = [sc for sc in score_components if sc.type == "stage"][0]

        self.assertEqual(
            stage_component.rendered_message,
            "The opportunity moved forward to a new stage: BOOKED.",
        )

        # Without a sentiment, the score is 20 (can't tell) + 10 (progress)
        self.assertEqual(score, 30)

    def test_meeting_review_stage_regressed_to_none(self):
        self.meeting_review = MeetingReview.objects.create(
            meeting=self.zoom_meeting,
            prev_stage=self.ready_stage.id,
            update_stage=None,
        )
        score, score_components = score_meeting(self.zoom_meeting)

        # Without a sentiment, the score is 20 (can't tell) - 10 (regressed)
        self.assertEqual(score, 10)

    def test_meeting_review_stage_regressed_prev_stage(self):
        self.meeting_review = MeetingReview.objects.create(
            meeting=self.zoom_meeting,
            prev_stage=self.booked_stage.id,
            update_stage=self.ready_stage.id,
        )
        score, score_components = score_meeting(self.zoom_meeting)

        # Without a sentiment, the score is 20 (can't tell) - 10 (regressed)
        self.assertEqual(score, 10)

    def test_meeting_review_stage_unchanged(self):
        self.meeting_review = MeetingReview.objects.create(
            meeting=self.zoom_meeting,
            prev_stage=self.booked_stage.id,
            update_stage=self.booked_stage.id,
        )
        score, score_components = score_meeting(self.zoom_meeting)

        # Without a sentiment, the score is 20 (can't tell) - 0 (unchanged)
        self.assertEqual(score, 20)

    def test_meeting_forecast_progress_from_none(self):
        self.meeting_review = MeetingReview.objects.create(
            meeting=self.zoom_meeting,
            forecast_strength=lead_consts.FORECAST_FIFTY_FIFTY,
        )
        score, score_components = score_meeting(self.zoom_meeting)

        # Without a sentiment, the score is 20 (can't tell) + 10 (progress)
        self.assertEqual(score, 30)

    def test_meeting_forecast_progress_from_prev(self):
        self.meeting_review = MeetingReview.objects.create(
            meeting=self.zoom_meeting,
            prev_forecast=lead_consts.FORECAST_FIFTY_FIFTY,
            forecast_strength=lead_consts.FORECAST_STRONG,
        )
        score, score_components = score_meeting(self.zoom_meeting)

        # Without a sentiment, the score is 20 (can't tell) + 10 (progress)
        self.assertEqual(score, 30)

    def test_meeting_forecast_regression_to_none(self):
        self.meeting_review = MeetingReview.objects.create(
            meeting=self.zoom_meeting,
            prev_forecast=lead_consts.FORECAST_FIFTY_FIFTY,
            forecast_strength=None,
        )
        score, score_components = score_meeting(self.zoom_meeting)

        # Without a sentiment, the score is 20 (can't tell) - 10 (regression)
        self.assertEqual(score, 10)

    def test_meeting_forecast_regression_to_prev(self):
        self.meeting_review = MeetingReview.objects.create(
            meeting=self.zoom_meeting,
            prev_forecast=lead_consts.FORECAST_STRONG,
            forecast_strength=lead_consts.FORECAST_FIFTY_FIFTY,
        )
        score, score_components = score_meeting(self.zoom_meeting)

        # Without a sentiment, the score is 20 (can't tell) - 10 (regression)
        self.assertEqual(score, 10)

    def test_meeting_forecast_unchanged(self):
        self.meeting_review = MeetingReview.objects.create(
            meeting=self.zoom_meeting,
            prev_forecast=lead_consts.FORECAST_STRONG,
            forecast_strength=lead_consts.FORECAST_STRONG,
        )
        score, score_components = score_meeting(self.zoom_meeting)

        # Without a sentiment, the score is 20 (can't tell) + 0 (unchanged)
        self.assertEqual(score, 20)

    def test_meeting_close_date_progress_from_none(self):
        self.meeting_review = MeetingReview.objects.create(
            meeting=self.zoom_meeting,
            prev_expected_close_date=None,
            updated_close_date=datetime(2020, 12, 15, tzinfo=pytz.UTC),
        )
        score, score_components = score_meeting(self.zoom_meeting)

        # Without a sentiment, the score is 20 (can't tell) + 5 (progress)
        self.assertEqual(score, 25)

    def test_meeting_close_date_progress_from_prev(self):
        self.meeting_review = MeetingReview.objects.create(
            meeting=self.zoom_meeting,
            prev_expected_close_date=datetime(2020, 12, 20, tzinfo=pytz.UTC),
            updated_close_date=datetime(2020, 12, 15, tzinfo=pytz.UTC),
        )
        score, score_components = score_meeting(self.zoom_meeting)

        # Without a sentiment, the score is 20 (can't tell) + 5 (progress)
        self.assertEqual(score, 25)

        # Check rendered message
        close_date_component = [
            sc for sc in score_components if sc.type == "close_date"
        ][0]
        self.assertEqual(
            close_date_component.rendered_message,
            "The opportunity's forecast close date improved. It is now: 12/15/2020",
        )

    def test_meeting_close_date_regression_from_prev(self):
        self.meeting_review = MeetingReview.objects.create(
            meeting=self.zoom_meeting,
            prev_expected_close_date=datetime(2020, 12, 15, tzinfo=pytz.UTC),
            updated_close_date=datetime(2020, 12, 20, tzinfo=pytz.UTC),
        )
        score, score_components = score_meeting(self.zoom_meeting)

        # Without a sentiment, the score is 20 (can't tell) - 5 (regression)
        self.assertEqual(score, 15)

    def test_meeting_close_date_regression_to_none(self):
        self.meeting_review = MeetingReview.objects.create(
            meeting=self.zoom_meeting,
            prev_expected_close_date=datetime(2020, 12, 15),
            updated_close_date=None,
        )
        score, score_components = score_meeting(self.zoom_meeting)

        # Without a sentiment, the score is 20 (can't tell) - 5 (regression)
        self.assertEqual(score, 15)

    def test_meeting_close_date_unchanged(self):
        self.meeting_review = MeetingReview.objects.create(
            meeting=self.zoom_meeting,
            prev_expected_close_date=datetime(2020, 12, 15),
            updated_close_date=datetime(2020, 12, 15),
        )
        score, score_components = score_meeting(self.zoom_meeting)

        # Without a sentiment, the score is 20 (can't tell) + 0 (unchanged)
        self.assertEqual(score, 20)

    def test_meeting_participant_count_none(self):
        self.zoom_meeting.participants_count = None
        self.zoom_meeting.save()
        self.meeting_review = MeetingReview.objects.create(meeting=self.zoom_meeting)
        score, score_components = score_meeting(self.zoom_meeting)

        # 20 (can't tell) + 0
        self.assertEqual(score, 20)

    def test_meeting_participant_count_zero(self):
        self.zoom_meeting.participants_count = 0
        self.zoom_meeting.save()
        self.meeting_review = MeetingReview.objects.create(meeting=self.zoom_meeting)
        score, score_components = score_meeting(self.zoom_meeting)

        # 20 (can't tell) + 0
        self.assertEqual(score, 20)

    def test_meeting_participant_count_one(self):
        self.zoom_meeting.participants_count = 1
        self.zoom_meeting.save()
        self.meeting_review = MeetingReview.objects.create(meeting=self.zoom_meeting)
        score, score_components = score_meeting(self.zoom_meeting)

        # 20 (can't tell) + 0
        self.assertEqual(score, 20)

    def test_meeting_participant_count_two(self):
        self.zoom_meeting.participants_count = 2
        self.zoom_meeting.save()
        self.meeting_review = MeetingReview.objects.create(meeting=self.zoom_meeting)
        score, score_components = score_meeting(self.zoom_meeting)

        # 20 (can't tell) + 2
        self.assertEqual(score, 22)

    def test_meeting_participant_count_three(self):
        self.zoom_meeting.participants_count = 3
        self.zoom_meeting.save()
        self.meeting_review = MeetingReview.objects.create(meeting=self.zoom_meeting)
        score, score_components = score_meeting(self.zoom_meeting)

        # 20 (can't tell) + 3
        self.assertEqual(score, 23)

    def test_meeting_participant_count_four(self):
        self.zoom_meeting.participants_count = 4
        self.zoom_meeting.save()
        self.meeting_review = MeetingReview.objects.create(meeting=self.zoom_meeting)
        score, score_components = score_meeting(self.zoom_meeting)

        # 20 (can't tell) + 4
        self.assertEqual(score, 24)

    def test_meeting_participant_count_five(self):
        self.zoom_meeting.participants_count = 5
        self.zoom_meeting.save()
        self.meeting_review = MeetingReview.objects.create(meeting=self.zoom_meeting)
        score, score_components = score_meeting(self.zoom_meeting)

        # 20 (can't tell) + 5
        self.assertEqual(score, 25)

    def test_meeting_participant_count_more_than_five(self):
        self.zoom_meeting.participants_count = 8
        self.zoom_meeting.save()
        self.meeting_review = MeetingReview.objects.create(meeting=self.zoom_meeting)
        score, score_components = score_meeting(self.zoom_meeting)

        # 20 (can't tell) + 5
        self.assertEqual(score, 25)

    def test_meeting_participation_score_high(self):
        meeting_duration = 60
        avg_participation_time = 53
        participants = 3

        # Update the meeting:
        #  - Duration is the actual length the meeting lasted
        #  - Total minutes is the total participation time of ALL
        #    participants, mocked here.
        self.zoom_meeting.duration = meeting_duration
        self.zoom_meeting.participants_count = participants
        self.zoom_meeting.total_minutes = (
            meeting_duration + (participants - 1) * avg_participation_time
        )
        self.zoom_meeting.save()

        # Create review and compute score
        self.meeting_review = MeetingReview.objects.create(meeting=self.zoom_meeting)
        score, score_components = score_meeting(self.zoom_meeting)

        # Check that participation score is correct by itself
        self.assertEqual(self.meeting_review.participation_score, 9)

        # Base of 20 points for "Can't Tell"
        # + Plus three points for participant count
        # + Plus ten points for meeting duration (instant over 60)
        # + Plus a score which should be the avg participation time as a
        #   percentage of meeting duration, rounded up, divided by 10.
        self.assertEqual(score, 42)

        # Check the resulting message of the 'participation' component
        participation_component = [
            sc for sc in score_components if sc.type == "participation"
        ][0]
        self.assertEqual(participation_component.points, 9)
        self.assertEqual(
            participation_component.message_tpl,
            "All attendees participated for the entire duration of the meeting.",
        )

    def test_meeting_participation_score_low(self):
        meeting_duration = 60
        avg_participation_time = 23
        participants = 2

        # Update the meeting:
        #  - Duration is the actual length the meeting lasted
        #  - Total minutes is the total participation time of ALL
        #    participants, mocked here.
        self.zoom_meeting.duration = meeting_duration
        self.zoom_meeting.participants_count = participants
        self.zoom_meeting.total_minutes = (
            meeting_duration + (participants - 1) * avg_participation_time
        )
        self.zoom_meeting.save()

        # Create review and compute score
        self.meeting_review = MeetingReview.objects.create(meeting=self.zoom_meeting)
        score, score_components = score_meeting(self.zoom_meeting)

        # Check that participation score is correct by itself
        self.assertEqual(self.meeting_review.participation_score, 4)

        # Base of 20 points for "Can't Tell"
        # + Plus two points for participant count
        # + Plus ten points for meeting duration (instant over 60)
        # + Plus a score which should be the avg participation time as a
        #   percentage of meeting duration, rounded up, divided by 10.
        self.assertEqual(score, 36)

        # Check the resulting message of the 'participation' component
        participation_component = [
            sc for sc in score_components if sc.type == "participation"
        ][0]
        self.assertEqual(participation_component.points, 4)
        self.assertEqual(
            participation_component.message_tpl,
            "Most attendees participated for less than half of the meeting.",
        )

    def test_meeting_duration_instant_over_60(self):
        self.zoom_meeting.type = 1
        self.zoom_meeting.duration = 65
        self.zoom_meeting.save()

        self.meeting_review = MeetingReview.objects.create(meeting=self.zoom_meeting)
        self.assertEqual(self.meeting_review.duration_score, "instant_over_60")

        score, score_components = score_meeting(self.zoom_meeting)

        # 20 (can't tell) + 10
        self.assertEqual(score, 30)

    def test_meeting_duration_instant_over_30(self):
        self.zoom_meeting.type = 1
        self.zoom_meeting.duration = 40
        self.zoom_meeting.save()

        self.meeting_review = MeetingReview.objects.create(meeting=self.zoom_meeting)
        self.assertEqual(self.meeting_review.duration_score, "instant_over_30")

        score, score_components = score_meeting(self.zoom_meeting)

        # 20 (can't tell) + 6
        self.assertEqual(score, 26)

    def test_meeting_duration_instant_over_20(self):
        self.zoom_meeting.type = 1
        self.zoom_meeting.duration = 20
        self.zoom_meeting.save()

        self.meeting_review = MeetingReview.objects.create(meeting=self.zoom_meeting)
        self.assertEqual(self.meeting_review.duration_score, "instant_over_20")

        score, score_components = score_meeting(self.zoom_meeting)

        # 20 (can't tell) + 3
        self.assertEqual(score, 23)

    def test_meeting_duration_planned_over_15(self):
        self.zoom_meeting.type = 0
        self.zoom_meeting.original_duration = 15
        self.zoom_meeting.duration = 35
        self.zoom_meeting.save()

        self.meeting_review = MeetingReview.objects.create(meeting=self.zoom_meeting)
        self.assertEqual(self.meeting_review.duration_score, "planned_over_15")

        score, score_components = score_meeting(self.zoom_meeting)

        # 20 (can't tell) + 10
        self.assertEqual(score, 30)

    def test_meeting_duration_planned_over_5(self):
        self.zoom_meeting.type = 0
        self.zoom_meeting.original_duration = 15
        self.zoom_meeting.duration = 25
        self.zoom_meeting.save()

        self.meeting_review = MeetingReview.objects.create(meeting=self.zoom_meeting)
        self.assertEqual(self.meeting_review.duration_score, "planned_over_5")

        score, score_components = score_meeting(self.zoom_meeting)

        # 20 (can't tell) + 10
        self.assertEqual(score, 26)

    def test_meeting_duration_planned_over_2(self):
        self.zoom_meeting.type = 0
        self.zoom_meeting.original_duration = 15
        self.zoom_meeting.duration = 17
        self.zoom_meeting.save()

        self.meeting_review = MeetingReview.objects.create(meeting=self.zoom_meeting)
        self.assertEqual(self.meeting_review.duration_score, "planned_over_2")

        score, score_components = score_meeting(self.zoom_meeting)

        # 20 (can't tell) + 3
        self.assertEqual(score, 23)

    def test_meeting_duration_planned_under_15(self):
        self.zoom_meeting.type = 0
        self.zoom_meeting.original_duration = 45
        self.zoom_meeting.duration = 15
        self.zoom_meeting.save()

        self.meeting_review = MeetingReview.objects.create(meeting=self.zoom_meeting)
        self.assertEqual(self.meeting_review.duration_score, "planned_under_15")

        score, score_components = score_meeting(self.zoom_meeting)

        # 20 (can't tell) - 5
        self.assertEqual(score, 15)

    def test_meeting_duration_planned_under_5(self):
        self.zoom_meeting.type = 0
        self.zoom_meeting.original_duration = 45
        self.zoom_meeting.duration = 35
        self.zoom_meeting.save()

        self.meeting_review = MeetingReview.objects.create(meeting=self.zoom_meeting)
        self.assertEqual(self.meeting_review.duration_score, "planned_over_2")

        score, score_components = score_meeting(self.zoom_meeting)

        # 20 (can't tell) + 3
        self.assertEqual(score, 23)

    def test_meeting_duration_planned_under_2(self):
        self.zoom_meeting.type = 0
        self.zoom_meeting.original_duration = 45
        self.zoom_meeting.duration = 42
        self.zoom_meeting.save()

        self.meeting_review = MeetingReview.objects.create(meeting=self.zoom_meeting)
        self.assertEqual(self.meeting_review.duration_score, "planned_over_2")

        score, score_components = score_meeting(self.zoom_meeting)

        # 20 (can't tell) + 3
        self.assertEqual(score, 23)
