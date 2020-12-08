import pdb

from managr.core.models import User
from managr.lead.models import Lead, Notification
from managr.slack import constants as slack_const
from managr.slack.helpers.utils import action_with_params, block_set
from managr.slack.helpers import block_builders


@block_set(required_context=["n"])
def reminder_block_set(context):
    # Bruno created decorator required context n = Notification
    # slack mentions format = <@slack_id>

    notif = Notification.objects.filter(id=context.get("n")).first()
    user = notif.user.slack_integration.slack_id

    if notif:
        return [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": ":calendar:  Reminder"},
            },
            {"type": "divider"},
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"<@{user}>  *{notif.meta['title']}*",
                },
            },
            {"type": "divider"},
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"*{notif.meta['content']}*",},
            },
        ]


@block_set(required_context=["l", "u", "m"])
def opp_inactive_block_set(context):
    # Bruno created decorator required context l= lead, u= user m=message
    # slack mentions format = <@slack_id>

    lead = Lead.objects.filter(id=context.get("l")).first()
    user = User.objects.filter(id=context.get("u")).first()
    message = context.get("m")
    if lead and user:
        return [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"<@{user.slack_integration.slack_id}>  *{message}*",
                },
            },
        ]
