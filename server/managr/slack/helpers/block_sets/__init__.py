from . import meeting_review_block_sets
from . import task_blocksets
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
        "create_task_modal": task_blocksets.create_task_modal_block_set,
        "initial_meeting_interaction": meeting_review_block_sets.initial_meeting_interaction_block_set,
        "meeting_review_modal": meeting_review_block_sets.meeting_review_modal_block_set,
        "attach_resource_interaction": meeting_review_block_sets.attach_resource_interaction_block_set,
        "create_or_search_modal": meeting_review_block_sets.create_or_search_modal_block_set,
        "create_modal_block_set": meeting_review_block_sets.create_modal_block_set,
        "disregard_meeting_review": meeting_review_block_sets.disregard_meeting_review_block_set,
        "final_meeting_interaction": meeting_review_block_sets.final_meeting_interaction_block_set,
        "no_change_interaction": meeting_review_block_sets.no_changes_interaction_block_set,
        "show_meeting_contacts": meeting_review_block_sets.meeting_contacts_block_set,
        "edit_meeting_contacts": meeting_review_block_sets.edit_meeting_contacts_block_set,
        "schedule_meeting_modal": meeting_review_block_sets.schedule_zoom_meeting_modal,
        "loading": common_blocksets.loading_block_set,
        "error_modal": common_blocksets.error_modal_block_set,
        "error_message": common_blocksets.error_message_block_set,
        "coming_soon_modal": common_blocksets.coming_soon_modal_block_set,
        "onboarding_interaction": common_blocksets.onboarding_interaction_block_set,
        "create_meeting_task": meeting_review_block_sets.create_meeting_task,
        "schedule_meeting": meeting_review_block_sets.schedule_meeting,
        "add_to_cadence": meeting_review_block_sets.add_to_cadence_block_set,
        "success_modal": common_blocksets.success_modal_block_set,
        "home_modal": common_blocksets.home_modal_block_set,
        "home_modal_generic": common_blocksets.home_modal_generic_block_set,
        "hour_options": common_blocksets.hour_options,
        "minute_options": common_blocksets.minute_options,
        "time_options": common_blocksets.time_options,
        "duration_options": common_blocksets.duration_options,
        "command_update_resource": command_views_blocksets.command_update_resource_interaction,
        "update_modal_block_set": command_views_blocksets.update_modal_block_set,
        "command_meeting_summary": command_views_blocksets.command_meeting_summary,
        "meeting_summary": meeting_review_block_sets.meeting_summary_blockset,
        "command_create_task": command_views_blocksets.command_create_task_interaction,
        "tasks_list": common_blocksets.tasks_list_block_set,
        "create_modal": command_views_blocksets.create_modal_block_set,
        "alert_instance": command_views_blocksets.alert_instance_block_set,
        "zoom_recording_blockset": common_blocksets.zoom_recording_blockset,
        "cadence_modal_blockset": command_views_blocksets.create_add_to_cadence_block_set,
        "select_account": command_views_blocksets.command_select_account_interaction,
    }
    return switcher.get(set_name)(context, *args, **kwargs)
