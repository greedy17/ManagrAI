import pdb

from managr.lead.models import Lead
from managr.slack import constants as slack_const
from managr.slack.helpers.utils import action_with_params
from managr.slack.helpers import block_builders


def select_different_opportunity(context):
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

    # make params here
    user_id_param = "user_id=" + context.get("user_id")
    lead_id_param = "lead_id=" + context.get("lead_id")
    organization_id_param = "organization_id=" + context.get("organization_id")

    return [
        block_builders.external_select(
            f"*Opportunity:* :dart: _{lead.title}_",
            action_with_params(
                slack_const.GET_USER_OPPORTUNITIES,
                params=[
                    user_id_param,
                    lead_id_param,
                    organization_id_param,
                ],
            ),
            placeholder="Select Other",
            block_id="select_new_opportunity",
        ),
    ]
