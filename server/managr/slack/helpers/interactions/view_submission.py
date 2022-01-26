import json
import pdb
import pytz
from datetime import datetime, date
import logging
import uuid
import time
from django.db.models import Q

from django.http import JsonResponse
from django.utils import timezone
from rest_framework.response import Response


from managr.api.decorators import log_all_exceptions
from managr.salesforce.adapter.exceptions import (
    FieldValidationError,
    RequiredFieldError,
    TokenExpired,
    UnhandledSalesforceError,
    SFNotFoundError,
)
from managr.utils.misc import custom_paginator
from managr.slack.helpers.block_sets.command_views_blocksets import custom_paginator_block
from managr.alerts.models import AlertInstance
from managr.organization.models import (
    Organization,
    Contact,
    Account,
    OpportunityLineItem,
    PricebookEntry,
)
from managr.core.models import User, MeetingPrepInstance
from managr.core.background import emit_create_calendar_event
from managr.outreach.tasks import emit_add_sequence_state
from managr.core.cron import generate_morning_digest
from managr.opportunity.models import Opportunity
from managr.zoom.models import ZoomMeeting
from managr.salesforce.models import MeetingWorkflow
from managr.salesforce import constants as sf_consts
from managr.slack import constants as slack_const
from managr.slack.models import OrgCustomSlackFormInstance
from managr.slack.helpers import block_builders
from managr.slack.helpers import requests as slack_requests
from managr.slack.helpers.utils import (
    action_with_params,
    NO_OP,
    processor,
    block_finder,
    check_contact_last_name,
)
from managr.salesforce.adapter.models import ContactAdapter, OpportunityAdapter, TaskAdapter
from managr.zoom import constants as zoom_consts
from managr.salesforce.routes import routes as model_routes
from managr.salesforce.adapter.routes import routes as adapter_routes
from managr.salesforce.background import (
    _process_create_new_resource,
    _process_create_task,
    emit_meeting_workflow_tracker,
    emit_add_update_to_sf,
    emit_add_products_to_sf,
    _send_recap,
)
from managr.slack.helpers.block_sets import get_block_set
from managr.salesloft.models import People
from managr.salesloft.background import emit_add_cadence_membership
from managr.zoom.background import emit_process_schedule_zoom_meeting

from managr.slack.helpers.exceptions import (
    UnHandeledBlocksException,
    InvalidBlocksFormatException,
    InvalidBlocksException,
    InvalidAccessToken,
)
from managr.api.decorators import slack_api_exceptions
from managr.organization.serializers import ContactSerializer

logger = logging.getLogger("managr")


@log_all_exceptions
@processor(required_context=["w", "form_type"])
def process_stage_next_page(payload, context):
    workflow = MeetingWorkflow.objects.get(id=context.get("w"))
    print("STAGE RELATED:", context)
    view = payload["view"]
    # if there are additional stage gating forms aggregate them and push them in 1 view
    # save current data to its form we will close all views at the end

    state = view["state"]["values"]
    private_metadata = json.loads(view["private_metadata"])

    review_form = workflow.forms.filter(template__form_type=context.get("form_type")).first()
    review_form.save_form(state)
    forms = workflow.forms.filter(template__form_type=slack_const.FORM_TYPE_STAGE_GATING).all()

    if len(forms):
        next_blocks = []
        for form in forms:
            next_blocks.extend(form.generate_form())
            context["f"] = f"{context['f']},{str(form.id)}"
        private_metadata.update({**context})
        if context.get("form_type") == "CREATE":
            callback_id = slack_const.COMMAND_FORMS__SUBMIT_FORM

        else:
            callback_id = slack_const.ZOOM_MEETING__PROCESS_MEETING_SENTIMENT
        return {
            "response_action": "push",
            "view": {
                "type": "modal",
                "title": {"type": "plain_text", "text": "Stage Related Fields"},
                "submit": {"type": "plain_text", "text": "Submit"},
                "blocks": next_blocks,
                "private_metadata": json.dumps(private_metadata),
                "callback_id": callback_id,
            },
        }
    return  # closes all views by default


@log_all_exceptions
@slack_api_exceptions(rethrow=True)
@processor(
    required_context=["w", "original_message_channel", "original_message_timestamp",]
)
def process_zoom_meeting_data(payload, context):
    # get context
    workflow = MeetingWorkflow.objects.get(id=context.get("w"))
    user = workflow.user
    slack_access_token = user.organization.slack_integration.access_token
    view = payload["view"]
    url = slack_const.SLACK_API_ROOT + slack_const.VIEWS_UPDATE
    loading_view_data = {
        "view_id": view["id"],
        "view": {
            "type": "modal",
            "title": {"type": "plain_text", "text": "Loading"},
            "blocks": get_block_set(
                "loading",
                {
                    "message": ":exclamation: SFDC is currently a bit slow :zany_face:, please wait a few seconds and click 'try again'",
                    "fill": True,
                },
            ),
            "private_metadata": view["private_metadata"],
        },
    }
    try:
        res = slack_requests.generic_request(
            url, loading_view_data, access_token=slack_access_token
        )
    except Exception as e:
        return logger.exception(
            f"Failed To Show Loading Screen for user  {str(user.id)} email {user.email} {e}"
        )

    # get state - state contains the values based on the block_id
    state = view["state"]["values"]
    # if we had a next page the form data for the review was already saved
    forms = workflow.forms.filter(template__form_type=slack_const.FORM_TYPE_STAGE_GATING)
    if len(forms):
        for form in forms:
            form.save_form(state)
    # otherwise we save the meeting review form
    else:
        form = workflow.forms.filter(template__form_type=slack_const.FORM_TYPE_UPDATE).first()
        form.update_source = "meeting"
        form.save_form(state)

    contact_forms = workflow.forms.filter(template__resource=slack_const.FORM_RESOURCE_CONTACT)

    ops = [
        # update
        f"{sf_consts.MEETING_REVIEW__UPDATE_RESOURCE}.{str(workflow.id)}",
        # create call log
        f"{sf_consts.MEETING_REVIEW__SAVE_CALL_LOG}.{str(workflow.id)}",
        # save meeting data
    ]
    for form in contact_forms:
        if form.template.form_type == slack_const.FORM_TYPE_CREATE:
            ops.append(
                f"{sf_consts.MEETING_REVIEW__CREATE_CONTACTS}.{str(workflow.id)},{str(form.id)}"
            )
        else:
            ops.append(
                f"{sf_consts.MEETING_REVIEW__UPDATE_CONTACTS}.{str(workflow.id)},{str(form.id)}"
            )

    # emit all events
    if len(workflow.operations_list):
        workflow.operations_list = [*workflow.operations_list, *ops]
    else:
        workflow.operations_list = ops

    ts, channel = workflow.slack_interaction.split("|")
    block_set = [
        *get_block_set("loading", {"message": ":rocket: We are saving your data to salesforce..."}),
    ]
    try:
        res = slack_requests.update_channel_message(
            channel, ts, slack_access_token, block_set=block_set
        )
    except Exception as e:
        logger.exception(
            f"Failed To Send Submit Interaction for user  with workflow {str(workflow.id)} email {workflow.user.email} {e}"
        )
        return {"response_action": "clear"}
    workflow.slack_interaction = f"{res['ts']}|{res['channel']}"
    workflow.save()
    workflow.begin_tasks()
    emit_meeting_workflow_tracker(str(workflow.id))

    return {"response_action": "clear"}


@log_all_exceptions
@processor(required_context=["f"])
def process_next_page_slack_commands_form(payload, context):
    # get context
    user = User.objects.get(id=context.get("u"))
    current_form_ids = context.get("f").split(",")
    view = payload["view"]
    state = view["state"]["values"]

    current_forms = user.custom_slack_form_instances.filter(id__in=current_form_ids)
    # save the main form
    main_form = current_forms.filter(template__form_type__in=["UPDATE", "CREATE"]).first()
    main_form.save_form(state)
    stage_forms = current_forms.exclude(template__form_type__in=["UPDATE", "CREATE"])
    slack_access_token = user.organization.slack_integration.access_token

    # currently only for update
    blocks = []
    for form in stage_forms:
        blocks.extend(form.generate_form())

    if len(blocks):

        return {
            "response_action": "push",
            "view": {
                "type": "modal",
                "title": {"type": "plain_text", "text": "Stage Related Fields"},
                "submit": {"type": "plain_text", "text": "Submit"},
                "blocks": blocks,
                "private_metadata": view["private_metadata"],
                "callback_id": slack_const.COMMAND_FORMS__SUBMIT_FORM,
            },
        }
    return


@log_all_exceptions
@processor(required_context=["f"])
def process_add_products_form(payload, context):
    # get context
    user = User.objects.get(slack_integration__slack_id=payload["user"]["id"])
    current_form_ids = context.get("f").split(",")
    view = payload["view"]
    state = view["state"]["values"]
    type = context.get("type", None)
    private_metadata = json.loads(view["private_metadata"])
    if type == "meeting":
        workflow = MeetingWorkflow.objects.get(id=context.get("w"))
        callback_id = slack_const.ZOOM_MEETING__PROCESS_MEETING_SENTIMENT
        product_form = workflow.forms.filter(template__resource="OpportunityLineItem").first()
    else:
        product_form = user.custom_slack_form_instances.get(id=context.get("product_form"))
        callback_id = slack_const.COMMAND_FORMS__SUBMIT_FORM
        private_metadata.update({"product_form_id": str(product_form.id)})
    current_forms = user.custom_slack_form_instances.filter(id__in=current_form_ids)
    # save the main form
    main_form = (
        current_forms.filter(template__form_type__in=["UPDATE", "CREATE"])
        .exclude(template__resource="OpportunityLineItem")
        .first()
    )
    products = OpportunityLineItem.objects.filter(opportunity=main_form.resource_id)
    main_form.save_form(state)

    # currently only for update
    blocks = []
    blocks.extend(product_form.generate_form())
    if len(blocks):

        return {
            "response_action": "push",
            "view": {
                "type": "modal",
                "title": {"type": "plain_text", "text": "Add Products Form"},
                "submit": {"type": "plain_text", "text": "Submit"},
                "blocks": blocks,
                "private_metadata": json.dumps(private_metadata),
                "callback_id": callback_id,
            },
        }
    return


@log_all_exceptions
@slack_api_exceptions(rethrow=True)
@processor(required_context=["f"])
def process_submit_resource_data(payload, context):
    # get context
    has_error = False
    state = payload["view"]["state"]["values"]
    current_form_ids = context.get("f").split(",")
    user = User.objects.get(id=context.get("u"))
    trigger_id = payload["trigger_id"]
    view_id = payload["view"]["id"]
    type = context.get("type")
    external_id = payload.get("view", {}).get("external_id", None)
    try:
        view_type, __unique_id = external_id.split(".")
    except ValueError:
        view_type = external_id
        pass
    current_forms = user.custom_slack_form_instances.filter(id__in=current_form_ids)
    main_form = (
        current_forms.filter(template__form_type__in=["UPDATE", "CREATE"])
        .exclude(template__resource="OpportunityLineItem")
        .first()
    )
    stage_forms = current_forms.exclude(template__form_type__in=["UPDATE", "CREATE"]).exclude(
        template__resource="OpportunityLineItem"
    )
    stage_form_data_collector = {}
    for form in stage_forms:
        form.update_source = type
        form.is_submitted = True
        form.submission_date = timezone.now()
        form.save_form(state)
        stage_form_data_collector = {**stage_form_data_collector, **form.saved_data}
    if not len(stage_forms):
        if main_form.template.form_type == "UPDATE":
            main_form.update_source = type
            main_form.is_submitted = True
            main_form.submission_date = timezone.now()
        main_form.save_form(state)
    all_form_data = {**stage_form_data_collector, **main_form.saved_data}
    slack_access_token = user.organization.slack_integration.access_token
    url = slack_const.SLACK_API_ROOT + slack_const.VIEWS_UPDATE
    loading_view_data = {
        "trigger_id": trigger_id,
        "view_id": view_id,
        "view": {
            "type": "modal",
            "title": {"type": "plain_text", "text": "Loading"},
            "blocks": get_block_set(
                "loading",
                {
                    "message": ":exclamation: SFDC is currently a bit slow :zany_face:, please wait a few seconds and click 'try again'",
                    "fill": True,
                },
            ),
            "private_metadata": json.dumps(context),
        },
    }
    try:
        res = slack_requests.generic_request(
            url, loading_view_data, access_token=slack_access_token
        )
    except Exception as e:
        return logger.exception(
            f"Failed To Update via command for user  {str(user.id)} email {user.email} {e}"
        )
    attempts = 1
    while True:
        sf = user.salesforce_account
        try:
            if main_form.template.form_type == "UPDATE":
                resource = main_form.resource_object.update_in_salesforce(all_form_data)
                break
            else:
                resource = _process_create_new_resource.now(current_form_ids)
                break

        except FieldValidationError as e:
            has_error = True
            blocks = (
                get_block_set(
                    "error_modal",
                    {
                        "message": f":no_entry: Uh-Ohhh it looks like we found an error, this error is based on Validations set up by your org\n *Error* : _{e}_"
                    },
                ),
            )
            break

        except RequiredFieldError as e:
            has_error = True
            blocks = get_block_set(
                "error_modal",
                {
                    "message": f":no_entry: Uh-Ohhh it looks like we found an error, this error is based on Required fields from Salesforce\n *Error* : _{e}_"
                },
            )
            break
        except UnhandledSalesforceError as e:
            has_error = True
            blocks = get_block_set(
                "error_modal",
                {
                    "message": f":no_entry: Uh-Ohhh it looks like we found an error, this error is new to us please see below\n *Error* : _{e}_"
                },
            )
            break

        except SFNotFoundError as e:
            has_error = True
            blocks = get_block_set(
                "error_modal",
                {
                    "message": f":no_entry: Uh-Ohhh it looks like we found an error, this error one of the resources does not exist\n *Error* : _{e}_"
                },
            )
            break

        except TokenExpired:
            if attempts >= 5:
                logger.exception(
                    f"Failed to Update data for user {str(user.id)} after {attempts} tries"
                )
                has_error = True
                blocks = get_block_set(
                    "error_modal",
                    {
                        "message": f":no_entry: Uh-Ohhh it looks like we've had an issue with your token\n *Error* : _{e}_"
                    },
                )
                break
            else:
                sf.regenerate_token()
                attempts += 1

        except ConnectionResetError:
            if attempts >= 5:
                logger.exception(
                    f"Failed to Update data for user {str(user.id)} after {attempts} tries because of connection error"
                )
                has_error = True
                blocks = get_block_set(
                    "error_modal",
                    {
                        "message": f":no_entry: Uh-Ohhh we had an error connecting to your salesforce instance please try again"
                    },
                )
                break
            else:
                time.sleep(2)
                attempts += 1

    if has_error:

        if not len(stage_forms):
            # add a special button to return the user back to edit their form
            # this is only required for single page forms
            blocks = [
                *blocks,
                block_builders.actions_block(
                    [
                        block_builders.simple_button_block(
                            "return to form",
                            str(main_form.id),
                            style="primary",
                            action_id=slack_const.RETURN_TO_FORM_MODAL,
                        )
                    ]
                ),
            ]
        url = slack_const.SLACK_API_ROOT + slack_const.VIEWS_UPDATE
        error_view_data = {
            "trigger_id": trigger_id,
            "view_id": view_id,
            "view": {
                "type": "modal",
                "title": {"type": "plain_text", "text": "Error"},
                "blocks": blocks,
                "private_metadata": json.dumps(context),
                "external_id": f"{view_type}.{str(uuid.uuid4())}",
            },
        }
        try:
            return slack_requests.generic_request(
                url, error_view_data, access_token=slack_access_token
            )
        except Exception as e:
            return logger.exception(
                f"Failed To Update via command for user  {str(user.id)} email {user.email} {e}"
            )
    pm = json.loads(payload["view"]["private_metadata"])
    if context.get("w"):
        url = slack_const.SLACK_API_ROOT + slack_const.VIEWS_UPDATE
        pm.update({"action": "EXISTING"})
        select_resource_view_data = {
            "trigger_id": trigger_id,
            "view_id": view_id,
            "view": {
                "type": "modal",
                "title": {"type": "plain_text", "text": main_form.template.resource},
                "callback_id": slack_const.ZOOM_MEETING__SELECTED_RESOURCE,
                "blocks": get_block_set(
                    "create_or_search_modal",
                    {
                        "w": context.get("w"),
                        "resource": current_forms.first().resource_type,
                        "resource_id": resource.integration_id,
                        "action": "EXISTING",
                    },
                ),
                "private_metadata": json.dumps(pm),
                "submit": {"type": "plain_text", "text": "Submit",},
            },
        }
        try:
            slack_requests.generic_request(
                url, select_resource_view_data, access_token=slack_access_token
            )
            return {"response_action": "clear"}
        except Exception as e:
            return logger.exception(
                f"Failed To Update the view for the workflow {str(user.id)} email {user.email} {e}"
            )

    else:
        current_forms.update(is_submitted=True, submission_date=timezone.now())
        form_id = current_form_ids[0]
        # update the channel message to clear it
        if main_form.template.form_type == "CREATE":
            text = f"Managr created {main_form.resource_type}"
            message = f"Successfully created *{main_form.resource_type}* _{resource.name if resource.name else resource.email}_"

        else:
            text = f"Managr updated {main_form.resource_type}"
            message = f":white_check_mark: Successfully updated *{main_form.resource_type}* _{main_form.resource_object.name}_"
        if len(user.slack_integration.recap_receivers) and type == "meeting":
            _send_recap(current_form_ids, None, True)
        if (
            all_form_data.get("meeting_comments") is not None
            and all_form_data.get("meeting_type") is not None
        ):
            emit_add_update_to_sf(str(main_form.id))
        if type == "alert":
            instance = AlertInstance.objects.get(id=context.get("alert_id"))
            main_form.alert_instance_id = instance
            main_form.save()
            alert_instances = AlertInstance.objects.filter(
                invocation=instance.invocation,
                channel=context.get("channel_id"),
                config_id=instance.config_id,
            ).filter(completed=False)
            alert_instance = alert_instances.first()
            text = instance.template.title
            blocks = [
                block_builders.header_block(f"{len(alert_instances)} results for workflow {text}"),
            ]
            if alert_instance:
                alert_instances = custom_paginator(
                    alert_instances, page=int(context.get("current_page"))
                )
                for alert_instance in alert_instances.get("results", []):
                    blocks = [
                        *blocks,
                        *get_block_set(
                            "alert_instance",
                            {
                                "instance_id": str(alert_instance.id),
                                "current_page": int(context.get("current_page")),
                            },
                        ),
                    ]
                    alert_instance.rendered_text = alert_instance.render_text()
                    alert_instance.save()
                if len(blocks):
                    blocks = [
                        *blocks,
                        *custom_paginator_block(
                            alert_instances,
                            instance.invocation,
                            context.get("channel_id"),
                            instance.config_id,
                        ),
                    ]
            else:
                blocks.append(
                    block_builders.simple_section("You're all finished with this workflow!")
                )
            slack_requests.update_channel_message(
                context.get("channel_id"),
                context.get("message_ts"),
                slack_access_token,
                block_set=blocks,
            )
            return {"response_action": "clear"}
        elif type == "prep":
            last_instance = (
                MeetingPrepInstance.objects.filter(user=user).order_by("-datetime_created").first()
            )
            prep_instance = MeetingPrepInstance.objects.filter(
                Q(invocation=last_instance.invocation) & Q(resource_id=main_form.resource_id)
            ).first()
            if prep_instance:
                prep_instance.form = main_form
                prep_instance.save()
            blocks = generate_morning_digest(
                user.id, last_instance.invocation, context.get("current_page")
            )
            slack_requests.update_channel_message(
                context.get("channel_id"),
                context.get("message_ts"),
                slack_access_token,
                block_set=blocks,
            )
            return {"response_action": "clear"}
        else:
            try:
                slack_requests.send_ephemeral_message(
                    user.slack_integration.channel,
                    user.organization.slack_integration.access_token,
                    user.slack_integration.slack_id,
                    text=text,
                    block_set=get_block_set(
                        "success_modal", {"message": message, "u": user.id, "form_id": form_id}
                    ),
                )
                update_view = {
                    "view_id": res["view"]["id"],
                    "view": {
                        "type": "modal",
                        "title": {"type": "plain_text", "text": "Success"},
                        "blocks": [
                            block_builders.simple_section(
                                f"Successfully updated {main_form.template.resource}", "mrkdwn"
                            )
                        ],
                    },
                }
                slack_requests.generic_request(
                    slack_const.SLACK_API_ROOT + slack_const.VIEWS_UPDATE,
                    update_view,
                    user.organization.slack_integration.access_token,
                )
            except Exception as e:
                logger.exception(
                    f"Failed to send ephemeral message to user informing them of successful update {user.email} {e}"
                )
                return {"response_action": "clear"}


@log_all_exceptions
@processor(required_context=["w"])
def process_zoom_meeting_attach_resource(payload, context):
    type = context.get("type", None)
    workflow = (
        MeetingPrepInstance.objects.get(id=context.get("w"))
        if type
        else MeetingWorkflow.objects.get(id=context.get("w"))
    )
    user = workflow.user
    slack_access_token = user.organization.slack_integration.access_token
    url = slack_const.SLACK_API_ROOT + slack_const.VIEWS_UPDATE
    # get state - state contains the values based on the block_id

    data = {
        "view_id": payload["view"]["id"],
        "view": {
            "type": "modal",
            "title": {"type": "plain_text", "text": "Success"},
            "blocks": get_block_set("success_modal", {}),
        },
    }
    state_values = payload["view"]["state"]["values"]
    meeting_resource = context.get("resource")
    if context.get("action") == "EXISTING":

        selected_action = [
            val.get("selected_option", {}).get("value", [])
            for val in state_values["select_existing"].values()
        ]
        selected_action = selected_action[0] if len(selected_action) else None
        workflow.resource_id = selected_action
        workflow.resource_type = meeting_resource
        workflow.save()
        # update the forms to the correct type

    else:
        # check to see if it already has the create form added and save that instead
        main_form = (
            workflow.forms.filter(template__form_type=slack_const.FORM_TYPE_CREATE,)
            .exclude(template__resource__in=["Contact", "OpportunityLineItem"])
            .first()
        )
        if main_form:
            stage_forms = workflow.forms.filter(
                template__form_type=slack_const.FORM_TYPE_STAGE_GATING
            ).exclude(template__resource=slack_const.FORM_RESOURCE_CONTACT)
            # if there are stage gating forms we need to save their data we already saved the main form's data

            if not len(stage_forms):
                main_form.save_form(state_values)
            else:
                # assume we already saved the forms for create
                for form in stage_forms:
                    form.save_form(state_values)
            try:
                resource = _process_create_new_resource.now(context.get("w"), meeting_resource)

            except FieldValidationError as e:

                return {
                    "response_action": "push",
                    "view": {
                        "type": "modal",
                        "title": {"type": "plain_text", "text": "An Error Occured"},
                        "blocks": get_block_set(
                            "error_modal",
                            {
                                "message": f":no_entry: Uh-Ohhh it looks like we found an error, this error is based on Validations set up by your org for {meeting_resource} objects\n *Error* : _{e}_"
                            },
                        ),
                    },
                }
            except RequiredFieldError as e:

                return {
                    "response_action": "push",
                    "view": {
                        "type": "modal",
                        "title": {"type": "plain_text", "text": "An Error Occurred"},
                        "blocks": get_block_set(
                            "error_modal",
                            {
                                "message": f":no_entry: Uh-Ohhh it looks like we found an error, this error is based on Required fields from Salesforce for {meeting_resource} objects\n *Error* : _{e}_"
                            },
                        ),
                    },
                }

            workflow.resource_id = str(resource.id)
            workflow.resource_type = meeting_resource

            workflow.save()

            # clear old forms (except contact forms)
            workflow.forms.exclude(
                template__resource__in=[
                    slack_const.FORM_RESOURCE_CONTACT,
                    slack_const.FORM_RESOURCE_OPPORTUNITYLINEITEM,
                ]
            ).delete()
            workflow.add_form(
                meeting_resource, slack_const.FORM_TYPE_UPDATE,
            )
    if type:
        ts = context.get("original_message_timestamp")
        channel = context.get("original_message_channel")
        meetings = MeetingPrepInstance.objects.filter(user=user.id).filter(
            invocation=workflow.invocation
        )
        paged_meetings = custom_paginator(meetings, count=1)
        paginate_results = paged_meetings.get("results", [])
        if len(paginate_results):
            current_instance = paginate_results[0]
            blockset = [
                *blocks,
                *get_block_set(
                    "calendar_reminders_blockset",
                    {"prep_id": str(current_instance.id), "u": str(user.id)},
                ),
                *custom_meeting_paginator_block(
                    paged_meetings, invocation, user.slack_integration.channel
                ),
            ]
    else:
        ts, channel = workflow.slack_interaction.split("|")
        workflow.forms.exclude(template__resource=slack_const.FORM_RESOURCE_CONTACT).delete()
        workflow.add_form(
            meeting_resource, slack_const.FORM_TYPE_UPDATE,
        )
        blocks_set = get_block_set("initial_meeting_interaction", {"w": context.get("w")})

    try:
        # update initial interaction workflow with new resource
        res = slack_requests.update_channel_message(
            channel, ts, slack_access_token, block_set=blocks_set
        )
        if type is None:
            workflow.slack_interaction = f"{res['ts']}|{res['channel']}"
        res = slack_requests.generic_request(url, data, access_token=slack_access_token)

    # add a message for user's if this failed
    except InvalidBlocksException as e:
        return logger.exception(
            f"Failed To Attach resource for user {str(workflow.id)} email {workflow.user.email} {e}"
        )
    except InvalidBlocksFormatException as e:
        return logger.exception(
            f"Failed To Attach resource for user {str(workflow.id)} email {workflow.user.email} {e}"
        )
    except UnHandeledBlocksException as e:
        return logger.exception(
            f"Failed To Attach resource for user {str(workflow.id)} email {workflow.user.email} {e}"
        )
    except InvalidAccessToken as e:
        return logger.exception(
            f"Failed To Attach resource for user {str(workflow.id)} email {workflow.user.email} {e}"
        )

    workflow.slack_view = res.get("view").get("id")
    workflow.save()
    return {"response_action": "clear"}


@log_all_exceptions
@processor(required_context=["w"])
def process_digest_attach_resource(payload, context):
    workflow = MeetingPrepInstance.objects.get(id=context.get("w"))
    user = workflow.user
    slack_access_token = user.organization.slack_integration.access_token
    url = slack_const.SLACK_API_ROOT + slack_const.VIEWS_UPDATE
    # get state - state contains the values based on the block_id

    data = {
        "view_id": payload["view"]["id"],
        "view": {
            "type": "modal",
            "title": {"type": "plain_text", "text": "Success"},
            "blocks": get_block_set("success_modal", {}),
        },
    }
    state_values = payload["view"]["state"]["values"]
    meeting_resource = context.get("resource")
    # check to see if it already has the create form added and save that instead
    selected_action = [
        val.get("selected_option", {}).get("value", [])
        for val in state_values["select_existing"].values()
    ]
    selected_action = selected_action[0] if len(selected_action) else None
    workflow.resource_id = selected_action
    workflow.resource_type = meeting_resource
    workflow.save()

    ts = context.get("original_message_timestamp")
    channel = context.get("original_message_channel")

    blocks_set = generate_morning_digest(user.id, workflow.invocation)
    try:
        # update initial interaction workflow with new resource
        res = slack_requests.update_channel_message(
            channel, ts, slack_access_token, block_set=blocks_set
        )
        res = slack_requests.generic_request(url, data, access_token=slack_access_token)

    # add a message for user's if this failed
    except InvalidBlocksException as e:
        return logger.exception(
            f"Failed To Attach resource for user {str(workflow.id)} email {workflow.user.email} {e}"
        )
    except InvalidBlocksFormatException as e:
        return logger.exception(
            f"Failed To Attach resource for user {str(workflow.id)} email {workflow.user.email} {e}"
        )
    except UnHandeledBlocksException as e:
        return logger.exception(
            f"Failed To Attach resource for user {str(workflow.id)} email {workflow.user.email} {e}"
        )
    except InvalidAccessToken as e:
        return logger.exception(
            f"Failed To Attach resource for user {str(workflow.id)} email {workflow.user.email} {e}"
        )


@processor()
def process_update_meeting_contact(payload, context):
    state = payload["view"]["state"]["values"]
    type = context.get("type", None)
    if type:
        workflow = MeetingPrepInstance.objects.get(id=context.get("w"))
        contact = dict(
            *filter(
                lambda contact: contact["_tracking_id"] == context.get("tracking_id"),
                workflow.participants,
            )
        )
        form = OrgCustomSlackFormInstance.objects.get(id=contact["_form"])
    else:
        workflow = MeetingWorkflow.objects.get(id=context.get("w"))
        contact = dict(
            *filter(
                lambda contact: contact["_tracking_id"] == context.get("tracking_id"),
                workflow.meeting.participants,
            )
        )
        form = workflow.forms.get(id=contact["_form"])
    form.save_form(state)
    user_id = workflow.user.id if type else workflow.user_id
    # reconstruct the current data with the updated data
    adapter = ContactAdapter.from_api(
        {**contact.get("secondary_data", {}), **form.saved_data}, str(user_id)
    )
    url = slack_const.SLACK_API_ROOT + slack_const.VIEWS_UPDATE
    trigger_id = payload["trigger_id"]
    view_id = context.get(str("current_view_id"))
    new_contact = {
        **contact,
        **adapter.as_dict,
        "id": contact.get("id", None),
        "__has_changes": True,
    }
    if type:
        part_index = None
        for index, participant in enumerate(workflow.participants):
            if participant["_tracking_id"] == new_contact["_tracking_id"]:
                part_index = index
                break
        workflow.participants = [
            *workflow.participants[:part_index],
            new_contact,
            *workflow.participants[part_index + 1 :],
        ]
        workflow.save()
        user = User.objects.get(id=user_id)
        org = user.organization
        access_token = org.slack_integration.access_token
        show_meeting_context = {"w": context.get("w"), "type": workflow.resource_type}
        # return {"response_action": "clear"}
    else:
        # replace the contact in the participants list
        part_index = None
        for index, participant in enumerate(workflow.meeting.participants):
            if participant["_tracking_id"] == new_contact["_tracking_id"]:
                part_index = index
                break
        workflow.meeting.participants = [
            *workflow.meeting.participants[:part_index],
            new_contact,
            *workflow.meeting.participants[part_index + 1 :],
        ]
        workflow.meeting.save()
        workflow = MeetingWorkflow.objects.get(id=context.get("w"))
        org = workflow.user.organization
        access_token = org.slack_integration.access_token
        show_meeting_context = {
            "w": context.get("w"),
            "original_message_channel": context.get("original_message_channel"),
            "original_message_timestamp": context.get("original_message_timestamp"),
        }
        if check_contact_last_name(workflow.id):
            update_res = slack_requests.update_channel_message(
                context.get("original_message_channel"),
                context.get("original_message_timestamp"),
                access_token,
                block_set=get_block_set("initial_meeting_interaction", {"w": context.get("w")}),
            )
    blocks = get_block_set("show_meeting_contacts", show_meeting_context,)
    # replace the contact in the participants list
    data = {
        "trigger_id": trigger_id,
        "view_id": view_id,
        "view": {
            "type": "modal",
            "callback_id": slack_const.ZOOM_MEETING__VIEW_MEETING_CONTACTS,
            "title": {"type": "plain_text", "text": "Contacts"},
            "blocks": blocks,
        },
    }
    try:
        res = slack_requests.generic_request(url, data, access_token=access_token)
    except InvalidBlocksException as e:
        return logger.exception(
            f"Failed To load update meeting contact modal for user with workflow {str(workflow.id)} email {workflow.user.email} {e}"
        )
    except InvalidBlocksFormatException as e:
        return logger.exception(
            f"Failed To load update meeting contact modal for user with workflow {str(workflow.id)} email {workflow.user.email} {e}"
        )
    except UnHandeledBlocksException as e:
        return logger.exception(
            f"Failed To load update meeting contact modal for user with workflow {str(workflow.id)} email {workflow.user.email} {e}"
        )
    except InvalidAccessToken as e:
        return logger.exception(
            f"Failed To load update meeting contact modal for user with workflow {str(workflow.id)} email {workflow.user.email} {e}"
        )

    return


@processor()
def process_edit_meeting_contact(payload, context):
    """This Submission returns the update form stacked on top of the view contacts form"""

    return {
        "response_action": "push",
        "view": {
            "type": "modal",
            "title": {"type": "plain_text", "text": "Edit Contact"},
            "submit": {"type": "plain_text", "text": "Save"},
            "blocks": get_block_set("edit_meeting_contacts", context,),
            "callback_id": slack_const.ZOOM_MEETING__UPDATE_PARTICIPANT_DATA,
            "private_metadata": json.dumps(context),
        },
    }


@processor()
def process_save_contact_data(payload, context):
    workflow = MeetingWorkflow.objects.get(id=context.get("w"))
    # update the old view to change edit contact to submit again

    state = payload["view"]["state"]["values"]
    ## save the checked contacts to the operations list
    create = []
    update = []
    for val in state.values():
        if val.get("CREATE") and len(val["CREATE"]["selected_options"]):
            create.append(val["CREATE"]["selected_options"][0]["value"])
        elif val.get("UPDATE") and len(val["UPDATE"]["selected_options"]):
            update.append(val["UPDATE"]["selected_options"][0]["value"])

    if not len(workflow.operations_list):
        workflow.operations_list = []
    if len(create):

        workflow.operations_list = [
            *workflow.operations_list,
            *[
                f"{sf_consts.MEETING_REVIEW__CREATE_CONTACTS}.{str(workflow.id)},{form}"
                for form in create
            ],
        ]

    if len(update):
        workflow.operations_list = [
            *workflow.operations_list,
            *[
                f"{sf_consts.MEETING_REVIEW__UPDATE_CONTACTS}.{str(workflow.id)},{form}"
                for form in update
            ],
        ]

    workflow.save()

    return


@log_all_exceptions
@processor(required_context=[])
def process_create_task(payload, context):

    user = User.objects.get(id=context.get("u"))

    slack_access_token = user.organization.slack_integration.access_token
    # get state - state contains the values based on the block_id

    state = payload["view"]["state"]["values"]

    activity_date = [
        value.get("selected_date") for value in state.get("managr_task_datetime", {}).values()
    ]
    owner_id = [
        value.get("selected_option") for value in state.get("managr_task_assign_to", {}).values()
    ]
    status = [
        value.get("selected_option") for value in state.get("managr_task_status", {}).values()
    ]

    if status[0] == None:
        status = "Not Started"
    else:
        status = status[0].get("value")

    related_to_type = [
        value.get("selected_option")
        for value in state.get("managr_task_related_to_resource", {}).values()
    ]
    related_to = [
        value.get("selected_option") for value in state.get("managr_task_related_to", {}).values()
    ]
    if len(related_to) and len(related_to_type):
        related_to = (
            model_routes.get(related_to_type[0].get("value"))
            .get("model")
            .objects.get(id=related_to[0].get("value"))
            .integration_id
        )

    data = {
        "Subject": state.get("managr_task_subject", {}).get("plain_input", {}).get("value"),
        "ActivityDate": activity_date[0] if len(activity_date) else None,
        "OwnerId": owner_id[0].get("value") if len(owner_id) else None,
        "Status": status,
    }

    if related_to and related_to_type:

        if related_to_type[0].get("value") != sf_consts.RESOURCE_SYNC_LEAD:
            data["WhatId"] = related_to
        else:
            data["WhoId"] = related_to

    try:

        _process_create_task.now(context.get("u"), data)

    except FieldValidationError as e:

        return {
            "response_action": "push",
            "view": {
                "type": "modal",
                "title": {"type": "plain_text", "text": "An Error Occured"},
                "blocks": get_block_set(
                    "error_modal",
                    {
                        "message": f":no_entry: Uh-Ohhh it looks like we found an error, this error is based on Validations set up by your org\n *Error* : _{e}_"
                    },
                ),
            },
        }
    except RequiredFieldError as e:

        return {
            "response_action": "push",
            "view": {
                "type": "modal",
                "title": {"type": "plain_text", "text": "An Error Occurred"},
                "blocks": get_block_set(
                    "error_modal",
                    {
                        "message": f":no_entry: Uh-Ohhh it looks like we found an error, this error is based on Required fields from Salesforce\n *Error* : _{e}_"
                    },
                ),
            },
        }
    except SFNotFoundError as e:

        return {
            "response_action": "push",
            "view": {
                "type": "modal",
                "title": {"type": "plain_text", "text": "An Error Occurred"},
                "blocks": get_block_set(
                    "error_modal",
                    {
                        "message": f":no_entry: Uh-Ohhh it looks like we found an error, this error one of the resources does not exist\n *Error* : _{e}_"
                    },
                ),
            },
        }

    except UnhandledSalesforceError as e:

        return {
            "response_action": "push",
            "view": {
                "type": "modal",
                "title": {"type": "plain_text", "text": "An Error Occurred"},
                "blocks": get_block_set(
                    "error_modal",
                    {
                        "message": f":no_entry: Uh-Ohhh it looks like we found an error, this error is new to us\n *Error* : _{e}_"
                    },
                ),
            },
        }

    # TODO: [MGR-830] Change this to be api.update method instead PB 03/31/21
    return {
        "response_action": "update",
        "view": {
            "type": "modal",
            "title": {"type": "plain_text", "text": "Task Created"},
            "blocks": [
                block_builders.simple_section(
                    ":white_check_mark: Successfully created task!", "mrkdwn"
                )
            ],
        },
    }


@log_all_exceptions
@slack_api_exceptions(rethrow=True)
@processor(required_context=[])
def process_schedule_meeting(payload, context):
    u = User.objects.get(id=context.get("u"))
    type = context.get("type", None)
    data = payload["view"]["state"]["values"]
    trigger_id = payload["trigger_id"]
    view_id = payload["view"]["id"]
    org = u.organization
    meta_data = json.loads(payload["view"]["private_metadata"])
    access_token = org.slack_integration.access_token
    description = data["meeting_description"]["meeting_data"]["value"]
    url = slack_const.SLACK_API_ROOT + slack_const.VIEWS_UPDATE
    participants = []
    if data["meeting_participants"][f"GET_USER_CONTACTS?u={u.id}"]["selected_options"]:
        query_data = Contact.objects.filter(
            id__in=list(
                map(
                    lambda val: val["value"],
                    data["meeting_participants"][f"GET_USER_CONTACTS?u={u.id}"]["selected_options"],
                )
            )
        ).values("email", "secondary_data")
        for participant in query_data:
            participants.append(
                {
                    "email": participant["email"],
                    "name": participant["secondary_data"]["Name"],
                    "status": "noreply",
                }
            )
    zoom_data = {
        "meeting_topic": data["meeting_topic"]["meeting_data"]["value"],
        "meeting_date": data["meeting_date"]["meeting_data"]["selected_date"],
        "meeting_hour": data["meeting_hour"]["meeting_data"]["selected_option"]["value"],
        "meeting_minute": data["meeting_minute"]["meeting_data"]["selected_option"]["value"],
        "meeting_time": data["meeting_time"]["meeting_data"]["selected_option"]["value"],
        "meeting_duration": data["meeting_duration"]["meeting_data"]["selected_option"]["value"],
    }
    loading_data = {
        "trigger_id": trigger_id,
        "view_id": view_id,
        "view": {
            "type": "modal",
            "title": {"type": "plain_text", "text": "Loading"},
            "blocks": get_block_set(
                "loading",
                {
                    "message": ":rocket: Creating your Zoom meeting and inviting contacts!",
                    "fill": True,
                },
            ),
        },
    }
    try:
        res = slack_requests.generic_request(url, loading_data, access_token=access_token)
        zoom_res = emit_process_schedule_zoom_meeting(u, zoom_data)
        cal_res = emit_create_calendar_event(
            u,
            zoom_res["topic"],
            zoom_res["start_time"],
            participants,
            zoom_res["join_url"],
            description,
        )
        return {
            "response_action": "update",
            "view": {
                "type": "modal",
                "title": {"type": "plain_text", "text": "Success"},
                "blocks": [block_builders.simple_section("Zoom meeting successfully scheduled")],
            },
        }
    except InvalidBlocksException as e:
        return logger.exception(
            f"Faild to update Zoom Schedule Meeting modal for user {u.email}, {e}"
        )
    except InvalidBlocksFormatException as e:
        return logger.exception(
            f"Faild to update Zoom Schedule Meeting modal for user {u.email}, {e}"
        )
    except UnHandeledBlocksException as e:
        return logger.exception(
            f"Faild to update Zoom Schedule Meeting modal for user {u.email}, {e}"
        )
    except InvalidAccessToken as e:
        return logger.exception(
            f"Faild to update Zoom Schedule Meeting modal for user {u.email}, {e}"
        )
    return


@log_all_exceptions
@slack_api_exceptions(rethrow=True)
@processor(required_context=["u"])
def process_add_contacts_to_cadence(payload, context):
    meta_data = json.loads(payload["view"]["private_metadata"])
    u = User.objects.get(id=context.get("u"))
    cadence_id = payload["view"]["state"]["values"]["select_cadence"][
        f"GET_CADENCE_OPTIONS?u={context.get('u')}"
    ]["selected_option"]["value"]
    trigger_id = payload["trigger_id"]
    view_id = payload["view"]["id"]

    org = u.organization
    access_token = org.slack_integration.access_token
    url = slack_const.SLACK_API_ROOT + slack_const.VIEWS_UPDATE
    contacts = [
        option["value"]
        for option in payload["view"]["state"]["values"]["select_people"][
            f"{slack_const.GET_PEOPLE_OPTIONS}?u={u.id}&resource_id={context.get('resource_id')}&resource_type={context.get('resource_type')}"
        ]["selected_options"]
    ]
    loading_data = {
        "trigger_id": trigger_id,
        "view_id": view_id,
        "view": {
            "type": "modal",
            "title": {"type": "plain_text", "text": "Loading"},
            "blocks": get_block_set(
                "loading",
                {"message": ":rocket: Putting contacts into your Cadence", "fill": True,},
            ),
        },
    }
    if len(contacts):
        res = slack_requests.generic_request(url, loading_data, access_token=access_token)
        success = 0
        failed = 0
        created = 0
        for person in contacts:
            person_res = emit_add_cadence_membership(person, cadence_id)
            if person_res["status"] == "Success":
                success += 1
            elif person_res["status"] == "Created":
                success += 1
                created += 1
            else:
                failed += 1
        logger.info(
            f"{success} out of {success + failed} added to cadence and {created} People created in Salesloft"
        )
        message = (
            f"{success}/{success + failed} added to cadence ({created} new People imported to Salesloft)"
            if created > 0
            else f"{success}/{success + failed} added to cadence"
        )
        update_res = slack_requests.send_ephemeral_message(
            u.slack_integration.channel,
            access_token,
            meta_data["slack_id"],
            block_set=[block_builders.simple_section(message)],
        )
        return
    else:
        update_res = slack_requests.send_ephemeral_message(
            u.slack_integration.channel,
            access_token,
            meta_data["slack_id"],
            block_set=[block_builders.simple_section(f"No people associated for {resource_id}")],
        )
        return


@log_all_exceptions
@slack_api_exceptions(rethrow=True)
@processor(required_context=["u"])
def process_add_contacts_to_sequence(payload, context):
    meta_data = json.loads(payload["view"]["private_metadata"])
    u = User.objects.get(id=context.get("u"))
    sequence_id = payload["view"]["state"]["values"]["select_sequence"][
        f"GET_SEQUENCE_OPTIONS?u={context.get('u')}"
    ]["selected_option"]["value"]
    trigger_id = payload["trigger_id"]
    view_id = payload["view"]["id"]

    org = u.organization
    access_token = org.slack_integration.access_token
    url = slack_const.SLACK_API_ROOT + slack_const.VIEWS_UPDATE
    contacts = [
        option["value"]
        for option in payload["view"]["state"]["values"]["select_people"][
            f"{slack_const.GET_PEOPLE_OPTIONS}?u={u.id}&resource_id={context.get('resource_id')}&resource_type={context.get('resource_type')}"
        ]["selected_options"]
    ]
    loading_data = {
        "trigger_id": trigger_id,
        "view_id": view_id,
        "view": {
            "type": "modal",
            "title": {"type": "plain_text", "text": "Loading"},
            "blocks": get_block_set(
                "loading",
                {"message": ":rocket: Putting contacts into your Cadence", "fill": True,},
            ),
        },
    }
    if len(contacts):
        res = slack_requests.generic_request(url, loading_data, access_token=access_token)
        success = 0
        failed = 0
        created = 0
        for contact in contacts:
            prospect_res = emit_add_sequence_state(contact, sequence_id)
            if prospect_res["status"] == "Success":
                success += 1
            elif prospect_res["status"] == "Created":
                success += 1
                created += 1
            else:
                failed += 1
        logger.info(
            f"{success} out of {success + failed} added to sequence and {created} Prospects created in Outreach"
        )
        message = (
            f"{success}/{success + failed} added to sequence ({created} new Prospects imported to Outreach)"
            if created > 0
            else f"{success}/{success + failed} added to sequence"
        )
        return {
            "response_action": "update",
            "view": {
                "type": "modal",
                "title": {"type": "plain_text", "text": "Success"},
                "blocks": [block_builders.simple_section(message)],
            },
        }
    else:
        update_res = slack_requests.send_ephemeral_message(
            u.slack_integration.channel,
            access_token,
            meta_data["slack_id"],
            block_set=[block_builders.simple_section(f"No people associated for {resource_id}")],
        )
        return


@log_all_exceptions
@slack_api_exceptions(rethrow=True)
@processor(required_context=["u"])
def process_get_notes(payload, context):
    meta_data = json.loads(payload["view"]["private_metadata"])
    u = User.objects.get(id=context.get("u"))
    trigger_id = payload["trigger_id"]
    view_id = payload["view"]["id"]
    org = u.organization
    access_token = org.slack_integration.access_token
    resource_id = payload["view"]["state"]["values"]["select_opp"][
        f"{slack_const.GET_LOCAL_RESOURCE_OPTIONS}?u={u.id}&resource=Opportunity"
    ]["selected_option"]["value"]
    opportunity = Opportunity.objects.get(id=resource_id)
    note_data = (
        OrgCustomSlackFormInstance.objects.filter(resource_id=resource_id)
        .filter(is_submitted=True)
        .values_list(
            "submission_date",
            "saved_data__meeting_type",
            "saved_data__meeting_comments",
            "saved_data__StageName",
            "previous_data__StageName",
        )
    )
    note_blocks = [block_builders.header_block(f"Notes for {opportunity.name}")]
    if note_data:
        for note in note_data:
            date = note[0].date()
            current_stage = note[3]
            previous_stage = note[4]
            block_message = f"*{date} - {note[1]}*\n"
            if current_stage and previous_stage:
                if current_stage != previous_stage:
                    block_message += f"Stage: ~{previous_stage}~ :arrow_right: {current_stage} \n"
            block_message += f"\nNotes:\n {note[2]}"
            note_blocks.append(block_builders.simple_section(block_message, "mrkdwn"))
            note_blocks.append({"type": "divider"})
    url = slack_const.SLACK_API_ROOT + slack_const.VIEWS_OPEN
    # loading_data = {
    #     "trigger_id": trigger_id,
    #     "view_id": view_id,
    #     "view": {
    #         "type": "modal",
    #         "title": {"type": "plain_text", "text": "Loading"},
    #         "blocks": get_block_set(
    #             "loading",
    #             {
    #                 "message": ":notebook_with_decorative_cover: Putting your notes together",
    #                 "fill": True,
    #             },
    #         ),
    #     },
    # }
    data = {
        "trigger_id": context.get("trigger_id"),
        "view_id": view_id,
        "view": {
            "type": "modal",
            "callback_id": "NONE",
            "title": {"type": "plain_text", "text": "Notes"},
            "blocks": note_blocks,
        },
    }
    loading_res = slack_requests.generic_request(url, data, access_token=access_token)
    # update_res = slack_requests.send_channel_message(
    #     u.slack_integration.channel, access_token, block_set=note_blocks,
    # )
    return


@log_all_exceptions
@slack_api_exceptions(rethrow=True)
@processor(required_context=["u"])
def process_send_recaps(payload, context):
    values = payload["view"]["state"]["values"]
    type = context.get("type")
    channels = list(values["__send_recap_to_channels"].values())[0]["selected_conversations"]
    leadership = [
        option["value"]
        for option in values["__send_recap_to_leadership"][
            f"GET_LOCAL_RESOURCE_OPTIONS?u={context.get('u')}&resource=User&field_id=e286d1d5-5447-47e6-ad55-5f54fdd2b00d"
        ]["selected_options"]
    ]
    reps = [
        option["value"]
        for option in values["__send_recap_to_reps"][
            f"GET_LOCAL_RESOURCE_OPTIONS?u={context.get('u')}&resource=User&field_id=fae88a10-53cc-470e-86ec-32376c041893"
        ]["selected_options"]
    ]
    if type == "meeting":
        workflow = MeetingWorkflow.objects.get(id=context.get("workflow_id"))
        # collect forms for resource meeting_review and if stages any stages related forms
        update_forms = workflow.forms.filter(
            template__form_type__in=[
                slack_const.FORM_TYPE_UPDATE,
                slack_const.FORM_TYPE_STAGE_GATING,
            ]
        )
    else:
        form_id = context.get("form_id")
        command_form = OrgCustomSlackFormInstance.objects.get(id=form_id)
        update_forms = [command_form]
    update_form_ids = []
    # aggregate the data
    send_to_recaps = {"channels": channels, "leadership": leadership, "reps": reps}
    data = dict()
    for form in update_forms:
        update_form_ids.append(str(form.id))
        data = {**data, **form.saved_data}
    _send_recap(update_form_ids, send_to_recaps)
    return


@log_all_exceptions
@slack_api_exceptions(rethrow=True)
@processor(required_context=["opp_item_id"])
def process_update_product(payload, context):
    has_error = False
    state = payload["view"]["state"]["values"]
    user = User.objects.get(id=context.get("u"))
    view_id = payload["view"]["id"]
    type = context.get("type", None)
    main_form = OrgCustomSlackFormInstance.objects.get(id=context.get("main_form"))
    product_form = user.custom_slack_form_instances.filter(
        template__resource="OpportunityLineItem"
    ).first()
    opp_line_item = OpportunityLineItem.objects.filter(id=product_form.resource_id).first()
    if (
        "HasSchedule" in opp_line_item.secondary_data
        and opp_line_item.secondary_data["HasSchedule"]
    ):
        state.pop("Quantity")
    product_form.save_form(state)
    slack_access_token = user.organization.slack_integration.access_token
    url = slack_const.SLACK_API_ROOT + slack_const.VIEWS_PUSH
    attempts = 1
    while True:
        sf = user.salesforce_account
        try:
            resource = product_form.resource_object.update_in_salesforce(
                str(user.id), product_form.saved_data
            )
            break
        except FieldValidationError as e:
            has_error = True
            blocks = (
                get_block_set(
                    "error_modal",
                    {
                        "message": f":no_entry: Uh-Ohhh it looks like we found an error, this error is based on Validations set up by your org\n *Error* : _{e}_"
                    },
                ),
            )
            break
        except RequiredFieldError as e:
            has_error = True
            blocks = get_block_set(
                "error_modal",
                {
                    "message": f":no_entry: Uh-Ohhh it looks like we found an error, this error is based on Required fields from Salesforce\n *Error* : _{e}_"
                },
            )
            break
        except UnhandledSalesforceError as e:
            has_error = True
            blocks = get_block_set(
                "error_modal",
                {
                    "message": f":no_entry: Uh-Ohhh it looks like we found an error, this error is new to us please see below\n *Error* : _{e}_"
                },
            )
            break
        except SFNotFoundError as e:
            has_error = True
            blocks = get_block_set(
                "error_modal",
                {
                    "message": f":no_entry: Uh-Ohhh it looks like we found an error, this error one of the resources does not exist\n *Error* : _{e}_"
                },
            )
            break
        except TokenExpired:
            if attempts >= 5:
                logger.exception(
                    f"Failed to Update data for user {str(user.id)} after {attempts} tries"
                )
                has_error = True
                blocks = get_block_set(
                    "error_modal",
                    {
                        "message": f":no_entry: Uh-Ohhh it looks like we've had an issue with your token\n *Error* : _{e}_"
                    },
                )
                break
            else:
                sf.regenerate_token()
                attempts += 1
        except ConnectionResetError:
            if attempts >= 5:
                logger.exception(
                    f"Failed to Update data for user {str(user.id)} after {attempts} tries because of connection error"
                )
                has_error = True
                blocks = get_block_set(
                    "error_modal",
                    {
                        "message": f":no_entry: Uh-Ohhh we had an error connecting to your salesforce instance please try again"
                    },
                )
                break
            else:
                time.sleep(2)
                attempts += 1
    if has_error:
        # add a special button to return the user back to edit their form
        # this is only required for single page forms
        blocks = [
            *blocks,
            block_builders.actions_block(
                [
                    block_builders.simple_button_block(
                        "return to form",
                        str(main_form.id),
                        style="primary",
                        action_id=slack_const.RETURN_TO_FORM_MODAL,
                    )
                ]
            ),
        ]
        url = slack_const.SLACK_API_ROOT + slack_const.VIEWS_UPDATE
        error_view_data = {
            "view_id": view_id,
            "view": {
                "type": "modal",
                "title": {"type": "plain_text", "text": "Error"},
                "blocks": blocks,
                "private_metadata": json.dumps(context),
            },
        }
        try:
            return slack_requests.generic_request(
                url, error_view_data, access_token=slack_access_token
            )
        except Exception as e:
            return logger.exception(
                f"Failed To Update via command for user  {str(user.id)} email {user.email} {e}"
            )
    pm = json.loads(payload["view"]["private_metadata"])
    product_form.is_submitted = True
    product_form.submission_date = timezone.now()
    product_form.update_source = type
    product_form.save()
    text = "Success"
    message = ":white_check_mark: Successfully updated product"
    if type == "alert":
        instance = AlertInstance.objects.get(id=context.get("alert_id"))
        alert_instances = AlertInstance.objects.filter(
            invocation=instance.invocation,
            channel=context.get("channel_id"),
            config_id=instance.config_id,
        ).filter(completed=False)
        alert_instance = alert_instances.first()
        alert_template = alert_instance.template
        text = alert_template.title
        blocks = [
            block_builders.header_block(f"{len(alert_instances)} results for workflow {text}"),
        ]
        alert_instances = custom_paginator(alert_instances, page=int(context.get("current_page")))
        for alert_instance in alert_instances.get("results", []):
            blocks = [
                *blocks,
                *get_block_set(
                    "alert_instance",
                    {
                        "instance_id": str(alert_instance.id),
                        "current_page": int(context.get("current_page")),
                    },
                ),
            ]
            alert_instance.rendered_text = alert_instance.render_text()
            alert_instance.save()
        if len(blocks):
            blocks = [
                *blocks,
                *custom_paginator_block(
                    alert_instances,
                    instance.invocation,
                    context.get("channel_id"),
                    instance.config_id,
                ),
            ]

        slack_requests.update_channel_message(
            context.get("channel_id"),
            context.get("message_ts"),
            slack_access_token,
            block_set=blocks,
        )
    else:
        return {
            "response_action": "update",
            "view": {
                "type": "modal",
                "title": {"type": "plain_text", "text": "Success"},
                "blocks": get_block_set("success_text_modal", {"message": message}),
            },
        }


@log_all_exceptions
@slack_api_exceptions(rethrow=True)
@processor(required_context=["f"])
def process_submit_product(payload, context):
    # get context
    state = payload["view"]["state"]["values"]
    current_form_ids = context.get("f").split(",")
    type = context.get("type", None)
    workflow_id = context.get("w", None)
    if workflow_id:
        workflow = MeetingWorkflow.objects.get(id=workflow_id)
    has_error = False
    blocks = None
    user = User.objects.get(id=context.get("u"))
    trigger_id = payload["trigger_id"]
    view_id = payload["view"]["id"]
    product_form_id = context.get("product_form", None)
    current_forms = user.custom_slack_form_instances.filter(id__in=current_form_ids)
    main_form = (
        current_forms.filter(template__form_type__in=["UPDATE", "CREATE"])
        .exclude(template__resource="OpportunityLineItem")
        .first()
    )
    if product_form_id:
        product_form = user.custom_slack_form_instances.get(id=product_form_id)
        product_form.save_form(state)
    slack_access_token = user.organization.slack_integration.access_token
    url = slack_const.SLACK_API_ROOT + slack_const.VIEWS_UPDATE
    loading_view_data = {
        "trigger_id": trigger_id,
        "view_id": view_id,
        "view": {
            "type": "modal",
            "title": {"type": "plain_text", "text": "Loading"},
            "blocks": get_block_set(
                "loading",
                {
                    "message": ":exclamation: SFDC is currently a bit slow :zany_face:, please wait a few seconds and click 'try again'",
                    "fill": True,
                },
            ),
            "private_metadata": json.dumps(context),
        },
    }
    try:
        res = slack_requests.generic_request(
            url, loading_view_data, access_token=slack_access_token
        )
    except Exception as e:
        return logger.exception(
            f"Failed To Update via command for user  {str(user.id)} email {user.email} {e}"
        )
    attempts = 1
    while True:
        sf = user.salesforce_account
        try:
            opp = Opportunity.objects.get(id=main_form.resource_id)
            entry = PricebookEntry.objects.get(
                integration_id=product_form.saved_data["PricebookEntryId"]
            )
            product_data = {
                **product_form.saved_data,
                "OpportunityId": opp.integration_id,
            }
            if "UnitPrice" not in product_form.saved_data:
                product_data["UnitPrice"] = str(entry.unit_price)
            if (
                "UnitPrice" in product_form.saved_data
                and product_form.saved_data["UnitPrice"] is None
            ):
                product_data["UnitPrice"] = str(entry.unit_price)
            resource = OpportunityLineItem.create_in_salesforce(product_data, context.get("u"))
            product_form.is_submitted = True
            product_form.submission_date = timezone.now()
            product_form.update_source = context.get("type")
            product_form.save()
            break
        except FieldValidationError as e:
            has_error = True
            blocks = (
                get_block_set(
                    "error_modal",
                    {
                        "message": f":no_entry: Uh-Ohhh it looks like we found an error, this error is based on Validations set up by your org\n *Error* : _{e}_"
                    },
                ),
            )
            break

        except RequiredFieldError as e:
            has_error = True
            blocks = get_block_set(
                "error_modal",
                {
                    "message": f":no_entry: Uh-Ohhh it looks like we found an error, this error is based on Required fields from Salesforce\n *Error* : _{e}_"
                },
            )
            break
        except UnhandledSalesforceError as e:
            has_error = True
            blocks = get_block_set(
                "error_modal",
                {
                    "message": f":no_entry: Uh-Ohhh it looks like we found an error, this error is new to us please see below\n *Error* : _{e}_"
                },
            )
            break

        except SFNotFoundError as e:
            has_error = True
            blocks = get_block_set(
                "error_modal",
                {
                    "message": f":no_entry: Uh-Ohhh it looks like we found an error, this error one of the resources does not exist\n *Error* : _{e}_"
                },
            )
            break

        except TokenExpired:
            if attempts >= 5:
                logger.exception(
                    f"Failed to Update data for user {str(user.id)} after {attempts} tries"
                )
                has_error = True
                blocks = get_block_set(
                    "error_modal",
                    {
                        "message": f":no_entry: Uh-Ohhh it looks like we've had an issue with your token\n *Error* : _{e}_"
                    },
                )
                break
            else:
                sf.regenerate_token()
                attempts += 1

        except ConnectionResetError:
            if attempts >= 5:
                logger.exception(
                    f"Failed to Update data for user {str(user.id)} after {attempts} tries because of connection error"
                )
                has_error = True
                blocks = get_block_set(
                    "error_modal",
                    {
                        "message": f":no_entry: Uh-Ohhh we had an error connecting to your salesforce instance please try again"
                    },
                )
                break
            else:
                time.sleep(2)
                attempts += 1
        except Exception as e:
            if attempts >= 5:
                logger.exception(
                    f"Failed to Update data for user {str(user.id)} after {attempts} tries because of connection error"
                )
                has_error = True
                blocks = get_block_set(
                    "error_modal",
                    {
                        "message": f":no_entry: Uh-Ohhh we had an unexpected error please try again: {e}"
                    },
                )
                break
            else:
                time.sleep(2)
                attempts += 1
    if has_error:
        blocks = [
            *blocks,
            block_builders.actions_block(
                [
                    block_builders.simple_button_block(
                        "return to form",
                        product_form_id,
                        style="primary",
                        action_id=slack_const.RETURN_TO_FORM_MODAL,
                    )
                ]
            ),
        ]
        url = slack_const.SLACK_API_ROOT + slack_const.VIEWS_UPDATE
        error_view_data = {
            "trigger_id": trigger_id,
            "view_id": view_id,
            "view": {
                "type": "modal",
                "title": {"type": "plain_text", "text": "Error"},
                "blocks": blocks,
                "private_metadata": json.dumps(context),
                "external_id": f"{'add_product'}.{str(uuid.uuid4())}",
            },
        }
        try:
            return slack_requests.generic_request(
                url, error_view_data, access_token=slack_access_token
            )
        except Exception as e:
            return logger.exception(
                f"Failed To Update via command for user  {str(user.id)} email {user.email} {e}"
            )
    blocks = (
        get_block_set(
            "update_modal_block_set",
            context={
                "type": context.get("type"),
                "f": context.get("f"),
                "u": context.get("u"),
                "resource_type": main_form.template.resource,
                "resource_id": main_form.resource_id,
            },
        )
        if type == "command"
        else get_block_set(
            "meeting_review_modal",
            context={
                "w": workflow_id,
                "f": str(workflow.forms.filter(template__form_type="UPDATE").first().id),
                "type": "meeting",
            },
        )
    )
    params = [
        f"f={str(main_form.id)}",
        f"product_form={str(product_form.id)}",
        f"type={type}",
    ]
    if workflow_id:
        params.append(f"w={workflow_id}")

    if type != "meeting":
        blocks.append(
            block_builders.actions_block(
                [
                    block_builders.simple_button_block(
                        "Add Product",
                        "ADD_PRODUCT",
                        action_id=action_with_params(
                            slack_const.PROCESS_ADD_PRODUCTS_FORM, params=params,
                        ),
                    )
                ],
                block_id="ADD_PRODUCT_BUTTON",
            ),
        )
        try:
            current_products = user.salesforce_account.list_resource_data(
                "OpportunityLineItem",
                0,
                filter=["AND IsDeleted = false", f"AND OpportunityId = '{opp.integration_id}'"],
            )
        except Exception as e:
            logger.exception(
                f"Error retreiving products for user {user.email} during submit product refresh: {e}"
            )
            blocks.append(
                block_builders.simple_section(
                    "There was an error retreiving your products :exclamation:", "mrkdwn"
                )
            )
        if current_products:
            for product in current_products:
                product_block = get_block_set(
                    "current_product_blockset",
                    {
                        "opp_item_id": product.integration_id,
                        "product_data": {
                            "name": product.name,
                            "quantity": product.quantity,
                            "total": product.total_price,
                        },
                        "u": str(user.id),
                        "main_form": str(main_form.id),
                    },
                )
                blocks.append(product_block)
    data = {
        "view_id": context.get("view_id"),
        "view": {
            "type": "modal",
            "callback_id": slack_const.COMMAND_FORMS__SUBMIT_FORM,
            "title": {"type": "plain_text", "text": f"Update {main_form.template.resource}"},
            "blocks": blocks,
            "private_metadata": json.dumps(context),
            "external_id": f"update_modal_block_set.{str(uuid.uuid4())}",
        },
    }

    data["view"]["submit"] = {"type": "plain_text", "text": "Submit", "emoji": True}

    slack_requests.generic_request(
        slack_const.SLACK_API_ROOT + slack_const.VIEWS_UPDATE,
        data,
        access_token=user.organization.slack_integration.access_token,
    )

    return {
        "response_action": "update",
        "view": {
            "type": "modal",
            "title": {"type": "plain_text", "text": "Product Created"},
            "blocks": [
                block_builders.simple_section(
                    ":white_check_mark: Successfully created product!", "mrkdwn"
                )
            ],
        },
    }


def handle_view_submission(payload):
    """
    This takes place when a modal's Submit button is clicked.
    """
    switcher = {
        slack_const.ZOOM_MEETING__SELECTED_RESOURCE: process_zoom_meeting_attach_resource,
        slack_const.ZOOM_MEETING__PROCESS_MEETING_SENTIMENT: process_zoom_meeting_data,
        slack_const.ZOOM_MEETING__EDIT_CONTACT: process_edit_meeting_contact,
        slack_const.ZOOM_MEETING__PROCESS_STAGE_NEXT_PAGE: process_stage_next_page,
        slack_const.ZOOM_MEETING__UPDATE_PARTICIPANT_DATA: process_update_meeting_contact,
        slack_const.ZOOM_MEETING__SAVE_CONTACTS: process_save_contact_data,
        slack_const.PROCESS_DIGEST_ATTACH_RESOURCE: process_digest_attach_resource,
        slack_const.COMMAND_FORMS__SUBMIT_FORM: process_submit_resource_data,
        slack_const.COMMAND_FORMS__PROCESS_NEXT_PAGE: process_next_page_slack_commands_form,
        slack_const.COMMAND_CREATE_TASK: process_create_task,
        slack_const.ZOOM_MEETING__SCHEDULE_MEETING: process_schedule_meeting,
        slack_const.ADD_TO_CADENCE: process_add_contacts_to_cadence,
        slack_const.ADD_TO_SEQUENCE: process_add_contacts_to_sequence,
        slack_const.GET_NOTES: process_get_notes,
        slack_const.PROCESS_SEND_RECAPS: process_send_recaps,
        slack_const.PROCESS_ADD_PRODUCTS_FORM: process_add_products_form,
        slack_const.PROCESS_UPDATE_PRODUCT: process_update_product,
        slack_const.PROCESS_SUBMIT_PRODUCT: process_submit_product,
    }

    callback_id = payload["view"]["callback_id"]
    view_context = json.loads(payload["view"]["private_metadata"])
    return switcher.get(callback_id, NO_OP)(payload, view_context)
