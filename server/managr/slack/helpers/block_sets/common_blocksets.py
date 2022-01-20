import pdb
from urllib.parse import urlencode
import pytz
import uuid
import logging
import json

from datetime import datetime

from django.db.models import Q
from rest_framework.decorators import action

from managr.utils.sites import get_site_url
from managr.core.models import User, Notification
from managr.opportunity.models import Opportunity, Lead
from managr.organization.models import Account, OpportunityLineItem
from managr.zoom.models import ZoomMeeting
from managr.salesforce.models import MeetingWorkflow
from managr.salesforce import constants as sf_consts
from managr.slack import constants as slack_const
from managr.slack.helpers.utils import action_with_params, block_set, map_fields_to_type
from managr.slack.helpers import block_builders
from managr.slack.helpers import requests as slack_requests
from managr.utils.misc import snake_to_space
from managr.salesforce.routes import routes as form_routes
from managr.slack.models import OrgCustomSlackForm, OrgCustomSlackFormInstance
from managr.gong.models import GongCall
from managr.core.models import NylasAuthAccount, User

from managr.salesforce.adapter.exceptions import (
    TokenExpired,
    FieldValidationError,
    RequiredFieldError,
    SFQueryOffsetError,
    SFNotFoundError,
    InvalidRefreshToken,
)
from managr.core.models import MeetingPrepInstance
from managr.slack.helpers.block_sets.meeting_review_block_sets import schedule_zoom_meeting_modal
from managr.slack.helpers.block_sets.command_views_blocksets import (
    create_modal_block_set,
    command_create_task_interaction,
    create_add_to_cadence_block_set,
    choose_opportunity_block_set,
)

logger = logging.getLogger("managr")


@block_set()
def loading_block_set(context):
    message = context.get("message", "Saving Data")
    fill = context.get("fill", False)
    if fill:
        blocks = [
            block_builders.simple_section(f"*{message}*", "mrkdwn"),
            block_builders.simple_image_block(
                "https://managr-images.s3.amazonaws.com/slack/logo_loading.gif", "Loading..."
            ),
        ]
    else:
        blocks = [
            block_builders.section_with_accessory_block(
                f"*{message}*",
                block_builders.simple_image_block(
                    "https://managr-images.s3.amazonaws.com/slack/logo_loading.gif", "Loading..."
                ),
            )
        ]
    return blocks


@block_set()
def success_modal_block_set(context):
    message = context.get("message", ":white_check_mark: Success!")
    user = context.get("u")
    form_id = context.get("form_id")
    blocks = [
        block_builders.section_with_button_block(
            "Send Recap",
            "SEND_RECAP",
            message,
            action_id=action_with_params(
                slack_const.PROCESS_SEND_RECAP_MODAL,
                params=[f"u={user}", f"form_id={form_id}", "type=command"],
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
def coming_soon_modal_block_set(context):
    blocks = [
        block_builders.simple_section(
            ":clock1: *This feature is in the works* :exclamation:", "mrkdwn"
        )
    ]
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
                f"Welcome <@{slack.slack_id}> I’m the Managr bot designed to help you automate your pipeline management process so you can focus on selling :clap:\n"
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
            f"{':white_check_mark:' if user.has_slack_integration else ':x:'} *<{get_site_url()}/settings/integrations|Slack>* is used to interact with you regarding your sales process",
            text_type="mrkdwn",
        ),
        block_builders.simple_section(
            f"{':white_check_mark:' if user.has_zoom_integration else ':x:'} *<{get_site_url()}/settings/integrations|Zoom>* is used to track your meetings to notify you so you can take action",
            text_type="mrkdwn",
        ),
        block_builders.simple_section(
            f"{':white_check_mark:' if user.has_salesforce_integration else ':x:'} *<{get_site_url()}/settings/integrations|Salesforce>* is the backbone of your integration we use this to keep track of your sales process",
            text_type="mrkdwn",
        ),
        block_builders.simple_section(
            f"{':white_check_mark:' if user.has_nylas_integration else ':x:'} *<{get_site_url()}/settings/integrations|Calendar>* will help us gather additional metadata about your meetings",
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
        *coming_soon_modal_block_set({}),
        block_builders.divider_block(),
    ]
    view = {"type": "home", "blocks": blocks}
    return view


@block_set()
def home_modal_generic_block_set(context):
    slack_id = context.get("slack_id")
    org_name = context.get("org_name")
    blocks = [
        block_builders.header_block("Join Managr!"),
        block_builders.divider_block(),
        block_builders.section_with_button_block(
            "Request Invite",
            slack_id,
            "Send a request to your team on Managr, we'll send them a DM with your info",
            action_id=slack_const.HOME_REQUEST_SLACK_INVITE,
            block_id="INVITE_BUTTON",
        ),
        block_builders.divider_block(),
        block_builders.simple_section(
            "*Once you've signed up you'll be able to integrate your accounts and use Managr to help you _SELL_* :moneybag:",
            "mrkdwn",
        ),
        block_builders.section_with_accessory_block(
            f"_Checkout the About Tab_",
            block_builders.simple_image_block(
                "https://managr-images.s3.amazonaws.com/slack/logo_loading.gif", "Loading..."
            ),
        ),
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
def calendar_reminders_blockset(context):
    meeting = MeetingPrepInstance.objects.get(id=context.get("prep_id"))
    user = User.objects.get(id=context.get("u"))
    data = meeting.event_data
    title = data["title"]
    unix_start_time = data["times"]["start_time"]
    utc_time = datetime.utcfromtimestamp(int(unix_start_time))
    tz = pytz.timezone(user.timezone)
    local_start = utc_time.astimezone(tz).strftime("%I:%M")

    am_or_pm = utc_time.astimezone(tz).strftime("%p")
    start_time = local_start + " " + am_or_pm
    type = meeting.resource_type if meeting.resource_type is not None else "prep"
    if type == "Opportunity":
        resource = Opportunity.objects.get(id=meeting.resource_id)
    elif type == "Account":
        resource = Account.objects.get(id=meeting.resource_id)
    elif type == "Lead":
        resource = Lead.objects.get(id=meeting.resource_id)
    else:
        resource = None
    text = f"{title}\n Starts at {start_time}\n Attendees: " + str(len(meeting.participants))
    if type != "prep":
        text += f"\n *{type} {resource.name}*"
    blocks = [
        block_builders.section_with_button_block(
            "View Attendees",
            section_text=text,
            button_value=context.get("prep_id"),
            action_id=action_with_params(
                slack_const.ZOOM_MEETING__VIEW_MEETING_CONTACTS,
                params=[f"w={str(meeting.id)}", f"type={type}",],
            ),
        ),
    ]
    action_blocks = []
    if type and type != "prep":
        action_blocks.append(
            block_builders.simple_button_block(
                f"Update {type} + Notes",
                meeting.resource_id,
                action_id=f"{slack_const.CHECK_IS_OWNER_FOR_UPDATE_MODAL}?u={str(user.id)}&resource={type}&current_page={context.get('current_page',1)}&type=prep",
                style="primary",
            )
        )
        action_blocks.append(
            block_builders.simple_button_block(
                f"Change {type}",
                f"type%{str(meeting.id)}",
                action_id=slack_const.ZOOM_MEETING__CREATE_OR_SEARCH,
            )
        )
        action_blocks.append(
            block_builders.simple_button_block(
                "View Notes",
                "get_notes",
                action_id=action_with_params(
                    slack_const.GET_NOTES,
                    params=[
                        f"u={str(user.id)}",
                        f"resource_id={str(meeting.resource_id)}",
                        f"resource_type={type}",
                        "type=prep",
                    ],
                ),
            )
        )

    else:
        action_blocks.append(
            block_builders.simple_button_block(
                "Map to Opportunity",
                f"type%{str(meeting.id)}",
                action_id=slack_const.ZOOM_MEETING__CREATE_OR_SEARCH,
                style="primary",
            )
        ),
    blocks.append(block_builders.actions_block(action_blocks, block_id=f"type%{str(meeting.id)}",))
    return blocks


@block_set()
def meeting_reminder_block_set(context):
    user = User.objects.get(id=context.get("u"))
    not_completed = context.get("not_completed")
    channel_info = slack_requests.get_channel_info(
        user.organization.slack_integration.access_token, user.slack_integration.zoom_channel
    )
    name = channel_info.get("channel").get("name")
    text = "meeting" if not_completed < 2 else "meetings"
    blocks = [
        block_builders.simple_section(
            f"FYI you have {not_completed} {text} from today that still need to be logged here: #{name}",
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
            f"Hey {name}, your team still has *{not_completed} {text}* from today that needs to be logged",
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
                f"u={context.get('u')}",
                f"main_form={context.get('main_form')}",
            ],
        ),
    )
    return blocks


@block_set()
def edit_product_block_set(context):
    opp_item = OpportunityLineItem.objects.get(id=context.get("opp_item_id"))
    user = User.objects.get(id=context.get("u"))
    template = (
        OrgCustomSlackForm.objects.for_user(user)
        .filter(Q(resource="OpportunityLineItem", form_type="CREATE"))
        .first()
    )
    slack_form = OrgCustomSlackFormInstance.objects.create(
        template=template, resource_id=str(opp_item.id), user=user
    )
    form_blocks = slack_form.generate_form(opp_item.secondary_data)
    return [*form_blocks]
