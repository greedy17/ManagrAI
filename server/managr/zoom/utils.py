from managr.zoom import constants as zoom_consts
from managr.slack import constants as slack_consts
from managr.organization.models import Stage

#
# Meeting Scoring Algorithm
#
# The scoring algo is made up of six components.
#
# 1. Sentiment (0-50 points)
# 2. Stage Progress (+/-10 points)
# 3. Forecast Progress (+/-10 points)
# 4. Close Date Progress (+/-5 points)
# 5. Attendance (0-5 points)
# 6. Participation (0-10 points)
# 7. Duration (-10-10 points)
#

# Data structure defining how meeting scores are computed.
SCORE_LOOKUP = {
    "meeting_sentiment": {
        zoom_consts.MEETING_SENTIMENT_GREAT: {
            "type": "meeting_sentiment",
            "points": 50,
            "impact": "positive",
            "message_tpl": "The rep said the meeting went great!",
            "message_delta": "",
        },
        zoom_consts.MEETING_SENTIMENT_FINE: {
            "type": "meeting_sentiment",
            "points": 0,
            "impact": "positive",
            "message_tpl": "The rep said the meeting did not go well.",
            "message_delta": "",
        },
        zoom_consts.MEETING_SENTIMENT_FINE: {
            "type": "meeting_sentiment",
            "points": 20,
            "impact": "positive",
            "message_tpl": "The rep said the meeting went fine.",
            "message_delta": "",
        },
    },
    "stage": {
        zoom_consts.MEETING_REVIEW_PROGRESSED: {
            "type": "stage",
            "points": 10,
            "impact": "positive",
            "message_tpl": "The opportunity moved forward to a new stage: {meeting.zoom_meeting_review.stage}.",
            "message_delta": "~{old_stage_name}~ {new_stage_name}",
        },
        zoom_consts.MEETING_REVIEW_REGRESSED: {
            "type": "stage",
            "points": 10,
            "impact": "negative",
            "message_tpl": "The opportunity moved backward to a previous stage: {meeting.zoom_meeting_review.stage}.",
            "message_delta": "~{old_stage_name}~ {new_stage_name}",
        },
        zoom_consts.MEETING_REVIEW_UNCHANGED: {
            "type": "stage",
            "points": 0,
            "impact": "positive",
            "message_tpl": "The opportunity's stage did not change.",
            "message_delta": "{old_stage_name} (no change)",
        },
    },
    "forecast_category": {
        zoom_consts.MEETING_REVIEW_PROGRESSED: {
            "type": "forecast",
            "points": 10,
            "impact": "positive",
            "message_tpl": "Improved to {meeting.zoom_meeting_review.forecast_category}.",
            "message_delta": "",
        },
        zoom_consts.MEETING_REVIEW_REGRESSED: {
            "type": "forecast",
            "points": 10,
            "impact": "negative",
            "message_tpl": "Worsened to {meeting.zoom_meeting_review.forecast_category}.",
            "message_delta": "",
        },
        zoom_consts.MEETING_REVIEW_UNCHANGED: {
            "type": "forecast",
            "points": 0,
            "impact": "positive",
            "message_tpl": "The opportunity's forecast did not change.",
            "message_delta": "{meeting.zoom_meeting_review.forecast_category} (no change)",
        },
    },
    "close_date": {
        zoom_consts.MEETING_REVIEW_PROGRESSED: {
            "type": "close_date",
            "points": 5,
            "impact": "positive",
            "message_tpl": "The opportunity's forecast close date improved. It is now: {new_close_date}",
            "message_delta": "~{old_close_date}~ {new_close_date}",
        },
        zoom_consts.MEETING_REVIEW_REGRESSED: {
            "type": "close_date",
            "points": 5,
            "impact": "negative",
            "message_tpl": "The opportunity's forecast close date moved back. It is now: {new_close_date}",
            "message_delta": "~{old_close_date}~ {new_close_date}",
        },
        zoom_consts.MEETING_REVIEW_UNCHANGED: {
            "type": "close_date",
            "points": 0,
            "impact": "positive",
            "message_tpl": "The opportunity's forecast close date didn't change.",
            "message_delta": "{old_close_date} (no change)",
        },
    },
    "amount": {
        zoom_consts.MEETING_REVIEW_PROGRESSED: {
            "type": "amount",
            "points": 5,
            "impact": "positive",
            "message_tpl": "The opportunity's closing amount has increased. It is now: ${new_amount}",
            "message_delta": "~${old_amount}~ ${new_amount}",
        },
        zoom_consts.MEETING_REVIEW_REGRESSED: {
            "type": "amount",
            "points": 5,
            "impact": "negative",
            "message_tpl": "The opportunity's closing amount has decreased. It is now: ${new_amount}",
            "message_delta": "~${old_amount}~ ${new_amount}",
        },
        zoom_consts.MEETING_REVIEW_UNCHANGED: {
            "type": "amount",
            "points": 0,
            "impact": "positive",
            "message_tpl": "The opportunity's closing amount didn't change.",
            "message_delta": "{old_amount} (no change)",
        },
    },
    "attendance": {
        0: {
            "type": "attendance",
            "points": 0,
            "impact": "positive",
            "message_tpl": "The meeting had only one attendee.",
            "message_delta": "",
        },
        2: {
            "type": "attendance",
            "points": 2,
            "impact": "positive",
            "message_tpl": "The meeting had two attendees.",
            "message_delta": "",
        },
        3: {
            "type": "attendance",
            "points": 3,
            "impact": "positive",
            "message_tpl": "The meeting had three attendees.",
            "message_delta": "",
        },
        4: {
            "type": "attendance",
            "points": 4,
            "impact": "positive",
            "message_tpl": "The meeting had very good attendance of at least 4 participants",
            "message_delta": "",
        },
        5: {
            "type": "attendance",
            "points": 5,
            "impact": "positive",
            "message_tpl": "The meeting had very good attendance of 5 or more participants",
            "message_delta": "",
        },
    },
    "duration": {
        "unknown": {
            "type": "duration",
            "points": 0,
            "impact": "positive",
            "message_tpl": "The meeting lasted {duration} minutes, we could not determine whether meeting lasted longer than planned or ended sooner.",
            "message_delta": "",
        },
        "planned_over_15": {
            "type": "duration",
            "points": 10,
            "impact": "positive",
            "message_tpl": "The meeting lasted {duration} minutes, it went over time by more than 15 minutes.",
            "message_delta": "",
        },
        "planned_under_15": {
            "type": "duration",
            "points": 5,
            "impact": "negative",
            "message_tpl": "The meeting lasted {duration} minutes, it was cut short by less than 15 minutes.",
            "message_delta": "",
        },
        "planned_under_15_plus": {
            "type": "duration",
            "points": 10,
            "impact": "negative",
            "message_tpl": "The meeting lasted {duration} minutes, it was cut short by more than 15 minutes.",
            "message_delta": "",
        },
        "planned_over_5": {
            "type": "duration",
            "points": 6,
            "impact": "positive",
            "message_tpl": "The meeting lasted {duration} minutes, it went over time by about 5 minutes.",
            "message_delta": "",
        },
        "planned_over_2": {
            "type": "duration",
            "points": 3,
            "impact": "positive",
            "message_tpl": "The meeting lasted {duration} minutes, it went over time by about 2 minutes.",
            "message_delta": "",
        },
        "planned_on_time": {
            "type": "duration",
            "points": 0,
            "impact": "positive",
            "message_tpl": "The meeting lasted {duration} minutes, it ended on time.",
            "message_delta": "",
        },
        "instant_over_60": {
            "type": "duration",
            "points": 10,
            "impact": "positive",
            "message_tpl": "This was an instant meeting that lasted over 60 minutes.",
            "message_delta": "",
        },
        "instant_over_30": {
            "type": "duration",
            "points": 6,
            "impact": "positive",
            "message_tpl": "This was an instant meeting that lasted around 30 minutes.",
            "message_delta": "",
        },
        "instant_over_20": {
            "type": "duration",
            "points": 3,
            "impact": "positive",
            "message_tpl": "This was an instant meeting that lasted around 20 minutes.",
            "message_delta": "",
        },
    },
}


class ScoreComponent:
    """Helper class for handling the components of the meeting score."""

    def __init__(
        self, meeting, type="unkown", points=0, impact="positive", message_tpl="", message_delta=""
    ):
        self.meeting = meeting
        self.type = type
        self._points = points
        self.impact = impact
        self.message_tpl = message_tpl
        self.message_delta = message_delta

    @property
    def rendered_message(self):
        # HACK: Provide general-purpose context to the formatter
        new_stage_name = ""
        new_close_date = ""
        new_amount = ""
        if self.meeting.zoom_meeting_review.stage:
            new_stage_name = self.meeting.zoom_meeting_review.stage
        if self.meeting.zoom_meeting_review.close_date:
            new_close_date = self.meeting.zoom_meeting_review.close_date.strftime("%m/%d/%Y")
        if self.meeting.zoom_meeting_review.amount:
            new_amount = self.meeting.zoom_meeting_review.amount
        # END HACK

        return self.message_tpl.format(
            meeting=self.meeting,
            new_stage_name=new_stage_name,
            new_close_date=new_close_date,
            new_amount=new_amount,
            duration=self.meeting.duration,
        )

    @property
    def rendered_message_delta(self):
        # HACK: Provide general-purpose context to the formatter
        new_stage_name = ""
        old_stage_name = ""
        new_close_date = ""
        old_close_date = ""
        new_amount = ""
        old_amount = ""
        if self.meeting.zoom_meeting_review.stage:
            new_stage_name = self.meeting.zoom_meeting_review.stage
        if self.meeting.zoom_meeting_review.prev_stage:
            old_stage_name = self.meeting.zoom_meeting_review.prev_stage
        if self.meeting.zoom_meeting_review.close_date:
            new_close_date = self.meeting.zoom_meeting_review.close_date.strftime("%m/%d/%Y")
        if self.meeting.zoom_meeting_review.prev_close_date:
            old_close_date = self.meeting.zoom_meeting_review.prev_close_date.strftime("%m/%d/%Y")
        if self.meeting.zoom_meeting_review.amount:
            new_amount = self.meeting.zoom_meeting_review.amount
        if self.meeting.zoom_meeting_review.prev_amount:
            old_amount = self.meeting.zoom_meeting_review.prev_amount
        # END HACK

        return self.message_delta.format(
            meeting=self.meeting,
            new_stage_name=new_stage_name,
            old_stage_name=old_stage_name,
            new_close_date=new_close_date,
            old_close_date=old_close_date,
            new_amount=new_amount,
            old_amount=old_amount,
        )

    @property
    def points(self):
        return self._points if self.impact == "positive" else -self._points

    @property
    def as_dict(self):
        return {
            "type": self.type,
            "points": self._points,
            "impact": self.impact,
            "message": self.rendered_message,
            "delta": self.rendered_message_delta,
        }


def score_meeting(meeting):
    """Score each component of the meeting.

    Returns a tuple of the score as an integer and a list of ScoreComponent instances.
    """
    if hasattr(meeting, "zoom_meeting_review"):
        zoom_meeting_review = meeting.zoom_meeting_review

        # "Clean" the meeting review data
        meeting_sentiment = zoom_meeting_review.meeting_sentiment or slack_consts.ZOOM_MEETING__FINE
        stage_progress = zoom_meeting_review.stage_progress
        forecast_progress = zoom_meeting_review.forecast_progress
        close_date_progress = zoom_meeting_review.close_date_progress
        participant_count_weighted = zoom_meeting_review.participant_count_weighted
        duration_score = zoom_meeting_review.duration_score
        amount_progress = zoom_meeting_review.amount_progress

        # Participation is treated differently, because it is a "raw" score.
        participation_score = zoom_meeting_review.participation_score
        participation_msg_tpl = ""
        if 0 < participation_score <= 5:
            participation_msg_tpl = "Most attendees participated for less than half of the meeting."
        elif 5 < participation_score <= 8:
            participation_msg_tpl = "Most attendees participated for the majority of the meeting."
        elif 8 < participation_score:
            participation_msg_tpl = (
                "All attendees participated for the entire duration of the meeting."
            )

        # Collect score components from the lookup and cast to ScoreComponent instance
        score_components = [
            ScoreComponent(meeting, **i)
            for i in [
                SCORE_LOOKUP["meeting_sentiment"][meeting_sentiment],
                SCORE_LOOKUP["stage"][stage_progress],
                SCORE_LOOKUP["forecast_category"][forecast_progress],
                SCORE_LOOKUP["close_date"][close_date_progress],
                SCORE_LOOKUP["attendance"][participant_count_weighted],
                {
                    "type": "participation",
                    "points": participation_score,
                    "impact": "positive",
                    "message_tpl": participation_msg_tpl,
                },
                SCORE_LOOKUP["duration"][duration_score],
                SCORE_LOOKUP["amount"][amount_progress],
            ]
        ]
        score = sum(sc.points for sc in score_components)

    ### score for participation

    return (score, score_components)
