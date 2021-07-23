ALERT_TARGET_GROUPS = [
    {"key": "Myself", "value": "SELF"},
    {"key": "All Managers", "value": "MANAGERS"},
    {"key": "All Reps", "value": "REPS"},
    {"key": "Everyone", "value": "ALL"},
    {"key": "SDR", "value": "SDR"},
]

ALERT_RECIPIENT_GROUPS = [
    *ALERT_TARGET_GROUPS,
    {"key": "Owner", "value": "OWNER"},
]

