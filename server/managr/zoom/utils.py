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
    "sentiment": {
        slack_consts.ZOOM_MEETING__GREAT: {
            "type": "sentiment",
            "points": 50,
            "impact": "positive",
            "message_tpl": "The rep said the meeting went great!",
        },
        slack_consts.ZOOM_MEETING__CANT_TELL: {
            "type": "sentiment",
            "points": 20,
            "impact": "positive",
            "message_tpl": "The rep said they can't tell how well the meeting went.",
        },
        slack_consts.ZOOM_MEETING__FINE: {
            "type": "sentiment",
            "points": 0,
            "impact": "positive",
            "message_tpl": "The rep said the meeting did not go well.",
        },
    },
    "stage": {
        zoom_consts.MEETING_REVIEW_PROGRESSED: {
            "type": "stage",
            "points": 10,
            "impact": "positive",
            "message_tpl": "The opportunity moved forward to a new stage: {new_stage_name}.",
        },
        zoom_consts.MEETING_REVIEW_REGRESSED: {
            "type": "stage",
            "points": 10,
            "impact": "negative",
            "message_tpl": "The opportunity moved backward to a previous stage: {new_stage_name}.",
        },
        zoom_consts.MEETING_REVIEW_UNCHANGED: {
            "type": "stage",
            "points": 0,
            "impact": "positive",
            "message_tpl": "The opportunity's stage did not change.",
        },
    },
    "forecast_category": {
        zoom_consts.MEETING_REVIEW_PROGRESSED: {
            "type": "forecast",
            "points": 10,
            "impact": "positive",
            "message_tpl": "The opportunity's forecast improved. It is now {meeting.meeting_review.forecast_category}.",
        },
        zoom_consts.MEETING_REVIEW_REGRESSED: {
            "type": "forecast",
            "points": 10,
            "impact": "negative",
            "message_tpl": "The opportunity's forecast decreased. It is now {meeting.meeting_review.forecast_category}.",
        },
        zoom_consts.MEETING_REVIEW_UNCHANGED: {
            "type": "forecast",
            "points": 0,
            "impact": "positive",
            "message_tpl": "The opportunity's forecast did not change.",
        },
    },
    "close_date": {
        zoom_consts.MEETING_REVIEW_PROGRESSED: {
            "type": "close_date",
            "points": 5,
            "impact": "positive",
            "message_tpl": "The opportunity's forecast close date improved. It is now: {new_close_date}",
        },
        zoom_consts.MEETING_REVIEW_REGRESSED: {
            "type": "close_date",
            "points": 5,
            "impact": "negative",
            "message_tpl": "The opportunity's forecast close date moved back. It is now: {new_close_date}",
        },
        zoom_consts.MEETING_REVIEW_UNCHANGED: {
            "type": "close_date",
            "points": 0,
            "impact": "positive",
            "message_tpl": "The opportunity's forecast close date didn't change.",
        },
    },
    "attendance": {
        0: {
            "type": "attendance",
            "points": 0,
            "impact": "positive",
            "message_tpl": "The meeting had only one attendee.",
        },
        2: {
            "type": "attendance",
            "points": 2,
            "impact": "positive",
            "message_tpl": "The meeting had two attendees.",
        },
        3: {
            "type": "attendance",
            "points": 3,
            "impact": "positive",
            "message_tpl": "The meeting had three attendees.",
        },
        4: {
            "type": "attendance",
            "points": 4,
            "impact": "positive",
            "message_tpl": "The meeting had very good attendance.",
        },
        5: {
            "type": "attendance",
            "points": 5,
            "impact": "positive",
            "message_tpl": "The meeting had very good attendance.",
        },
    },
    "duration": {
        "unknown": {
            "type": "duration",
            "points": 0,
            "impact": "positive",
            "message_tpl": "Could not determine the meeting duration.",
        },
        "planned_over_15": {
            "type": "duration",
            "points": 10,
            "impact": "positive",
            "message_tpl": "The meeting went over time by more than 15 minutes.",
        },
        "planned_under_15": {
            "type": "duration",
            "points": 5,
            "impact": "negative",
            "message_tpl": "The meeting was cut short by more than 15 minutes.",
        },
        "planned_over_5": {
            "type": "duration",
            "points": 6,
            "impact": "positive",
            "message_tpl": "The meeting went over time by about 5 minutes.",
        },
        "planned_over_2": {
            "type": "duration",
            "points": 3,
            "impact": "positive",
            "message_tpl": "The meeting went over time by about 2 minutes.",
        },
        "instant_over_60": {
            "type": "duration",
            "points": 10,
            "impact": "positive",
            "message_tpl": "This was an instant meeting that lasted over 60 minutes.",
        },
        "instant_over_30": {
            "type": "duration",
            "points": 6,
            "impact": "positive",
            "message_tpl": "This was an instant meeting that lasted around 30 minutes.",
        },
        "instant_over_20": {
            "type": "duration",
            "points": 3,
            "impact": "positive",
            "message_tpl": "This was an instant meeting that lasted around 20 minutes.",
        },
    },
}


class ScoreComponent:
    """Helper class for handling the components of the meeting score."""

    def __init__(self, meeting, type="unkown", points=0, impact="positive", message_tpl=""):
        self.meeting = meeting
        self.type = type
        self._points = points
        self.impact = impact
        self.message_tpl = message_tpl

    @property
    def rendered_message(self):
        # HACK: Provide general-purpose context to the formatter
        new_stage_name = ""
        new_close_date = ""
        if self.meeting.meeting_review.stage:
            stage = Stage.objects.get(id=self.meeting.meeting_review.stage)
            new_stage_name = stage.label
        if self.meeting.meeting_review.close_date:
            new_close_date = self.meeting.meeting_review.close_date.strftime("%m/%d/%Y")
        # END HACK

        return self.message_tpl.format(
            meeting=self.meeting, new_stage_name=new_stage_name, new_close_date=new_close_date,
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
        }


def score_meeting(meeting):
    """Score each component of the meeting.

    Returns a tuple of the score as an integer and a list of ScoreComponent instances.
    """
    if hasattr(meeting, "meeting_review"):
        meeting_review = meeting.meeting_review

        # "Clean" the meeting review data
        sentiment = meeting_review.sentiment or slack_consts.ZOOM_MEETING__CANT_TELL
        stage_progress = meeting_review.stage_progress
        forecast_progress = meeting_review.forecast_progress
        close_date_progress = meeting_review.close_date_progress
        participant_count_weighted = meeting_review.participant_count_weighted
        duration_score = meeting_review.duration_score

        # Participation is treated differently, because it is a "raw" score.
        participation_score = meeting_review.participation_score
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
                SCORE_LOOKUP["sentiment"][sentiment],
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
            ]
        ]
        score = sum(sc.points for sc in score_components)

    ### score for participation

    return (score, score_components)
