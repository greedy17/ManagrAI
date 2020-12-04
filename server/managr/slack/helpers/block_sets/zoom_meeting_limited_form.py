import pdb

from managr.lead.models import Lead
from managr.slack import constants as slack_const
from managr.slack.helpers.utils import action_with_params
from managr.slack.helpers import block_builders


def zoom_meeting_limited_form(context):
    """
    Required context:
    {
        user_id,
        lead_id,
        organization_id,
    }
    """
    # validate context
    required_context = [
        "user_id",
        "lead_id",
        "organization_id",
    ]
    for prop in required_context:
        if context.get(prop) is None:
            raise ValueError(f"context missing: {prop}")

    lead = Lead.objects.get(pk=context.get("lead_id"))
    stage = lead.status.as_slack_option if lead.status else None

    # make params here
    user_id_param = "user_id=" + context.get("user_id")
    lead_id_param = "lead_id=" + context.get("lead_id")
    organization_id_param = "organization_id=" + context.get("organization_id")

    return [
        {
            "type": "section",
            "fields": [
                {"type": "mrkdwn", "text": "*Opportunity:*"},
                {"type": "plain_text", "text": f":dart: {lead.title}", "emoji": True},
            ],
        },
        {"type": "divider"},
        block_builders.external_select(
            "*Meeting Type*",
            action_with_params(
                slack_const.GET_ORGANIZATION_ACTION_CHOICES,
                params=[organization_id_param],
            ),
        ),
        block_builders.external_select(
            "*Update Stage*",
            action_with_params(
                slack_const.GET_ORGANIZATION_STAGES,
                params=[organization_id_param],
            ),
            initial_option=stage,
        ),
        {
            "type": "input",
            "optional": True,
            # "block_id": "input123",
            "label": {"type": "plain_text", "text": "Description"},
            "element": {
                "type": "plain_text_input",
                "multiline": True,
                # "action_id": slack_const.ZOOM_MEETING__GREAT,
                "placeholder": {"type": "plain_text", "text": "How'd it go?"},
            },
        },
        {
            "type": "input",
            "optional": True,
            # "block_id": "input123",
            "label": {"type": "plain_text", "text": "Next Step"},
            "element": {
                "type": "plain_text_input",
                # "action_id": slack_const.ZOOM_MEETING__GREAT,
                "placeholder": {"type": "plain_text", "text": "What's the plan?"},
            },
        },
    ]
