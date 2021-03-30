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
def create_task_block_set(context):
    # get the meeting
    # workflow = MeetingWorkflow.objects.get(id=context.get("u"))
    # check the resource attached to this meeting

    # resource = workflow.resource
    # meeting = workflow.meeting
    # workflow_id_param = "u=" + context.get("u")
    # user_timezone = meeting.zoom_account.timezone
    # start_time = meeting.start_time
    # end_time = meeting.end_time
    # formatted_start = (
    #     datetime.strftime(
    #         start_time.astimezone(pytz.timezone(user_timezone)), "%a, %B, %Y %I:%M %p"
    #     )
    #     if start_time
    #     else start_time
    # )
    # formatted_end = (
    #     datetime.strftime(end_time.astimezone(pytz.timezone(user_timezone)), "%a, %B, %Y %I:%M %p")
    #     if end_time
    #     else end_time
    # )
    default_blocks = [
        {"type": "divider"},
        block_builders.section_with_accessory_block(
            # f"*{meeting.topic}*\n{formatted_start} - {formatted_end}\n *Attendees:* {meeting.participants_count}",
            "dmmy",
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
                slack_const.ZOOM_MEETING__VIEW_MEETING_CONTACTS, params=[],
            ),
        ),
        {"type": "divider"},
    ]
    # if not resource:
    title_section = _initial_interaction_message()
    # else:
    #     name = resource.name
    #     title_section = _initial_interaction_message(name, workflow.resource_type)
    blocks = [
        block_builders.simple_section(title_section, "mrkdwn",),
        *default_blocks,
    ]
    # action button blocks
    action_blocks = [
        block_builders.simple_button_block(
            "Attach/Change",
            "dsfdsf",
            # str(workflow.id),
            action_id=slack_const.ZOOM_MEETING__CREATE_OR_SEARCH,
            style="primary",
        ),
        block_builders.simple_button_block(
            "Disregard",
            "adasdasd",
            # str(workflow.id),
            action_id=slack_const.ZOOM_MEETING__DISREGARD_REVIEW,
            style="danger",
        ),
    ]

    # if (
    #     workflow.resource_type == slack_const.FORM_RESOURCE_OPPORTUNITY
    #     or workflow.resource_type == slack_const.FORM_RESOURCE_ACCOUNT
    # ):
    #     action_blocks = [
    #         block_builders.simple_button_block(
    #             "Review",
    #             str(workflow.id),
    #             action_id=slack_const.ZOOM_MEETING__INIT_REVIEW,
    #             style="primary",
    #         ),
    #         *action_blocks,
    #     ]
    # elif workflow.resource_type == slack_const.FORM_RESOURCE_LEAD:
    #     action_blocks = [
    #         block_builders.simple_button_block(
    #             "Convert Lead",
    #             str(workflow.id),
    #             action_id=action_with_params(
    #                 slack_const.ZOOM_MEETING__CONVERT_LEAD, params=[f"u={str(workflow.user.id)}"]
    #             ),
    #             style="primary",
    #         ),
    #         *action_blocks,
    #     ]
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

