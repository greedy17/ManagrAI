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

test = [
    {
        "type": "actions",
        "elements": [
            {
                "type": "button",
                "text": {"type": "plain_text", "text": "Next 5 Results"},
                "value": "click_me_123",
            }
        ],
    },
    {"type": "divider"},
    {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "*<fakeLink.toYourApp.com|Comprehensive Benefits Catalogue - 2019>*\nInformation about all the benfits we offer is...",
        },
        "accessory": {
            "type": "static_select",
            "placeholder": {"type": "plain_text", "text": "Manage"},
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
        "text": {
            "type": "mrkdwn",
            "text": "*<fakeLink.toYourApp.com|Use Case Catalogue - CF Presentation - [June 12, 2018]>*\nThis is presentation will continue to be updated as...",
        },
        "accessory": {
            "type": "static_select",
            "placeholder": {"type": "plain_text", "text": "Manage"},
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
        "text": {
            "type": "mrkdwn",
            "text": "*<fakeLink.toYourApp.com|Self-Serve Learning Options Catalogue>*\nSee the learning and development options we...",
        },
        "accessory": {
            "type": "static_select",
            "placeholder": {"type": "plain_text", "text": "Manage"},
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
        "text": {
            "type": "mrkdwn",
            "text": "*<fakeLink.toYourApp.com|Customer Support - Workflow Diagram Catalogue>*\nThis resource was put together by members of...",
        },
        "accessory": {
            "type": "static_select",
            "placeholder": {"type": "plain_text", "text": "Manage"},
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
        "text": {
            "type": "mrkdwn",
            "text": "*<fakeLink.toYourApp.com|Use Case Catalogue>*\nUse Case Catalogue for the following departments/roles...",
        },
        "accessory": {
            "type": "static_select",
            "placeholder": {"type": "plain_text", "text": "Manage"},
            "options": [
                {
                    "text": {"type": "plain_text", "text": "Edit it"},
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
    {"type": "divider"},
    {
        "type": "section",
        "text": {"type": "mrkdwn", "text": ":mag: Search results for *Cata*"},
    },
]


def get_block_set(set_name):
    switcher = {
        "zoom_meeting_initial": zoom_meeting_initial,
        # "zoom_meeting_complete_form": zoom_meeting_complete_form,
        # "zoom_meeting_limited_form": zoom_meeting_limited_form,
        "test": test,
    }
    return switcher.get(set_name)
