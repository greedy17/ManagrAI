import pytz
import json
import logging
from django.conf import settings
from datetime import datetime, date
from django.db.models import Q
from managr.utils.sites import get_site_url
from managr.core.models import User, MeetingPrepInstance
from managr.salesforce.models import MeetingWorkflow, SObjectField
from managr.crm.models import ObjectField
from managr.salesforce import constants as sf_consts
from managr.slack import constants as slack_const
from managr.slack.helpers.utils import (
    action_with_params,
    block_set,
    block_finder,
)
from managr.slack.helpers import block_builders, block_sets
from managr.crm.utils import CRM_SWITCHER
from managr.slack.models import OrgCustomSlackForm, OrgCustomSlackFormInstance

logger = logging.getLogger("managr")


def _initial_interaction_message(resource_name=None, resource_type=None, meeting_title=None):
    if not resource_type:
        return f"*New Task:* Log your meeting :calendar: *{meeting_title}*"

    return f"*New Task:* Log your meeting :calendar: {resource_type} *{resource_name}*"


def generate_edit_contact_form(field, id, value, optional=True):
    return block_builders.input_block(field, block_id=id, initial_value=value, optional=optional)


def generate_contact_group(index, contact, instance_url, crm):
    # get fields from form and display values based on this form as label value in multi block
    integration_id = contact.get("integration_id")
    integration_source = contact.get("integration_source")
    # get fields show only these items if they exist in the secondary data as options
    contact_secondary_data = contact.get("secondary_data", {})
    title_api = "Title" if integration_source == "SALESFORCE" else "jobtitle"
    first_name_api = "FirstName" if integration_source == "SALESFORCE" else "firstname"
    last_name_api = "LastName" if integration_source == "SALESFORCE" else "lastname"
    mobile_api = "MobilePhone" if integration_source == "SALESFORCE" else "mobilephone"
    phone_api = "Phone" if integration_source == "SALESFORCE" else "phone"
    title = (
        contact_secondary_data.get(title_api)
        if contact_secondary_data.get(title_api, "")
        and len(contact_secondary_data.get(title_api, ""))
        else "N/A"
    )
    first_name = (
        contact_secondary_data.get(first_name_api)
        if contact_secondary_data.get(first_name_api, "")
        and len(contact_secondary_data.get(first_name_api, ""))
        else "N/A"
    )
    last_name = (
        contact_secondary_data.get(last_name_api)
        if contact_secondary_data.get(last_name_api, "")
        and len(contact_secondary_data.get(last_name_api, ""))
        else "N/A :exclamation: *Required*"
    )

    email = contact.get("email") if contact.get("email", "") not in ["", None] else "N/A"
    mobile_number = (
        contact_secondary_data.get(mobile_api)
        if contact_secondary_data.get(mobile_api) and len(contact_secondary_data.get(mobile_api))
        else "N/A"
    )
    phone_number = (
        contact_secondary_data.get(phone_api)
        if contact_secondary_data.get(phone_api) and len(contact_secondary_data.get(phone_api))
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
            "text": {"type": "plain_text", "text": f"View In {crm}"},
            "value": f"View In {crm}",
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
    channel = f"original_message_channel={context.get('original_message_channel')}"
    timestamp = f"original_message_timestamp={context.get('original_message_timestamp')}"

    if type:
        block_sets = []
        workflow = MeetingPrepInstance.objects.get(id=context.get("w"))
        contacts = workflow.participants
        crm_account = workflow.user.crm_account
    else:
        block_sets = []
        workflow = MeetingWorkflow.objects.get(id=context.get("w"))
        meeting = workflow.meeting
        contacts = meeting.participants
        crm_account = workflow.user.crm_account
    # list contacts we already had from sf
    contacts_in_crm = list(filter(lambda contact: contact["integration_id"], contacts))

    contacts_not_in_crm = list(
        filter(lambda contact: contact.get("integration_id", None) in [None, ""], contacts,)
    )

    if len(contacts_not_in_crm):
        block_sets.extend(
            [block_builders.simple_section(f"Contacts below are not in {workflow.user.crm}")]
        ) if type else block_sets.extend(
            [
                block_builders.simple_section(
                    ":busts_in_silhouette: *Attendees below will be saved as Contacts*", "mrkdwn",
                )
            ]
        )

    for i, contact in enumerate(contacts_not_in_crm):
        workflow_id_param = f"w={str(workflow.id)}"
        tracking_id_param = f"tracking_id={contact['_tracking_id']}"
        params = (
            [workflow_id_param, tracking_id_param, channel, timestamp, f"type={type}",]
            if type
            else [workflow_id_param, tracking_id_param, channel, timestamp]
        )
        block_sets.append(
            generate_contact_group(i, contact, crm_account.instance_url, workflow.user.crm)
        )
        # pass meeting id and contact index
        if type:
            if type != "prep":
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
                            }
                        ],
                    }
                )
        else:
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

    if len(contacts_in_crm):
        block_sets.extend(
            [
                block_builders.simple_section(
                    ":cloud: *Attendees below are already saved as Contacts*", "mrkdwn",
                ),
            ]
        )

    for i, contact in enumerate(contacts_in_crm):
        tracking_id_param = f"tracking_id={contact['_tracking_id']}"
        workflow_id_param = f"w={str(workflow.id)}"
        params = (
            [workflow_id_param, channel, timestamp, f"type={type}",]
            if type
            else [workflow_id_param, tracking_id_param, channel, timestamp]
        )
        block_sets.append(
            generate_contact_group(i, contact, crm_account.instance_url, workflow.user.crm)
        )
        # pass meeting id and contact index
        if type:
            if type != "prep":
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
                            }
                        ],
                    }
                )
        else:
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
        block_sets.append({"type": "divider"})
    return block_sets


@block_set(required_context=["w"])
def edit_meeting_contacts_block_set(context):
    type = context.get("type", None)
    if type:
        workflow = MeetingPrepInstance.objects.get(id=context.get("w"))
        contact = dict(
            *filter(
                lambda contact: contact["_tracking_id"] == context.get("tracking_id"),
                workflow.participants,
            )
        )
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
    user = workflow.user
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

        slack_form = OrgCustomSlackFormInstance.objects.get(id=contact.get("_form"))
    if not slack_form:
        return [
            block_builders.simple_section(
                "It seems we are still generating this form please try again in a few"
            )
        ]

    if not len(slack_form.template.custom_fields.all()):
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
    # If else meeting if has attribute workflow, meeting or else workflow.meeting
    meeting = workflow.meeting
    user_timezone = workflow.user.timezone
    title = meeting.topic
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
    title_section_text = (
        _initial_interaction_message(resource.name, workflow.resource_type)
        if workflow.resource_type
        else _initial_interaction_message(meeting_title=meeting.topic)
    )
    title_section = block_builders.simple_section(title_section_text, "mrkdwn")

    blocks = [
        title_section,
        {"type": "divider"},
        block_builders.section_with_accessory_block(
            f":calendar: *{title}*\n{formatted_start} - {formatted_end}\nAttendees: {len(meeting.participants)}",
            block_builders.simple_image_block(
                "https://managr-images.s3.amazonaws.com/slack/logo_loading.gif", "Managr Logo"
            ),
            text_type="mrkdwn",
        ),
        block_builders.actions_block(
            [
                block_builders.simple_button_block(
                    f"Review {len(meeting.participants)} Attendees",
                    str(workflow.id),
                    action_id=action_with_params(
                        slack_const.ZOOM_MEETING__VIEW_MEETING_CONTACTS,
                        params=[f"w={str(workflow.id)}"],
                    ),
                )
            ]
        ),
        {"type": "divider"},
    ]
    resource_button = (
        f"Change {workflow.resource_type}" if workflow.resource_type else "Link to CRM Record"
    )
    resource_block = (
        block_builders.section_with_button_block(
            resource_button,
            str(workflow.id),
            f"*{workflow.resource_type}* {resource.name}",
            action_id=slack_const.ZOOM_MEETING__CREATE_OR_SEARCH,
        )
        if workflow.resource_type
        else block_builders.simple_button_block(
            resource_button,
            str(workflow.id),
            action_id=slack_const.ZOOM_MEETING__CREATE_OR_SEARCH,
            style="primary",
        )
    )
    if workflow.resource_type and workflow.resource_type != "Opportunity":
        resource_block["accessory"]["style"] = "primary"

    action_blocks = []
    if workflow.resource_type:
        blocks.append(resource_block)
        action_blocks.append(
            block_builders.simple_button_block(
                f"Update {workflow.resource_type} + Notes",
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
                        slack_const.ZOOM_MEETING__CONVERT_LEAD,
                        params=[f"u={str(workflow.user.id)}&w={str(workflow.id)}"],
                    ),
                    style="primary",
                ),
            )
        action_blocks.append(
            block_builders.simple_button_block(
                "No Update Needed",
                str(workflow.id),
                action_id=slack_const.ZOOM_MEETING__PROCESS_NO_CHANGES,
                style="danger",
            )
        )
    else:
        action_blocks.append(resource_block)
    blocks.append(block_builders.actions_block(action_blocks))
    return blocks


@block_set(required_context=["w"])
def meeting_review_modal_block_set(context):
    workflow = MeetingWorkflow.objects.get(id=context.get("w"))
    user = workflow.user
    slack_form = workflow.forms.filter(template__form_type=slack_const.FORM_TYPE_UPDATE).first()
    if user.organization.has_products and slack_form.template.resource == "Opportunity":
        try:
            current_products = user.salesforce_account.list_resource_data(
                "OpportunityLineItem",
                0,
                filter=[
                    "AND IsDeleted = false",
                    f"AND OpportunityId = '{slack_form.resource_object.integration_id}'",
                ],
            )
        except Exception as e:
            logger.exception(f"Failed to retrieve current products due to <{e}>")
    blocks = []
    resource = "Task" if user.crm == "SALESFORCE" else "Meeting"
    field = "Type" if user.crm == "SALESFORCE" else "hs_meeting_outcome"
    type_text = "Note Type" if user.crm == "SALESFORCE" else "Meeting Outcome"
    try:
        note_options = user.crm_account.get_individual_picklist_values(resource, field)
        note_options = note_options.values if user.crm == "SALESFORCE" else note_options.values()
        note_options_list = [
            block_builders.option(opt.get("label"), opt.get("value")) for opt in note_options
        ]
        blocks.append(
            block_builders.static_select(
                type_text, options=note_options_list, block_id="managr_task_type"
            )
        )
    except Exception as e:
        logger.exception(f"Could not pull note type for {user.email} due to <{e}>")
    # additional validations
    if len(slack_form.saved_data):
        blocks.extend(slack_form.generate_form(slack_form.saved_data))
    else:
        blocks.extend(slack_form.generate_form())
    # static blocks
    if slack_form:
        stage_name = "StageName" if user.crm == "SALESFORCE" else "dealstage"
        try:
            index, block = block_finder(stage_name, blocks)
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

    if user.organization.has_products and slack_form.template.resource == "Opportunity":
        params = [
            f"f={str(slack_form.id)}",
            f"u={str(user.id)}",
            f"w={str(workflow.id)}",
            "type=meeting",
        ]
        buttons = []
        if slack_form.resource_object.secondary_data["Pricebook2Id"]:
            params.append(f"pricebook={slack_form.resource_object.secondary_data['Pricebook2Id']}")
        buttons.append(
            block_builders.simple_button_block(
                "Add Product",
                "ADD_PRODUCT",
                action_id=action_with_params(slack_const.PROCESS_ADD_PRODUCTS_FORM, params=params,),
            )
        )
        if len(user.crm_account.custom_objects) > 0:
            buttons.append(
                block_builders.simple_button_block(
                    "Add Custom Object",
                    "ADD_CUSTOM_OBJECT",
                    action_id=action_with_params(
                        slack_const.PROCESS_PICK_CUSTOM_OBJECT, params=params,
                    ),
                )
            )
        blocks.append(block_builders.actions_block(buttons, block_id="ADD_EXTRA_OBJECTS_BUTTON",),)
        if current_products:
            for product in current_products:
                product_block = block_sets.get_block_set(
                    "current_product_blockset",
                    {
                        "opp_item_id": product.integration_id,
                        "product_data": {
                            "name": product.name,
                            "quantity": product.quantity,
                            "total": product.total_price,
                        },
                        "u": str(user.id),
                        "main_form": str(slack_form.id),
                    },
                )
                blocks.append(product_block)
    return blocks


@block_set(required_context=["w"])
def attach_resource_interaction_block_set(context, *args, **kwargs):
    """This interaction updates the message to show a drop down of resources"""
    workflow = MeetingWorkflow.objects.get(id=context.get("w"))
    type = context.get("type", None)
    action = (
        f"{slack_const.ZOOM_MEETING__SELECTED_RESOURCE}?w={context.get('w')}&type={type}"
        if type
        else f"{slack_const.ZOOM_MEETING__SELECTED_RESOURCE}?w={context.get('w')}"
    )
    options = (
        slack_const.MEETING_RESOURCE_ATTACHMENT_OPTIONS
        if workflow.user.crm == "SALESFORCE"
        else slack_const.MEETING_RESOURCE_HUBSPOT_ATTACHMENT_OPTIONS
    )
    resource = "Opportunity" if workflow.user.crm == "SALESFORCE" else "Deal"
    blocks = [
        block_builders.static_select(
            f":information_source: Select a CRM record type",
            [*map(lambda resource: block_builders.option(resource, resource), options,)],
            action_id=action,
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
            CRM_SWITCHER[user.crm][resource_type]["model"]
            .objects.filter(integration_id=resource_id)
            .first()
        )
    action_id = f"{slack_const.GET_CRM_RESOURCE_OPTIONS}?u={str(user.id)}&resource_type={resource_type}&add_opts={json.dumps(additional_opts)}&__block_action={slack_const.ZOOM_MEETING__SELECTED_RESOURCE_OPTION}"
    return [
        block_builders.external_select(
            f"*Search for an {resource_type}*",
            action_id,
            block_id="select_existing",
            placeholder="Type to search",
            initial_option=block_builders.option(resource.name, str(resource.id))
            if resource_id and resource
            else None,
        )
    ]


@block_set(required_context=["w", "resource_type"])
def create_modal_block_set(context, *args, **kwargs):
    """Shows a modal to create a resource"""
    workflow = MeetingWorkflow.objects.get(id=context.get("w"))
    user = workflow.user
    resource_type = context.get("resource_type")
    if resource_type in user.crm_account.custom_objects:
        template = (
            OrgCustomSlackForm.objects.for_user(user).filter(custom_object=resource_type).first()
        )
    else:
        template = (
            OrgCustomSlackForm.objects.for_user(user)
            .filter(
                Q(resource=context.get("resource_type"), form_type=slack_const.FORM_TYPE_CREATE,)
            )
            .first()
        )
    if template:
        blocks = []
        type_text = "Note Type" if user.crm == "SALESFORCE" else "Meeting Outcome"
        resource = "Task" if user.crm == "SALESFORCE" else "Meeting"
        field = "Type" if user.crm == "SALESFORCE" else "hs_meeting_outcome"
        type_text = "Note Type" if user.crm == "SALESFORCE" else "Meeting Outcome"
        note_options = user.crm_account.get_individual_picklist_values(resource, field)
        note_options = note_options.values if user.crm == "SALESFORCE" else note_options.values()
        note_options_list = [
            block_builders.option(opt.get("label"), opt.get("value")) for opt in note_options
        ][:25]
        blocks.append(
            block_builders.static_select(
                type_text, options=note_options_list, block_id="managr_task_type"
            )
        )
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
        blocks.extend(form_blocks)
        stage_name = "StageName" if user.crm == "SALESFORCE" else "dealstage"
        try:
            index, block = block_finder(stage_name, blocks)
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
            "Duration (in minutes)",
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
        block_builders.multi_external_select(
            "*Add internal people to this meeting*",
            action_id=f"{slack_const.GET_LOCAL_RESOURCE_OPTIONS}?u={user.id}&resource_type={slack_const.SLACK_ACTION_RESOURCE_USER}",
            block_id="meeting_internals",
            placeholder="Search Users",
        ),
        block_builders.input_block(
            "Extra Emails to add:",
            placeholder="Separate emails with a comma",
            block_id="meeting_extras",
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
        block_builders.context_block("Only Managr users will show up here*"),
        SObjectField.objects.get(pk="fae88a10-53cc-470e-86ec-32376c041893").to_slack_field(
            user=user
        ),
        block_builders.context_block("Only Managr users will show up here*"),
    ]
    return blocks


@block_set(required_context=["u"])
def convert_meeting_lead_block_set(context):
    user = User.objects.get(id=context.get("u"))
    user_option = user.as_slack_option
    status = SObjectField.objects.filter(Q(salesforce_object="Lead") & Q(api_name="Status")).first()
    if status:
        status_options = status.to_slack_field()
    blocks = [
        block_builders.input_block(
            "Create New", block_id="Opportunity_NAME_INPUT", placeholder="New Opportunity Name"
        ),
        block_builders.actions_block(
            [
                block_builders.checkbox_input(
                    [
                        block_builders.checkbox_option(
                            "Choose existing Opportunity", "EXISTING_OPPORTUNITY",
                        )
                    ],
                    action_id=action_with_params(
                        slack_const.PROCESS_LEAD_INPUT_SWITCH,
                        params=[
                            f"u={context.get('u')}",
                            "input=Opportunity",
                            f"w={context.get('w')}",
                        ],
                    ),
                )
            ],
            "LEAD_CHECKBOX_OPPORTUNITY",
        ),
        block_builders.divider_block(),
        block_builders.simple_section(
            "Create new Account based off your Lead's company", block_id="Account_NAME_INPUT"
        ),
        block_builders.actions_block(
            [
                block_builders.checkbox_input(
                    [
                        block_builders.checkbox_option(
                            "Choose existing Account", "EXISTING_ACCOUNT",
                        )
                    ],
                    action_id=action_with_params(
                        slack_const.PROCESS_LEAD_INPUT_SWITCH,
                        params=[f"u={context.get('u')}", "input=Account", f"w={context.get('w')}"],
                    ),
                )
            ],
            "LEAD_CHECKBOX_ACCOUNT",
        ),
        block_builders.divider_block(),
        block_builders.simple_section(
            "Create new Contact based off your Lead information", block_id="Contact_NAME_INPUT"
        ),
        block_builders.actions_block(
            [
                block_builders.checkbox_input(
                    [
                        block_builders.checkbox_option(
                            "Choose existing Contact", "EXISTING_CONTACT",
                        )
                    ],
                    action_id=action_with_params(
                        slack_const.PROCESS_LEAD_INPUT_SWITCH,
                        params=[f"u={context.get('u')}", "input=Contact", f"w={context.get('w')}"],
                    ),
                )
            ],
            "LEAD_CHECKBOX_CONTACT",
        ),
        block_builders.divider_block(),
        status_options,
        block_builders.external_select(
            "Record Owner",
            action_with_params(
                slack_const.GET_LOCAL_RESOURCE_OPTIONS,
                params=[
                    f"u={context.get('u')}",
                    f"resource_type={slack_const.SLACK_ACTION_RESOURCE_USER}",
                ],
            ),
            block_id="RECORD_OWNER",
            initial_option=user_option,
        ),
    ]
    return blocks


@block_set(required_context=["u"])
def convert_lead_block_set(context):
    user = User.objects.get(id=context.get("u"))
    user_option = user.as_slack_option
    status = (
        ObjectField.objects.for_user(user)
        .filter(Q(crm_object="Lead") & Q(api_name="Status"))
        .first()
    )
    if status:
        converted_options = [
            option
            for option in status.crm_picklist_options.values
            if option["attributes"]["converted"]
        ]
        status_options = list(
            map(
                lambda option: block_builders.option(option["label"], option["value"]),
                converted_options,
            )
        )
        status_block = block_builders.static_select(
            f"*{status.reference_display_label}*",
            status_options,
            action_id=None,
            block_id=status.api_name,
        )
    blocks = [
        block_builders.input_block(
            "Create New", block_id="Opportunity_NAME_INPUT", placeholder="New Opportunity Name"
        ),
        block_builders.actions_block(
            [
                block_builders.checkbox_input(
                    [
                        block_builders.checkbox_option(
                            "Choose existing Opportunity", "EXISTING_OPPORTUNITY",
                        )
                    ],
                    action_id=action_with_params(
                        slack_const.PROCESS_LEAD_INPUT_SWITCH,
                        params=[
                            f"u={context.get('u')}",
                            "input=Opportunity",
                            f"resource_id={context.get('resource_id')}",
                        ],
                    ),
                )
            ],
            "LEAD_CHECKBOX_OPPORTUNITY",
        ),
        block_builders.divider_block(),
        block_builders.simple_section(
            "Create new Account based off your Lead's company", block_id="Account_NAME_INPUT"
        ),
        block_builders.actions_block(
            [
                block_builders.checkbox_input(
                    [
                        block_builders.checkbox_option(
                            "Choose existing Account", "EXISTING_ACCOUNT",
                        )
                    ],
                    action_id=action_with_params(
                        slack_const.PROCESS_LEAD_INPUT_SWITCH,
                        params=[
                            f"u={context.get('u')}",
                            "input=Account",
                            f"resource_id={context.get('resource_id')}",
                        ],
                    ),
                )
            ],
            "LEAD_CHECKBOX_ACCOUNT",
        ),
        block_builders.divider_block(),
        block_builders.simple_section(
            "Create new Contact based off your Lead information", block_id="Contact_NAME_INPUT"
        ),
        block_builders.actions_block(
            [
                block_builders.checkbox_input(
                    [
                        block_builders.checkbox_option(
                            "Choose existing Contact", "EXISTING_CONTACT",
                        )
                    ],
                    action_id=action_with_params(
                        slack_const.PROCESS_LEAD_INPUT_SWITCH,
                        params=[
                            f"u={context.get('u')}",
                            "input=Contact",
                            f"resource_id={context.get('resource_id')}",
                        ],
                    ),
                )
            ],
            "LEAD_CHECKBOX_CONTACT",
        ),
        block_builders.divider_block(),
        status_block,
        block_builders.external_select(
            "Record Owner",
            action_with_params(
                slack_const.GET_LOCAL_RESOURCE_OPTIONS,
                params=[
                    f"u={context.get('u')}",
                    f"resource_type={slack_const.SLACK_ACTION_RESOURCE_USER}",
                ],
            ),
            block_id="RECORD_OWNER",
            initial_option=user_option,
        ),
    ]
    return blocks


@block_set(required_context=["u"])
def paginated_meeting_blockset(context):
    u = User.objects.get(id=context.get("u"))
    date = context.get("date", None)
    user_timezone = u.timezone
    if date:
        todays_date = datetime.strptime(date, "%Y-%m-%d")
    else:
        todays_date = datetime.today()
    workflows = MeetingWorkflow.objects.for_user(u, str(todays_date.date()))
    date_string = (
        f":calendar: Today's Meetings: *{todays_date.month}/{todays_date.day}/{todays_date.year}*"
    )
    blocks = [
        block_builders.section_with_button_block(
            "Sync Calendar",
            "sync_calendar",
            date_string,
            action_id=action_with_params(
                slack_const.MEETING_REVIEW_SYNC_CALENDAR,
                [f"u={str(u.id)}", f"date={str(todays_date.date())}"],
            ),
        ),
        {"type": "divider"},
    ]
    for workflow in workflows:
        meeting = workflow.meeting
        title = meeting.topic
        start_time = meeting.start_time
        end_time = meeting.end_time
        formatted_start = (
            datetime.strftime(start_time.astimezone(pytz.timezone(user_timezone)), "%I:%M %p")
            if start_time
            else start_time
        )
        formatted_end = (
            datetime.strftime(end_time.astimezone(pytz.timezone(user_timezone)), "%I:%M %p")
            if end_time
            else end_time
        )
        section_text = f"*{title}*\n{formatted_start} - {formatted_end}"
        if len(workflow.failed_task_description):
            message = ""
            for i, m in enumerate(workflow.failed_task_description):
                m_split = m.split(".")
                if i == len(workflow.failed_task_description) - 1:
                    message += f"{m_split[0]}"
                else:
                    message += f"{m_split[0]},"
            block = block_builders.section_with_button_block(
                "Return to Form",
                "RETURN_TO_FORM",
                section_text=f":no_entry_sign: Uh-oh we hit a validation:\n{message}\n{title}",
                block_id=str(workflow.id),
                action_id=action_with_params(
                    slack_const.ZOOM_MEETING__INIT_REVIEW,
                    params=[f"u={str(workflow.user.id)}", f"w={str(workflow.id)}", "type=meeting",],
                ),
            )
        elif len(workflow.operations) and workflow.progress < 100:
            crm = "Salesforce" if u.crm == "SALESFORCE" else "HubSpot"
            block = block_builders.simple_section(
                f":rocket: Sending data to {crm}...\n{title}", "mrkdwn"
            )
        elif workflow.progress == 100:
            section_text = f":white_check_mark: *Meeting Logged*\n{title}"
            form_ids = [str(id) for id in list(workflow.forms.all().values_list("id", flat=True))]
            block = block_builders.section_with_button_block(
                "Use Generative AI",
                "GENERATIVE ACTION",
                section_text=section_text,
                block_id=str(workflow.id),
                action_id=action_with_params(
                    slack_const.OPEN_GENERATIVE_ACTION_MODAL,
                    params=[
                        f"u={str(workflow.user.id)}",
                        f"form_ids={'.'.join(form_ids)}",
                        "type=meeting",
                        f"workflow_id={str(workflow.id)}",
                    ],
                ),
            )

        else:
            action_id = (
                f"{slack_const.MEETING_ATTACH_RESOURCE_MODAL}?w={str(workflow.id)}&u={str(u.id)}"
            )
            block = block_builders.section_with_button_block(
                "Log Meeting",
                "log_meeting",
                section_text=section_text,
                block_id=str(workflow.id),
                style="primary",
                action_id=action_id,
            )
        blocks.append(block)
    return blocks
