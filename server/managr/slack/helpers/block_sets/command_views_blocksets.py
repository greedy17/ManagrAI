import json
from django.conf import settings
from urllib.parse import urlencode
from managr.utils.sites import get_site_url
from managr.salesforce.models import MeetingWorkflow
from managr.salesforce import constants as sf_consts
from managr.slack import constants as slack_const
from managr.slack.helpers.utils import (
    action_with_params,
    block_set,
)
from managr.slack.helpers import block_builders, block_sets
from managr.slack.models import OrgCustomSlackFormInstance
from managr.alerts.models import AlertInstance
from managr.salesforce.routes import routes as sf_routes
from managr.hubspot.routes import routes as hs_routes
from managr.core.models import User

CRM_SWITCHER = {"SALESFORCE": sf_routes, "HUBSPOT": hs_routes}


def resource_options(crm):
    if crm == "SALESFORCE":
        return [
            block_builders.option("Opportunity", "Opportunity"),
            block_builders.option("Account", "Account"),
            block_builders.option("Lead", "Lead"),
            block_builders.option("Contact", "Contact"),
        ]
    else:
        return [
            block_builders.option("Deal", "Deal"),
            block_builders.option("Company", "Company"),
            block_builders.option("Contact", "Contact"),
        ]


@block_set(required_context=["resource_type", "u"])
def command_update_resource_interaction(context):
    # form = OrgCustomSlackFormInstances.objects.get(id=context.get("f"))
    user = User.objects.get(id=context.get("u"))
    return [
        block_builders.external_select(
            f"*Search for an {context.get('resource_type')}*",
            f"{slack_const.COMMAND_FORMS__GET_LOCAL_RESOURCE_OPTIONS}?u={str(user.id)}&resource_type={context.get('resource_type')}",
            block_id="select_existing",
            placeholder="Type to search",
        ),
    ]


@block_set(required_context=["u"])
def command_select_account_interaction(context):
    user = User.objects.get(id=context.get("u"))
    return [
        block_builders.external_select(
            f"*Search for an account*",
            f"{slack_const.GET_USER_ACCOUNTS}?u={str(user.id)}&type={context.get('type')}&system={context.get('system')}",
            block_id="select_existing",
            placeholder="Type to search",
        ),
    ]


@block_set(required_context=["u"])
def command_create_task_interaction(context):
    # form = OrgCustomSlackFormInstances.objects.get(id=context.get("f"))
    user = User.objects.get(id=context.get("u"))
    resource_type = context.get("resource_type")
    return [
        block_builders.section_with_button_block(
            "Create Task",
            "CREATE_A_TASK",
            "Create A New Task",
            action_id=action_with_params(
                slack_const.ZOOM_MEETING__CREATE_TASK,
                params=[f"u={str(user.id)}", f"resource_type={resource_type}"],
            ),
        )
    ]


@block_set(required_context=["resource_type", "u"])
def command_meeting_summary(context):
    # form = OrgCustomSlackFormInstances.objects.get(id=context.get("f"))
    user = User.objects.get(id=context.get("u"))
    return [
        block_builders.external_select(
            f"*Search for an {context.get('resource_type')}*",
            f"{slack_const.COMMAND_SUMMARY__GET_LOCAL_RESOURCE_OPTIONS}?u={str(user.id)}&resource_type={context.get('resource_type')}",
            block_id="select_existing",
            placeholder="Type to search",
        ),
    ]


def custom_paginator_block(
    pagination_object, invocation, channel, config_id, action_id=slack_const.PAGINATE_ALERTS
):
    next_page = pagination_object.get("next_page", None)
    prev_page = pagination_object.get("previous_page", None)
    blocks = []
    button_blocks = []
    page_context = {"invocation": invocation, "channel": channel, "config_id": config_id}

    if prev_page:
        prev_page_button = block_builders.simple_button_block(
            "Previous",
            str(prev_page),
            style="danger",
            action_id=f"{action_id}?{urlencode({**page_context,'new_page':int(prev_page)})}",
        )
        button_blocks.append(prev_page_button)
    if next_page:
        next_page_button = block_builders.simple_button_block(
            "Next",
            str(next_page),
            action_id=f"{action_id}?{urlencode({**page_context,'new_page':int(next_page)})}",
        )
        button_blocks.append(next_page_button)
    if len(button_blocks):
        blocks.append(block_builders.actions_block(button_blocks))

    blocks.append(block_builders.context_block(f"Showing {pagination_object.get('page')}"))
    return blocks


def custom_clips_paginator_block(
    pagination_object, user_id, action_id=slack_const.PROCESS_SEND_CLIPS
):
    next_page = pagination_object.get("next_page", None)
    prev_page = pagination_object.get("previous_page", None)
    blocks = []
    button_blocks = []
    page_context = {"u": user_id}

    if prev_page:
        prev_page_button = block_builders.simple_button_block(
            "Previous",
            str(prev_page),
            style="danger",
            action_id=f"{action_id}?{urlencode({**page_context,'new_page':int(prev_page)})}",
        )
        button_blocks.append(prev_page_button)
    if next_page:
        next_page_button = block_builders.simple_button_block(
            "Next",
            str(next_page),
            action_id=f"{action_id}?{urlencode({**page_context,'new_page':int(next_page)})}",
        )
        button_blocks.append(next_page_button)
    if len(button_blocks):
        blocks.append(block_builders.actions_block(button_blocks))

    blocks.append(block_builders.context_block(f"Showing {pagination_object.get('page')}"))
    return blocks


def custom_inline_paginator_block(pagination_object, invocation, config_id, api_name):
    next_page = pagination_object.get("next_page", None)
    prev_page = pagination_object.get("previous_page", None)
    blocks = []
    button_blocks = []
    page_context = {"invocation": invocation, "config_id": config_id, "api_name": api_name}

    if prev_page:
        prev_page_button = block_builders.simple_button_block(
            "Previous",
            str(prev_page),
            style="danger",
            action_id=f"{slack_const.PAGINATE_INLINE_ALERTS}?{urlencode({**page_context,'new_page':int(prev_page)})}",
        )
        button_blocks.append(prev_page_button)
    if next_page:
        next_page_button = block_builders.simple_button_block(
            "Save + Continue",
            str(next_page),
            action_id=f"{slack_const.PAGINATE_INLINE_ALERTS}?{urlencode({**page_context,'new_page':int(next_page)})}",
        )
        button_blocks.append(next_page_button)
    else:
        next_page_button = block_builders.simple_button_block(
            "Submit",
            str(next_page),
            action_id=f"{slack_const.PROCESS_SUBMIT_INLINE_ALERT_DATA}?{urlencode({**page_context})}",
            style="primary",
        )
        button_blocks.append(next_page_button)
    if len(button_blocks):
        blocks.append(block_builders.actions_block(button_blocks))

    blocks.append(block_builders.context_block(f"Showing {pagination_object.get('page')}"))
    return blocks


def custom_alert_app_paginator_block(pagination_object, invocation, config_id, app_value):
    next_page = pagination_object.get("next_page", None)
    prev_page = pagination_object.get("previous_page", None)
    blocks = []
    button_blocks = []
    page_context = {"invocation": invocation, "config_id": config_id, "app": app_value}

    if prev_page:
        prev_page_button = block_builders.simple_button_block(
            "Previous",
            str(prev_page),
            style="danger",
            action_id=f"{slack_const.PAGINATE_APP_ALERTS}?{urlencode({**page_context,'new_page':int(prev_page)})}",
        )
        button_blocks.append(prev_page_button)
    if next_page:
        next_page_button = block_builders.simple_button_block(
            "Next",
            str(next_page),
            action_id=f"{slack_const.PAGINATE_APP_ALERTS}?{urlencode({**page_context,'new_page':int(next_page)})}",
        )
        button_blocks.append(next_page_button)
    if len(button_blocks):
        blocks.append(block_builders.actions_block(button_blocks))

    blocks.append(block_builders.context_block(f"Showing {pagination_object.get('page')}"))
    return blocks


@block_set(required_context=["instance_id"])
def alert_instance_block_set(context):
    """
    Builds out the message based on the template the of the alert
    divider -
    message - alert template message
    divider
    update button
    """
    instance = AlertInstance.objects.get(id=context.get("instance_id"))
    user = instance.user
    config = instance.config
    resource_owner = instance.resource.owner
    in_channel = False
    if config and config.recipient_type == "SLACK_CHANNEL":
        in_channel = True
    if instance.form_instance.all().first() and instance.form_instance.all().first().is_submitted:
        form = OrgCustomSlackFormInstance.objects.get(
            id=instance.form_instance.all()
            .exclude(template__resource="OpportunityLineItem")
            .first()
            .id
        )
        message = f":white_check_mark: Successfully updated *{form.resource_type}* _{form.resource_object.name if form.resource_type not in ['Lead', 'Contact'] else form.resource_object.email}_"
        blocks = block_sets.get_block_set(
            "success_modal", {"u": str(user.id), "form_ids": str(form.id), "message": message,},
        )
    else:
        blocks = [
            block_builders.section_with_button_block(
                f"Update {instance.template.resource_type}",
                "update_crm",
                instance.render_text(),
                text_type="mrkdwn",
                block_id=f"{instance.id}_text",
                action_id=action_with_params(
                    slack_const.PROCESS_SHOW_ALERT_UPDATE_RESOURCE_FORM,
                    params=[
                        f"u={str(user.id)}",
                        f"alert_id={str(instance.id)}",
                        f"current_page={context.get('current_page',1)}",
                        f"resource_id={str(instance.resource_id)}",
                        f"resource_type={instance.template.resource_type}",
                    ],
                ),
            ),
        ]

    if in_channel or (user.id != resource_owner.id):
        blocks.append(
            block_builders.context_block(
                f"_This {instance.template.resource_type} is owned by_ *{resource_owner.full_name}*",
                "mrkdwn",
            ),
        )
    blocks.append(block_builders.divider_block())
    return blocks


@block_set(required_context=["u"])
def update_modal_block_set(context, *args, **kwargs):
    """Shows a modal to update a resource"""
    resource_type = context.get("resource_type", None)
    resource_id = context.get("resource_id", None)
    user_id = context.get("u")
    form_ids = context.get("f")
    type = context.get("type")
    main_form = None
    if form_ids:
        form_ids = form_ids.split(",")
    if form_ids and len(form_ids):
        main_form = OrgCustomSlackFormInstance.objects.filter(
            id__in=form_ids, template__form_type__in=["UPDATE", "CREATE"]
        ).first()
    user = User.objects.get(id=user_id)
    resource_opts = resource_options(user.crm)
    blocks = []
    blocks.append(
        block_builders.static_select(
            "Related to type",
            resource_opts,
            action_id=f"{slack_const.UPDATE_TASK_SELECTED_RESOURCE}?u={user_id}",
            block_id="managr_task_related_to_resource",
            initial_option=block_builders.option(resource_type, resource_type)
            if resource_type
            else None,
        )
    )
    if (not resource_id and resource_type) or (resource_id and resource_type):
        blocks.append(
            block_builders.external_select(
                f"*Search for an {context.get('resource_type')}*",
                f"{slack_const.GET_CRM_RESOURCE_OPTIONS}?u={user_id}&resource_type={resource_type}&type={type}",
                block_id="select_existing",
                placeholder="Type to search",
                initial_option=block_builders.option(resource_id, resource_id)
                if resource_id
                else None,
            ),
        )

    if main_form:
        slack_form = main_form
        form_blocks = slack_form.generate_form(slack_form.saved_data)
        if len(form_blocks):
            blocks = [*form_blocks]
        else:

            blocks = [
                block_builders.section_with_button_block(
                    "Forms",
                    "form",
                    f"Please add fields to your {context.get('resource')} update form",
                    url=f"{get_site_url()}/forms",
                    block_id=slack_const.NO_FORM_FIELDS,
                )
            ]
    return blocks


@block_set(required_context=["u", "w"])
def update_meeting_block_set(context, *args, **kwargs):
    """Shows a modal to update a resource"""
    resource_type = context.get("resource_type", None)
    resource_id = context.get("resource_id", None)
    user_id = context.get("u")
    user = User.objects.get(id=user_id)
    blocks = []
    resource_opts = resource_options(user.crm)
    if len(user.crm_account.custom_objects):
        custom_options = [
            block_builders.option(custom_obj, custom_obj)
            for custom_obj in user.crm_account.custom_objects
        ]
        resource_opts.extend(custom_options)
    blocks.append(
        block_builders.static_select(
            "Related to type",
            resource_opts,
            action_id=f"{slack_const.UPDATE_TASK_SELECTED_RESOURCE}?u={user_id}&w={context.get('w')}",
            block_id="managr_task_related_to_resource",
            initial_option=block_builders.option(resource_type, resource_type)
            if resource_type
            else None,
        )
    )
    if (not resource_id and resource_type) or (resource_id and resource_type):
        additional_opts = [
            {
                "label": f"NEW {resource_type} (create)",
                "value": f'CREATE_NEW.{context.get("resource")}',
            }
        ]

        blocks.append(
            block_builders.external_select(
                f"*Search for a {context.get('resource_type')}*",
                f"{slack_const.ZOOM_MEETING__SELECTED_RESOURCE_OPTION}?u={user_id}&resource_type={resource_type}&add_opts={json.dumps(additional_opts)}",
                block_id="select_existing",
                placeholder="Type to search",
                initial_option=block_builders.option(resource_id, resource_id)
                if resource_id
                else None,
            ),
        )
    return blocks


@block_set(required_context=["u"])
def create_modal_block_set(context, *args, **kwargs):
    """Shows a modal to create a resource"""
    resource_type = context.get("resource_type", None)

    user_id = context.get("u")
    form_id = context.get("f")
    user = User.objects.get(id=user_id)
    blocks = []
    if form_id:
        slack_form = OrgCustomSlackFormInstance.objects.get(id=form_id)
        form_blocks = slack_form.generate_form()
        if len(form_blocks):
            blocks = [*form_blocks]
            if len(user.crm_account.custom_objects) > 0:
                params = [
                    f"f={str(slack_form.id)}",
                    f"u={user_id}",
                    "type=command",
                ]
                custom_object_button = block_builders.simple_button_block(
                    "Add Custom Object",
                    "ADD_CUSTOM_OBJECT",
                    action_id=action_with_params(
                        slack_const.PROCESS_PICK_CUSTOM_OBJECT, params=params,
                    ),
                )
                blocks.append(block_builders.actions_block([custom_object_button]))
        else:

            blocks = [
                block_builders.section_with_button_block(
                    "Forms",
                    "form",
                    f"Please add fields to your {resource_type} create form",
                    url=f"{get_site_url()}/forms",
                )
            ]

    return blocks


@block_set(required_context=["u"])
def create_add_to_cadence_block_set(context):
    user_id = context.get("u")
    blocks = [
        block_builders.external_select(
            f"*Select Cadence:*",
            f"{slack_const.GET_CADENCE_OPTIONS}?u={user_id}",
            block_id="select_cadence",
            placeholder="Type to search",
        ),
    ]
    if context.get("resource_type", None) != "Contact":
        blocks.append(
            block_builders.multi_external_select(
                f"*Add Contacts from {context.get('resource_name')} to selected Cadence*:",
                f"{slack_const.GET_CONTACT_OPTIONS}?u={user_id}&resource_id={context.get('resource_id')}&resource_type={context.get('resource_type')}",
                block_id="select_people",
                placeholder="Type to search",
            ),
        )
    return blocks


@block_set(required_context=["u"])
def create_add_to_sequence_block_set(context):
    user_id = context.get("u")
    blocks = [
        block_builders.external_select(
            "*Select Sequence:*",
            f"{slack_const.GET_SEQUENCE_OPTIONS}?u={user_id}",
            block_id="select_sequence",
            placeholder="Type to search",
        ),
    ]
    if context.get("resource_type", None) != "Contact":
        blocks.append(
            block_builders.multi_external_select(
                f"*Add Contacts from {context.get('resource_name')} to selected Sequence*:",
                f"{slack_const.GET_CONTACT_OPTIONS}?u={user_id}&resource_id={context.get('resource_id')}&resource_type={context.get('resource_type')}",
                block_id="select_people",
                placeholder="Type to search",
            ),
        )
    return blocks


@block_set(required_context=["u"])
def choose_opportunity_block_set(context):
    user_id = context.get("u", None)
    type = context.get("type")
    blocks = [
        block_builders.external_select(
            "Which opportunity would you like your notes for?",
            f"{slack_const.GET_NOTES}?u={user_id}&resource_type={sf_consts.RESOURCE_SYNC_OPPORTUNITY}&type={type}",
            block_id="select_opp",
            placeholder="Type to search",
        )
    ]
    return blocks


@block_set(required_context=["u"])
def update_command_block_set(context):
    from managr.core.models import NoteTemplate

    user = User.objects.get(id=context.get("u"))
    user_id = context.get("u")
    update_label = (
        "Update Salesforce (Form)" if user.crm == "SALESFORCE" else "Update HubSpot (Form)"
    )
    crm = "Salesforce" if user.crm == "SALESFORCE" else "HubSpot"
    options = [
        block_builders.option(update_label, "UPDATE_RESOURCE"),
    ]
    templates_query = NoteTemplate.objects.for_user(user)
    template_options = (
        [template.as_slack_option for template in templates_query]
        if len(templates_query)
        else [block_builders.option("You have no templates", "NONE")]
    )
    for action in slack_const.MANAGR_ACTIONS:
        options.append(block_builders.option(action[1], action[0]))
    if user.crm == "SALESFORCE":
        for action in slack_const.SALESFORCE_ACTIONS:
            options.append(block_builders.option(action[1], action[0]))
    if hasattr(user, "outreach_account"):
        options.append(block_builders.option("Add To Sequence", "ADD_SEQUENCE"))
    if hasattr(user, "salesloft_account"):
        options.append(block_builders.option("Add To Cadence", "ADD_CADENCE"))
    if hasattr(user, "gong_account"):
        options.append(block_builders.option("Call Recording", "CALL_RECORDING"))
    if not settings.IN_PROD:
        options.append(block_builders.option("News Summary", "NEWS_SUMMARY"))
        options.append(block_builders.option("Reset Meetings", "RESET_MEETINGS"))
    blocks = [
        block_builders.input_block(
            f"Update {crm} using conversational AI",
            placeholder=f"Update {'Opportunity' if user.crm == 'SALESFORCE' else 'Deal'} Pied Piper...",
            block_id="CHAT_PROMPT",
            multiline=True,
            optional=False,
        ),
        block_builders.context_block("Powered by ChatGPT © :robot_face:"),
        block_builders.static_select(
            "Select Template",
            template_options,
            f"{slack_const.PROCESS_INSERT_CHAT_TEMPLATE}?u={user_id}",
            block_id="SELECT_TEMPLATE",
        ),
        {"type": "divider"},
        block_builders.static_select(
            "Other options",
            options,
            f"{slack_const.COMMAND_MANAGR_ACTION}?u={user_id}",
            block_id="select_action",
            placeholder="Type to search",
        ),
    ]
    return blocks


@block_set(required_context=["u"])
def actions_block_set(context):
    user_id = context.get("u")
    action_options = [
        block_builders.option("Get Summary", "GET_SUMMARY"),
        block_builders.option("Deal Review", "DEAL_REVIEW"),
        block_builders.option("Call Summary", "CALL_SUMMARY"),
        block_builders.option("Call Analysis", "CALL_ANALYSIS"),
        block_builders.option("Ask Managr", "ASK_MANAGR"),
    ]
    blocks = [
        block_builders.input_block(
            f"Take action using conversational AI",
            placeholder=f"Type or select an action template",
            block_id="CHAT_PROMPT",
            multiline=True,
            optional=False,
        ),
        block_builders.context_block("Powered by ChatGPT © :robot_face:"),
        block_builders.static_select(
            "Prompt Templates",
            action_options,
            f"{slack_const.PROCESS_INSERT_ACTION_TEMPLATE}?u={user_id}",
            block_id="SELECT_TEMPLATE",
        ),
    ]
    return blocks


@block_set(required_context=["u"])
def command_select_resource_interaction(context):
    user = User.objects.get(id=context.get("u"))
    return [
        block_builders.external_select(
            f"*Search for an account*",
            f"{slack_const.GET_USER_ACCOUNTS}?u={str(user.id)}&type={context.get('type')}&system={context.get('system')}",
            block_id="select_existing",
            placeholder="Type to search",
        ),
    ]


@block_set(required_context=["u"])
def pick_resource_modal_block_set(context, *args, **kwargs):
    """Shows a modal to update a resource"""
    user_id = context.get("u")
    user = User.objects.get(id=user_id)
    default_resource = "Opportunity" if user.crm == "SALESFORCE" else "Deal"
    resource_type = context.get("resource_type", default_resource)
    resource_id = context.get("resource_id", None)
    options = [
        block_builders.option(resource, resource.capitalize())
        for resource in context.get("options").split("%")
    ]
    blocks = []
    blocks.append(
        block_builders.static_select(
            "Related to type",
            options,
            action_id=f"{slack_const.PROCESS_SELECT_RESOURCE}?u={user_id}&options={context.get('options')}&action_id={context.get('action_id')}",
            block_id="selected_object_type",
            initial_option=block_builders.option(resource_type, resource_type)
            if resource_type
            else None,
        )
    )
    if (not resource_id and resource_type) or (resource_id and resource_type):
        blocks.append(
            block_builders.external_select(
                f"*Search for an {resource_type}*",
                action_id=f"{context.get('action_id')}?u={user_id}&resource_type={resource_type}",
                block_id="selected_object",
                placeholder="Type to search",
                initial_option=block_builders.option(resource_id, resource_id)
                if resource_id
                else None,
            ),
        )
    return blocks


@block_set()
def ask_managr_blockset(context, *args, **kwargs):
    """Shows a modal to update a resource"""
    blocks = [
        block_builders.input_block(
            "Type your request here",
            placeholder=f"What's the next steps?",
            block_id="CHAT_PROMPT",
            multiline=True,
            optional=False,
        ),
    ]
    return blocks


@block_set(required_context=["u"])
def initial_inline_blockset(context, *args, **kwargs):
    switch_to = context.get("switch_to")
    user = User.objects.get(id=context.get("u"))
    invocation = context.get("invocation")
    config_id = context.get("config_id")
    field_name = "Properties" if user.crm == "HUBSPOT" else "Fields"
    action_blocks = [
        block_builders.simple_button_block(
            f"Switch to {'See Details' if switch_to == 'message' else f'Update {field_name}'}",
            "switch_inline",
            action_id=action_with_params(
                slack_const.PROCESS_SWITCH_ALERT_MESSAGE,
                params=[
                    f"invocation={invocation}",
                    f"config_id={config_id}",
                    f"u={str(user.id)}",
                    f"switch_to={'message' if switch_to == 'message' else 'inline'}",
                    f"channel={context.get('channel')}",
                ],
            ),
        ),
        block_builders.simple_button_block(
            "Run Deal Review",
            "deal_review",
            action_id=action_with_params(
                slack_const.PROCESS_SWITCH_TO_DEAL_REVIEW,
                params=[
                    f"invocation={invocation}",
                    f"channel={context.get('channel')}",
                    f"u={str(user.id)}",
                    f"config_id={config_id}",
                ],
            ),
        ),
        block_builders.simple_button_block(
            "Update in Bulk",
            "bulk_update",
            action_id=action_with_params(
                slack_const.PROCESS_BULK_UPDATE,
                params=[f"invocation={invocation}", f"config_id={config_id}", f"u={str(user.id)}",],
            ),
        ),
    ]
    return block_builders.actions_block(action_blocks)


@block_set(required_context=["u"])
def reset_meeting_block_set(context, *args, **kwargs):
    import datetime
    from managr.salesforce.models import MeetingWorkflow

    meeting_day = context.get("meeting_day", None)
    user_id = context.get("u")
    user = User.objects.get(id=user_id)
    meetings = (
        MeetingWorkflow.objects.filter(user=user)
        .order_by("-datetime_created")
        .values_list("datetime_created", flat=True)
    )[:50]
    meetings = list(set([datetime.datetime.strftime(date, "%Y-%m-%d") for date in meetings]))
    meeting_options = [block_builders.option(meeting, meeting) for meeting in meetings]
    blocks = []
    blocks.append(
        block_builders.static_select(
            "Select which date you would like to reset from (date is in year-month-day format)",
            meeting_options,
            action_id=f"{slack_const.CHOOSE_RESET_MEETING_DAY}?u={user_id}",
            block_id="selected_day",
        )
    )
    if meeting_day:
        meeting_for_date = list(MeetingWorkflow.objects.for_user(user, date=meeting_day))
        meeting_options_for_date = [
            block_builders.option(meeting.meeting.topic, str(meeting.id))
            for meeting in meeting_for_date
        ]
        blocks.append(
            block_builders.multi_static_select(
                "Select which meeting to reset",
                meeting_options_for_date,
                block_id="selected_meetings",
            ),
        )
    return blocks

@block_set()
def news_summary_blockset(context):
    blocks = [
        block_builders.input_block(
            "Enter your new search", optional=False, block_id="SEARCH", multiline=True
        ),
        block_builders.input_block(
            "What would you like included in your summary?",
            block_id="OUTPUT_INSTRUCTIONS",
            multiline=True,
        ),
        block_builders.actions_block(
            [
                block_builders.simple_button_block(
                    "Use a template",
                    "USE_TEMPLATE",
                    action_id=slack_const.ADD_NEWS_SUMMARY_TEMPLATE,
                )
            ],
            block_id="USE_TEMPLATE_BLOCK",
        ),
    ]
    return blocks