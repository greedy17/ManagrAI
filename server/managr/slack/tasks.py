import logging
import uuid

from managr.slack.helpers import requests as slack_requests
from managr.core.models import User
from managr.alerts.models import AlertInstance
from background_task import background
from managr.utils.misc import custom_paginator
from managr.slack.helpers import block_builders
from managr.slack.helpers.block_sets import get_block_set
from managr.slack.helpers.utils import USER_APP_OPTIONS, action_with_params
from managr.slack.helpers.block_sets.command_views_blocksets import custom_paginator_block
from managr.slack.models import OrgCustomSlackFormInstance
from managr.slack import constants as slack_const

logger = logging.getLogger("managr")


def emit_update_slack_message(context, main_form_id):
    verbose_name = f"update-slack-block-{context.get('u')}-{str(uuid.uuid4())}"
    return _update_slack_message(context, main_form_id, verbose_name=verbose_name)


@background()
def _update_slack_message(context, main_form_id):
    user = User.objects.get(id=context.get("u"))
    slack_access_token = user.organization.slack_integration.access_token
    instance = AlertInstance.objects.get(id=context.get("alert_id"))
    alert_instances = AlertInstance.objects.filter(
        invocation=instance.invocation,
        channel=context.get("channel_id"),
        config_id=instance.config_id,
    ).filter(completed=False)
    main_form = OrgCustomSlackFormInstance.objects.get(id=main_form_id)
    alert_instance = alert_instances.first()
    text = instance.template.title
    blocks = [
        block_builders.header_block(f"{len(alert_instances)} results for workflow {text}"),
    ]
    action_blocks = (
        get_block_set(
            "initial_inline_blockset",
            context={
                "u": str(user.id),
                "invocation": instance.invocation,
                "config_id": str(instance.config_id),
                "channel": context.get("channel_id"),
                "switch_to": "inline",
            },
        ),
    )
    blocks.extend(action_blocks)

    options = USER_APP_OPTIONS(user, instance.config.template.resource_type)
    blocks.append(
        block_builders.static_select(
            "Pick an action",
            options,
            action_id=action_with_params(
                slack_const.PROCESS_SHOW_APP_SELECT,
                params=[
                    f"invocation={instance.invocation}",
                    f"config_id={str(instance.config_id)}",
                    f"u={str(user.id)}",
                ],
            ),
            placeholder="Connected Apps",
        ),
    )
    if alert_instance:
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
    else:
        blocks.append(block_builders.simple_section("You're all finished with this workflow!"))
    try:
        slack_requests.update_channel_message(
            context.get("channel_id"),
            context.get("message_ts"),
            slack_access_token,
            block_set=blocks,
        )
        main_form.alert_instance_id = instance
        main_form.save()
    except Exception as e:
        logger.exception(f"Failed to update alert blocks for {user.email} because of <{e}>")
    return
