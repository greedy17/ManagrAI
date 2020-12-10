# NOTE: This is an example payload received @ /slack/api/interactive-endpoint
block_actions_type = {
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

block_suggestions_type = {
    "type": "block_suggestion",
    "user": {
        "id": "UUTLULA84",
        "username": "bruno",
        "name": "bruno",
        "team_id": "T03EVK2FC",
    },
    "container": {"type": "view", "view_id": "V01FXMRB6KX"},
    "api_app_id": "A01ERE1QAE9",
    "token": "CVwUTl7hjscZVSzOtPDw76JK",
    "action_id": "GET_ORGANIZATION_STAGES",
    "block_id": "niDr",
    "value": "testtaasd",
    "team": {"id": "T03EVK2FC", "domain": "thinknimble"},
    "view": {
        "id": "V01FXMRB6KX",
        "team_id": "T03EVK2FC",
        "type": "modal",
        "blocks": [
            {"type": "divider", "block_id": "DHU"},
            {
                "type": "section",
                "block_id": "DigJh",
                "fields": [
                    {"type": "mrkdwn", "text": "*Opportunity:*", "verbatim": False},
                    {
                        "type": "plain_text",
                        "text": ":dart: Dunder Mifflin",
                        "emoji": True,
                    },
                ],
            },
            {"type": "divider", "block_id": "Rxsc"},
            {
                "type": "section",
                "block_id": "BqF",
                "text": {"type": "mrkdwn", "text": "*Meeting Type*", "verbatim": False},
                "accessory": {
                    "type": "static_select",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Select",
                        "emoji": True,
                    },
                    "options": [
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "Manage it",
                                "emoji": True,
                            },
                            "value": "value-0",
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "Read it",
                                "emoji": True,
                            },
                            "value": "value-1",
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "Save it",
                                "emoji": True,
                            },
                            "value": "value-2",
                        },
                    ],
                    "action_id": "crWE",
                },
            },
            {
                "type": "section",
                "block_id": "niDr",
                "text": {"type": "mrkdwn", "text": "*Update Stage*", "verbatim": False},
                "accessory": {
                    "type": "external_select",
                    "action_id": "ZOOM_MEETING__GREAT",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Select",
                        "emoji": True,
                    },
                },
            },
            {
                "type": "section",
                "block_id": "G0cY",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Forecast Strength*",
                    "verbatim": False,
                },
                "accessory": {
                    "type": "static_select",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Select",
                        "emoji": True,
                    },
                    "options": [
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "Manage it",
                                "emoji": True,
                            },
                            "value": "value-0",
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "Read it",
                                "emoji": True,
                            },
                            "value": "value-1",
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "Save it",
                                "emoji": True,
                            },
                            "value": "value-2",
                        },
                    ],
                    "action_id": "Kgj4y",
                },
            },
            {
                "type": "input",
                "block_id": "95fP/",
                "label": {"type": "plain_text", "text": "Description", "emoji": True},
                "optional": True,
                "dispatch_action": False,
                "element": {
                    "type": "plain_text_input",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "How'd it go?",
                        "emoji": True,
                    },
                    "multiline": True,
                    "dispatch_action_config": {
                        "trigger_actions_on": ["on_enter_pressed"]
                    },
                    "action_id": "v+tz",
                },
            },
            {
                "type": "section",
                "block_id": "6Bwx",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Expected Close Date*",
                    "verbatim": False,
                },
                "accessory": {
                    "type": "datepicker",
                    "initial_date": "1990-04-28",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Select a date",
                        "emoji": True,
                    },
                    "action_id": "OQ2I",
                },
            },
            {
                "type": "input",
                "block_id": "EaNB",
                "label": {"type": "plain_text", "text": "Next Steps", "emoji": True},
                "optional": True,
                "dispatch_action": False,
                "element": {
                    "type": "plain_text_input",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "What's the plan?",
                        "emoji": True,
                    },
                    "dispatch_action_config": {
                        "trigger_actions_on": ["on_enter_pressed"]
                    },
                    "action_id": "itmgj",
                },
            },
        ],
        "private_metadata": "",
        "callback_id": "modal-identifier",
        "state": {
            "values": {
                "6Bwx": {"OQ2I": {"type": "datepicker", "selected_date": "1990-04-28"}}
            }
        },
        "hash": "1606939382.Qd2U07Th",
        "title": {"type": "plain_text", "text": "Log Meeting", "emoji": True},
        "clear_on_close": False,
        "notify_on_close": False,
        "close": None,
        "submit": {"type": "plain_text", "text": "Submit", "emoji": True},
        "previous_view_id": None,
        "root_view_id": "V01FXMRB6KX",
        "app_id": "A01ERE1QAE9",
        "external_id": "",
        "app_installed_team_id": "T03EVK2FC",
        "bot_id": "B01EV93U1M0",
    },
}

view_submission_type = {
    "type": "view_submission",
    "team": {"id": "T03EVK2FC", "domain": "thinknimble"},
    "user": {
        "id": "UUTLULA84",
        "username": "bruno",
        "name": "bruno",
        "team_id": "T03EVK2FC",
    },
    "api_app_id": "A01ERE1QAE9",
    "token": "CVwUTl7hjscZVSzOtPDw76JK",
    "trigger_id": "1561704066449.3505648522.f19fee2542ffdecfb185344e2e835c40",
    "view": {
        "id": "V01GB6YN1NY",
        "team_id": "T03EVK2FC",
        "type": "modal",
        "blocks": [
            {
                "type": "section",
                "block_id": "target_block_1",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Opportunity:* :dart: _Montgomery County_",
                    "verbatim": False,
                },
                "accessory": {
                    "type": "external_select",
                    "action_id": "GET_USER_OPPORTUNITIES?user_id=3dddd261-93b1-46fe-a83e-bc064551362a&lead_id=2e248459-62b1-479d-871f-c468caaebf95&organization_id=700287d3-4ce6-4803-a236-b18e160729a7",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Select Other",
                        "emoji": True,
                    },
                    "min_query_length": 0,
                },
            }
        ],
        "private_metadata": '{"original_message_channel": "D01F4KWEAH0", "original_message_timestamp": "1607047508.000200", "action_query_string": "ZOOM_MEETING__DIFFERENT_OPPORTUNITY?user_id=3dddd261-93b1-46fe-a83e-bc064551362a&lead_id=2e248459-62b1-479d-871f-c468caaebf95&organization_id=700287d3-4ce6-4803-a236-b18e160729a7", "user_id": "3dddd261-93b1-46fe-a83e-bc064551362a", "lead_id": "2e248459-62b1-479d-871f-c468caaebf95", "organization_id": "700287d3-4ce6-4803-a236-b18e160729a7"}',
        "callback_id": "ZOOM_MEETING__DIFFERENT_OPPORTUNITY",
        "state": {
            "values": {
                "target_block_1": {
                    "GET_USER_OPPORTUNITIES?user_id=3dddd261-93b1-46fe-a83e-bc064551362a&lead_id=2e248459-62b1-479d-871f-c468caaebf95&organization_id=700287d3-4ce6-4803-a236-b18e160729a7": {
                        "type": "external_select",
                        "selected_option": None,
                    }
                }
            }
        },
        "hash": "1607048962.taeODcd8",
        "title": {"type": "plain_text", "text": "Change Opportunity", "emoji": True},
        "clear_on_close": False,
        "notify_on_close": False,
        "close": None,
        "submit": {"type": "plain_text", "text": "Submit", "emoji": True},
        "previous_view_id": None,
        "root_view_id": "V01GB6YN1NY",
        "app_id": "A01ERE1QAE9",
        "external_id": "",
        "app_installed_team_id": "T03EVK2FC",
        "bot_id": "B01EV93U1M0",
    },
    "response_urls": [],
}
