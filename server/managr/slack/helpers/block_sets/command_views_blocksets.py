import pdb
import pytz
import uuid
import json

from urllib.parse import urlencode, quote_plus, urlparse
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
    block_finder,
)
from managr.slack.helpers import block_builders
from managr.utils.misc import snake_to_space
from managr.salesforce.routes import routes as form_routes
from managr.slack.models import OrgCustomSlackForm, OrgCustomSlackFormInstance
from managr.alerts.models import AlertInstance


@block_set(required_context=["resource_type", "u"])
def command_update_resource_interaction(context):
    # form = OrgCustomSlackFormInstances.objects.get(id=context.get("f"))
    user = User.objects.get(id=context.get("u"))
    return [
        block_builders.external_select(
            f"*Search for an {context.get('resource_type')}*",
            f"{slack_const.COMMAND_FORMS__GET_LOCAL_RESOURCE_OPTIONS}?u={str(user.id)}&resource={context.get('resource_type')}",
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
            f"{slack_const.GET_USER_ACCOUNTS}?u={str(user.id)}&type={context.get('type')}",
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
            f"{slack_const.COMMAND_SUMMARY__GET_LOCAL_RESOURCE_OPTIONS}?u={str(user.id)}&resource={context.get('resource_type')}",
            block_id="select_existing",
            placeholder="Type to search",
        ),
    ]


def custom_paginator_block(pagination_object, invocation, channel, config_id):
    next_page = pagination_object.get("next_page", None)
    prev_page = pagination_object.get("previous_page", None)
    blocks = [
        block_builders.context_block(f"Alert Returned {pagination_object.get('count')} results")
    ]
    button_blocks = []
    page_context = {"invocation": invocation, "channel": channel, "config_id": config_id}

    if prev_page:
        prev_page_button = block_builders.simple_button_block(
            "Previous",
            str(prev_page),
            style="danger",
            action_id=f"{slack_const.PAGINATE_ALERTS}?{urlencode({**page_context,'new_page':int(prev_page)})}",
        )
        button_blocks.append(prev_page_button)
    if next_page:
        next_page_button = block_builders.simple_button_block(
            "Next",
            str(next_page),
            action_id=f"{slack_const.PAGINATE_ALERTS}?{urlencode({**page_context,'new_page':int(next_page)})}",
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
    blocks = [
        block_builders.section_with_button_block(
            f"Update {instance.template.resource_type}",
            instance.resource_id,
            instance.render_text(),
            action_id=f"{slack_const.CHECK_IS_OWNER_FOR_UPDATE_MODAL}?u={str(resource_owner.id)}&resource={instance.template.resource_type}",
            style="primary",
        ),
    ]
    if instance.template.resource_type != "Lead":
        blocks.append(
            block_builders.section_with_button_block(
                "Add to Cadence",
                "add_to_cadence",
                "Add contacts to Cadence",
                style="danger",
                action_id=action_with_params(
                    slack_const.ADD_TO_CADENCE_MODAL,
                    params=[
                        f"u={str(user.id)}",
                        f"resource_id={str(instance.resource_id)}",
                        f"resource_name={instance.resource.name}",
                        f"resource_type={instance.template.resource_type}",
                    ],
                ),
            ),
        )
    if in_channel or (user.id != resource_owner.id):
        blocks.append(
            block_builders.context_block(
                f"_This {instance.template.resource_type} is owned by_ *{resource_owner.full_name}*",
                "mrkdwn",
            ),
        )
    blocks.append(block_builders.context_block(f"Triggered from alert {instance.template.title}"))
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
    blocks = []
    blocks.append(
        block_builders.static_select(
            "Related to type",
            [
                block_builders.option("Opportunity", "Opportunity"),
                block_builders.option("Account", "Account"),
                block_builders.option("Lead", "Lead"),
                block_builders.option("Contact", "Contact"),
            ],
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
                f"{slack_const.COMMAND_FORMS__GET_LOCAL_RESOURCE_OPTIONS}?u={user_id}&resource={resource_type}&type={type}",
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


@block_set(required_context=["u"])
def create_modal_block_set(context, *args, **kwargs):
    """Shows a modal to create a resource"""
    resource_type = context.get("resource_type", None)

    user_id = context.get("u")
    form_id = context.get("f")

    blocks = []

    if form_id:
        slack_form = OrgCustomSlackFormInstance.objects.get(id=form_id)
        form_blocks = slack_form.generate_form(
            slack_form.saved_data
        )  # optionally pass any saved data from this form
        if len(form_blocks):
            blocks = [*form_blocks]
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
        block_builders.multi_external_select(
            f"*Add Contacts from {context.get('resource_name')} to selected Cadence*:",
            f"{slack_const.GET_PEOPLE_OPTIONS}?u={user_id}&resource_id={context.get('resource_id')}&resource_type={context.get('resource_type')}",
            block_id="select_people",
            placeholder="Type to search",
        ),
    ]
    return blocks

