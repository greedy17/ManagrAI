import logging
import json
import pytz
import uuid
import random
from datetime import datetime

from django.conf import settings

from background_task import background
from rest_framework.exceptions import ValidationError

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
)
from managr.salesforce.routes import routes as model_routes
from managr.salesforce.adapter.exceptions import (
    TokenExpired,
    FieldValidationError,
    RequiredFieldError,
    SFQueryOffsetError,
    SFNotFoundError,
)

from ..models import AlertTemplate, AlertInstance


logger = logging.getLogger("managr")


def emit_init_alert(alert_id):
    return _process_init_alert(alert_id)


@background()
def _process_init_alert(alert_id,):

    template = AlertTemplate.objects.filter(id=alert_id).first()
    if not template:
        return logger.exception(f"Could not find Alert template to send {alert_id}")
    users = template.get_users

    for user in users:
        _process_check_alert()


@background()
def _process_check_alert(alert_id, user_id):

    template = AlertTemplate.objects.filter(id=alert_id).first()
    resource = template.resource_type
    route = model_routes[resource]
    model_class = route["model"]
    user = template.get_users.filter(id=user_id).first()
    if not template:
        return logger.exception(f"Could not find Alert template to send {alert_id}")
    attempts = 1
    while True:
        sf = user.salesforce_account
        try:
            res = sf.adapter_class.execute_alert_query(
                template.url_str(user), template.resource_type
            )
            logger.info(f"Pulled total {len(res)} from request for {resource} matching alert query")
            break
        except TokenExpired:
            if attempts >= 5:
                return logger.exception(
                    f"Failed to sync {resource} data for user {user_id} after {attempts} tries"
                )
            else:
                sf.regenerate_token()
                attempts += 1
        except SFQueryOffsetError:
            return logger.warning(
                f"Failed to sync some data for resource {resource} for user {user_id} because of SF LIMIT"
            )

    # check if we have it in our db to inform our user
    ## currently only createting alert isntance if exists in db

    for item in res:
        existing = model_class.objects.filter(integration_id=item.integration_id).first()
        if existing:
            # create alert instance to keep on hand and track errors
            instance = AlertInstance.objects.create(
                template_id=alert_id, user_id=user_id, resource_id=str(existing.id)
            )
            if hasattr(user, "slack_integration"):
                channel_id = user.slack_integration.channel
                access_token = user.organization.slack_integration.access_token
                text = "WILL CHANGE TO PROVIDED TEXT"
                blocks = [
                    block_builders.header_block(template.title),
                    block_builders.divider_block(),
                    block_builders.simple_section(
                        f"Triggered an alert for {instance.resource.name}"
                    ),
                ]
                res = slack_requests.send_channel_message(
                    channel_id, access_token, text=text, block_set=blocks
                )
                print(res)

