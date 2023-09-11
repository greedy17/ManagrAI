import logging
import kronos
import datetime

from django.utils import timezone
from django.db.models import Q

from managr.slack.helpers import block_builders
from managr.alerts.models import AlertConfig
from managr.core import constants as core_consts
from managr.core.models import NylasAuthAccount, User
from managr.core.nylas.auth import revoke_access_token
from managr.slack.helpers import requests as slack_requests

logger = logging.getLogger("managr")


def to_date_string(date):
    if not date:
        return "n/a"
    d = datetime.datetime.strptime(date, "%Y-%m-%d")
    return d.strftime("%a, %B %d, %Y")


def process_current_alert_list(user_id):
    user = User.objects.get(id=user_id)
    configs = AlertConfig.objects.filter(Q(template__user=user.id, template__is_active=True))
    alert_blocks = [
        block_builders.simple_section(f":eyes: *Pipeline Monitor*", "mrkdwn"),
    ]
    if configs:
        for config in configs:
            channel_info = slack_requests.get_channel_info(
                user.organization.slack_integration.access_token, config.recipients[0]
            )
            name = channel_info.get("channel").get("name")
            alert_blocks = [
                *alert_blocks,
                block_builders.simple_section(f"{config.template.title}: #{name}", "mrkdwn"),
            ]
    else:
        alert_blocks.append(
            block_builders.simple_section("Your pipeline look good today :thumbsup: ", "mrkdwn")
        )
    return alert_blocks


@kronos.register("0 0 * * *")
def revoke_tokens():
    expire = timezone.now() + datetime.timedelta(days=5)
    """ revokes tokens for email auth accounts in state of sync_error, stopped, invalid """
    nylas_tokens = NylasAuthAccount.objects.filter(
        sync_status__in=core_consts.NYLAS_SYNC_STATUSES_FAILING, last_edited__gte=expire
    ).values_list("access_token", flat=True)
    for token in nylas_tokens:
        revoke_access_token(token)
