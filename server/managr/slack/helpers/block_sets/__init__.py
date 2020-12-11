from .zoom_meeting_initial import zoom_meeting_initial
from .zoom_meeting_complete_form import zoom_meeting_complete_form
from .zoom_meeting_limited_form import zoom_meeting_limited_form
from .selected_different_opportunity import select_different_opportunity
from .confirm_meeting_logged import confirm_meeting_logged
from . import alert_blocksets as slack_alerts

# Mockups, page 3: https://docs.google.com/document/d/1KIvznxOqPb7WuFOXsFcKMawxq8-8T2gpb2sYNdIqLL4/edit#heading=h.xa1nnwnl2is5
# Slack Block-Builder: https://app.slack.com/block-kit-builder/
# Block References: https://api.slack.com/reference/block-kit/block-elements

# Each blockObj has certain requirements that the Block-Builder may not add.
# I mainly observed this with missing action_id property for different blocks and sub-objects
# These forms need to leverage proper managr.slack.constants for action_ids, so we can
# identify the action properly later on when it is triggered by user and we receive data via webhook


def get_block_set(set_name, context={}):
    """
    Returns array of Slack UI blocks
    """
    switcher = {
        "zoom_meeting_initial": zoom_meeting_initial,
        "zoom_meeting_complete_form": zoom_meeting_complete_form,
        "zoom_meeting_limited_form": zoom_meeting_limited_form,
        "select_different_opportunity": select_different_opportunity,
        "confirm_meeting_logged": confirm_meeting_logged,
        "reminder_block_set": slack_alerts.reminder_block_set,
        "opp_inactive_block_set": slack_alerts.opp_inactive_block_set,
        "opp_closed_report_generated": slack_alerts.opp_closed_report_generated,
        "reminder_contact_block_set": slack_alerts.reminder_contact_block_set,
        "meeting_review_score": slack_alerts.meeting_review_score,
    }
    return switcher.get(set_name)(context)
