import pdb


from managr.core.models import User, Notification
from managr.opportunity.models import Opportunity, OpportunityScore
from managr.zoom.models import ZoomMeeting
from managr.salesforce import constants as sf_consts
from managr.slack import constants as slack_const
from managr.slack.helpers.utils import action_with_params, block_set
from managr.slack.helpers import block_builders
from managr.utils.misc import snake_to_space


def generate_edit_contact_form(field, id, value):
    return block_builders.input_block(field, block_id=id, initial_value=value, optional=True)


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
        """
        if not contact.get("integration_id", None):
            block_sets.append(
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {"type": "plain_text", "text": "Remove From Meeting"},
                            "value": "click_me_123",
                            "action_id": f"edit-contact-{i}",
                        }
                    ],
                }
            )
        """
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
