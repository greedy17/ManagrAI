from . import alert_blocksets as slack_alerts
from . import meeting_review_block_sets
from . import common_blocksets
from . import command_views_blocksets

# Mockups, page 3: https://docs.google.com/document/d/1KIvznxOqPb7WuFOXsFcKMawxq8-8T2gpb2sYNdIqLL4/edit#heading=h.xa1nnwnl2is5
# Slack Block-Builder: https://app.slack.com/block-kit-builder/
# Block References: https://api.slack.com/reference/block-kit/block-elements

# Each blockObj has certain requirements that the Block-Builder may not add.
# I mainly observed this with missing action_id property for different blocks and sub-objects
# These forms need to leverage proper managr.slack.constants for action_ids, so we can
# identify the action properly later on when it is triggered by user and we receive data via webhook


def get_block_set(set_name, context={}, *args, **kwargs):
    """
    Returns array of Slack UI blocks
    """
    switcher = {
        "initial_meeting_interaction": meeting_review_block_sets.initial_meeting_interaction_block_set,
        "meeting_review_modal": meeting_review_block_sets.meeting_review_modal_block_set,
        "attach_resource_interaction": meeting_review_block_sets.attach_resource_interaction_block_set,
        "create_or_search_modal": meeting_review_block_sets.create_or_search_modal_block_set,
        "search_modal_block_set": meeting_review_block_sets.search_modal_block_set,
        "create_modal_block_set": meeting_review_block_sets.create_modal_block_set,
        "disregard_meeting_review": meeting_review_block_sets.disregard_meeting_review_block_set,
        "final_meeting_interaction": meeting_review_block_sets.final_meeting_interaction_block_set,
        "reminder_block_set": slack_alerts.reminder_block_set,
        "opp_inactive_block_set": slack_alerts.opp_inactive_block_set,
        "opp_closed_report_generated": slack_alerts.opp_closed_report_generated,
        "reminder_contact_block_set": slack_alerts.reminder_contact_block_set,
        "meeting_review_score": slack_alerts.meeting_review_score,
        "show_lead_contacts": slack_alerts.lead_contacts_block_set,
        "show_lead_logs": slack_alerts.lead_activity_log_block_set,
        "show_meeting_score_description": slack_alerts.meeting_score_description_block_set,
        "lead_score_block_set": slack_alerts.lead_score_block_set,
        "show_lead_score_description": slack_alerts.lead_score_description_block_set,
        "show_meeting_contacts": meeting_review_block_sets.meeting_contacts_block_set,
        "edit_meeting_contacts": meeting_review_block_sets.edit_meeting_contacts_block_set,
        "loading": common_blocksets.loading_block_set,
        "error_modal": common_blocksets.error_modal_block_set,
        "error_message": common_blocksets.error_message_block_set,
        "coming_soon_modal": common_blocksets.coming_soon_modal_block_set,
        "create_meeting_task": meeting_review_block_sets.create_meeting_task,
        "success_modal": common_blocksets.success_modal_block_set,
        "command_update_resource": command_views_blocksets.command_update_resource_interaction,
        "update_modal_block_set": command_views_blocksets.update_modal_block_set,
        "command_meeting_summary": command_views_blocksets.command_meeting_summary,
    }
    return switcher.get(set_name)(context, *args, **kwargs)
