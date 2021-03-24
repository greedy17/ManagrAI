import pdb

from managr.core.models import User, Notification
from managr.opportunity.models import Opportunity
from managr.zoom.models import ZoomMeeting

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
            {"type": "header", "text": {"type": "plain_text", "text": ":calendar:  Reminder"},},
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


@block_set(required_context=["l", "u", "m", "t"])
def opp_inactive_block_set(context):
    # Bruno created decorator required context l= lead, u= user m=message
    # slack mentions format = <@slack_id>

    lead = Lead.objects.filter(id=context.get("l")).first()
    user = User.objects.filter(id=context.get("u")).first()
    lead_param = "l=" + context["l"]
    title = context.get("t")
    message = context.get("m")
    if lead and user:
        return [
            {"type": "section", "text": {"type": "mrkdwn", "text": f" :bangbang:  *{title}*",},},
            {"type": "divider"},
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"<@{user.slack_integration.slack_id}> {message}",
                },
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "View Contacts"},
                        "action_id": action_with_params(
                            slack_const.SHOW_LEAD_CONTACTS, params=[lead_param],
                        ),
                    },
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "View Logs"},
                        "action_id": action_with_params(
                            slack_const.SHOW_LEAD_LOGS, params=[lead_param],
                        ),
                    },
                ],
            },
        ]


@block_set(required_context=["score_paragraph"])
def meeting_score_description_block_set(context):

    # slack mentions format = <@slack_id>

    score_paragraph = context.get("score_paragraph")
    obj = {
        "type": "section",
        "text": {"type": "mrkdwn", "text": f"{score_paragraph}",},
    }

    return obj


@block_set(required_context=["m"])
def meeting_review_score(context):
    # Bruno created decorator required context l= lead, u= user m=message
    # slack mentions format = <@slack_id>

    meeting = ZoomMeeting.objects.filter(id=context.get("m")).first()
    user = meeting.zoom_account.user
    meeting_param = "m=" + context["m"]
    meeting_type = meeting.meeting_review.meeting_type
    action_choice = (
        user.organization.action_choices.filter(id=meeting_type).first() if meeting_type else "N/A"
    )
    if meeting:
        return [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f":heavy_check_mark: *{meeting.zoom_account.user.full_name}* meeting with *{meeting.opportunity.name}* scored *{meeting.meeting_score}*, it was a {action_choice.title}. Click below to see the summary.",
                },
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "View Meeting Score Summary",},
                        "action_id": action_with_params(
                            slack_const.SHOW_MEETING_SCORE_COMPONENTS, params=[meeting_param],
                        ),
                    },
                ],
            },
        ]


@block_set(required_context=["ls"])
def lead_score_block_set(context):
    # Bruno created decorator required context l= lead, u= user m=message
    # slack mentions format = <@slack_id>

    lead_score = LeadScore.objects.select_related("lead").filter(id=context.get("ls")).first()
    lead = lead_score.lead
    user = lead.claimed_by
    lead_score_param = "ls=" + context["ls"]
    if lead:
        return [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f":heavy_check_mark: A score for opportunity *{lead.title}* claimed by *{user.full_name}* is {lead_score.final_score}",
                },
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "View Scoring Components",},
                        "action_id": action_with_params(
                            slack_const.SHOW_LEAD_SCORE_COMPONENTS, params=[lead_score_param],
                        ),
                    },
                ],
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
    worked_with_text = f"{user.full_name} did not work with one specific contact"
    if primary_contact:
        first_name = primary_contact.get("first_name", None)
        last_name = primary_contact.get("last_name", None)
        worked_with_text = f"{user.full_name} Primarily worked with {first_name} {last_name}"

    if lead and user:
        return [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"Boom closed {lead.title} for ${lead.closing_amount} :heavy_check_mark:",
                },
            },
            {"type": "divider"},
            {"type": "section", "text": {"type": "mrkdwn", "text": f"<@{user_slack}>"},},
            {"type": "section", "text": {"type": "mrkdwn", "text": worked_with_text,},},
            {"type": "section", "text": {"type": "mrkdwn", "text": "see the full report below"},},
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


@block_set(required_context=["contact"])
def lead_contacts_block_set(context):

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


@block_set(required_context=["activity"])
def lead_activity_log_block_set(context):

    # slack mentions format = <@slack_id>

    activity = context.get("activity")
    if activity.action_timestamp:
        formatted_date = activity.action_timestamp.strftime("%m/%d/%Y %I:%M %p")
    else:
        formatted_date = "Date Time info unavailable"
    obj = {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": f"*Activity:* {activity.activity}\n *Date and Time:* {formatted_date}",
        },
    }

    return obj


@block_set(required_context=["score_components"])
def lead_score_description_block_set(context):

    # slack mentions format = <@slack_id>

    score_components = context.get("score_components")
    obj = {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": f"*{score_components['label']}* \n *Score:* {score_components['score']}\n *Insight:* {score_components['insight']}",
        },
    }

    return obj
