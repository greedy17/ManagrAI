import pdb

from managr.lead.models import Lead
from managr.slack import constants as slack_const
from managr.slack.helpers.utils import action_with_params, block_set
from managr.slack.helpers import block_builders


@block_set(required_context=["o", "l", "m"])
def zoom_meeting_complete_form(context):
    lead = Lead.objects.get(pk=context.get("l"))
    stage = lead.status.as_slack_option if lead.status else None
    forecast = lead.forecast.as_slack_option if lead.forecast else None

    expected_close_date = (
        str(lead.expected_close_date.date()) if lead.expected_close_date else None
    )
    amount = lead.amount if lead.amount else None

    # make params here
    organization_id_param = "o=" + context.get("o")

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
            block_id="meeting_type",
        ),
        block_builders.external_select(
            "*Update Stage*",
            action_with_params(
                slack_const.GET_ORGANIZATION_STAGES, params=[organization_id_param],
            ),
            initial_option=stage,
            block_id="stage",
        ),
        block_builders.external_select(
            "*Forecast Strength*",
            slack_const.GET_LEAD_FORECASTS,
            initial_option=forecast,
            block_id="forecast",
        ),
        {
            "type": "input",
            "optional": True,
            "label": {"type": "plain_text", "text": "Description"},
            "element": {
                "type": "plain_text_input",
                "multiline": True,
                "action_id": slack_const.DEFAULT_ACTION_ID,
                "placeholder": {"type": "plain_text", "text": "How'd it go?"},
            },
            "block_id": "description",
        },
        block_builders.datepicker(
            date=expected_close_date,
            label="*Expected Close Date*",
            action_id=slack_const.DEFAULT_ACTION_ID,
            block_id="expected_close_date",
        ),
        {
            "type": "input",
            "optional": True,
            "label": {"type": "plain_text", "text": "Next Step"},
            "element": {
                "type": "plain_text_input",
                "action_id": slack_const.DEFAULT_ACTION_ID,
                "placeholder": {"type": "plain_text", "text": "What's the plan?"},
            },
            "block_id": "next_step",
        },
        {
            "type": "input",
            "optional": True,
            "label": {"type": "plain_text", "text": "Amount"},
            "element": {
                "type": "plain_text_input",
                "action_id": slack_const.DEFAULT_ACTION_ID,
                "placeholder": {"type": "plain_text", "text": "Amount?"},
            },
            "block_id": "amount",
        },
    ]
