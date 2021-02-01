import pdb

from managr.opportunity.models import Opportunity
from managr.slack import constants as slack_const
from managr.slack.helpers.utils import action_with_params, block_set
from managr.slack.helpers import block_builders


@block_set(required_context=["u", "opp"])
def select_different_opportunity(context):
    opp = Opportunity.objects.get(pk=context.get("opp"))

    # make params here
    user_id_param = "u=" + context.get("u")

    return [
        block_builders.external_select(
            f"*Opportunity:* :dart: _{opp.title}_",
            action_with_params(slack_const.GET_USER_OPPORTUNITIES, params=[user_id_param,],),
            placeholder="Select Other",
            block_id="new_opportunity",
            min_query_length=1,
        ),
    ]
