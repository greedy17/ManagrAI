import pdb
import uuid
import pytz
import math
from datetime import datetime


from managr.opportunity.models import Opportunity
from managr.slack import constants as slack_const
from managr.slack.helpers.utils import (
    action_with_params,
    get_lead_rating_emoji,
    block_set,
)

# TODO: this and other zoom-flow block_sets will likely need "m" for meeting ID


def generate_sentiment_button(text, value, params):
    return {
        "type": "button",
        "text": {"type": "plain_text", "text": text},
        "value": value,
        "action_id": action_with_params(
            slack_const.ZOOM_MEETING__PROCESS_MEETING_SENTIMENT, params=params,
        ),
    }


@block_set(required_context=["o", "u", "opp", "m"])
def zoom_meeting_initial(context):
    opportunity = Opportunity.objects.get(pk=context["opp"])
    description = opportunity.description or "No Description"
    next_step = opportunity.next_step or "No Next Step"
    meeting = opportunity.meetings.filter(id=context["m"]).first()
    # make params here
    user_id_param = "u=" + context["u"]
    opportunity_id_param = "opp=" + context["opp"]
    meeting_id_param = "m=" + context["m"]

    organization_id_param = "o=" + context["o"]
    sentiment_param = lambda x: f"sentiment={x}"

    get_time_stamp_id = lambda: f"id={math.floor(datetime.timestamp(datetime.now()))}"
    user_timezone = meeting.zoom_account.timezone
    start_time = meeting.start_time
    end_time = meeting.end_time
    formatted_start = (
        datetime.strftime(
            start_time.astimezone(pytz.timezone(user_timezone)), "%a, %B, %Y %I:%M %p"
        )
        if start_time
        else start_time
    )
    formatted_end = (
        datetime.strftime(end_time.astimezone(pytz.timezone(user_timezone)), "%a, %B, %Y %I:%M %p")
        if end_time
        else end_time
    )
    params = lambda sentiment: [
        user_id_param,
        opportunity_id_param,
        organization_id_param,
        meeting_id_param,
        sentiment_param(sentiment),
    ]

    return [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"Your meeting regarding :dart: *{opportunity.title}* just ended, how'd it go?",
            },
        },
        {"type": "divider"},
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*<fakeLink.toUserProfiles.com|{meeting.topic}>*\n{formatted_start} - {formatted_end}\n *Attendees:* {meeting.participants_count}",
            },
            "accessory": {
                "type": "image",
                "image_url": "https://api.slack.com/img/blocks/bkb_template_images/notifications.png",
                "alt_text": "calendar thumbnail",
            },
        },
        {"type": "divider"},
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
        {"type": "divider"},
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*{opportunity.title}*\n{description}\n{next_step}",
            },
        },
        {"type": "divider"},
        {
            "type": "actions",
            "elements": [
                generate_sentiment_button(
                    "Great!",
                    slack_const.ZOOM_MEETING__GREAT,
                    params(slack_const.ZOOM_MEETING__GREAT),
                ),
                generate_sentiment_button(
                    "Not Well",
                    slack_const.ZOOM_MEETING__NOT_WELL,
                    params(slack_const.ZOOM_MEETING__NOT_WELL),
                ),
                generate_sentiment_button(
                    "Can't Tell",
                    slack_const.ZOOM_MEETING__CANT_TELL,
                    params(slack_const.ZOOM_MEETING__CANT_TELL),
                ),
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "Different Opportunity",},
                    "value": slack_const.ZOOM_MEETING__DIFFERENT_OPPORTUNITY,
                    "action_id": action_with_params(
                        slack_const.ZOOM_MEETING__DIFFERENT_OPPORTUNITY,
                        params=[
                            user_id_param,
                            opportunity_id_param,
                            organization_id_param,
                            meeting_id_param,
                        ],
                    ),
                },
            ],
        },
    ]
