import json
import pdb
import pytz
from datetime import datetime
import logging
import uuid
import time


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
from managr.organization.models import Organization, Contact, Account
from managr.core.models import User
from managr.core.background import emit_create_calendar_event
from managr.opportunity.models import Opportunity
from managr.zoom.models import ZoomMeeting
from managr.salesforce.models import MeetingWorkflow
from managr.salesforce import constants as sf_consts
from managr.slack import constants as slack_const
from managr.slack.models import OrgCustomSlackFormInstance
from managr.slack.helpers import block_builders
from managr.slack.helpers import requests as slack_requests
from managr.slack.helpers.utils import action_with_params, NO_OP, processor, block_finder
from managr.slack.helpers.block_sets import get_block_set
from managr.salesforce.adapter.models import ContactAdapter, OpportunityAdapter, TaskAdapter
from managr.zoom import constants as zoom_consts
from managr.salesforce.routes import routes as model_routes
from managr.salesforce.adapter.routes import routes as adapter_routes
from managr.salesforce.background import (
    _process_create_new_resource,
    _process_create_task,
    emit_meeting_workflow_tracker,
    emit_add_update_to_sf,
    _send_recap,
)
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

logger = logging.getLogger("managr")


@log_all_exceptions
@processor(required_context=["w", "form_type"])
def process_stage_next_page(payload, context):
    workflow = MeetingWorkflow.objects.get(id=context.get("w"))
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

    trigger_id = payload["trigger_id"]
    view_id = view["id"]
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
                    "message": ":exclamation:Please *DO NOT* close this window :exclamation:... SFDC is currently a bit slow :zany_face:",
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
        get_block_set("create_meeting_task", {"w": str(workflow.id)}),
    ]
    try:
        res = slack_requests.update_channel_message(
            channel, ts, slack_access_token, block_set=block_set
        )
    except Exception as e:
        return logger.exception(
            f"Failed To Send Submit Interaction for user  with workflow {str(workflow.id)} email {workflow.user.email} {e}"
        )
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
    main_form = current_forms.filter(template__form_type__in=["UPDATE", "CREATE"]).first()
    print(main_form.template.form_type)
    stage_forms = current_forms.exclude(template__form_type__in=["UPDATE", "CREATE"])
    stage_form_data_collector = {}
    for form in stage_forms:
        form.update_source = type
        form.save_form(state)
        stage_form_data_collector = {**stage_form_data_collector, **form.saved_data}
    if not len(stage_forms):
        if main_form.template.form_type == "UPDATE":
            main_form.update_source = type
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
                    "message": ":exclamation:Please *DO NOT* close this window :exclamation:... SFDC is currently a bit slow :zany_face:",
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
            return slack_requests.generic_request(
                url, select_resource_view_data, access_token=slack_access_token
            )
        except Exception as e:
            return logger.exception(
                f"Failed To Update the view for the workflow {str(user.id)} email {user.email} {e}"
            )

    else:
        current_forms.update(is_submitted=True, submission_date=timezone.now())

        # update the channel message to clear it
        if main_form.template.form_type == "CREATE":
            text = f"Managr created {main_form.resource_type}"
            message = f"Successfully created *{main_form.resource_type}* _{resource.name if resource.name else resource.email}_"

        else:
            text = f"Managr updated {main_form.resource_type}"
            message = f"Successfully updated *{main_form.resource_type}* _{main_form.resource_object.name}_"

        if (
            all_form_data.get("__send_recap_to_leadership") is not None
            or all_form_data.get("__send_recap_to_reps") is not None
            or all_form_data.get("__send_recap_to_channels") is not None
        ):
            _send_recap(current_form_ids)
        if (
            all_form_data.get("meeting_comments") is not None
            and all_form_data.get("meeting_type") is not None
        ):
            emit_add_update_to_sf(str(main_form.id))
        url = slack_const.SLACK_API_ROOT + slack_const.VIEWS_UPDATE
        success_view_data = {
            "trigger_id": trigger_id,
            "view_id": view_id,
            "view": {
                "type": "modal",
                "title": {"type": "plain_text", "text": "Success"},
                "blocks": get_block_set("success_modal", {"message": message},),
                "private_metadata": json.dumps(context),
                "clear_on_close": True,
            },
        }
        try:
            slack_requests.generic_request(url, success_view_data, access_token=slack_access_token)

        except Exception as e:
            logger.exception(
                f"Failed To Update slack view from loading to success modal  {str(user.id)} email {user.email} {e}"
            )
            pass
        try:
            slack_requests.send_ephemeral_message(
                user.slack_integration.channel,
                user.organization.slack_integration.access_token,
                user.slack_integration.slack_id,
                text=text,
                block_set=get_block_set("success_modal", {"message": message},),
            )
        except Exception as e:
            return logger.exception(
                f"Failed to send ephemeral message to user informing them of successful update {user.email} {e}"
            )

    return {"response_action": "clear"}


@log_all_exceptions
@processor(required_context=["w"])
def process_zoom_meeting_attach_resource(payload, context):
    workflow = MeetingWorkflow.objects.get(id=context.get("w"))
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
            .exclude(template__resource="Contact")
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

    ts, channel = workflow.slack_interaction.split("|")
    # clear old forms (except contact forms)
    workflow.forms.exclude(template__resource=slack_const.FORM_RESOURCE_CONTACT).delete()
    workflow.add_form(
        meeting_resource, slack_const.FORM_TYPE_UPDATE,
    )
    try:
        # update initial interaction workflow with new resource
        res = slack_requests.update_channel_message(
            channel,
            ts,
            slack_access_token,
            block_set=get_block_set("initial_meeting_interaction", {"w": context.get("w")}),
        )
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


@processor()
def process_update_meeting_contact(payload, context):
    state = payload["view"]["state"]["values"]
    workflow = MeetingWorkflow.objects.get(id=context.get("w"))
    contact = dict(
        *filter(
            lambda contact: contact["_tracking_id"] == context.get("tracking_id"),
            workflow.meeting.participants,
        )
    )

    form = workflow.forms.get(id=contact["_form"])
    form.save_form(state)
    # reconstruct the current data with the updated data
    adapter = ContactAdapter.from_api(
        {**contact.get("secondary_data", {}), **form.saved_data}, str(workflow.user_id)
    )
    new_contact = {
        **contact,
        **adapter.as_dict,
        "id": contact.get("id", None),
        "__has_changes": True,
    }
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
    action = slack_const.VIEWS_UPDATE
    url = slack_const.SLACK_API_ROOT + action
    trigger_id = payload["trigger_id"]
    view_id = payload["view"]["id"]
    workflow = MeetingWorkflow.objects.get(id=context.get("w"))

    org = workflow.user.organization

    access_token = org.slack_integration.access_token
    blocks = get_block_set("show_meeting_contacts", {"w": context.get("w")},)

    data = {
        "trigger_id": trigger_id,
        "view_id": view_id,
        "view": {
            "type": "modal",
            "callback_id": slack_const.ZOOM_MEETING__VIEW_MEETING_CONTACTS,
            "title": {"type": "plain_text", "text": "Contacts"},
            "submit": {"type": "plain_text", "text": "Submit"},
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
            "blocks": [*get_block_set("success_modal"),],
        },
    }


@log_all_exceptions
@slack_api_exceptions(rethrow=True)
@processor(required_context=[])
def process_schedule_meeting(payload, context):
    u = User.objects.get(id=context.get("u"))
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
        updated_message = slack_requests.update_channel_message(
            meta_data["original_message_channel"],
            meta_data["original_message_timestamp"],
            access_token,
            block_set=json.dumps(meta_data["current_block"]),
        )
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
@processor(required_context=["resource_id", "u", "resource_type"])
def process_add_contacts_to_cadence(payload, context):
    u = User.objects.get(id=context.get("u"))
    cadence_id = payload["view"]["state"]["values"]["select_cadence"][
        f"GET_CADENCE_OPTIONS?u={context.get('u')}"
    ]["selected_option"]["value"]
    trigger_id = payload["trigger_id"]
    view_id = payload["view"]["id"]
    org = u.organization
    access_token = org.slack_integration.access_token
    url = slack_const.SLACK_API_ROOT + slack_const.VIEWS_UPDATE
    resource_type = context.get("resource_type")
    if resource_type == "opportunity":
        resource = Opportunity.objects.get(id=context.get("resource_id"))
    else:
        resource = Account.objects.get(id=context.get("resource_id"))
    contacts = resource.contacts.all().values_list("email", flat=True)
    people = People.objects.filter(email__in=contacts).values_list("people_id", flat=True)
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
    if len(people):
        res = slack_requests.generic_request(url, loading_data, access_token=access_token)
        for person in people:
            person_res = emit_add_cadence_membership(person, cadence_id)
        return
    else:
        return


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
        slack_const.COMMAND_FORMS__SUBMIT_FORM: process_submit_resource_data,
        slack_const.COMMAND_FORMS__PROCESS_NEXT_PAGE: process_next_page_slack_commands_form,
        slack_const.COMMAND_CREATE_TASK: process_create_task,
        slack_const.ZOOM_MEETING__SCHEDULE_MEETING: process_schedule_meeting,
        slack_const.ADD_TO_CADENCE: process_add_contacts_to_cadence,
    }

    callback_id = payload["view"]["callback_id"]
    view_context = json.loads(payload["view"]["private_metadata"])
    return switcher.get(callback_id, NO_OP)(payload, view_context)
