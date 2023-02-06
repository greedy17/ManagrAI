import logging
import time
from django.utils import timezone
from background_task import background

from managr.api.decorators import slack_api_exceptions, log_all_exceptions
from managr.alerts.models import AlertInstance, AlertConfig
from managr.core.models import User
from managr.slack.helpers.block_sets import get_block_set
from managr.slack.helpers import block_builders
from managr.slack.helpers import requests as slack_requests
from managr.slack import constants as slack_const
from managr.slack.helpers.utils import action_with_params
from managr.slack.models import OrgCustomSlackFormInstance, OrgCustomSlackForm
from managr.utils.misc import custom_paginator
from managr.crm.models import ObjectField
from managr.slack.helpers.block_sets.command_views_blocksets import (
    custom_paginator_block,
    custom_inline_paginator_block,
)
from managr.crm import exceptions as crm_exceptions
from managr.slack.helpers import exceptions as slack_exceptions
from managr.salesforce.utils import swap_public_fields, process_text_field_format
from managr.crm.routes import model_routes

logger = logging.getLogger("managr")


def ADD_UPDATE_TO_CRM_FUNCTION(crm):
    from managr.salesforce.background import emit_add_update_to_sf
    from managr.hubspot.tasks import emit_add_update_to_hs

    if crm == "SALESFORCE":
        return emit_add_update_to_sf
    else:
        return emit_add_update_to_hs


def background_create_resource(crm):
    from managr.salesforce.background import _process_create_new_resource
    from managr.hubspot.tasks import _process_create_new_hs_resource

    if crm == "SALESFORCE":
        return _process_create_new_resource
    else:
        return _process_create_new_hs_resource


def emit_send_paginated_alerts(payload, context):
    _process_send_paginated_alerts(payload, context)


def emit_send_paginated_inline_alerts(payload, context):
    _process_send_paginated_inline_alerts(payload, context)


def emit_send_next_page_paginated_inline_alerts(payload, context):
    _prcocess_send_next_page_paginated_inline_alerts(payload, context)


def emit_process_submit_resource_data(payload, context):
    return _process_submit_resource_data(payload, context)


@background(schedule=0)
@log_all_exceptions
def _process_send_paginated_alerts(payload, context):
    channel_id = payload.get("channel", {}).get("id", None)
    ts = payload.get("message", {}).get("ts", None)
    user_slack_id = payload.get("user", {}).get("id", None)
    user = User.objects.filter(slack_integration__slack_id=user_slack_id).first()
    if not user:
        return
    access_token = user.organization.slack_integration.access_token
    invocation = context.get("invocation")
    channel = context.get("channel")
    config_id = context.get("config_id")
    alert_instances = AlertInstance.objects.filter(
        invocation=invocation, channel=channel, config_id=config_id
    ).filter(completed=False)
    alert_instance = alert_instances.first()
    if not alert_instance:
        # check if the config was deleted
        config = AlertConfig.objects.filter(id=config_id).first()
        if not config:
            error_blocks = get_block_set(
                "error_modal",
                {
                    "message": ":no_entry: The settings for these instances was deleted the data is no longer available"
                },
            )
            slack_requests.update_channel_message(
                channel_id, ts, access_token, text="Error", block_set=error_blocks
            )
        return
    alert_template = alert_instance.template
    action_blocks = [
        block_builders.simple_button_block(
            "Switch to In-Line",
            "switch_inline",
            action_id=action_with_params(
                slack_const.PROCESS_SWITCH_ALERT_MESSAGE,
                params=[
                    f"invocation={invocation}",
                    f"config_id={config_id}",
                    f"u={str(user.id)}",
                    f"switch_to={'inline'}",
                ],
            ),
        ),
        block_builders.simple_button_block(
            "Update in Bulk",
            "bulk_update",
            action_id=action_with_params(
                slack_const.PROCESS_BULK_UPDATE,
                params=[f"invocation={invocation}", f"config_id={config_id}", f"u={str(user.id)}",],
            ),
        ),
    ]
    action_blocks.append(
        block_builders.simple_button_block(
            "Get Summary",
            "get_summary",
            action_id=action_with_params(
                slack_const.GET_SUMMARY,
                params=[f"invocation={invocation}", f"config_id={config_id}", f"u={str(user.id)}",],
            ),
        )
    )
    blocks = [
        block_builders.header_block(
            f":bell: {len(alert_instances)} results for workflow {alert_template.title}"
        ),
        block_builders.actions_block(action_blocks),
        {"type": "divider"},
    ]
    alert_instances = custom_paginator(alert_instances, page=int(context.get("new_page", 1)))
    for alert_instance in alert_instances.get("results", []):
        blocks = [
            *blocks,
            *get_block_set(
                "alert_instance",
                {
                    "instance_id": str(alert_instance.id),
                    "current_page": int(context.get("new_page", 1)),
                },
            ),
        ]
        alert_instance.rendered_text = alert_instance.render_text()
        alert_instance.save()
    if len(blocks):
        blocks = [
            *blocks,
            *custom_paginator_block(alert_instances, invocation, channel, config_id),
        ]
    try:
        slack_requests.generic_request(
            payload["response_url"],
            {"replace_original": True, "blocks": blocks},
            access_token=access_token,
        )
    except slack_exceptions.UnHandeledBlocksException:
        logger.exception(f"Send paginated alerts background task has unhandled blocks: {blocks}")
        blocks = [
            *get_block_set(
                "initial_alert_blockset",
                {
                    "channel": channel,
                    "user": str(user.id),
                    "config_id": config_id,
                    "invocation": invocation,
                    "title": f"*New Task:* {len(alert_instances)} {alert_template.title}",
                },
            ),
            block_builders.context_block(f"Owned by {user.full_name}"),
        ]
        blocks = [
            block_builders.simple_section("There was an error building your alerts :warning:"),
            *blocks,
        ]
        slack_requests.generic_request(
            payload["response_url"],
            {"replace_original": True, "blocks": blocks},
            access_token=access_token,
        )
    except Exception as e:
        logger.exception(f"Exeception on process send paginated alerts <{e}>")
    return


@background(schedule=0)
@log_all_exceptions
def _process_send_paginated_inline_alerts(payload, context):
    value = payload.get("actions", [])[0].get("selected_option", {}).get("value", None)
    user_slack_id = payload.get("user", {}).get("id", None)
    user = User.objects.filter(slack_integration__slack_id=user_slack_id).first()
    if not user:
        return
    access_token = user.organization.slack_integration.access_token
    invocation = context.get("invocation")
    config_id = context.get("config_id")
    instances = AlertInstance.objects.filter(user=user, invocation=invocation, config__id=config_id)
    field = ObjectField.objects.get(
        api_name=value, user=user, crm_object=instances.first().template.resource_type
    )
    blocks = payload.get("message").get("blocks")[:2]
    blocks.append({"type": "divider"})
    template = (
        OrgCustomSlackForm.objects.for_user(user)
        .filter(
            resource=instances.first().template.resource_type,
            form_type=slack_const.FORM_TYPE_UPDATE,
        )
        .first()
    )
    instances = custom_paginator(instances, page=int(context.get("new_page", 1)))
    for alert_instance in instances.get("results", []):
        if not alert_instance.form_instance.exists():
            form = OrgCustomSlackFormInstance.objects.create(
                user=user, template=template, resource_id=alert_instance.resource_id
            )
            form.alert_instance_id = alert_instance
            form.save()
        else:
            form = alert_instance.form_instance.all().first()
        field_value = alert_instance.resource.secondary_data[value]
        field_block = (
            field.to_slack_field(field_value, user, resource_id=alert_instance.resource_id)
            if value == "dealstage"
            else field.to_slack_field(field_value, user)
        )
        field_block[
            "block_id"
        ] = f"{field_block['block_id']}.{str(invocation)}.{str(alert_instance.id)}"
        if "label" in field_block.keys():
            field_block["label"]["text"] = f"{alert_instance.resource.name}"
        else:
            field_block["text"]["text"] = f"{alert_instance.resource.name}"
        if value in ["dealstage", "StageName"]:
            field_block["accessory"][
                "action_id"
            ] = f"{slack_const.ALERT_INLINE_STAGE_SELECTED}?u={str(user.id)}&f={str(form.id)}"
        blocks.append(field_block)
    if len(blocks):
        blocks.append({"type": "divider"})
        blocks = [
            *blocks,
            *custom_inline_paginator_block(instances, invocation, config_id, value),
        ]
    slack_requests.generic_request(
        payload["response_url"],
        {"replace_original": True, "blocks": blocks},
        access_token=access_token,
    )
    return


@background(schedule=0)
@log_all_exceptions
def _prcocess_send_next_page_paginated_inline_alerts(payload, context):
    value = context.get("api_name")
    state = payload["state"]["values"]
    to_delete_keys = [id for id in state.keys() if value not in id]
    for id in to_delete_keys:
        del state[id]
    for key in state:
        block_id_values = key.split(".")
        form = OrgCustomSlackFormInstance.objects.filter(
            alert_instance_id=block_id_values[2]
        ).first()
        saved_data_ref = None
        if len(form.saved_data):
            saved_data_ref = form.saved_data
        form.save_form({value: state[key]})
        if saved_data_ref:
            saved_data_ref.update(form.saved_data)
            form.save_form(saved_data_ref, False)
    user_slack_id = payload.get("user", {}).get("id", None)
    user = User.objects.filter(slack_integration__slack_id=user_slack_id).first()
    if not user:
        return
    access_token = user.organization.slack_integration.access_token
    invocation = context.get("invocation")
    config_id = context.get("config_id")
    instances = AlertInstance.objects.filter(user=user, invocation=invocation, config__id=config_id)
    field = ObjectField.objects.get(
        api_name=value, user=user, crm_object=instances.first().template.resource_type
    )
    blocks = payload.get("message").get("blocks")[:2]
    blocks.append({"type": "divider"})
    template = (
        OrgCustomSlackForm.objects.for_user(user)
        .filter(
            resource=instances.first().template.resource_type,
            form_type=slack_const.FORM_TYPE_UPDATE,
        )
        .first()
    )
    instances = custom_paginator(instances, page=int(context.get("new_page", 1)))
    for alert_instance in instances.get("results", []):
        field_value = alert_instance.resource.secondary_data[value]
        if not alert_instance.form_instance.exists():
            form = OrgCustomSlackFormInstance.objects.create(
                user=user, template=template, resource_id=alert_instance.resource_id
            )
            form.alert_instance_id = alert_instance
            form.save()
        else:
            form = alert_instance.form_instance.all().first()
            if value in form.saved_data:
                field_value = form.saved_data[value]
        field_block = (
            field.to_slack_field(field_value, user, resource_id=alert_instance.resource_id)
            if value == "dealstage"
            else field.to_slack_field(field_value, user)
        )
        field_block[
            "block_id"
        ] = f"{field_block['block_id']}.{str(invocation)}.{str(alert_instance.id)}"
        if "label" in field_block.keys():
            field_block["label"]["text"] = f"{alert_instance.resource.name}"
        else:
            field_block["text"]["text"] = f"{alert_instance.resource.name}"
        if value in ["dealstage", "StageName"]:
            field_block["accessory"][
                "action_id"
            ] = f"{slack_const.ALERT_INLINE_STAGE_SELECTED}?u={str(user.id)}&f={str(form.id)}"
        blocks.append(field_block)
    if len(blocks):
        blocks.append({"type": "divider"})

        blocks = [
            *blocks,
            *custom_inline_paginator_block(instances, invocation, config_id, value),
        ]
    slack_requests.generic_request(
        payload["response_url"],
        {"replace_original": True, "blocks": blocks},
        access_token=access_token,
    )
    return


@background(schedule=0)
@slack_api_exceptions(rethrow=0)
def _process_submit_resource_data(payload, context):
    has_error = False
    user = User.objects.get(id=context.get("u"))
    slack_access_token = user.organization.slack_integration.access_token
    sending_blocks = get_block_set("loading", {"message": ":rocket: Sending your data to the CRM"})
    message_ref = context.get("message_ref", None)
    if message_ref:
        channel, ts = message_ref.split("|")
    try:
        if message_ref:
            sending_res = slack_requests.update_channel_message(
                channel, ts, slack_access_token, block_set=sending_blocks,
            )
        else:
            sending_res = slack_requests.send_channel_message(
                user.slack_integration.channel, slack_access_token, block_set=sending_blocks,
            )
    except Exception as e:
        logger.exception(f"Failed to send updating message to {user.email} due to {e}")
    state = swap_public_fields(payload["view"]["state"]["values"])
    current_form_ids = context.get("f").split(",")
    current_forms = user.custom_slack_form_instances.filter(id__in=current_form_ids)
    main_form = current_forms.filter(template__form_type__in=["UPDATE", "CREATE"]).first()
    stage_forms = current_forms.filter(template__form_type="STAGE_GATING")
    stage_form_data_collector = {}
    for form in stage_forms:
        form.save_form(state)
        stage_form_data_collector = {**stage_form_data_collector, **form.saved_data}
    if not len(stage_forms):
        main_form.save_form(state)
    all_form_data = {**stage_form_data_collector, **main_form.saved_data}
    formatted_saved_data = process_text_field_format(
        str(user.id), main_form.template.resource, all_form_data
    )
    attempts = 1
    while True:
        crm = user.crm_account
        try:
            if main_form.template.form_type == "UPDATE":
                main_form.resource_object.update(all_form_data)
                resource = main_form.resource_object
                main_form.resource_object.update_database_values(all_form_data)

            else:
                create_route = model_routes(user.crm)
                resource_func = background_create_resource(user.crm)
                resource = resource_func.now(current_form_ids)
                new_resource = create_route[main_form.template.resource]["model"].objects.get(
                    integration_id=resource.integration_id
                )

                main_form.resource_id = str(new_resource.id)
                main_form.save()
            current_forms.update(
                is_submitted=True, update_source="command", submission_date=timezone.now()
            )
            break
        except crm_exceptions.FieldValidationError as e:
            has_error = True
            blocks = get_block_set(
                "error_modal",
                {
                    "message": f":no_entry: Uh-Ohhh it looks like we found an error, this error is based on Validations set up by your org\n *Error* : _{e}_"
                },
            )
            break
        except crm_exceptions.RequiredFieldError as e:
            has_error = True
            blocks = get_block_set(
                "error_modal",
                {
                    "message": f":no_entry: Uh-Ohhh it looks like we found an error, this error is based on Required fields from Salesforce\n *Error* : _{e}_"
                },
            )
            break
        except crm_exceptions.UnhandledCRMError as e:
            has_error = True
            blocks = get_block_set(
                "error_modal",
                {
                    "message": f":no_entry: Uh-Ohhh it looks like we found an error, this error is new to us please see below\n *Error* : _{e}_"
                },
            )
            break

        except crm_exceptions.SFNotFoundError as e:
            has_error = True
            blocks = get_block_set(
                "error_modal",
                {
                    "message": f":no_entry: Uh-Ohhh it looks like we found an error, this error one of the resources does not exist\n *Error* : _{e}_"
                },
            )
            break

        except crm_exceptions.TokenExpired as e:
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
                crm.regenerate_token()
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
            logger.exception(
                f"Failed to Update data for user {str(user.id)} after {attempts} tries because of {e}"
            )
            has_error = True
            blocks = get_block_set(
                "error_modal",
                {"message": f":no_entry: Uh-Ohhh we had an error updating your Salesforce {e}"},
            )
            break
    if has_error:
        form_id = str(main_form.id) if not len(stage_forms) else str(stage_forms.first().id)
        blocks = [
            *blocks,
            block_builders.actions_block(
                [
                    block_builders.simple_button_block(
                        "return to form",
                        form_id,
                        style="primary",
                        action_id=action_with_params(
                            slack_const.RETURN_TO_FORM_BUTTON,
                            [
                                f"f={context.get('f')}",
                                f"u={str(user.id)}",
                                f"resource_type={main_form.template.resource}",
                            ],
                        ),
                    )
                ]
            ),
        ]
        try:
            slack_requests.update_channel_message(
                sending_res["channel"],
                sending_res["ts"],
                block_set=blocks,
                access_token=slack_access_token,
            )
        except Exception as e:
            logger.exception(
                f"Failed To Update via command for user  {str(user.id)} email {user.email} {e}"
            )
        return {"response_action": "clear"}
    # update the channel message to clear it
    if main_form.template.form_type == "CREATE":
        message = f":white_check_mark: Successfully created *{main_form.resource_type}* _{resource.name if hasattr(resource, 'name') else resource.email}_"
    else:
        message = f":white_check_mark: Successfully updated *{main_form.resource_type}* _{resource.name if hasattr(resource, 'name') else resource.email}_"
    if (
        all_form_data.get("meeting_comments") is not None
        and all_form_data.get("meeting_type") is not None
    ):
        ADD_UPDATE_TO_CRM_FUNCTION(user.crm)(str(main_form.id))
    try:
        slack_requests.update_channel_message(
            sending_res["channel"],
            sending_res["ts"],
            block_set=get_block_set(
                "success_modal", {"message": message, "u": user.id, "form_ids": context.get("f")},
            ),
            access_token=slack_access_token,
        )
    except Exception as e:
        logger.exception(
            f"Failed to send ephemeral message to user informing them of successful update {user.email} {e}"
        )
    return
