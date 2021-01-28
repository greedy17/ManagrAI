import pdb

from managr.opportunity.models import Opportunity
from managr.opportunity import constants as opp_consts
from managr.slack import constants as slack_const
from managr.slack.helpers.utils import action_with_params, block_set
from managr.slack.helpers import block_builders


@block_set(required_context=["o", "opp", "m"])
def zoom_meeting_complete_form(context):
    opportunity = Opportunity.objects.get(pk=context.get("opp"))
    stage = (
        block_builders.option(opportunity.stage.label, str(opportunity.stage.id))
        if opportunity.stage
        else None
    )
    forecast_category = (
        block_builders.option(
            *list(
                map(
                    lambda x: (x[1], x[0]),
                    list(
                        filter(
                            lambda category: category[0] == opportunity.forecast_category,
                            opp_consts.FORECAST_CHOICES,
                        )
                    ),
                )
            )[0]
        )
        if opportunity.forecast_category
        else None
    )

    close_date = str(opportunity.close_date) if opportunity.close_date else None
    amount = opportunity.amount if opportunity.amount else None

    # make params here
    organization_id_param = "o=" + context.get("o")

    blocks = [
        {
            "type": "section",
            "fields": [
                {"type": "mrkdwn", "text": "*Opportunity:*"},
                {"type": "plain_text", "text": f":dart: {opportunity.title}", "emoji": True},
            ],
        },
        {"type": "divider"},
        block_builders.external_select(
            "*Meeting Type*",
            action_with_params(
                slack_const.GET_ORGANIZATION_ACTION_CHOICES, params=[organization_id_param],
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
            slack_const.GET_OPPORTUNITY_FORECASTS,
            initial_option=forecast_category,
            block_id="forecast_category",
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
            date=close_date,
            label="*Close Date*",
            action_id=slack_const.DEFAULT_ACTION_ID,
            block_id="close_date",
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
                "initial_value": str(amount),
            },
            "block_id": "amount",
        },
    ]
    ### TODO: this is currently done manually but is not reliable
    if context["sentiment"] == slack_const.ZOOM_MEETING__NOT_WELL:
        # no forecast no expected close date
        del blocks[4]
        del blocks[5]

    return blocks
