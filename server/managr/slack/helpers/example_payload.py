# NOTE: This is an example payload received @ /slack/api/interactive-endpoint
example = {
    "type": "block_actions",
    "user": {
        "id": "UUTLULA84",
        "username": "bruno",
        "name": "bruno",
        "team_id": "T03EVK2FC",
    },
    "api_app_id": "A01ERE1QAE9",
    "token": "CVwUTl7hjscZVSzOtPDw76JK",
    "container": {
        "type": "message",
        "message_ts": "1606841022.000200",
        "channel_id": "D01F4KWEAH0",
        "is_ephemeral": False,
    },
    "trigger_id": "1564642614880.3505648522.e1e021d95f8f0a7dfbd263e07c5eb8ba",
    "team": {"id": "T03EVK2FC", "domain": "thinknimble"},
    "channel": {"id": "D01F4KWEAH0", "name": "directmessage"},
    "message": {
        "bot_id": "B01EV93U1M0",
        "type": "message",
        "text": "This content can't be displayed.",
        "user": "U01FK4G9LG0",
        "ts": "1606841022.000200",
        "team": "T03EVK2FC",
        "blocks": [
            {
                "type": "section",
                "block_id": "C9C13",
                "text": {
                    "type": "mrkdwn",
                    "text": "{{name}} your meeting with *{{account.lead}}* just ended, how'd it go?",
                    "verbatim": False,
                },
            },
            {"type": "divider", "block_id": "npa/"},
            {
                "type": "section",
                "block_id": "9w22a",
                "text": {
                    "type": "mrkdwn",
                    "text": "*<fakeLink.toUserProfiles.com|Zoom Meeting Title Here>*\nTuesday, January 21 4:00-4:30pm\nBuilding 2 - Havarti Cheese (3)\n2 guests",
                    "verbatim": False,
                },
                "accessory": {
                    "type": "image",
                    "image_url": "https://api.slack.com/img/blocks/bkb_template_images/notifications.png",
                    "alt_text": "calendar thumbnail",
                },
            },
            {"type": "divider", "block_id": "bcN"},
            {
                "type": "section",
                "block_id": "yWggd",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Lead Name Here*\n:star::star::star::star:Lead Rating Here\n Lead.PrimaryDescription here.\n Lead.SecondaryDescription here.",
                    "verbatim": False,
                },
                "accessory": {
                    "type": "image",
                    "image_url": "https://s3-media3.fl.yelpcdn.com/bphoto/c7ed05m9lC2EmA3Aruue7A/o.jpg",
                    "alt_text": "alt text for image",
                },
            },
            {"type": "divider", "block_id": "L5ac"},
            {
                "type": "actions",
                "block_id": "k+/nO",
                "elements": [
                    {
                        "type": "button",
                        "action_id": "TEST_ID_1",
                        "text": {
                            "type": "plain_text",
                            "text": "Great!",
                            "emoji": True,
                        },
                        "value": "GREAT",
                    },
                    {
                        "type": "button",
                        "action_id": "TEST_ID_2",
                        "text": {
                            "type": "plain_text",
                            "text": "Not well...",
                            "emoji": True,
                        },
                        "value": "NOT_WELL",
                    },
                ],
            },
        ],
    },
    "response_url": "https://hooks.slack.com/actions/T03EVK2FC/1537712549141/j22pRr0u2nvaZXU56JUADLpl",
    "actions": [
        {
            "action_id": "TEST_ID_1",
            "block_id": "k+/nO",
            "text": {"type": "plain_text", "text": "Great!", "emoji": True},
            "value": "GREAT",
            "type": "button",
            "action_ts": "1606841054.842256",
        }
    ],
}
