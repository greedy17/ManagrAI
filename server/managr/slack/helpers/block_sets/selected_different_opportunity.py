import pdb

from managr.lead.models import Lead
from managr.slack import constants as slack_const
from managr.slack.helpers.utils import action_with_params, block_set
from managr.slack.helpers import block_builders


@block_set(required_context=["u", "l"])
def select_different_opportunity(context):
    lead = Lead.objects.get(pk=context.get("l"))

    # make params here
    user_id_param = "u=" + context.get("u")

    return [
        block_builders.external_select(
            f"*Opportunity:* :dart: _{lead.title}_",
            action_with_params(
                slack_const.GET_USER_OPPORTUNITIES,
                params=[
                    user_id_param,
                ],
            ),
            placeholder="Select Other",
            block_id="select_new_opportunity",
        ),
    ]
