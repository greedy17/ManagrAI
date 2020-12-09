import pdb

from managr.core.models import User
from managr.lead.models import Lead, Notification, Reminder
from managr.report.models import StoryReport
from managr.slack import constants as slack_const
from managr.slack.helpers.utils import action_with_params, block_set
from managr.slack.helpers import block_builders


@block_set(required_context=["r"])
def reminder_block_set(context):
    # Bruno created decorator required context n = Notification
    # slack mentions format = <@slack_id>

    reminder = Reminder.objects.filter(id=context.get("r")).first()
    user = reminder.created_by.slack_integration.slack_id

    reminder_param = "r=" + context["r"]
    if reminder:
        notify_at = reminder.datetime_for.strftime("%m/%d/%Y %I:%M %p")
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
                    "text": f"<@{user}>  *{reminder.title}*\n{reminder.content} @{notify_at}\nFor lead *{reminder.created_for.title}*",
                },
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "View Contacts"},
                        "action_id": action_with_params(
                            slack_const.SHOW_REMINDER_CONTACTS, params=[reminder_param],
                        ),
                    },
                ],
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


@block_set(required_context=["l", "r"])
def opp_closed_report_generated(context):
    # Bruno created decorator required context l= lead, u= user m=message
    # slack mentions format = <@slack_id>

    lead = Lead.objects.filter(id=context.get("l")).first()
    user = lead.claimed_by
    user_slack = user.slack_integration.slack_id
    report = lead.story_reports.filter(id=context.get("r")).first()
    primary_contact = report.data["lead"].get("primary_contact", None)

    if lead and user:
        return [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"Boom closed {lead.title} for ${lead.closing_amount} :clapping:",
                },
            },
            {"type": "divider"},
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"<@{user_slack}>"},
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"{user.full_name} Primarily worked with {primary_contact}",
                },
            },
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": "see the full report below"},
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "View Report"},
                        "url": report.client_side_url,
                    },
                ],
            },
        ]


@block_set(required_context=["contact"])
def reminder_contact_block_set(context):

    # slack mentions format = <@slack_id>

    contact = context.get("contact")

    obj = {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": f"Name: {contact.full_name}\nemail: {contact.email}\nphone: {contact.phone_number_1}",
        },
    }

    return obj

