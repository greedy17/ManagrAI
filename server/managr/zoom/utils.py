from managr.zoom import constants as zoom_consts
from managr.slack import constants as slack_consts


def score_meeting(meeting):
    current_score = 0
    scoring_components = {
        "sentiment": {
            slack_consts.ZOOM_MEETING__GREAT: {"points": 50, "impact": "positive"},
            slack_consts.ZOOM_MEETING__CANT_TELL: {"points": 20, "impact": "positive"},
            slack_consts.ZOOM_MEETING__NOT_WELL: {"points": 0, "impact": "positive"},
        },
        "stage": {
            zoom_consts.MEETING_REVIEW_PROGRESSED: {
                "points": 10,
                "impact": "positive",
            },
            zoom_consts.MEETING_REVIEW_REGRESSED: {"points": 10, "impact": "negative"},
            zoom_consts.MEETING_REVIEW_UNCHANGED: {"points": 0, "impact": "positive"},
        },
        "forecast": {
            zoom_consts.MEETING_REVIEW_PROGRESSED: {
                "points": 10,
                "impact": "positive",
            },
            zoom_consts.MEETING_REVIEW_REGRESSED: {"points": 10, "impact": "negative"},
            zoom_consts.MEETING_REVIEW_UNCHANGED: {"points": 0, "impact": "positive"},
        },
        "expected_close_date": {
            zoom_consts.MEETING_REVIEW_PROGRESSED: {"points": 5, "impact": "positive"},
            zoom_consts.MEETING_REVIEW_REGRESSED: {"points": 5, "impact": "negative"},
            zoom_consts.MEETING_REVIEW_UNCHANGED: {"points": 0, "impact": "positive"},
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
                2: {"points": 0, "impact": "positive"},
                3: {"points": 2, "impact": "positive"},
                4: {"points": 4, "impact": "positive"},
                5: {"points": 5, "impact": "positive"},
            },
            "participation": lambda total_minutes, duration, attendees: round(
                ((total_minutes - duration) / (attendees - 1) * 10)
            ),
        },
    }

    if hasattr(meeting, "meeting_review"):
        stage_progress = meeting.meeting_review.stage_progress
        forecast_progress = meeting.meeting_review.forecast_progress
        expected_close_date_progress = (
            meeting.meeting_review.expected_close_date_progress
        )

        score_items = []
        score_items.append(
            scoring_components["sentiment"][meeting.meeting_review.sentiment]
        )
        score_items.append(scoring_components["stage"][stage_progress])
        score_items.append(scoring_components["forecast"][forecast_progress])
        score_items.append(
            scoring_components["expected_close_date"][expected_close_date_progress]
        )
        score_items.append(
            scoring_components["participants"]["attendees"][
                meeting.participant_count_weighted
            ]
        )

        for item in score_items:
            if item["impact"] == "positive":
                current_score += item["points"]
            if item["impact"] == "negative":
                current_score -= item["points"]
    ### score for participation

    return current_score

