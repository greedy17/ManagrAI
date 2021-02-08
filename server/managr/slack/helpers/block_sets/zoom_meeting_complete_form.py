import pdb

from managr.opportunity.models import Opportunity
from managr.opportunity import constants as opp_consts
from managr.slack import constants as slack_const
from managr.slack.helpers.utils import action_with_params, block_set, block_finder
from managr.slack.helpers import block_builders


@block_set(required_context=["o", "opp", "m"])
def zoom_meeting_complete_form(context):
    opportunity = Opportunity.objects.get(pk=context.get("opp"))
    sf_account = opportunity.imported_by.salesforce_account
    extra_fields = list(map(lambda field_name: field_name, sf_account.object_fields))

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
        block_builders.simple_section_multiple(
            [
                block_builders.text_block("*Opportunity*", "mrkdwn"),
                block_builders.text_block(f":dart: {opportunity.title}", "mrkdwn"),
            ]
        ),
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
            "*Forecast Category*",
            slack_const.GET_OPPORTUNITY_FORECASTS,
            initial_option=forecast_category,
            block_id="forecast_category",
        ),
        block_builders.input_block(
            "Description",
            placeholder="How'd it go?",
            multiline=True,
            action_id=slack_const.DEFAULT_ACTION_ID,
            block_id="description",
            optional=True,
        ),
        block_builders.datepicker(
            date=close_date,
            label="*Close Date*",
            action_id=slack_const.DEFAULT_ACTION_ID,
            block_id="close_date",
        ),
        block_builders.input_block(
            "Amount",
            placeholder="Amount?",
            action_id=slack_const.DEFAULT_ACTION_ID,
            block_id="amount",
            optional=True,
            initial_value=str(amount),
        ),
    ]
    if "NextStep" in extra_fields:
        blocks.append(
            block_builders.input_block(
                "Next Step",
                placeholder="What's the plan?",
                action_id=slack_const.DEFAULT_ACTION_ID,
                block_id="NextStep",
                optional=True,
            ),
        )

    ### TODO: this is currently done manually but is not reliable
    if context["sentiment"] == slack_const.ZOOM_MEETING__NOT_WELL:
        # no forecast no expected close date
        del blocks[4]
        del blocks[5]

    return blocks
