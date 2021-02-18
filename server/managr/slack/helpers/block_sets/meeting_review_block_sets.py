import pdb
import pytz
import uuid
import json

from datetime import datetime

from managr.core.models import User, Notification
from managr.opportunity.models import Opportunity
from managr.zoom.models import ZoomMeeting
from managr.salesforce import constants as sf_consts
from managr.slack import constants as slack_const
from managr.slack.helpers.utils import action_with_params, block_set, map_fields_to_type
from managr.slack.helpers import block_builders
from managr.utils.misc import snake_to_space
from managr.salesforce.routes import routes as form_routes


def _initial_interaction_base_message():
    return f"I've noticed your :calendar: meeting just ended"


def _initial_interaction_no_resource():
    # attach/create, account/opportunity, disregard
    return f"{_initial_interaction_base_message()} but couldn't find an Opportunity or Account to link what would you like to do?"


def _initial_interaction_w_resource(resource_type, resource_name):
    # replace opp, review disregard
    return f"{_initial_interaction_base_message()} and found this {resource_type} *{resource_name}* associated with it what would you like to do?"


def generate_edit_contact_form(field, id, value, optional=True):
    return block_builders.input_block(field, block_id=id, initial_value=value, optional=optional)


def generate_contact_group(index, contact, instance_url):
    integration_id = contact.get("integration_id")
    title = (
        contact.get("title")
        if contact.get("title", "") and len(contact.get("title", ""))
        else "N/A"
    )
    first_name = (
        contact.get("first_name")
        if contact.get("first_name", "") and len(contact.get("first_name", ""))
        else "N/A"
    )
    last_name = (
        contact.get("last_name")
        if contact.get("last_name", "") and len(contact.get("last_name", ""))
        else "N/A"
    )

    email = (
        contact.get("email")
        if contact.get("email", "") and len(contact.get("email", ""))
        else "N/A"
    )
    mobile_number = (
        contact.get("mobile_number")
        if contact.get("mobile_number") and len(contact.get("mobile_number"))
        else "N/A"
    )
    phone_number = (
        contact.get("phone_number")
        if contact.get("phone_number") and len(contact.get("phone_number"))
        else "N/A"
    )

    blocks = block_builders.simple_section(
        f"*Title:* {title}\n*First Name:* {first_name}\n*Last Name:* {last_name}\n*Email:* {email}\n*Mobile Phone:* {mobile_number}\n*Phone:* {phone_number}",
        "mrkdwn",
    )

    if integration_id:
        blocks["accessory"] = {
            "type": "button",
            "text": {"type": "plain_text", "text": "View In Salesforce"},
            "value": "View In Salesforce",
            "url": sf_consts.SALESFORCE_CONTACT_VIEW_URI(instance_url, integration_id),
            "action_id": f"button-action-{integration_id}",
        }

    return blocks


@block_set(required_context=["m"])
def meeting_contacts_block_set(context):
    meeting = ZoomMeeting.objects.filter(id=context.get("m")).first()

    contacts = meeting.participants
    sf_account = meeting.zoom_account.user.salesforce_account

    block_sets = [
        {"type": "header", "text": {"type": "plain_text", "text": "Review Meeting Participants",},},
        {"type": "divider"},
    ]
    contacts_in_sf = list(filter(lambda contact: contact["from_integration"], contacts))
    contacts_added_to_sf = list(
        filter(
            lambda contact: not contact["from_integration"] and contact["integration_id"], contacts
        )
    )
    contacts_not_added = list(
        filter(
            lambda contact: not contact["from_integration"]
            and (not contact["integration_id"] or not len(contact["integration_id"])),
            contacts,
        )
    )

    if len(contacts_not_added):
        block_sets.append(
            block_builders.simple_section(
                ":exclamation: *Managr did not add these participants from the meeting to Salesforce*",
                "mrkdwn",
            )
        )

    #### order matters ####
    for i, contact in enumerate(contacts_not_added):
        meeting_id_param = f"m={str(meeting.id)}"
        contact_index_param = f"contact_index={i}"
        block_sets.append(generate_contact_group(i, contact, sf_account.instance_url))
        # pass meeting id and contact index
        block_sets.append(
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "Edit Details"},
                        "value": "click_me_123",
                        "action_id": action_with_params(
                            slack_const.ZOOM_MEETING__EDIT_CONTACT,
                            params=[meeting_id_param, contact_index_param],
                        ),
                    }
                ],
            }
        )
        if not contact.get("integration_id", None):
            block_sets.append(
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {"type": "plain_text", "text": "Don't Save"},
                            "value": "click_me_123",
                            "action_id": action_with_params(
                                slack_const.ZOOM_MEETING__REMOVE_CONTACT,
                                params=[meeting_id_param, contact_index_param],
                            ),
                        }
                    ],
                }
            )

    if len(contacts_added_to_sf):
        block_sets.append(
            block_builders.simple_section(
                ":white_check_mark: *Managr added these participants from the meeting to Salesforce*",
                "mrkdwn",
            )
        )
    else:
        block_sets.append(
            block_builders.simple_section(
                "_All of the participants from your meeting where already in Salesforce_", "mrkdwn"
            )
        )

    for i, contact in enumerate(contacts_added_to_sf):
        meeting_id_param = f"m={str(meeting.id)}"
        contact_index_param = f"contact_index={i+len(contacts_not_added)}"
        block_sets.append(generate_contact_group(i, contact, sf_account.instance_url))
        # pass meeting id and contact index
        block_sets.append(
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "Edit Details"},
                        "value": "click_me_123",
                        "action_id": action_with_params(
                            slack_const.ZOOM_MEETING__EDIT_CONTACT,
                            params=[meeting_id_param, contact_index_param],
                        ),
                    }
                ],
            }
        )
        block_sets.append({"type": "divider"})

    if len(contacts_in_sf):
        block_sets.append(
            block_builders.simple_section(
                ":dart: *Managr found these attendees as contacts in Salesforce*", "mrkdwn",
            )
        )
    else:
        block_sets.append(
            block_builders.simple_section(
                "_All of the participants from your meeting where added by Managr to Salesforce_",
                "mrkdwn",
            )
        )

    for i, contact in enumerate(contacts_in_sf):
        meeting_id_param = f"m={str(meeting.id)}"
        contact_index_param = f"contact_index={i+len(contacts_not_added)+len(contacts_added_to_sf)}"
        block_sets.append(generate_contact_group(i, contact, sf_account.instance_url))
        # pass meeting id and contact index
        block_sets.append(
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "Edit Details"},
                        "value": "click_me_123",
                        "action_id": action_with_params(
                            slack_const.ZOOM_MEETING__EDIT_CONTACT,
                            params=[meeting_id_param, contact_index_param],
                        ),
                    }
                ],
            }
        )

        block_sets.append({"type": "divider"})
    return block_sets


@block_set(required_context=["meeting", "contact"])
def edit_meeting_contacts_block_set(context):
    contact = context["contact"]
    blocks = [
        generate_edit_contact_form("Title", "title", contact["title"]),
        generate_edit_contact_form("First Name", "first_name", contact["first_name"]),
        generate_edit_contact_form("Last Name", "last_name", contact["last_name"], optional=False),
        generate_edit_contact_form("Email", "email", contact["email"]),
        generate_edit_contact_form("Mobile Phone", "mobile_phone", contact["mobile_phone"]),
        generate_edit_contact_form("Phone", "phone_number", contact["phone_number"]),
    ]
    return blocks


def generate_sentiment_button(text, value, params):
    return {
        "type": "button",
        "text": {"type": "plain_text", "text": text},
        "value": value,
        "action_id": action_with_params(
            slack_const.ZOOM_MEETING__PROCESS_MEETING_SENTIMENT, params=params,
        ),
    }


@block_set(required_context=["m"])
def initial_meeting_interaction_block_set(context):
    # get the meeting
    meeting = ZoomMeeting.objects.filter(id=context["m"]).first()
    # check the resource attached to this meeting
    meeting_resource = meeting.meeting_resource
    opportunity = meeting.opportunity
    account = meeting.linked_account

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
    default_blocks = [
        {"type": "divider"},
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*{meeting.topic}*\n{formatted_start} - {formatted_end}\n *Attendees:* {meeting.participants_count}",
            },
            "accessory": {
                "type": "image",
                "image_url": "https://api.slack.com/img/blocks/bkb_template_images/notifications.png",
                "alt_text": "calendar thumbnail",
            },
        },
        {"type": "divider"},
    ]
    if not meeting_resource:
        blocks = [
            block_builders.simple_section(_initial_interaction_no_resource(), "mrkdwn",),
            *default_blocks,
            block_builders.actions_block(
                blocks=[
                    block_builders.simple_button_block(
                        "Attach Manually",
                        str(meeting.id),
                        action_id=slack_const.ZOOM_MEETING__CREATE_OR_SEARCH,
                        style="primary",
                    ),
                    block_builders.simple_button_block(
                        "Disregard",
                        str(meeting.id),
                        action_id=slack_const.ZOOM_MEETING__DISREGARD_REVIEW,
                        style="danger",
                    ),
                ]
            ),
        ]
    else:
        blocks = [
            block_builders.simple_section(
                _initial_interaction_w_resource(
                    meeting_resource,
                    opportunity.title if meeting_resource == "Opportunity" else account.name,
                ),
                "mrkdwn",
            ),
            *default_blocks,
            block_builders.actions_block(
                blocks=[
                    block_builders.simple_button_block(
                        "Review",
                        str(meeting.id),
                        action_id=slack_const.ZOOM_MEETING__INIT_REVIEW,
                        style="primary",
                    ),
                    block_builders.simple_button_block(
                        f"Change {meeting.meeting_resource}",
                        str(meeting.id),
                        action_id=slack_const.ZOOM_MEETING__CREATE_OR_SEARCH,
                    ),
                    block_builders.simple_button_block(
                        "Disregard",
                        str(meeting.id),
                        action_id=slack_const.ZOOM_MEETING__DISREGARD_REVIEW,
                        style="danger",
                    ),
                ]
            ),
        ]

    """blocks = [
        block_builders.actions_block(
            blocks=[
                block_builders.simple_button_block(
                    "Great!", str(meeting.id), action_id=slack_const.ZOOM_MEETING__GREAT,
                ),
                block_builders.simple_button_block(
                    "Not Well", str(meeting.id), action_id=slack_const.ZOOM_MEETING__NOT_WELL,
                ),
                block_builders.simple_button_block(
                    "Can't Tell", str(meeting.id), action_id=slack_const.ZOOM_MEETING__CANT_TELL,
                ),
            ]
        )
    ] """
    return blocks


@block_set(required_context=["m"])
def meeting_review_modal_block_set(context):
    meeting = ZoomMeeting.objects.filter(id=context["m"]).first()
    user = meeting.zoom_account.user
    organization = user.organization

    # get user slack form
    if meeting.meeting_resource == "Opportunity":

        slack_form = organization.custom_slack_forms.filter(
            form_type=slack_const.FORM_TYPE_MEETING_REVIEW, resource="Opportunity"
        ).first()
        opportunity = meeting.opportunity
        fields = slack_form.config.get("fields", [])
        values = opportunity.secondary_data
    elif meeting.meeting_resource == "Account":
        account = meeting.linked_account
        fields = slack_form.config.get("fields", [])
        values = account.secondary_data

    for k, value in values.items():
        for i, field in enumerate(fields):
            if field["key"] == k:
                field["value"] = value
                fields[i] = field

    blocks = map_fields_to_type(fields)

    # make params here

    return blocks


@block_set(required_context=["m"])
def attach_resource_interaction_block_set(context, *args, **kwargs):
    """ This modal allows a user attach an existing resource or create a new one """
    meeting = ZoomMeeting.objects.filter(id=context.get("m")).first()
    meeting_resource = meeting.meeting_resource

    # if there is no meeting resource this is from the interaction where no resource was found
    if not meeting_resource:
        blocks = [
            block_builders.static_select(
                "Select a resource to attach to the meeting",
                [
                    block_builders.option("Opportunity", "Opportunity"),
                    block_builders.option("Account", "Account"),
                ],
                action_id=f"{slack_const.ZOOM_MEETING__SELECTED_RESOURCE}?m={context.get('m')}",
            ),
        ]

    return blocks


@block_set(required_context=["m", "resource"])
def create_or_search_modal_block_set(context):
    blocks = [
        block_builders.static_select(
            "Would you like to create a new item or search for an existing option",
            [block_builders.option("Search", "SEARCH"), block_builders.option("Create", "CREATE"),],
            action_id=f"{slack_const.ZOOM_MEETING__SELECTED_CREATE_OR_SEARCH}?m={context.get('m')}&resource={context.get('resource')}",
        ),
    ]
    if context.get("selected_option", None):
        blocks[0]["accessory"]["initial_option"] = context.get("selected_option")

    return blocks


@block_set(required_context=["m", "resource"])
def search_modal_block_set(context, *args, **kwargs):
    m = ZoomMeeting.objects.get(id=context.get("m"))
    user = m.zoom_account.user
    return [
        block_builders.external_select(
            f"*Search for an {context.get('resource')}*",
            f"{slack_const.GET_LOCAL_RESOURCE_OPTIONS}?u={str(user.id)}&resource={context.get('resource')}",
            block_id="select_existing",
        )
    ]


@block_set(required_context=["m", "resource"])
def create_modal_block_set(context, *args, **kwargs):
    """ Shows a modal to create/select a resource """
    m = ZoomMeeting.objects.get(id=context.get("m"))
    user = m.zoom_account.user
    slack_form = user.organization.custom_slack_forms.filter(
        form_type=slack_const.FORM_TYPE_CREATE, resource=context.get("resource")
    ).first()
    fields = slack_form.config.get("fields", [])
    blocks = map_fields_to_type(fields)

    return blocks

