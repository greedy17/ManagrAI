import pdb

from managr.lead.models import Lead
from managr.slack import constants as slack_const
from managr.slack.helpers.utils import action_with_params, block_set
from managr.slack.helpers import block_builders


@block_set(required_context=["l"])
def confirm_meeting_logged(context):
    lead = Lead.objects.get(pk=context.get("l"))

    return [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f":heavy_check_mark: Logged note for :calendar:  *_meeting.title_* regarding :dart: {lead.title} ",
            },
        },
    ]
