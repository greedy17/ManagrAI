import pdb
import pytz
import uuid
import json
import logging

from datetime import datetime, date

from django.db.models import Q

from managr.utils.sites import get_site_url
from managr.core.models import User, Notification
from managr.opportunity.models import Opportunity, Lead
from managr.organization.models import Account, Contact
from managr.zoom.models import ZoomMeeting
from managr.salesforce.models import MeetingWorkflow, SObjectField
from managr.salesforce import constants as sf_consts
from managr.slack import constants as slack_const
from managr.slack.helpers.utils import (
    action_with_params,
    block_set,
    map_fields_to_type,
    block_finder,
    check_contact_last_name,
    get_random_no_update_message,
    get_random_update_message,
)

from managr.slack.helpers import block_builders, block_sets
from managr.utils.misc import snake_to_space
from managr.salesforce.routes import routes as form_routes
from managr.slack.models import OrgCustomSlackForm, OrgCustomSlackFormInstance

logger = logging.getLogger("managr")


def _initial_interaction_message(
    name, resource_name=None, resource_type=None, missing_attendees=False
):
    if not resource_type:
        return f"Hey {name}, your meeting just ended!"

    # replace opp, review disregard
    if missing_attendees:
        return f"Hey {name}, your meeting just ended! Missing attendee info:exclamation:"
    return f"Hey {name}, your meeting just ended and contacts look good :+1:"


def generate_edit_contact_form(field, id, value, optional=True):
    return block_builders.input_block(field, block_id=id, initial_value=value, optional=optional)


def generate_contact_group(index, contact, instance_url):
    # get fields from form and display values based on this form as label value in multi block
    integration_id = contact.get("integration_id")
    # get fields show only these items if they exist in the secondary data as options
    contact_secondary_data = contact.get("secondary_data", {})
    title = (
        contact_secondary_data.get("Title")
        if contact_secondary_data.get("Title", "") and len(contact_secondary_data.get("Title", ""))
        else "N/A"
    )
    first_name = (
        contact_secondary_data.get("FirstName")
        if contact_secondary_data.get("FirstName", "")
        and len(contact_secondary_data.get("FirstName", ""))
        else "N/A"
    )
    last_name = (
        contact_secondary_data.get("LastName")
        if contact_secondary_data.get("LastName", "")
        and len(contact_secondary_data.get("LastName", ""))
        else "N/A :exclamation: *Required*"
    )

    email = contact.get("email") if contact.get("email", "") not in ["", None] else "N/A"
    mobile_number = (
        contact_secondary_data.get("MobilePhone")
        if contact_secondary_data.get("MobilePhone")
        and len(contact_secondary_data.get("MobilePhone"))
        else "N/A"
    )
    phone_number = (
        contact_secondary_data.get("Phone")
        if contact_secondary_data.get("Phone") and len(contact_secondary_data.get("Phone"))
        else "N/A"
    )

    blocks = block_builders.simple_section(
        f"*Title:* {title}\n*First Name:* {first_name}\n*Last Name:* {last_name}\n*Email:* {email}\n*Mobile Phone:* {mobile_number}\n*Phone:* {phone_number}",
        "mrkdwn",
    )

    if integration_id:
        # url button to show in sf
        blocks["accessory"] = {
            "type": "button",
            "text": {"type": "plain_text", "text": "View In Salesforce"},
            "value": "View In Salesforce",
            "url": sf_consts.SALESFORCE_CONTACT_VIEW_URI(instance_url, integration_id),
            "action_id": f"button-action-{integration_id}",
        }
    return blocks


@block_set(required_context=["w"])
def create_meeting_task(context):
    workflow = MeetingWorkflow.objects.get(id=context.get("w"))

    return block_builders.section_with_button_block(
        "Create Task",
        "CREATE_A_TASK",
        "Would you like to create a task?",
        action_id=action_with_params(
            slack_const.ZOOM_MEETING__CREATE_TASK,
            params=[
                f"u={str(workflow.user.id)}",
                f"resource_type={workflow.resource_type}",
                f"resource_id={workflow.resource_id}",
            ],
        ),
    )


@block_set(required_context=["w"])
def schedule_meeting(context):
    workflow = MeetingWorkflow.objects.get(id=context.get("w"))

    return block_builders.section_with_button_block(
        "Schedule Zoom Meeting",
        "SCHEDULE_MEETING",
        "Schedule another Zoom meeting?",
        style="primary",
        action_id=action_with_params(
            slack_const.ZOOM_MEETING__MEETING_DETAILS, params=[f"u={str(workflow.user.id)}"],
        ),
    )


@block_set(required_context=["u", "resource_type", "resource_id", "resource_name"])
def add_to_cadence_block_set(context):
    return block_builders.section_with_button_block(
        "Add to Cadence",
        "add_to_cadence",
        "Add contacts to Cadence",
        style="danger",
        action_id=action_with_params(
            slack_const.ADD_TO_CADENCE_MODAL,
            params=[
                f"u={context.get('u')}",
                f"resource_id={context.get('resource_id')}",
                f"resource_name={context.get('resource_name')}",
                f"resource_type={context.get('resource_type')}",
            ],
        ),
    )


@block_set(required_context=["w"])
def meeting_contacts_block_set(context):
    # if this is a returning view it will also contain the selected contacts
    type = context.get("type", None)
    channel = f"channel={context.get('original_message_channel')}"
    timestamp = f"timestamp={context.get('original_message_timestamp')}"

    if type:
        block_sets = []
        if type == "Opportunity":
            workflow = Opportunity.objects.get(id=context.get("w"))
        elif type == "Account":
            workflow = Account.objects.get(id=context.get("w"))
        else:
            workflow = Lead.objects.get(id=context.get("w"))
        contact_ids = context.get("meeting_participants").split("%")
        form_ids = context.get("meeting_forms").split("%")
        forms = list(OrgCustomSlackFormInstance.objects.filter(id__in=form_ids).values())
        contacts = list(Contact.objects.filter(id__in=contact_ids).values())
        sf_account = workflow.owner.salesforce_account
    else:
        block_sets = [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": "Attendees below will be saved as Contacts"},
            },
            {"type": "divider"},
        ]
        workflow = MeetingWorkflow.objects.get(id=context.get("w"))
        meeting = workflow.meeting
        contacts = meeting.participants
        sf_account = meeting.zoom_account.user.salesforce_account
    # list contacts we already had from sf
    contacts_in_sf = list(filter(lambda contact: contact["integration_id"], contacts))

    contacts_not_in_sf = list(
        filter(lambda contact: contact.get("integration_id", None) in [None, ""], contacts,)
    )

    if len(contacts_not_in_sf):
        block_sets.extend(
            [block_builders.simple_section("Contacts below are not in salesforce")]
        ) if type else block_sets.extend(
            [
                block_builders.simple_section(
                    "_Click_ *'Edit'* _to fill in the missing details. Click_ *'Remove'* _to discard_",
                    "mrkdwn",
                )
            ]
        )

    for i, contact in enumerate(contacts_not_in_sf):
        if type:
            resource_id = list(
                filter(
                    lambda resource: resource["resource_id"] == contact["id"], contacts_not_in_sf
                )
            )
            resource_id_param = f"resource_id={context.get(resource_id)}"
        else:
            workflow_id_param = f"w={str(workflow)}" if type else f"w={str(workflow.id)}"
            tracking_id_param = f"tracking_id={contact['_tracking_id']}"
            params = (
                [
                    workflow_id_param,
                    tracking_id_param,
                    channel,
                    timestamp,
                    f"type={type}",
                    f"participants={context.get('meeting_participants')}",
                    f"forms={context.get('meeting_forms')}",
                ]
                if type
                else [workflow_id_param, tracking_id_param, channel, timestamp]
            )
        block_sets.append(generate_contact_group(i, contact, sf_account.instance_url))
        # pass meeting id and contact index
        if not type:
            block_sets.append(
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {"type": "plain_text", "text": "Edit Contact"},
                            "value": slack_const.ZOOM_MEETING__EDIT_CONTACT,
                            "action_id": action_with_params(
                                slack_const.ZOOM_MEETING__EDIT_CONTACT, params=params,
                            ),
                            "style": "primary",
                        },
                        {
                            "type": "button",
                            "text": {"type": "plain_text", "text": "Remove From Meeting"},
                            "value": slack_const.ZOOM_MEETING__EDIT_CONTACT,
                            "action_id": action_with_params(
                                slack_const.ZOOM_MEETING__REMOVE_CONTACT, params=params,
                            ),
                            "style": "danger",
                        },
                    ],
                }
            )

    if len(contacts_in_sf):
        block_sets.extend(
            [
                block_builders.simple_section(
                    ":dart: *Attendees below are already saved as Contacts*", "mrkdwn",
                ),
            ]
        )
    else:
        block_sets.append(
            block_builders.simple_section(
                "_All of the participants from your meeting where added by Managr to Salesforce_",
                "mrkdwn",
            )
        )
    for i, contact in enumerate(contacts_in_sf):
        if type:
            resource_id = list(
                filter(lambda resource: resource["resource_id"] == str(contact["id"]), forms)
            )[0]
            resource_id_param = f"resource_id={str(resource_id['id'])}"
        else:

            tracking_id_param = f"tracking_id={contact['_tracking_id']}"
        workflow_id_param = f"w={str(workflow.id)}"
        params = (
            [
                workflow_id_param,
                resource_id_param,
                channel,
                timestamp,
                f"type={type}",
                f"participants={context.get('meeting_participants')}",
                f"forms={context.get('meeting_forms')}",
            ]
            if type
            else [workflow_id_param, tracking_id_param, channel, timestamp]
        )
        block_sets.append(generate_contact_group(i, contact, sf_account.instance_url))
        # pass meeting id and contact index
        if not type:
            block_sets.append(
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {"type": "plain_text", "text": "Edit Contact"},
                            "value": slack_const.ZOOM_MEETING__EDIT_CONTACT,
                            "action_id": action_with_params(
                                slack_const.ZOOM_MEETING__EDIT_CONTACT, params=params,
                            ),
                            "style": "primary",
                        },
                        {
                            "type": "button",
                            "text": {"type": "plain_text", "text": "Remove From Meeting"},
                            "value": "click_me_123",
                            "action_id": action_with_params(
                                slack_const.ZOOM_MEETING__REMOVE_CONTACT, params=params,
                            ),
                            "style": "danger",
                        },
                    ],
                }
            )
        block_sets.append({"type": "divider"})
    return block_sets


@block_set(required_context=["w"])
def edit_meeting_contacts_block_set(context):
    print(context, "edit_meeting_contacts")
    type = context.get("type", None)
    if type:
        resource_form = OrgCustomSlackFormInstance.objects.get(id=context.get("resource_id"))
        contact = Contact.objects.get(id=resource_form.resource_id).__dict__
    else:
        workflow = MeetingWorkflow.objects.get(id=context.get("w"))
        meeting = workflow.meeting
        contact = dict(
            *filter(
                lambda contact: contact["_tracking_id"] == context.get("tracking_id"),
                meeting.participants,
            )
        )
    # if it already has an existing form it will be used
    user = resource_form.user if type else workflow.user
    form_id = contact.get("_form")
    if form_id in ["", None]:
        form_type = (
            slack_const.FORM_TYPE_UPDATE
            if contact.get("integration_id", None) not in ["", None]
            else slack_const.FORM_TYPE_CREATE
        )
        template = (
            OrgCustomSlackForm.objects.for_user(user)
            .filter(form_type=form_type, resource=slack_const.FORM_RESOURCE_CONTACT)
            .first()
        )
        # try to create the form on the fly
        if type:
            slack_form = OrgCustomSlackFormInstance.objects.create(user=user, template=template)
        else:
            slack_form = OrgCustomSlackFormInstance.objects.create(
                user=user, template=template, workflow=workflow
            )
    else:
        slack_form = (
            resource_form if type else workflow.forms.filter(id=contact.get("_form")).first()
        )
    if not slack_form:
        return [
            block_builders.simple_section(
                "It seems we are still generating this form please try again in a few"
            )
        ]

    if not len(slack_form.template.fields.all()):
        logger.info(
            f"instance id: {str(slack_form.id)},instance template id: {str(slack_form.template.id)}"
        )
        return [
            block_builders.section_with_button_block(
                "Forms",
                "form",
                "Please add fields to your contact update form",
                url=f"{get_site_url()}/forms",
            )
        ]
    else:

        slack_form = slack_form.generate_form(contact["secondary_data"])
        return slack_form


@block_set(required_context=["w"])
def initial_meeting_interaction_block_set(context):
    # get the meeting
    workflow = MeetingWorkflow.objects.get(id=context.get("w"))
    # check the resource attached to this meeting
    resource = workflow.resource
    meeting = workflow.meeting
    workflow_id_param = "w=" + context.get("w")
    contact_check = check_contact_last_name(context.get("w"))
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
        datetime.strftime(end_time.astimezone(pytz.timezone(user_timezone)), "%I:%M %p")
        if end_time
        else end_time
    )

    if workflow.resource_type:
        title_section_text = (
            _initial_interaction_message(
                workflow.user.first_name, resource.name, workflow.resource_type, False
            )
            if contact_check
            else _initial_interaction_message(
                workflow.user.first_name, resource.name, workflow.resource_type, True
            )
        )
        if contact_check:
            attendees_button = block_builders.section_with_button_block(
                "Review Attendees",
                str(workflow.id),
                title_section_text,
                action_id=action_with_params(
                    slack_const.ZOOM_MEETING__VIEW_MEETING_CONTACTS, params=[workflow_id_param,]
                ),
            )
        else:
            attendees_button = block_builders.section_with_button_block(
                "Review Attendees",
                str(workflow.id),
                title_section_text,
                action_id=action_with_params(
                    slack_const.ZOOM_MEETING__VIEW_MEETING_CONTACTS, params=[workflow_id_param,]
                ),
                style="danger",
            )
        change_opp_button = (
            "Change Opportunity"
            if workflow.resource_type == "Opportunity"
            else "Map to Opportunity"
        )
        blocks = [
            attendees_button,
            {"type": "divider"},
            block_builders.section_with_button_block(
                change_opp_button,
                str(workflow.id),
                f":calendar: Meeting {meeting.topic} was mapped to: _{workflow.resource_type}_ *{workflow.resource.name}*",
                action_id=slack_const.ZOOM_MEETING__CREATE_OR_SEARCH,
            ),
        ]
    else:
        blocks = [
            block_builders.section_with_button_block(
                "Map to Opportunity",
                str(workflow.id),
                _initial_interaction_message(workflow.user.first_name),
                action_id=slack_const.ZOOM_MEETING__CREATE_OR_SEARCH,
                style="primary",
            ),
            {"type": "divider"},
            block_builders.section_with_accessory_block(
                f":calendar: *{meeting.topic}*\n{formatted_start} - {formatted_end}\n Attendees: {meeting.participants_count}",
                block_builders.simple_image_block(
                    "https://managr-images.s3.amazonaws.com/slack/logo_loading.gif", "Managr Logo"
                ),
                text_type="mrkdwn",
            ),
        ]

    action_blocks = []
    if (
        workflow.resource_type == slack_const.FORM_RESOURCE_OPPORTUNITY
        or workflow.resource_type == slack_const.FORM_RESOURCE_ACCOUNT
    ):
        action_blocks.append(
            block_builders.simple_button_block(
                f"Update {workflow.resource_type} + Add Notes",
                str(workflow.id),
                action_id=slack_const.ZOOM_MEETING__INIT_REVIEW,
                style="primary",
            ),
        )
    if workflow.resource_type == slack_const.FORM_RESOURCE_LEAD:
        action_blocks.append(
            block_builders.simple_button_block(
                "Convert Lead",
                str(workflow.id),
                action_id=action_with_params(
                    slack_const.ZOOM_MEETING__CONVERT_LEAD, params=[f"u={str(workflow.user.id)}"]
                ),
                style="primary",
            ),
        )

    if workflow.resource_type:
        action_blocks.append(
            block_builders.simple_button_block(
                "No Update Needed",
                str(workflow.id),
                action_id=slack_const.ZOOM_MEETING__PROCESS_NO_CHANGES,
                style="danger",
            )
        )
    if contact_check and workflow.resource_type:
        blocks.append({"type": "divider"})
        blocks.append(block_builders.actions_block(action_blocks))
    return blocks


@block_set(required_context=["w"])
def meeting_review_modal_block_set(context):
    workflow = MeetingWorkflow.objects.get(id=context.get("w"))
    user = workflow.user
    slack_form = workflow.forms.filter(template__form_type=slack_const.FORM_TYPE_UPDATE).first()

    blocks = []

    # additional validations

    blocks.extend(slack_form.generate_form())
    # static blocks
    if slack_form:
        try:
            index, block = block_finder("StageName", blocks)
        except ValueError:
            # did not find the block
            block = None
            pass

        if block:
            action_id = slack_const.ZOOM_MEETING__STAGE_SELECTED + f"?w={context.get('w')}"
            block = {
                **block,
                "accessory": {**block["accessory"], "action_id": f"{action_id}",},
            }
            blocks = [*blocks[:index], block, *blocks[index + 1 :]]

    # make params here

    return blocks


@block_set(required_context=["w"])
def attach_resource_interaction_block_set(context, *args, **kwargs):
    """This interaction updates the message to show a drop down of resources"""
    blocks = [
        block_builders.static_select(
            ":information_source: Select an object to attach to the meeting",
            [
                *map(
                    lambda resource: block_builders.option(resource, resource),
                    slack_const.MEETING_RESOURCE_ATTACHMENT_OPTIONS,
                )
            ],
            action_id=f"{slack_const.ZOOM_MEETING__SELECTED_RESOURCE}?w={context.get('w')}",
            block_id=slack_const.ZOOM_MEETING__ATTACH_RESOURCE_SECTION,
        ),
    ]

    return blocks


@block_set(required_context=["w", "resource"])
def create_or_search_modal_block_set(context):
    additional_opts = []
    resource_type = context.get("resource")
    if not resource_type == "Lead":
        additional_opts = [
            {
                "label": f"NEW {resource_type} (create)",
                "value": f'CREATE_NEW.{context.get("resource")}',
            }
        ]

    workflow = MeetingWorkflow.objects.get(id=context.get("w"))
    user = workflow.user
    resource_id = context.get("resource_id", None)
    # if an id is already passed (Aka this is recurrsive) get the resource
    if resource_id:
        resource = (
            form_routes[resource_type]["model"].objects.filter(integration_id=resource_id).first()
        )

    return [
        block_builders.external_select(
            f"*Search for an {resource_type}*",
            f"{slack_const.GET_LOCAL_RESOURCE_OPTIONS}?u={str(user.id)}&resource={resource_type}&add_opts={json.dumps(additional_opts)}&__block_action={slack_const.ZOOM_MEETING__SELECTED_RESOURCE_OPTION}",
            block_id="select_existing",
            placeholder="Type to search",
            initial_option=block_builders.option(resource.name, str(resource.id))
            if resource_id and resource
            else None,
        )
    ]


@block_set(required_context=["w", "resource"])
def create_modal_block_set(context, *args, **kwargs):
    """Shows a modal to create a resource"""
    workflow = MeetingWorkflow.objects.get(id=context.get("w"))
    user = workflow.user
    existing_form_id = context.get("f", None)
    if existing_form_id:
        existing_form = workflow.forms.filter(id=existing_form_id).first()
        if not existing_form:
            existing_form.add(existing_form)
        form_blocks = existing_form.generate_form(existing_form.saved_data)
    else:

        template = (
            OrgCustomSlackForm.objects.for_user(user)
            .filter(
                Q(resource=context.get("resource"), form_type=slack_const.FORM_TYPE_CREATE,)
                & Q(Q(stage=kwargs.get("stage", None)) | Q(stage=kwargs.get("stage", "")))
            )
            .first()
        )
        if template:
            workflow.forms.filter(
                template__form_type__in=[
                    slack_const.FORM_TYPE_CREATE,
                    slack_const.FORM_TYPE_STAGE_GATING,
                ]
            ).exclude(template__resource=slack_const.FORM_RESOURCE_CONTACT).delete()
            # remove old instance (in case there was an error that required the form to add fields)

            slack_form = OrgCustomSlackFormInstance.objects.create(
                user=user, template=template, workflow=workflow
            )
            form_blocks = slack_form.generate_form()
    if len(form_blocks):
        blocks = [*form_blocks]
    else:

        blocks = [
            block_builders.section_with_button_block(
                "Forms",
                "form",
                f"Please add fields to your {context.get('resource')} create form",
                url=f"{get_site_url()}/forms",
            )
        ]
    return blocks


@block_set(required_context=["w"])
def disregard_meeting_review_block_set(context, *args, **kwargs):
    """Shows a modal to create/select a resource"""
    w = MeetingWorkflow.objects.get(id=context.get("w"))
    blocks = [
        block_builders.section_with_button_block(
            "Review",
            str(w.id),
            f":thumbsup: okay, you can always come back to review *{w.meeting.topic}* :calendar:",
            action_id=slack_const.ZOOM_MEETING__RESTART_MEETING_FLOW,
        )
    ]

    return blocks


@block_set(required_context=["w"])
def final_meeting_interaction_block_set(context):
    workflow = MeetingWorkflow.objects.get(id=context.get("w"))
    meeting = workflow.meeting
    meeting_form = workflow.forms.filter(template__form_type=slack_const.FORM_TYPE_UPDATE).first()
    meet_type = meeting_form.saved_data.get("meeting_type", None)
    text = (
        get_random_no_update_message(meeting.topic)
        if meet_type == "No Update"
        else get_random_update_message(meeting.topic)
    )
    blocks = [
        block_builders.section_with_button_block(
            "Send Recap",
            "SEND_RECAP",
            text,
            action_id=action_with_params(
                slack_const.PROCESS_SEND_RECAP_MODAL,
                params=[
                    f"u={str(workflow.user.id)}",
                    f"workflow_id={str(workflow.id)}",
                    "type=meeting",
                ],
            ),
        )
    ]
    return blocks


@block_set(required_context=["w"])
def no_changes_interaction_block_set(context):
    workflow = MeetingWorkflow.objects.get(id=context.get("w"))

    meeting = workflow.meeting

    blocks = [
        block_builders.simple_section(
            f":+1: Got it! No updated needed for meeting *{meeting.topic}* ", "mrkdwn",
        ),
    ]

    return blocks


@block_set(required_context=["w"])
def meeting_summary_blockset(context):
    workflow = MeetingWorkflow.objects.get(id=context.get("w"))
    meeting = workflow.meeting
    review = meeting.zoom_meeting_review
    summary = meeting.zoom_meeting_review.meeting_review_summary
    user_timezone = meeting.zoom_account.timezone
    start_time = meeting.start_time

    formatted_start = (
        datetime.strftime(start_time.astimezone(pytz.timezone(user_timezone)), "%m/%d/%Y")
        if start_time
        else start_time
    )

    blocks = [
        block_builders.simple_section(
            f"Review for {workflow.user.first_name} {workflow.user.last_name}'s meeting with *Meeting Topic {meeting.topic}* For {workflow.resource_type} {workflow.resource.name}",
            "mrkdwn",
        ),
    ]
    meeting_type = review.meeting_type
    meeting_start = formatted_start
    stage_component = list(filter(lambda comp: comp.type == "stage", summary))
    forecast_component = list(filter(lambda comp: comp.type == "forecast", summary))
    close_date_component = list(filter(lambda comp: comp.type == "close_date", summary))
    duration_component = list(filter(lambda comp: comp.type == "duration", summary))
    attendance_component = list(filter(lambda comp: comp.type == "attendance", summary))
    amount_component = list(filter(lambda comp: comp.type == "amount", summary))
    stage_message = (
        stage_component[0].rendered_message_delta
        if stage_component[0].rendered_message_delta
        else stage_component[0].rendered_message
    )
    amount_message = (
        amount_component[0].rendered_message_delta
        if amount_component[0].rendered_message_delta
        else amount_component[0].rendered_message
    )
    close_date_message = (
        close_date_component[0].rendered_message_delta
        if close_date_component[0].rendered_message_delta
        else close_date_component[0].rendered_message
    )

    review_str = f"*Meeting Type:* {meeting_type}\n*Meeting Date:* {meeting_start}\n*Stage Update:* {stage_message}\n*Forecast:* {forecast_component[0].rendered_message}\n*Amount:* {amount_message} \n*Close Date:* {close_date_message}\n"
    if review.next_step not in ["", None]:
        review_str = f"{review_str}*Next Step:* {review.next_step}\n"

    review_str = f"{review_str}*Managr Insights:* {attendance_component[0].rendered_message} {duration_component[0].rendered_message}\n*Meeting Comments:*\n {review.meeting_comments}"
    blocks.append(block_builders.simple_section(review_str, "mrkdwn"))

    return blocks


@block_set(required_context=[])
def schedule_zoom_meeting_modal(context):
    user = User.objects.get(id=context.get("u"))
    today = str(date.today())
    blocks = [
        block_builders.input_block(
            "Meeting Topic",
            placeholder="Enter your topic",
            optional=False,
            block_id="meeting_topic",
            action_id="meeting_data",
        ),
        block_builders.datepicker(
            today, block_id="meeting_date", action_id="meeting_data", label="Meeting Date"
        ),
        block_builders.static_select(
            "Start Time (Hour)",
            block_sets.get_block_set("hour_options"),
            action_id="meeting_data",
            placeholder="Hour",
            block_id="meeting_hour",
        ),
        block_builders.static_select(
            "Start Time (Minutes)",
            block_sets.get_block_set("minute_options"),
            action_id="meeting_data",
            placeholder="Minutes",
            block_id="meeting_minute",
        ),
        block_builders.static_select(
            "AM/PM",
            block_sets.get_block_set("time_options"),
            action_id="meeting_data",
            initial_option={"text": {"type": "plain_text", "text": "AM"}, "value": "AM"},
            block_id="meeting_time",
        ),
        block_builders.static_select(
            "Duration",
            block_sets.get_block_set("duration_options"),
            action_id="meeting_data",
            initial_option={"text": {"type": "plain_text", "text": "30"}, "value": "30"},
            block_id="meeting_duration",
        ),
        block_builders.input_block(
            "Description",
            placeholder="Put your adgenda and notes here",
            action_id="meeting_data",
            block_id="meeting_description",
            multiline=True,
        ),
        block_builders.multi_external_select(
            "*Add Contacts to this meeting*",
            action_id=f"{slack_const.GET_USER_CONTACTS}?u={user.id}",
            block_id="meeting_participants",
            placeholder="Search Contacts",
        ),
    ]
    return blocks


@block_set(required_context=["u"])
def send_recap_block_set(context):
    user = User.objects.get(id=context.get("u"))
    blocks = [
        *SObjectField.objects.get(pk="fd4207a6-fec0-4f0b-9ce1-6aaec31d39ed").to_slack_field(
            user=user
        ),
        SObjectField.objects.get(pk="e286d1d5-5447-47e6-ad55-5f54fdd2b00d").to_slack_field(
            user=user
        ),
        SObjectField.objects.get(pk="fae88a10-53cc-470e-86ec-32376c041893").to_slack_field(
            user=user
        ),
    ]
    return blocks
