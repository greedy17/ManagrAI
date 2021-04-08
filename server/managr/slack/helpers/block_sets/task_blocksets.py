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
from managr.salesforce.routes import routes as model_routes


def _initial_interaction_message(resource_name=None, resource_type=None):
    if not resource_type:
        return "I've noticed your meeting just ended but couldn't find an Opportunity or Account or Lead to link what would you like to do?"

    # replace opp, review disregard
    return f"I've noticed your meeting with {resource_type} *{resource_name}* just ended would you like to log this meeting?"


@block_set()
def coming_soon_modal_block_set(context):
    blocks = [
        block_builders.simple_section(
            ":clock1: *This feature is in the works* :exclamation:", "mrkdwn"
        )
    ]
    return blocks


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
        block_builders.datepicker(block_id="managr_task_datetime", label="Due Date"),
        block_builders.static_select(
            "Related to type",
            [
                block_builders.option("Opportunity", "Opportunity"),
                block_builders.option("Account", "Account"),
                # block_builders.option("Contact", "Contact"),
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


@block_set(required_context=["u"])
def list_tasks_block_set(context):

    user = User.objects.get(id=context.get("u"))
    # print(user.__dict__)

    # TODO: Update this to render list of tasks as text once
    # tasks are coming from the API
    blocks = [block_builders.simple_section("Hello world")]
    # blocks = [
    #     block_builders.section_with_button_block(
    #         "Create Task",
    #         "CREATE_A_TASK",
    #         "Would you like to create a task from this meeting?",
    #         action_id=action_with_params(
    #             slack_const.ZOOM_MEETING__LIST_TASKS,
    #             params=[
    #                 f"u={str(user.id)}",
    #                 # f"resource_type={workflow.resource_type}",
    #                 # f"resource_id={workflow.resource_id}",
    #             ],
    #         ),
    #     )
    # ]

    # resource = context.get("resource_id")
    # resource_type = context.get("resource_type")
    # user = User.objects.get(id=context.get("u"))

    return blocks
