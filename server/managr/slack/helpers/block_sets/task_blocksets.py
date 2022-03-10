import pdb
import pytz
import uuid
import json

from datetime import datetime, date

from django.db.models import Q

from managr.utils.sites import get_site_url
from managr.core.models import User, Notification
from managr.opportunity.models import Opportunity
from managr.salesforce.models import MeetingWorkflow
from managr.salesforce import constants as sf_consts
from managr.slack import constants as slack_const
from managr.slack.helpers.utils import action_with_params, block_set, map_fields_to_type
from managr.slack.helpers import block_builders
from managr.utils.misc import snake_to_space
from managr.salesforce.routes import routes as form_routes
from managr.slack.models import OrgCustomSlackForm, OrgCustomSlackFormInstance
from managr.salesforce.routes import routes as model_routes


@block_set(required_context=["u"])
def create_task_modal_block_set(context):
    resource = context.get("resource_id")
    resource_type = context.get("resource_type")
    user = User.objects.get(id=context.get("u"))

    related_type_initial_option = (
        block_builders.option(resource_type, resource_type) if resource_type else None
    )
    related_to = None
    if resource and resource_type:
        related_to = model_routes.get(resource_type).get("model").objects.get(id=resource).name

    related_to_initial_option = (
        block_builders.option(related_to, resource) if resource and related_to else None
    )

    blocks = [
        block_builders.input_block("Subject", optional=False, block_id="managr_task_subject",),
        # HACK:- According to slack values are cached based on block_id since this is a sub block adding action_id seems to preserve the value
        block_builders.datepicker(
            block_id="managr_task_datetime", label="Due Date", action_id="DO_NOTHING"
        ),
        block_builders.static_select(
            "Related to type",
            [
                block_builders.option("Opportunity", "Opportunity"),
                block_builders.option("Account", "Account"),
                block_builders.option("Contact", "Contact"),
                block_builders.option("Lead", "Lead"),
            ],
            action_id=f"{slack_const.UPDATE_TASK_SELECTED_RESOURCE}?u={context.get('u')}",
            block_id="managr_task_related_to_resource",
            initial_option=related_type_initial_option,
        ),
        block_builders.external_select(
            "Related To",
            f"{slack_const.GET_LOCAL_RESOURCE_OPTIONS}?u={context.get('u')}&resource={resource_type}",
            block_id="managr_task_related_to",
            initial_option=related_to_initial_option,
        ),
    ]

    action_query = f"{slack_const.GET_EXTERNAL_RELATIONSHIP_OPTIONS}?u={context.get('u')}&relationship=User&fields=name"

    blocks.append(
        block_builders.external_select(
            "Assign To",
            action_query,
            block_id="managr_task_assign_to",
            initial_option=block_builders.option(
                user.full_name, user.salesforce_account.salesforce_id
            ),
        )
    )
    action_query = f"{slack_const.GET_EXTERNAL_PICKLIST_OPTIONS}?u={context.get('u')}&resource=Task&field=Status"

    blocks.append(
        block_builders.external_select("Status", action_query, block_id="managr_task_status")
    )

    return blocks


@block_set(required_context=["u"])
def create_event_modal_block_set(context):
    resource = context.get("resource_id")
    resource_type = context.get("resource_type")
    user = User.objects.get(id=context.get("u"))

    related_type_initial_option = (
        block_builders.option(resource_type, resource_type) if resource_type else None
    )
    related_to = None
    if resource and resource_type:
        related_to = model_routes.get(resource_type).get("model").objects.get(id=resource).name

    related_to_initial_option = (
        block_builders.option(related_to, resource) if resource and related_to else None
    )

    blocks = [
        block_builders.input_block("Subject", optional=False, block_id="managr_event_subject",),
        # HACK:- According to slack values are cached based on block_id since this is a sub block adding action_id seems to preserve the value
        block_builders.datepicker(
            block_id="managr_event_date", label="Date of Event", action_id="DO_NOTHING"
        ),
        block_builders.timepicker(
            block_id="managr_event_time", label="Start time of Event", action_id="DO_NOTHING"
        ),
        block_builders.input_block(
            "Duration (in minutes) of Event", 0, block_id="managr_event_duration", optional=False
        ),
        block_builders.static_select(
            "Related to type",
            [
                block_builders.option("Opportunity", "Opportunity"),
                block_builders.option("Account", "Account"),
                block_builders.option("Contact", "Contact"),
                block_builders.option("Lead", "Lead"),
            ],
            action_id=f"{slack_const.UPDATE_TASK_SELECTED_RESOURCE}?u={context.get('u')}",
            block_id="managr_event_related_to_resource",
            initial_option=related_type_initial_option,
        ),
        block_builders.external_select(
            "Related To",
            f"{slack_const.GET_LOCAL_RESOURCE_OPTIONS}?u={context.get('u')}&resource={resource_type}",
            block_id="managr_event_related_to",
            initial_option=related_to_initial_option,
        ),
    ]

    action_query = f"{slack_const.GET_EXTERNAL_RELATIONSHIP_OPTIONS}?u={context.get('u')}&relationship=User&fields=name"

    blocks.append(
        block_builders.external_select(
            "Assign To",
            action_query,
            block_id="managr_event_assign_to",
            initial_option=block_builders.option(
                user.full_name, user.salesforce_account.salesforce_id
            ),
        )
    )

    return blocks
