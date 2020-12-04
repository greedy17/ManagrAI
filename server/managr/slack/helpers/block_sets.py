from managr.core.models import User
from managr.lead.models import Lead
from managr.organization.models import Organization

from managr.slack import constants as slack_const
from managr.slack.helpers.utils import action_with_params, get_lead_rating_emoji
from managr.slack.helpers import block_builders
import pdb

# TODO: build block_sets for zoom meeting forms.
# Mockups, page 3: https://docs.google.com/document/d/1KIvznxOqPb7WuFOXsFcKMawxq8-8T2gpb2sYNdIqLL4/edit#heading=h.xa1nnwnl2is5
# Slack Block-Builder: https://app.slack.com/block-kit-builder/
# Block References: https://api.slack.com/reference/block-kit/block-elements

# Each blockObj has certain requirements that the Block-Builder may not add.
# I mainly observed this with missing action_id property for different blocks and sub-objects
# These forms need to leverage proper managr.slack.constants for action_ids, so we can
# identify the action properly later on when it is triggered by user and we receive data via webhook


def zoom_meeting_initial(context):
    """
    Required context:
    {
        user_id,
        lead_id,
        organization_id,
        meeting_id?
    }
    """
    # validate context
    required_context = ["lead_id", "organization_id", "user_id"]
    for prop in required_context:
        if context.get(prop) is None:
            raise ValueError(f"context missing: {prop}")

    lead = Lead.objects.get(pk=context["lead_id"])
    primary_description = lead.primary_description or "No Primary Description"
    secondary_description = lead.secondary_description or "No Secondary Description"

    # make params here
    user_id_param = "user_id=" + context["user_id"]
    lead_id_param = "lead_id=" + context["lead_id"]
    organization_id_param = "organization_id=" + context["organization_id"]

    return [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"Your meeting regarding *{lead.title}* just ended, how'd it go?",
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
                    "text": {
                        "type": "plain_text",
                        "text": "Not well...",
                    },
                    "value": slack_const.ZOOM_MEETING__NOT_WELL,
                    "action_id": action_with_params(
                        slack_const.ZOOM_MEETING__NOT_WELL,
                        params=[user_id_param, lead_id_param, organization_id_param],
                    ),
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Different Opportunity",
                    },
                    "value": slack_const.ZOOM_MEETING__DIFFERENT_OPPORTUNITY,
                    "action_id": action_with_params(
                        slack_const.ZOOM_MEETING__DIFFERENT_OPPORTUNITY,
                        params=[user_id_param, lead_id_param, organization_id_param],
                    ),
                },
            ],
        },
    ]


def zoom_meeting_complete_form(context):
    """
    Required context:
    {
        user_id,
        lead_id,
        organization_id,
    }
    """
    # validate context
    required_context = [
        "user_id",
        "lead_id",
        "organization_id",
    ]
    for prop in required_context:
        if context.get(prop) is None:
            raise ValueError(f"context missing: {prop}")

    lead = Lead.objects.get(pk=context.get("lead_id"))
    stage = lead.status.as_slack_option if lead.status else None
    forecast = lead.forecast.as_slack_option if lead.forecast else None
    expected_close_date = (
        str(lead.expected_close_date.date()) if lead.expected_close_date else None
    )

    # make params here
    user_id_param = "user_id=" + context.get("user_id")
    lead_id_param = "lead_id=" + context.get("lead_id")
    organization_id_param = "organization_id=" + context.get("organization_id")

    return [
        {
            "type": "section",
            "fields": [
                {"type": "mrkdwn", "text": "*Opportunity:*"},
                {"type": "plain_text", "text": f":dart: {lead.title}", "emoji": True},
            ],
        },
        {"type": "divider"},
        block_builders.external_select(
            "*Meeting Type*",
            action_with_params(
                slack_const.GET_ORGANIZATION_ACTION_CHOICES,
                params=[organization_id_param],
            ),
        ),
        block_builders.external_select(
            "*Update Stage*",
            action_with_params(
                slack_const.GET_ORGANIZATION_STAGES,
                params=[organization_id_param],
            ),
            initial_option=stage,
        ),
        block_builders.external_select(
            "*Forecast Strength*",
            action_with_params(slack_const.GET_LEAD_FORECASTS, params=[lead_id_param]),
            initial_option=forecast,
        ),
        {
            "type": "input",
            "optional": True,
            # "block_id": "input123",
            "label": {"type": "plain_text", "text": "Description"},
            "element": {
                "type": "plain_text_input",
                "multiline": True,
                # "action_id": slack_const.ZOOM_MEETING__GREAT,
                "placeholder": {"type": "plain_text", "text": "How'd it go?"},
            },
        },
        block_builders.datepicker(
            date=expected_close_date, label="*Expected Close Date*"
        ),
        {
            "type": "input",
            "optional": True,
            # "block_id": "input123",
            "label": {"type": "plain_text", "text": "Next Step"},
            "element": {
                "type": "plain_text_input",
                # "action_id": slack_const.ZOOM_MEETING__GREAT,
                "placeholder": {"type": "plain_text", "text": "What's the plan?"},
            },
        },
    ]


def zoom_meeting_limited_form(context):
    """
    Required context:
    {
        user_id,
        lead_id,
        organization_id,
    }
    """
    # validate context
    required_context = [
        "user_id",
        "lead_id",
        "organization_id",
    ]
    for prop in required_context:
        if context.get(prop) is None:
            raise ValueError(f"context missing: {prop}")

    lead = Lead.objects.get(pk=context.get("lead_id"))
    stage = lead.status.as_slack_option if lead.status else None

    # make params here
    user_id_param = "user_id=" + context.get("user_id")
    lead_id_param = "lead_id=" + context.get("lead_id")
    organization_id_param = "organization_id=" + context.get("organization_id")

    return [
        {
            "type": "section",
            "fields": [
                {"type": "mrkdwn", "text": "*Opportunity:*"},
                {"type": "plain_text", "text": f":dart: {lead.title}", "emoji": True},
            ],
        },
        {"type": "divider"},
        block_builders.external_select(
            "*Meeting Type*",
            action_with_params(
                slack_const.GET_ORGANIZATION_ACTION_CHOICES,
                params=[organization_id_param],
            ),
        ),
        block_builders.external_select(
            "*Update Stage*",
            action_with_params(
                slack_const.GET_ORGANIZATION_STAGES,
                params=[organization_id_param],
            ),
            initial_option=stage,
        ),
        {
            "type": "input",
            "optional": True,
            # "block_id": "input123",
            "label": {"type": "plain_text", "text": "Description"},
            "element": {
                "type": "plain_text_input",
                "multiline": True,
                # "action_id": slack_const.ZOOM_MEETING__GREAT,
                "placeholder": {"type": "plain_text", "text": "How'd it go?"},
            },
        },
        {
            "type": "input",
            "optional": True,
            # "block_id": "input123",
            "label": {"type": "plain_text", "text": "Next Step"},
            "element": {
                "type": "plain_text_input",
                # "action_id": slack_const.ZOOM_MEETING__GREAT,
                "placeholder": {"type": "plain_text", "text": "What's the plan?"},
            },
        },
    ]


def select_different_opportunity(context):
    """
    Required context:
    {
        user_id,
        lead_id,
        organization_id,
    }
    """
    # validate context
    required_context = [
        "user_id",
        "lead_id",
        "organization_id",
    ]
    for prop in required_context:
        if context.get(prop) is None:
            raise ValueError(f"context missing: {prop}")

    lead = Lead.objects.get(pk=context.get("lead_id"))

    # make params here
    user_id_param = "user_id=" + context.get("user_id")
    lead_id_param = "lead_id=" + context.get("lead_id")
    organization_id_param = "organization_id=" + context.get("organization_id")

    return [
        block_builders.external_select(
            f"*Opportunity:* :dart: _{lead.title}_",
            action_with_params(
                slack_const.GET_USER_OPPORTUNITIES,
                params=[
                    user_id_param,
                    lead_id_param,
                    organization_id_param,
                ],
            ),
            placeholder="Select Other",
            block_id="select_new_opportunity",
        ),
    ]


def get_block_set(set_name, context={}):
    """
    Returns array of Slack UI blocks
    """
    switcher = {
        "zoom_meeting_initial": zoom_meeting_initial,
        "zoom_meeting_complete_form": zoom_meeting_complete_form,
        "zoom_meeting_limited_form": zoom_meeting_limited_form,
        "select_different_opportunity": select_different_opportunity,
    }
    return switcher.get(set_name)(context)
