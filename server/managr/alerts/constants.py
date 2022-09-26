from django.conf import settings

ALERT_TARGET_GROUPS = [
    {"key": "Myself", "value": "SELF"},
    {"key": "All Managers", "value": "MANAGERS"},
    {"key": "All Reps", "value": "REPS"},
    {"key": "Everyone", "value": "ALL"},
    {"key": "SDR", "value": "SDR"},
    {"key": "My Team", "value": "TEAM"},
]

ALERT_RECIPIENT_GROUPS = [
    *ALERT_TARGET_GROUPS,
    {"key": "Owner", "value": "OWNER"},
]

if settings.IN_DEV:
    ALERT_PIPELINE_URL = "http://localhost:8080/pipelines"
elif settings.IN_STAGING:
    ALERT_PIPELINE_URL = "https://staging.managr.ai/pipelines"
else:
    ALERT_PIPELINE_URL = "https://app.managr.ai/pipelines"
