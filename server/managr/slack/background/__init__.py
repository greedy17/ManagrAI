import logging
from background_task import background

from managr.api.decorators import slack_api_exceptions, log_all_exceptions
from managr.alerts.models import AlertInstance, AlertConfig
from managr.core.models import User
from managr.slack.helpers.block_sets import get_block_set
from managr.slack.helpers import block_builders
from managr.slack.helpers import requests as slack_requests
from managr.slack import constants as slack_const
from managr.slack.helpers.utils import action_with_params
from managr.utils.misc import custom_paginator

from managr.slack.helpers.block_sets.command_views_blocksets import custom_paginator_block


def emit_send_paginated_alerts(payload, context):
    _process_send_paginated_alerts(payload, context)


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
    bulk_update_block = block_builders.simple_button_block(
        "Update in Bulk",
        "bulk_update",
        action_id=action_with_params(
            slack_const.PROCESS_BULK_UPDATE,
            params=[f"invocation={invocation}", f"config_id={config_id}", f"u={str(user.id)}",],
        ),
    )
    summary_block = block_builders.simple_button_block(
        "Get Summary",
        "get_summary",
        action_id=action_with_params(
            slack_const.GET_SUMMARY,
            params=[f"invocation={invocation}", f"config_id={config_id}", f"u={str(user.id)}",],
        ),
    )
    blocks = [
        block_builders.header_block(
            f"{len(alert_instances)} results for workflow {alert_template.title}"
        ),
        block_builders.actions_block([bulk_update_block, summary_block]),
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
    slack_requests.generic_request(
        payload["response_url"],
        {"replace_original": True, "blocks": blocks},
        access_token=access_token,
    )
    return
