import pdb
import pytz
import uuid
import json
import logging

from datetime import datetime

from django.db.models import Q

from managr.utils.sites import get_site_url
from managr.core.models import User, Notification
from managr.opportunity.models import Opportunity
from managr.zoom.models import ZoomMeeting
from managr.salesforce.models import MeetingWorkflow
from managr.salesforce import constants as sf_consts
from managr.slack import constants as slack_const
from managr.slack.helpers.utils import (
    action_with_params,
    block_set,
    map_fields_to_type,
)

from managr.slack.helpers import block_builders
from managr.utils.misc import snake_to_space
from managr.salesforce.routes import routes as form_routes
from managr.slack.models import OrgCustomSlackForm, OrgCustomSlackFormInstance

logger = logging.getLogger("managr")


def _initial_interaction_message(resource_name=None, resource_type=None):
    if not resource_type:
        return "I've noticed your meeting just ended but couldn't find an Opportunity or Account or Lead to link what would you like to do?"

    # replace opp, review disregard
    return f"I've noticed your meeting with {resource_type} *{resource_name}* just ended would you like to log this meeting?"


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
        else "N/A"
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
    print("create meeting task")
    print(workflow.__dict__)

    return block_builders.section_with_button_block(
        "Create Task",
        "CREATE_A_TASK",
        "Would you like to create a task from this meeting?",
        action_id=action_with_params(
            slack_const.ZOOM_MEETING__CREATE_TASK, params=[f"u={str(workflow.user.id)}"],
        ),
    )


@block_set()
def convert_lead_block_set(context):
    from .common_blocksets import coming_soon_modal_block_set

    return coming_soon_modal_block_set()


@block_set(required_context=["w"])
def meeting_contacts_block_set(context):
    # if this is a returning view it will also contain the selected contacts

    workflow = MeetingWorkflow.objects.get(id=context.get("w"))
    meeting = workflow.meeting

    contacts = meeting.participants
    sf_account = meeting.zoom_account.user.salesforce_account

    block_sets = [
        {"type": "header", "text": {"type": "plain_text", "text": "Review Meeting Participants",},},
        {"type": "divider"},
    ]
    # list contacts we already had from sf
    contacts_in_sf = list(filter(lambda contact: contact["integration_id"], contacts))

    contacts_not_in_sf = list(
        filter(lambda contact: contact.get("integration_id", None) in [None, ""], contacts,)
    )

    if len(contacts_not_in_sf):
        block_sets.extend(
            [
                block_builders.simple_section(
                    ":exclamation: *Managr did not add these participants from the meeting to Salesforce*",
                    "mrkdwn",
                ),
                block_builders.simple_section(
                    f":ballot_box_with_check: _These contacts will be added to Salesforce and attached to the {workflow.resource_type}_",
                    "mrkdwn",
                ),
            ]
        )

    for i, contact in enumerate(contacts_not_in_sf):
        workflow_id_param = f"w={str(workflow.id)}"
        tracking_id_param = f"tracking_id={contact['_tracking_id']}"
        block_sets.append(generate_contact_group(i, contact, sf_account.instance_url))
        # pass meeting id and contact index
        block_sets.append(
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "Click To Select for Editing"},
                        "value": slack_const.ZOOM_MEETING__EDIT_CONTACT,
                        "action_id": action_with_params(
                            slack_const.ZOOM_MEETING__EDIT_CONTACT,
                            params=[workflow_id_param, tracking_id_param],
                        ),
                    },
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "Remove From Meeting"},
                        "value": slack_const.ZOOM_MEETING__EDIT_CONTACT,
                        "action_id": action_with_params(
                            slack_const.ZOOM_MEETING__REMOVE_CONTACT,
                            params=[workflow_id_param, tracking_id_param],
                        ),
                    },
                ],
            }
        )

    if len(contacts_in_sf):
        block_sets.extend(
            [
                block_builders.simple_section(
                    ":dart: *Managr found these attendees as contacts in Salesforce*", "mrkdwn",
                ),
                block_builders.simple_section(
                    f":ballot_box_with_check: _These contacts will be attached to the {workflow.resource_type}_",
                    "mrkdwn",
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
        workflow_id_param = f"w={str(workflow.id)}"
        tracking_id_param = f"tracking_id={contact['_tracking_id']}"

        block_sets.append(generate_contact_group(i, contact, sf_account.instance_url))
        # pass meeting id and contact index
        block_sets.append(
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "Click To Select for Editing"},
                        "value": slack_const.ZOOM_MEETING__EDIT_CONTACT,
                        "action_id": action_with_params(
                            slack_const.ZOOM_MEETING__EDIT_CONTACT,
                            params=[workflow_id_param, tracking_id_param],
                        ),
                    },
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "Remove From Meeting"},
                        "value": "click_me_123",
                        "action_id": action_with_params(
                            slack_const.ZOOM_MEETING__REMOVE_CONTACT,
                            params=[workflow_id_param, tracking_id_param],
                        ),
                    },
                ],
            }
        )

        block_sets.append({"type": "divider"})
    return block_sets


@block_set(required_context=["w", "tracking_id"])
def edit_meeting_contacts_block_set(context):

    workflow = MeetingWorkflow.objects.get(id=context.get("w"))
    meeting = workflow.meeting
    contact = dict(
        *filter(
            lambda contact: contact["_tracking_id"] == context.get("tracking_id"),
            meeting.participants,
        )
    )
    # if it already has an existing form it will be used
    form_id = contact.get("_form")
    if form_id in ["", None]:
        form_type = (
            slack_const.FORM_TYPE_UPDATE
            if contact.get("integration_id", None) not in ["", None]
            else slack_const.FORM_TYPE_CREATE
        )
        template = (
            OrgCustomSlackForm.objects.for_user(workflow.user)
            .filter(form_type=form_type, resource=slack_const.FORM_RESOURCE_CONTACT)
            .first()
        )
        # try to create the form on the fly
        slack_form = OrgCustomSlackFormInstance.objects.create(
            user=workflow.user, template=template, workflow=workflow
        )
    else:
        slack_form = workflow.forms.filter(id=contact.get("_form")).first()
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
        block_builders.section_with_accessory_block(
            f"*{meeting.topic}*\n{formatted_start} - {formatted_end}\n *Attendees:* {meeting.participants_count}",
            block_builders.simple_image_block(
                "https://api.slack.com/img/blocks/bkb_template_images/notifications.png",
                "calendar thumbnail",
            ),
        ),
        block_builders.section_with_button_block(
            "Review Meeting Participants",
            slack_const.ZOOM_MEETING__VIEW_MEETING_CONTACTS,
            "Review the people who joined your meeting before saving them to Salesforce",
            action_id=action_with_params(
                slack_const.ZOOM_MEETING__VIEW_MEETING_CONTACTS, params=[workflow_id_param,],
            ),
        ),
        {"type": "divider"},
    ]
    if not resource:
        title_section = _initial_interaction_message()
    else:
        name = resource.name
        title_section = _initial_interaction_message(name, workflow.resource_type)
    blocks = [
        block_builders.simple_section(title_section, "mrkdwn",),
        *default_blocks,
    ]
    # action button blocks
    action_blocks = [
        block_builders.simple_button_block(
            "Attach/Change",
            str(workflow.id),
            action_id=slack_const.ZOOM_MEETING__CREATE_OR_SEARCH,
            style="primary",
        ),
        block_builders.simple_button_block(
            "Disregard",
            str(workflow.id),
            action_id=slack_const.ZOOM_MEETING__DISREGARD_REVIEW,
            style="danger",
        ),
    ]

    if (
        workflow.resource_type == slack_const.FORM_RESOURCE_OPPORTUNITY
        or workflow.resource_type == slack_const.FORM_RESOURCE_ACCOUNT
    ):
        action_blocks = [
            block_builders.simple_button_block(
                "Review",
                str(workflow.id),
                action_id=slack_const.ZOOM_MEETING__INIT_REVIEW,
                style="primary",
            ),
            *action_blocks,
        ]
    elif workflow.resource_type == slack_const.FORM_RESOURCE_LEAD:
        action_blocks = [
            block_builders.simple_button_block(
                "Convert Lead",
                str(workflow.id),
                action_id=action_with_params(
                    slack_const.ZOOM_MEETING__CONVERT_LEAD, params=[f"u={str(workflow.user.id)}"]
                ),
                style="primary",
            ),
            *action_blocks,
        ]
    blocks.append(block_builders.actions_block(action_blocks))

    return blocks


@block_set(required_context=["w"])
def meeting_review_modal_block_set(context):
    workflow = MeetingWorkflow.objects.get(id=context.get("w"))
    user = workflow.user
    slack_form = workflow.forms.filter(
        template__form_type=slack_const.FORM_TYPE_MEETING_REVIEW
    ).first()

    blocks = [
        block_builders.simple_section(
            ":exclamation: *Please fill out all fields, not doing so may result in errors*",
            "mrkdwn",
        ),
    ]

    # additional validations
    validations = None
    if validations:

        blocks.extend(
            [
                block_builders.simple_section(
                    ":warning: *_Additional Validations required to avoid errors_*", "mrkdwn"
                ),
                block_builders.simple_section_multiple(
                    list(
                        map(
                            lambda validation: block_builders.text_block(
                                f'_{validation[0]+1}. {validation[1]["message"]}_', "mrkdwn"
                            ),
                            enumerate(validations),
                        )
                    )
                ),
            ]
        )

    blocks.extend(slack_form.generate_form())
    # static blocks

    # make params here

    return blocks


@block_set(required_context=["w"])
def attach_resource_interaction_block_set(context, *args, **kwargs):
    """ This interaction updates the message to show a drop down of resources """
    blocks = [
        block_builders.static_select(
            ":information_source: Select a resource to attach to the meeting",
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
    options = [
        block_builders.option("Search", "SEARCH"),
    ]
    if context.get("resource") != sf_consts.RESOURCE_SYNC_LEAD:
        options.append(block_builders.option("Create", "CREATE"),)
    blocks = [
        block_builders.static_select(
            "Would you like to create a new item or search for an existing option",
            options,
            # action_id=f"{slack_const.ZOOM_MEETING__SELECTED_CREATE_OR_SEARCH}?w={context.get('w')}&resource={context.get('resource')}",
            block_id="create_or_search",
            action_id="selected_option",
        ),
    ]

    return blocks


@block_set(required_context=["w", "resource"])
def search_modal_block_set(context, *args, **kwargs):
    workflow = MeetingWorkflow.objects.get(id=context.get("w"))
    user = workflow.user
    return [
        block_builders.external_select(
            f"*Search for an {context.get('resource')}*",
            f"{slack_const.GET_LOCAL_RESOURCE_OPTIONS}?u={str(user.id)}&resource={context.get('resource')}",
            block_id="select_existing",
        )
    ]


@block_set(required_context=["w", "resource"])
def create_modal_block_set(context, *args, **kwargs):
    """ Shows a modal to create a resource """
    workflow = MeetingWorkflow.objects.get(id=context.get("w"))
    user = workflow.user
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
            blocks = [
                block_builders.simple_section(
                    ":exclamation: *Please fill out all fields, not doing so may result in errors*",
                    "mrkdwn",
                ),
            ]

            blocks = [*blocks, *form_blocks]
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
    """ Shows a modal to create/select a resource """
    w = MeetingWorkflow.objects.get(id=context.get("w"))
    user = w.user
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

    blocks = [
        block_builders.simple_section(
            f":heavy_check_mark: Logged meeting :calendar: for *{meeting.topic}* regarding :dart: {workflow.resource.name}",
            "mrkdwn",
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
            f"*Meeting Topic: {meeting.topic}* For {workflow.resource_type} {workflow.resource.name}",
            "mrkdwn",
        ),
        block_builders.simple_section(f"*Meeting Type:*  {review.meeting_type}", "mrkdwn",),
        block_builders.simple_section(f"*Meeting Date:*  {formatted_start}", "mrkdwn",),
    ]

    stage_component = list(filter(lambda comp: comp.type == "stage", summary))
    forecast_component = list(filter(lambda comp: comp.type == "forecast", summary))
    close_date_component = list(filter(lambda comp: comp.type == "close_date", summary))
    duration_component = list(filter(lambda comp: comp.type == "duration", summary))
    attendance_component = list(filter(lambda comp: comp.type == "attendance", summary))
    amount_component = list(filter(lambda comp: comp.type == "amount", summary))

    blocks.append(
        block_builders.simple_section(
            f"*Stage Update:* {stage_component[0].rendered_message}", "mrkdwn",
        )
    )
    blocks.append(
        block_builders.simple_section(
            f"*Forecast:* {forecast_component[0].rendered_message}", "mrkdwn",
        )
    )
    # amount blockset
    blocks.append(
        block_builders.simple_section(
            f"*Amount:* {amount_component[0].rendered_message}", "mrkdwn",
        )
    )

    blocks.append(
        block_builders.simple_section(
            f"*Close Date:* {close_date_component[0].rendered_message}", "mrkdwn",
        )
    )

    if review.next_step not in ["", None]:
        blocks.append(block_builders.simple_section(f"*Next Step:* {review.next_step}", "mrkdwn"))

    blocks.append(
        block_builders.simple_section(
            f"*Helpful Hints:* {attendance_component[0].rendered_message}, {duration_component[0].rendered_message} ",
            "mrkdwn",
        )
    )
    blocks.append(
        block_builders.simple_section(f"*Meeting Comments:* {review.meeting_comments}", "mrkdwn",)
    )

    return blocks

