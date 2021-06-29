import logging
import json
import pytz
import uuid
import random
from datetime import datetime

from django.conf import settings
from django.db.models import Q
from django.utils import timezone

from background_task import background
from rest_framework.exceptions import ValidationError

from managr.api.decorators import sf_api_exceptions, slack_api_exceptions
from managr.slack import constants as slack_const

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


def emit_init_alert(config_id):
    return _process_init_alert(config_id)


def emit_send_alert(instance_id, scheduled_time=timezone.now()):
    if isinstance(scheduled_time, str):
        scheduled_time = datetime.strptime(scheduled_time, "%Y-%m-%dT%H:%M%z")

    return _process_send_alert(str(instance_id), schedule=scheduled_time)


@background(queue="MANAGR_ALERTS_QUEUE")
def _process_init_alert(config_id):

    config = AlertConfig.objects.filter(id=config_id).first()
    if not config:
        return logger.exception(f"Could not find config for template to send {config_id}")
    template = config.template
    users = template.get_users

    for user in users:
        run_time = config.calculate_scheduled_time_for_alert(user).strftime("%Y-%m-%dT%H:%M%z")
        _process_check_alert(config_id, str(user.id), run_time)


@background(queue="MANAGR_ALERTS_QUEUE")
@sf_api_exceptions(rethrow=True)
def _process_check_alert(config_id, user_id, run_time):
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
            if config.recipient_type == "USER_LEVEL":
                for user_group in config.recipients:

                    if user_group == "SELF":
                        instance = AlertInstance.objects.create(
                            template_id=alert_id,
                            user_id=template_user.id,
                            resource_id=str(existing.id),
                            instance_meta=instance_meta,
                            config=config,
                            channel=template_user.slack_integration.channel
                            if hasattr(template_user, "slack_integration")
                            else None,
                        )

                        emit_send_alert(str(instance.id), scheduled_time=run_time)
                    elif user_group == "OWNER":
                        instance = AlertInstance.objects.create(
                            template_id=alert_id,
                            user_id=user.id,
                            resource_id=str(existing.id),
                            instance_meta=instance_meta,
                            config=config,
                            channel=user.slack_integration.channel
                            if hasattr(user, "slack_integration")
                            else None,
                        )

                        emit_send_alert(str(instance.id), scheduled_time=run_time)
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

                        users = template.user.organization.users.filter(query).distinct()
                        for u in users:
                            instance = AlertInstance.objects.create(
                                template_id=alert_id,
                                user_id=u.id,
                                resource_id=str(existing.id),
                                instance_meta=instance_meta,
                                config=config,
                                channel=u.slack_integration.channel
                                if hasattr(u, "slack_integration")
                                else None,
                            )

                            emit_send_alert(str(instance.id), scheduled_time=run_time)
            elif config.recipient_type == "SLACK_CHANNEL":
                for channel in config.recipients:
                    instance = AlertInstance.objects.create(
                        template_id=alert_id,
                        user_id=template_user.id,
                        resource_id=str(existing.id),
                        instance_meta=instance_meta,
                        channel=channel,
                        config=config,
                    )
                    emit_send_alert(str(instance.id), scheduled_time=run_time)

    return


@background(queue="MANAGR_ALERTS_QUEUE", schedule=0)
@sf_api_exceptions(rethrow=True)
@slack_api_exceptions()
def _process_send_alert(instance_id):
    alert_instance = AlertInstance.objects.filter(id=instance_id).select_related("user").first()
    instance_user = alert_instance.user
    if hasattr(instance_user, "slack_integration"):
        channel_id = (
            alert_instance.channel
            if alert_instance.channel
            else instance_user.slack_integration.channel
        )
        access_token = instance_user.organization.slack_integration.access_token
        text = alert_instance.template.message_template.notification_text
        blocks = get_block_set("alert_instance", {"instance_id": str(alert_instance.id)})
        try:
            slack_requests.send_channel_message(
                channel_id, access_token, text=text, block_set=blocks
            )

            alert_instance.rendered_text = alert_instance.render_text()
            alert_instance.sent_at = timezone.now()
            alert_instance.save()
        except CannotSendToChannel:
            try:
                slack_requests.send_channel_message(
                    alert_instance.template.user.slack_integration.channel,
                    access_token,
                    text=text,
                    block_set=[
                        block_builders.simple_section(
                            "Cannot send alert to channel please add Managr to the channel by @ tagging managr *@Managr* you can re run this alert through the preview page with the _run now_ button",
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
