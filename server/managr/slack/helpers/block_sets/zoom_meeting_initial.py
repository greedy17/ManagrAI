import pdb

from managr.lead.models import Lead
from managr.slack import constants as slack_const
from managr.slack.helpers.utils import (
    action_with_params,
    get_lead_rating_emoji,
    block_set,
)

# TODO: this and other zoom-flow block_sets will likely need "m" for meeting ID


@block_set(required_context=["o", "u", "l"])
def zoom_meeting_initial(context):
    lead = Lead.objects.get(pk=context["l"])
    primary_description = lead.primary_description or "No Primary Description"
    secondary_description = lead.secondary_description or "No Secondary Description"

    # make params here
    user_id_param = "u=" + context["u"]
    lead_id_param = "l=" + context["l"]
    organization_id_param = "o=" + context["o"]

    return [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"Your meeting regarding :dart: *{lead.title}* just ended, how'd it go?",
            },
        },
        {"type": "divider"},
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*<fakeLink.toUserProfiles.com|Zoom Meeting Title Here>*\nTuesday, January 21 4:00-4:30pm\nBuilding 2 - Havarti Cheese (3)\n2 guests",
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
                "type": "mrkdwn",
                "text": f"*{lead.title}*\n{get_lead_rating_emoji(lead.rating)}\n{primary_description}\n{secondary_description}",
            },
            "accessory": {
                "type": "image",
                "image_url": "https://s3-media3.fl.yelpcdn.com/bphoto/c7ed05m9lC2EmA3Aruue7A/o.jpg",
                "alt_text": "alt text for image",
            },
        },
        {"type": "divider"},
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "Great!"},
                    "value": slack_const.ZOOM_MEETING__GREAT,
                    "action_id": action_with_params(
                        slack_const.ZOOM_MEETING__GREAT,
                        params=[user_id_param, lead_id_param, organization_id_param],
                    ),
                },
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "Not well...",},
                    "value": slack_const.ZOOM_MEETING__NOT_WELL,
                    "action_id": action_with_params(
                        slack_const.ZOOM_MEETING__NOT_WELL,
                        params=[user_id_param, lead_id_param, organization_id_param],
                    ),
                },
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "Different Opportunity",},
                    "value": slack_const.ZOOM_MEETING__DIFFERENT_OPPORTUNITY,
                    "action_id": action_with_params(
                        slack_const.ZOOM_MEETING__DIFFERENT_OPPORTUNITY,
                        params=[user_id_param, lead_id_param, organization_id_param],
                    ),
                },
            ],
        },
    ]
