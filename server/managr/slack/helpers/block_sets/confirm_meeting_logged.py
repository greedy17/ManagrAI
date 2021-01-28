import pdb

from managr.opportunity.models import Opportunity
from managr.slack import constants as slack_const
from managr.slack.helpers.utils import action_with_params, block_set
from managr.slack.helpers import block_builders


@block_set(required_context=["opp", "m"])
def confirm_meeting_logged(context):
    opp = Opportunity.objects.get(pk=context.get("opp"))
    meeting = opp.meetings.filter(id=context.get("m")).first()

    return [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f":heavy_check_mark: Logged meeting for :calendar:  *{meeting.topic}* regarding :dart: {opp.title}",
            },
        },
    ]
