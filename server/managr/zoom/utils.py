from managr.zoom import constants as zoom_consts
from managr.slack import constants as slack_consts

# Data structure defining how meeting scores are computed.
SCORE_LOOKUP = {
    "sentiment": {
        slack_consts.ZOOM_MEETING__GREAT: {
            "points": 50,
            "impact": "positive",
            "message_tpl": "The rep said the meeting went great.",
        },
        slack_consts.ZOOM_MEETING__CANT_TELL: {
            "points": 20,
            "impact": "positive",
            "message_tpl": "The rep said they can't tell how well the meeting went.",
        },
        slack_consts.ZOOM_MEETING__NOT_WELL: {
            "points": 0,
            "impact": "positive",
            "message_tpl": "The rep said the meeting did not go well.",
        },
    },
    "stage": {
        zoom_consts.MEETING_REVIEW_PROGRESSED: {
            "points": 10,
            "impact": "positive",
            "message_tpl": "The opportunity moved forward to a new stage: {meeting.update_stage}.",
        },
        zoom_consts.MEETING_REVIEW_REGRESSED: {
            "points": 10,
            "impact": "negative",
            "message_tpl": "The opportunity moved backward to a previous stage: {meeting.update_stage}.",
        },
        zoom_consts.MEETING_REVIEW_UNCHANGED: {
            "points": 0,
            "impact": "positive",
            "message_tpl": "The opportunity's stage did not change.",
        },
    },
    "forecast": {
        zoom_consts.MEETING_REVIEW_PROGRESSED: {
            "points": 10,
            "impact": "positive",
            "message_tpl": "The opportunity's forecast improved. It is now {meeting.forecast_strength}",
        },
        zoom_consts.MEETING_REVIEW_REGRESSED: {
            "points": 10,
            "impact": "negative",
            "message_tpl": "The opportunity's forecast decreased. It is now {meeting.forecast_strength}",
        },
        zoom_consts.MEETING_REVIEW_UNCHANGED: {
            "points": 0,
            "impact": "positive",
            "message_tpl": "The opportunity's forecast did not change.",
        },
    },
    "expected_close_date": {
        zoom_consts.MEETING_REVIEW_PROGRESSED: {
            "points": 5,
            "impact": "positive",
            "message_tpl": "The opportunity's forecast close date improved. It is now: {meeting.updated_close_date}",
        },
        zoom_consts.MEETING_REVIEW_REGRESSED: {
            "points": 5,
            "impact": "negative",
            "message_tpl": "The opportunity's forecast close date moved back. It is now: {meeting.updated_close_date}",
        },
        zoom_consts.MEETING_REVIEW_UNCHANGED: {
            "points": 0,
            "impact": "positive",
            "message_tpl": "The opportunity's forecast close date didn't change.",
        },
    },
    "duration": {
        "meeting_type": {
            "planned": {
                "over": {
                    "15": {"points": 10, "impact": "positive"},
                    "5": {"points": 6, "impact": "positive"},
                    "2": {"points": 3, "impact": "positive"},
                },
            },
            "instant": {
                "over": {
                    "60": {"points": 10, "impact": "positive"},
                    "30": {"points": 6, "impact": "positive"},
                    "20": {"points": 3, "impact": "positive"},
                },
            },
        }
    },
    "participants": {
        "attendees": {
            0: {"points": 0, "impact": "positive"},
            2: {"points": 2, "impact": "positive"},
            3: {"points": 3, "impact": "positive"},
            4: {"points": 4, "impact": "positive"},
            5: {"points": 5, "impact": "positive"},
        },
        "participation": lambda total_minutes, duration, attendees: round(
            ((total_minutes - duration) / (attendees - 1) * 10)
        ),
    },
}


class ScoreComponent:
    """Helper class for handling the components of the meeting score."""

    def __init__(self, meeting, points=0, impact="positive", message_tpl=""):
        self.meeting = meeting
        self._points = points
        self.impact = impact
        self.message_tpl = message_tpl

    @property
    def rendered_message(self):
        return self.message_tpl.format(meeting=self.meeting)

    @property
    def points(self):
        return self._points if self.impact == "positive" else -self._points

    @property
    def as_dict(self):
        return {
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
        expected_close_date_progress = meeting_review.expected_close_date_progress
        participant_count_weighted = meeting_review.participant_count_weighted

        # Collect score components from the lookup and cast to ScoreComponent instance
        score_components = [
            ScoreComponent(meeting, **i)
            for i in [
                SCORE_LOOKUP["sentiment"][sentiment],
                SCORE_LOOKUP["stage"][stage_progress],
                SCORE_LOOKUP["forecast"][forecast_progress],
                SCORE_LOOKUP["expected_close_date"][expected_close_date_progress],
                SCORE_LOOKUP["participants"]["attendees"][participant_count_weighted],
            ]
        ]
        score = sum(sc.points for sc in score_components)

    ### score for participation

    return (score, score_components)

