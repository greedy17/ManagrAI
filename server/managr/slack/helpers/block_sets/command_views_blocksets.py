import pdb
import pytz
import uuid
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


@block_set(required_context=["resource_type", "u"])
def command_update_resource_interaction(context):
    # form = OrgCustomSlackFormInstances.objects.get(id=context.get("f"))
    user = User.objects.get(id=context.get("u"))
    return [
        block_builders.external_select(
            f"*Search for an {context.get('resource_type')}*",
            f"{slack_const.COMMAND_FORMS__GET_LOCAL_RESOURCE_OPTIONS}?u={str(user.id)}&resource={context.get('resource_type')}",
            block_id="select_existing",
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
        ),
    ]


@block_set(required_context=["u"])
def update_modal_block_set(context, *args, **kwargs):
    """Shows a modal to update a resource"""
    resource_type = context.get("resource_type", None)
    resource_id = context.get("resource_id", None)
    user_id = context.get("u")
    form_id = context.get("f")
    user = User.objects.get(id=user_id)
    blocks = []
    blocks.append(
        block_builders.static_select(
            "Related to type",
            [
                block_builders.option("Opportunity", "Opportunity"),
                block_builders.option("Account", "Account"),
                # block_builders.option("Contact", "Contact"),
                block_builders.option("Lead", "Lead"),
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
                f"{slack_const.COMMAND_FORMS__GET_LOCAL_RESOURCE_OPTIONS}?u={user_id}&resource={resource_type}",
                block_id="select_existing",
            ),
        )

    if form_id:
        slack_form = OrgCustomSlackFormInstance.objects.get(id=form_id)
        form_blocks = slack_form.generate_form()
        if len(form_blocks):
            blocks.append(
                block_builders.simple_section(
                    ":exclamation: *Please fill out all fields, not doing so may result in errors*",
                    "mrkdwn",
                ),
            )

            blocks = [*blocks, *form_blocks]
        else:

            blocks = [
                block_builders.section_with_button_block(
                    "Forms",
                    "form",
                    f"Please add fields to your {context.get('resource')} update form",
                    url=f"{get_site_url()}/forms",
                )
            ]
    return blocks
