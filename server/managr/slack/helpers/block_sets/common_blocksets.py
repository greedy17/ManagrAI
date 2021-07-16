import pdb
import pytz
import uuid
import logging
import json

from datetime import datetime

from django.db.models import Q

from managr.utils.sites import get_site_url
from managr.core.models import User, Notification
from managr.opportunity.models import Opportunity
from managr.zoom.models import ZoomMeeting
from managr.salesforce.models import MeetingWorkflow
from managr.salesforce import constants as sf_consts
from managr.slack import constants as slack_const
from managr.slack.helpers.utils import action_with_params, block_set, map_fields_to_type
from managr.slack.helpers import block_builders
from managr.utils.misc import snake_to_space
from managr.salesforce.routes import routes as form_routes
from managr.slack.models import OrgCustomSlackForm, OrgCustomSlackFormInstance
from managr.salesforce.adapter.exceptions import (
    TokenExpired,
    FieldValidationError,
    RequiredFieldError,
    SFQueryOffsetError,
    SFNotFoundError,
    InvalidRefreshToken,
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
    message = context.get("message", ":clap: Success!")
    show_image = context.get("show_image", True)
    blocks = [block_builders.simple_section(message, "mrkdwn")]
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
        if t.what_id:
            # first check for opp
            obj = user.imported_opportunity.filter(integration_id=t.what_id).first()
            if not obj:
                obj = user.imported_account.filter(integration_id=t.what_id).first()
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
