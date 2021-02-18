import pdb

from managr.opportunity.models import Opportunity
from managr.slack import constants as slack_const
from managr.slack.helpers.utils import action_with_params, block_set
from managr.slack.helpers import block_builders


@block_set(required_context=["opp", "m"])
def confirm_meeting_logged(context):
    opp = Opportunity.objects.get(pk=context.get("opp"))
    meeting = opp.meetings.filter(id=context.get("m")).first()
    meeting_id_param = "m=" + context["m"]

    blocks = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f":heavy_check_mark: Logged meeting :calendar: for *{meeting.topic}* regarding :dart: {opp.title}",
            },
        },
    ]
    if context.get("show_contacts", False):
        blocks.append(
            {
                "type": "section",
                "text": {
                    "type": "plain_text",
                    "text": "Review the people who joined your meeting and save them to Salesforce",
                },
                "accessory": {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "Review Meeting Participants",},
                    "value": slack_const.ZOOM_MEETING__VIEW_MEETING_CONTACTS,
                    "action_id": action_with_params(
                        slack_const.ZOOM_MEETING__VIEW_MEETING_CONTACTS, params=[meeting_id_param,],
                    ),
                },
            },
        )
        return blocks

