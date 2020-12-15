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
            "progressed": {"points": 10, "impact": "positive"},
            "regressed": {"points": 10, "impact": "negative"},
            "unchanged": {"points": 0, "impact": "positive"},
        },
        "forecast": {
            "progressed": {"points": 10, "impact": "positive"},
            "regressed": {"points": 10, "impact": "negative"},
            "unchanged": {"points": 0, "impact": "positive"},
        },
        "expected_close_date": {
            "progressed": {"points": 5, "impact": "positive"},
            "regressed": {"points": 5, "impact": "negative"},
            "unchanged": {"points": 0, "impact": "positive"},
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
    }
