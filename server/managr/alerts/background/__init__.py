import logging
import json
import pytz
import uuid
import random
from datetime import datetime
from functools import reduce
from urllib.parse import urlencode, quote_plus, urlparse

from django.conf import settings
from django.db.models import Q
from django.utils import timezone

from background_task import background


from rest_framework.exceptions import ValidationError


from managr.api.decorators import sf_api_exceptions, slack_api_exceptions
from managr.slack import constants as slack_const
from managr.utils.misc import custom_paginator

from managr.slack.helpers.block_sets.command_views_blocksets import custom_paginator_block
from managr.slack.helpers import requests as slack_requests
from managr.slack.helpers.utils import process_action_id, NO_OP, processor, block_finder
from managr.slack.helpers.block_sets import get_block_set
from managr.slack.helpers import block_builders
from managr.slack.helpers.exceptions import (
    UnHandeledBlocksException,
    InvalidBlocksFormatException,
    InvalidBlocksException,
    InvalidAccessToken,
    CannotSendToChannel,
)
from managr.salesforce.routes import routes as model_routes
from managr.salesforce.adapter.exceptions import (
    TokenExpired,
    FieldValidationError,
    RequiredFieldError,
    SFQueryOffsetError,
    SFNotFoundError,
)

from ..models import AlertTemplate, AlertInstance, AlertConfig


logger = logging.getLogger("managr")


def emit_init_alert(config_id, invocation):
    return _process_init_alert(config_id, invocation)


def emit_send_alert(invocation, channel, config_id, scheduled_time=timezone.now()):
    if isinstance(scheduled_time, str):
        scheduled_time = datetime.strptime(scheduled_time, "%Y-%m-%dT%H:%M%z")

    return _process_send_alert(invocation, channel, config_id, schedule=scheduled_time)


@background(queue="MANAGR_ALERTS_QUEUE")
def _process_init_alert(config_id, invocation):

    config = AlertConfig.objects.filter(id=config_id).first()
    if not config:
        return logger.exception(f"Could not find config for template to send {config_id}")
    users = config.target_users

    for user in users:

        _process_check_alert(config_id, str(user.id), invocation, None)


@background(queue="MANAGR_ALERTS_QUEUE")
@sf_api_exceptions(rethrow=True)
def _process_check_alert(config_id, user_id, invocation, run_time):
    config = AlertConfig.objects.filter(id=config_id).first()
    template = config.template
    alert_id = str(template.id)
    resource = template.resource_type
    route = model_routes[resource]
    model_class = route["model"]
    user = template.get_users.filter(id=user_id).first()
    template_user = template.user

    attempts = 1
    if not hasattr(user, "salesforce_account"):
        return
    while True:
        sf = user.salesforce_account
        try:
            res = sf.adapter_class.execute_alert_query(
                template.url_str(user, config_id), template.resource_type
            )
            logger.info(f"Pulled total {len(res)} from request for {resource} matching alert query")
            break
        except TokenExpired:
            if attempts >= 5:
                return logger.exception(
                    f"Failed to retrieve alerts for {resource} data for user {user_id} after {attempts} tries"
                )
            else:
                sf.regenerate_token()
                attempts += 1
        except SFQueryOffsetError:
            return logger.warning(
                f"Failed to sync some data for resource {resource} for user {user_id} because of SF LIMIT"
            )

    instances = []
    for item in res:
        existing = model_class.objects.filter(integration_id=item.integration_id).first()
        if existing:
            # create alert instance to keep on hand and track errors
            instance_meta = {
                "query_sent": template.url_str(user, config_id),
                "results_count": len(res),
                "errors": [],
            }
            # create instance for each user group it will be sent to
            query = Q()
            run_time = (
                run_time
                if run_time
                else config.calculate_scheduled_time_for_alert(user).strftime("%Y-%m-%dT%H:%M%z")
            )
            if config.recipient_type == "USER_LEVEL":
                for user_group in config.recipients:

                    if user_group == "SELF":

                        query |= Q(id=template_user.id, is_active=True)
                    elif user_group == "OWNER":
                        query |= Q(id=user.id, is_active=True)
                    else:
                        if user_group == "MANAGERS":
                            query |= Q(Q(user_level="MANAGER", is_active=True))

                        elif user_group == "REPS":
                            query |= Q(user_level="REP", is_active=True)

                        elif user_group == "SDR":
                            query |= Q(user_level="SDR", is_active=True)

                        elif user_group == "ALL":

                            query = Q(is_active=True) & Q(
                                Q(user_level="MANAGER") | Q(user_level="REP") | Q(user_level="SDR")
                            )
                        else:
                            try:
                                uuid.UUID(user_group)
                                query |= Q(id=user_group)
                            except ValueError:
                                continue

                users = template.user.organization.users.filter(query).distinct()
                for u in users:
                    instance = AlertInstance.objects.create(
                        template_id=alert_id,
                        user_id=u.id,
                        resource_id=str(existing.id),
                        instance_meta=instance_meta,
                        config=config,
                        invocation=invocation,
                        channel=u.slack_integration.channel
                        if hasattr(u, "slack_integration")
                        else None,
                    )
                    instances = [
                        *instances,
                        {
                            "invocation": instance.invocation,
                            "channel": instance.channel,
                            "config_id": str(config.id),
                        },
                    ]

                    # emit_send_alert(str(instance.id), scheduled_time=run_time)
            elif config.recipient_type == "SLACK_CHANNEL":
                for channel in config.recipients:
                    instance = AlertInstance.objects.create(
                        template_id=alert_id,
                        user_id=template_user.id,
                        resource_id=str(existing.id),
                        instance_meta=instance_meta,
                        channel=channel,
                        invocation=invocation,
                        config=config,
                    )
                    # emit_send_alert(str(instance.id), scheduled_time=run_time)
                    instances = [
                        *instances,
                        {
                            "invocation": instance.invocation,
                            "channel": instance.channel,
                            "config_id": str(config.id),
                        },
                    ]

    def reduce_fn(acc, curr):
        key = f"{curr['config_id']}.{curr['channel']}"
        if not acc:
            acc = {key: list(curr.values())}
            return acc
        elif acc.get(key):
            return acc
        else:
            acc = {**acc, key: list(curr.values())}
            return acc

    bg_tasks = dict(reduce(reduce_fn, instances, {}))
    for task_vals in bg_tasks.values():

        emit_send_alert(*task_vals, scheduled_time=run_time)
    return


@background(queue="MANAGR_ALERTS_QUEUE", schedule=0)
@sf_api_exceptions(rethrow=True)
@slack_api_exceptions()
def _process_send_alert(invocation, channel, config_id):
    alert_instances = AlertInstance.objects.filter(
        invocation=invocation, channel=channel, config_id=config_id
    )
    if not alert_instances.first():
        return
    template = alert_instances.first().template
    channel_id = None
    instance_user = alert_instances.first().user
    if hasattr(instance_user, "slack_integration"):
        channel_id = (
            alert_instances.first().channel
            if alert_instances.first().channel
            else instance_user.slack_integration.channel
        )
    alert_instances = custom_paginator(alert_instances)
    access_token = template.user.organization.slack_integration.access_token
    text = template.title
    blocks = []

    for alert_instance in alert_instances.get("results", []):
        blocks = [
            *blocks,
            *get_block_set("alert_instance", {"instance_id": str(alert_instance.id)}),
        ]
        alert_instance.rendered_text = alert_instance.render_text()
        alert_instance.save()

    if len(blocks):
        blocks = [
            *blocks,
            *custom_paginator_block(alert_instances, invocation, channel, config_id),
        ]
        try:
            slack_requests.send_channel_message(
                channel_id, access_token, text=text, block_set=blocks
            )
            alert_instances.update(sent_at=timezone.now())

        except CannotSendToChannel:
            try:
                slack_requests.send_channel_message(
                    alert_instance.template.user.slack_integration.channel,
                    access_token,
                    text=text,
                    block_set=[
                        block_builders.simple_section(
                            f"Cannot send alert to one of the channels you selected, please add <@{alert_instance.template.user.organization.slack_integrations.bot_user_id}> to the channel <#{channel_id}>",
                            "mrkdwn",
                        )
                    ],
                )
            except Exception:
                logger.info(
                    f"failed to send notification to user that alert could not be sent to channel because managr is not part of channel {alert_instance.template.user}"
                )

        except Exception as e:
            raise (e)

    return alert_instance
