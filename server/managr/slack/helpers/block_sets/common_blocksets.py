import pdb
from urllib.parse import urlencode
import pytz
import uuid
import logging
import json
from django.conf import settings
from datetime import datetime

from django.db.models import Q
from managr.utils.sites import get_site_url
from managr.core.models import User
from managr.organization.models import OpportunityLineItem
from managr.slack import constants as slack_const
from managr.slack.helpers.utils import action_with_params, block_set
from managr.slack.helpers import block_builders
from managr.slack.helpers import requests as slack_requests
from managr.slack.models import OrgCustomSlackForm, OrgCustomSlackFormInstance
from managr.core.models import User

from managr.crm.exceptions import (
    TokenExpired,
    InvalidRefreshToken,
)

logger = logging.getLogger("managr")


@block_set()
def loading_block_set(context):
    message = context.get("message", "Saving Data")
    fill = context.get("fill", False)
    if fill:
        blocks = [
            block_builders.simple_section(f"{message}", "mrkdwn"),
            block_builders.simple_image_block(
                "https://managr-images.s3.amazonaws.com/slack/new_logo_loading.gif", "Loading..."
            ),
        ]
    else:
        blocks = [
            block_builders.section_with_accessory_block(
                f"*{message}*",
                block_builders.simple_image_block(
                    "https://managr-images.s3.amazonaws.com/slack/new_logo_loading.gif",
                    "Loading...",
                ),
            )
        ]
    return blocks


@block_set()
def direct_to_block_set(context):
    slack_context = context.get("slack")
    blocks = [
        block_builders.simple_section(f"{context.get('title')}", "mrkdwn"),
        block_builders.actions_block(
            [
                block_builders.simple_button_block(
                    "Log Meeting", "complete_in_slack", action_id=slack_context, style="primary"
                ),
            ]
        ),
    ]
    return blocks


@block_set()
def success_modal_block_set(context):
    message = context.get("message", ":white_check_mark: Success!")
    user = context.get("u")
    form_ids = context.get("form_ids")
    blocks = [
        block_builders.section_with_button_block(
            "Generate Content",
            "GENERATIVE ACTION",
            section_text=message,
            action_id=action_with_params(
                slack_const.OPEN_GENERATIVE_ACTION_MODAL,
                params=[
                    f"u={user}",
                    f"form_ids={form_ids}",
                    "type=command",
                ],
            ),
        )
    ]
    return blocks


@block_set()
def bulk_recap_block_set(context):
    message = context.get("message", ":white_check_mark: Success!")
    user = context.get("u")
    form_ids = context.get("form_ids")
    blocks = [
        block_builders.section_with_button_block(
            "Send Recap",
            "SEND_RECAP",
            message,
            action_id=action_with_params(
                slack_const.PROCESS_SEND_RECAP_MODAL,
                params=[
                    f"u={user}",
                    f"form_ids={form_ids}",
                    f"bulk_status={context.get('bulk_status')}",
                ],
            ),
        )
    ]
    return blocks


@block_set()
def success_text_block_set(context):
    message = context.get("message", ":clap: Success!")
    blocks = [block_builders.simple_section(message, text_type="mrkdwn")]
    return blocks


@block_set()
def error_modal_block_set(context):
    message = context.get("message", ":no_entry: Ugh-Ohhhh.. We've hit a snag!")
    show_image = context.get("show_image", True)
    blocks = [block_builders.simple_section(message, "mrkdwn")]
    return blocks


@block_set()
def error_message_block_set(context):
    message = context.get("message", ":no_entry: Ugh-Ohhhh.. We've hit a snag!")
    return [block_builders.simple_section(message, "mrkdwn")]


@block_set()
def onboarding_interaction_block_set(context):
    user_id = context.get("u")
    user = User.objects.filter(id=user_id).first()
    slack = user.slack_integration
    blocks = [
        block_builders.simple_section(
            (
                f"Welcome <@{slack.slack_id}> I’m the ManagrAI bot designed to help you automate your pipeline management process so you can focus on selling :clap:\n"
                "*I can help you:*\n"
                "- Put your pipeline on autopilot :raised_hands:\n"
                "- Update SFDC in seconds, adding meeting attendees as Contacts :file_cabinet:\n"
                "- Steamline SDR handoffs :moneybag:\n"
                "- Facilitate deal review and internal communication:busts_in_silhouette:"
            ),
            "mrkdwn",
        ),
    ]
    return blocks


@block_set()
def tasks_list_block_set(context={}):
    def to_date_string(date):
        if not date:
            return "n/a"
        d = datetime.strptime(date, "%Y-%m-%d")
        return d.strftime("%a, %B %d, %Y")

    user_id = context.get("u")
    user = User.objects.get(id=user_id)
    tasks = []
    task_blocks = []
    has_error = False
    if not user.has_salesforce_integration:
        return [block_builders.simple_section("Salesforce not integrated")]
    attempts = 1
    while True:
        ## TODO this is repetitive we need to get the new sf info after update maybe move this to the bottom within the except
        sf = user.salesforce_account
        try:
            tasks = sf.adapter_class.list_tasks()
            break

        except TokenExpired:
            if attempts >= 5:
                logger.exception(f"Failed to gather tasks after 5 tries")
                has_error = True
                break
            else:
                try:
                    sf.regenerate_token()
                except InvalidRefreshToken:
                    logger.exception(f"Failed to refresh token due to an invalid refresh token")
                    has_error = True
                    break

                attempts += 1
    if has_error:
        return [block_builders.simple_section("There was a problem with your salesforce account")]

    if not len(tasks):
        return [
            block_builders.simple_section(":clap: You have no incomplete tasks today.", "mrkdwn")
        ]

    task_blocks.extend(
        [
            block_builders.simple_section(f"You have *{len(tasks)}* upcoming tasks", "mrkdwn"),
            block_builders.divider_block(),
        ]
    )
    for t in tasks:
        resource = "_salesforce object n/a_"
        # get the resource if it is what_id is for account/opp
        # get the resource if it is who_id is for lead
        resource_type = None
        if t.what_id:
            # first check for opp
            obj = user.imported_opportunity.filter(integration_id=t.what_id).first()
            resource_type = "Opportunity"
            if not obj:
                obj = user.imported_account.filter(integration_id=t.what_id).first()
                resource_type = "Account"
            if obj:
                resource = f"*{obj.name}*"

        elif t.who_id:
            obj = user.imported_lead.filter(integration_id=t.who_id).first()
            if obj:
                resource = f"*{obj.name}*"
        task_blocks.extend(
            [
                block_builders.simple_section(
                    f"{resource}, due _*{to_date_string(t.activity_date)}*_, {t.subject} `{t.status}`",
                    "mrkdwn",
                ),
                block_builders.section_with_button_block(
                    "View Task",
                    "view_task",
                    "_View task in salesforce_",
                    url=f"{user.salesforce_account.instance_url}/lightning/r/Task/{t.id}/view",
                ),
                block_builders.divider_block(),
            ]
        )
    return task_blocks


@block_set()
def home_modal_block_set(context):
    user_id = context.get("u")
    user = User.objects.filter(id=user_id).first()
    slack = user.slack_integration
    integration_blocks = [
        block_builders.simple_section(
            f"{':white_check_mark:' if user.has_slack_integration else ':x:'} *<{get_site_url()}/chat|Slack>* is used to interact with you regarding your sales process",
            text_type="mrkdwn",
        ),
        block_builders.simple_section(
            f"{':white_check_mark:' if user.has_zoom_integration else ':x:'} *<{get_site_url()}/chat|Zoom>* is used to track your meetings to notify you so you can take action",
            text_type="mrkdwn",
        ),
        block_builders.simple_section(
            f"{':white_check_mark:' if user.has_salesforce_integration else ':x:'} *<{get_site_url()}/chat|Salesforce>* is the backbone of your integration we use this to keep track of your sales process",
            text_type="mrkdwn",
        ),
        block_builders.simple_section(
            f"{':white_check_mark:' if user.has_nylas_integration else ':x:'} *<{get_site_url()}/chat|Calendar>* will help us gather additional metadata about your meetings",
            text_type="mrkdwn",
        ),
    ]

    blocks = [
        block_builders.header_block("Welcome To Managr"),
        block_builders.divider_block(),
        block_builders.simple_section("*Integrations*", "mrkdwn"),
        *integration_blocks,
        block_builders.divider_block(),
        block_builders.simple_section("*Today's Tasks*", "mrkdwn"),
        *tasks_list_block_set(context),
        block_builders.divider_block(),
        block_builders.simple_section("*Alerts*", "mrkdwn"),
        block_builders.divider_block(),
    ]
    view = {"type": "home", "blocks": blocks}
    return view


@block_set()
def hour_options(context):
    hours = list(range(1, 13))
    blocks = [block_builders.option(str(val), str(val)) for val in hours]
    return blocks


@block_set()
def minute_options(context):
    minutes = list(range(0, 56, 5))
    blocks = []
    for minute in minutes:
        minute = str(minute)
        if len(minute) < 2:
            minute = "0" + minute
        blocks.append(block_builders.option(minute, minute))
    return blocks


@block_set()
def time_options(context):
    time = ["AM", "PM"]
    blocks = [block_builders.option(val, val) for val in time]
    return blocks


@block_set()
def duration_options(context):
    times = list(range(0, 56, 5))
    blocks = []
    for time in times:
        time = str(time)
        if len(time) < 2:
            time = "0" + time
        blocks.append(block_builders.option(time, time))
    return blocks


@block_set()
def zoom_recording_blockset(context):
    url = context["url"]
    topic = context["topic"]
    blocks = [
        block_builders.section_with_button_block(
            "Download Recording",
            "download_recording",
            f"Your recording of {topic} is ready to share",
            url=url,
        ),
        block_builders.context_block("*Download link will expire after 24 hours"),
    ]
    return blocks


@block_set()
def zoom_fake_recording(context):
    url = context["url"]
    topic = context["topic"]
    blocks = [
        block_builders.section_with_button_block(
            "Download Recording",
            "download_recording",
            f"Your recording of {topic} is ready to share",
            url=url,
        ),
        block_builders.context_block("*Download link will expire after 24 hours"),
    ]
    return blocks


@block_set()
def workflow_reminder_block_set(context):
    workflow_count = context.get("workflow_count")
    text = "workflow" if workflow_count < 2 else "workflows"
    blocks = [
        block_builders.simple_section(
            f"We noticed you only have {workflow_count} {text} activated. Activate some more to boost your productivity!"
        )
    ]
    return blocks


@block_set()
def meeting_reminder_block_set(context):
    user = User.objects.get(id=context.get("u"))
    not_completed = context.get("not_completed")
    text = "meeting" if not_completed == 1 else "meetings"
    if user.slack_integration.zoom_channel:
        channel_info = slack_requests.get_channel_info(
            user.organization.slack_integration.access_token, user.slack_integration.zoom_channel
        )
        name = channel_info.get("channel").get("name")
        message_text = (
            f":wave: You have {not_completed} un-logged {text}. Please log them here #{name}"
        )
    else:
        message_text = f":wave: You have {not_completed} un-logged {text}. Please log them."
    blocks = [
        block_builders.simple_section(
            message_text,
            "mrkdwn",
        )
    ]
    return blocks


@block_set()
def message_meeting_block_set():
    message = "this is a test"
    blocks = [
        block_builders.simple_section(
            f"This is a {message}",
            "mrkdwn",
        )
    ]
    return blocks


@block_set()
def manager_meeting_reminder_block_set(context):
    not_completed = context.get("not_completed")
    name = context.get("name")
    text = "meeting" if not_completed < 2 else "meetings"
    blocks = [
        block_builders.simple_section(
            f"{not_completed} {text} left to complete",
            "mrkdwn",
        )
    ]
    return blocks


def current_product_block_set(context):
    opp_item_id = context.get("opp_item_id")
    data = context.get("product_data")
    text = f"{data['name']}\nQuantity: {data['quantity']}\nTotal Price: {round(data['total'],2)}"
    blocks = block_builders.section_with_button_block(
        "Edit Product",
        "EDIT_PRODUCT",
        text,
        action_id=action_with_params(
            slack_const.PROCESS_SHOW_EDIT_PRODUCT_FORM,
            params=[
                f"opp_item_id={opp_item_id}",
                f"main_form={context.get('main_form')}",
                f"u={context.get('u')}",
            ],
        ),
    )
    return blocks


@block_set()
def edit_product_block_set(context):
    opp_item = OpportunityLineItem.objects.get(integration_id=context.get("opp_item_id"))
    user = User.objects.get(id=context.get("u"))
    template = (
        OrgCustomSlackForm.objects.for_user(user)
        .filter(Q(resource="OpportunityLineItem", form_type="UPDATE"))
        .first()
    )
    slack_form = OrgCustomSlackFormInstance.objects.create(
        template=template, resource_id=str(opp_item.id), user=user
    )
    form_blocks = slack_form.generate_form()
    return [*form_blocks]


@block_set()
def initial_alert_message(context):
    title = context.get("title")
    invocation = context.get("invocation")
    channel = context.get("channel")
    config_id = context.get("config_id")
    u = context.get("user")
    user = User.objects.get(id=u)
    if settings.IN_DEV:
        url = "http://localhost:8080/pipelines"
    elif settings.IN_STAGING:
        url = "https://staging.managr.ai/pipelines"
    else:
        url = "https://app.managr.ai/pipelines"
    blocks = [
        block_builders.simple_section(title, "mrkdwn"),
        block_builders.actions_block(
            [
                block_builders.simple_button_block(
                    f"Update {'Fields' if user.crm == 'SALESFORCE' else 'Properties'}",
                    "switch_inline",
                    action_id=action_with_params(
                        slack_const.PROCESS_SWITCH_ALERT_MESSAGE,
                        params=[
                            f"invocation={invocation}",
                            f"config_id={config_id}",
                            f"u={u}",
                            f"switch_to={'inline'}",
                        ],
                    ),
                    style="primary",
                ),
                block_builders.simple_button_block(
                    "Run Deal Review",
                    "deal_review",
                    action_id=action_with_params(
                        slack_const.PROCESS_SWITCH_TO_DEAL_REVIEW,
                        params=[
                            f"invocation={invocation}",
                            f"channel={channel}",
                            f"u={u}",
                            f"config_id={config_id}",
                        ],
                    ),
                ),
                block_builders.simple_button_block(
                    "See Details",
                    "access_apps",
                    action_id=action_with_params(
                        slack_const.PROCESS_SWITCH_ALERT_MESSAGE,
                        params=[
                            f"invocation={invocation}",
                            f"channel={channel}",
                            f"u={u}",
                            f"config_id={config_id}",
                            f"switch_to={'message'}",
                        ],
                    ),
                ),
            ]
        ),
    ]
    return blocks


@block_set()
def resource_action_blockset(context):
    user = User.objects.get(id=context.get("u"))
    resource_type = context.get("resource_type")
    options = []
    if user.has_zoom_integration:
        options.append(block_builders.option("Log Meeting", "LOG_MEETING"))
    options.extend(
        [
            block_builders.option(f"Update {resource_type}", "UPDATE_FORM"),
            block_builders.option("Add Notes", "ADD_NOTES"),
            block_builders.option("Ask Managr", "ASK_MANAGR"),
            block_builders.option(f"{resource_type} Review", "REVIEW"),
        ]
    )
    if not settings.IN_PROD:
        options.append(block_builders.option("News Summary", "NEWS_SUMMARY"))

    blocks = [
        block_builders.static_select(
            "What would you like to do?",
            options,
            action_id=action_with_params(
                slack_const.PROCESS_RESOURCE_SELECTED_ACTION, params=[f"u={str(user.id)}"]
            ),
        ),
    ]
    return blocks


@block_set()
def use_transcript_message(context):
    transcript_option = context.pop("transcript_option", "Yes")
    meeting_date = context.get("meeting_date", str(datetime.today().date()))
    blocks = [
        block_builders.datepicker(
            meeting_date,
            action_id=action_with_params(
                slack_const.CHOOSE_MEETING_OPTIONS, [f"u={context.get('u')}"]
            ),
            block_id="MEETING_DATE",
            label="Meeting date",
        ),
        block_builders.external_select(
            "Select your meeting",
            action_id=action_with_params(
                slack_const.PROCESS_GET_MEETING_OPTIONS,
                [f"u={context.get('u')}", f"meeting_date={meeting_date}"],
            ),
            block_id="MEETING_OPTIONS",
        ),
        block_builders.static_select(
            "Use AI to summarize & autofill CRM?",
            [block_builders.option("Yes", "YES"), block_builders.option("No", "NO")],
            initial_option=block_builders.option(transcript_option, transcript_option.upper()),
            block_id="YES_NO",
        ),
    ]
    return blocks


def update_form_blockset(context):
    from managr.slack.helpers.utils import block_finder

    user = User.objects.get(id=context.get("u"))
    resource_id = context.get("resource_id")
    resource_type = context.get("resource_type")
    template = user.team.team_forms.all().filter(form_type="UPDATE", resource=resource_type).first()
    form = OrgCustomSlackFormInstance.objects.create(
        template=template, user=user, resource_id=resource_id
    )
    blocks = form.generate_form()
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
            "accessory": {
                **block["accessory"],
                "action_id": f"{action_id}",
            },
        }
        blocks = [*blocks[:index], block, *blocks[index + 1 :]]

    return [*blocks]


def chat_prompt_blockset(context):
    from managr.core.models import NoteTemplate

    user = User.objects.get(id=context.get("u"))
    templates_query = NoteTemplate.objects.for_user(user)
    template_options = (
        [template.as_slack_option for template in templates_query]
        if len(templates_query)
        else [block_builders.option("You have no templates", "NONE")]
    )
    crm = "Salesforce" if user.crm == "SALESFORCE" else "HubSpot"
    blocks = [
        block_builders.input_block(
            f"Log Notes to CRM using conversation AI",
            block_id="CHAT_PROMPT",
            multiline=True,
            optional=False,
        ),
        block_builders.context_block("Powered by ChatGPT © :robot_face:"),
    ]
    return blocks
