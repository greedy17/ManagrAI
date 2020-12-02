from managr.slack import constants as slack_const

# TODO: build block_sets for zoom meeting forms.
# Mockups, page 3: https://docs.google.com/document/d/1KIvznxOqPb7WuFOXsFcKMawxq8-8T2gpb2sYNdIqLL4/edit#heading=h.xa1nnwnl2is5
# Slack Block-Builder: https://app.slack.com/block-kit-builder/
# Block References: https://api.slack.com/reference/block-kit/block-elements

# Each blockObj has certain requirements that the Block-Builder may not add.
# I mainly observed this with missing action_id property for different blocks and sub-objects
# These forms need to leverage proper managr.slack.constants for action_ids, so we can
# identify the action properly later on when it is triggered by user and we receive data via webhook


zoom_meeting_initial = [
    {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "{{name}} your meeting with *{{account.lead}}* just ended, how'd it go?",
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
            "text": "*Lead Name Here*\n:star::star::star::star:Lead Rating Here\n Lead.PrimaryDescription here.\n Lead.SecondaryDescription here.",
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
                "text": {"type": "plain_text", "text": "Great!", "emoji": True},
                "value": "GREAT",
                "action_id": slack_const.ZOOM_MEETING__GREAT,
            },
            {
                "type": "button",
                "text": {"type": "plain_text", "text": "Not well...", "emoji": True},
                "value": "NOT_WELL",
                "action_id": slack_const.ZOOM_MEETING__NOT_WELL,
            },
        ],
    },
]

zoom_meeting_complete_form = [
    {"type": "divider"},
    {
        "type": "section",
        "fields": [
            {"type": "mrkdwn", "text": "*Opportunity:*"},
            {"type": "plain_text", "text": ":dart: Dunder Mifflin", "emoji": True},
        ],
    },
    {"type": "divider"},
    {
        "type": "section",
        "text": {"type": "mrkdwn", "text": "*Meeting Type*"},
        "accessory": {
            "type": "static_select",
            # "action_id": slack_const.ZOOM_MEETING__GREAT,
            "placeholder": {"type": "plain_text", "text": "Select"},
            "options": [
                {
                    "text": {"type": "plain_text", "text": "Manage it"},
                    "value": "value-0",
                },
                {
                    "text": {"type": "plain_text", "text": "Read it"},
                    "value": "value-1",
                },
                {
                    "text": {"type": "plain_text", "text": "Save it"},
                    "value": "value-2",
                },
            ],
        },
    },
    {
        "type": "section",
        "text": {"type": "mrkdwn", "text": "*Update Stage*"},
        "accessory": {
            "type": "external_select",
            "action_id": slack_const.GET_ORGANIZATION_STAGES,
            "placeholder": {"type": "plain_text", "text": "Select"},
            "min_query_length": 0,
            # "initial_option": {
            # }
        },
    },
    {
        "type": "section",
        "text": {"type": "mrkdwn", "text": "*Forecast Strength*"},
        "accessory": {
            "type": "static_select",
            # "action_id": slack_const.ZOOM_MEETING__GREAT,
            "placeholder": {"type": "plain_text", "text": "Select"},
            "options": [
                {
                    "text": {"type": "plain_text", "text": "Manage it"},
                    "value": "value-0",
                },
                {
                    "text": {"type": "plain_text", "text": "Read it"},
                    "value": "value-1",
                },
                {
                    "text": {"type": "plain_text", "text": "Save it"},
                    "value": "value-2",
                },
            ],
        },
    },
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
        "type": "section",
        "text": {"type": "mrkdwn", "text": "*Expected Close Date*"},
        "accessory": {
            "type": "datepicker",
            "initial_date": "1990-04-28",
            "placeholder": {"type": "plain_text", "text": "Select a date"},
            # "action_id": slack_const.ZOOM_MEETING__GREAT,
        },
    },
    {
        "type": "input",
        "optional": True,
        # "block_id": "input123",
        "label": {"type": "plain_text", "text": "Next Steps"},
        "element": {
            "type": "plain_text_input",
            # "action_id": slack_const.ZOOM_MEETING__GREAT,
            "placeholder": {"type": "plain_text", "text": "What's the plan?"},
        },
    },
]

zoom_meeting_limited_form = [
    {"type": "divider"},
    {
        "type": "section",
        "fields": [
            {"type": "mrkdwn", "text": "*Opportunity:*"},
            {"type": "plain_text", "text": ":dart: Dunder Mifflin", "emoji": True},
        ],
    },
    {"type": "divider"},
    {
        "type": "section",
        "text": {"type": "mrkdwn", "text": "*Meeting Type*"},
        "accessory": {
            "type": "static_select",
            # "action_id": slack_const.ZOOM_MEETING__GREAT,
            "placeholder": {"type": "plain_text", "text": "Select"},
            "options": [
                {
                    "text": {"type": "plain_text", "text": "Manage it"},
                    "value": "value-0",
                },
                {
                    "text": {"type": "plain_text", "text": "Read it"},
                    "value": "value-1",
                },
                {
                    "text": {"type": "plain_text", "text": "Save it"},
                    "value": "value-2",
                },
            ],
        },
    },
    {
        "type": "section",
        "text": {"type": "mrkdwn", "text": "*Update Stage*"},
        "accessory": {
            "type": "static_select",
            # "action_id": slack_const.ZOOM_MEETING__GREAT,
            "placeholder": {"type": "plain_text", "text": "Select"},
            "options": [
                {
                    "text": {"type": "plain_text", "text": "Manage it"},
                    "value": "value-0",
                },
                {
                    "text": {"type": "plain_text", "text": "Read it"},
                    "value": "value-1",
                },
                {
                    "text": {"type": "plain_text", "text": "Save it"},
                    "value": "value-2",
                },
            ],
        },
    },
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
        "label": {"type": "plain_text", "text": "Next Steps"},
        "element": {
            "type": "plain_text_input",
            # "action_id": slack_const.ZOOM_MEETING__GREAT,
            "placeholder": {"type": "plain_text", "text": "What's the plan?"},
        },
    },
]


def get_block_set(set_name):
    switcher = {
        "zoom_meeting_initial": zoom_meeting_initial,
        "zoom_meeting_complete_form": zoom_meeting_complete_form,
        "zoom_meeting_limited_form": zoom_meeting_limited_form,
    }
    return switcher.get(set_name)
