import logging
import json
import httpx
import datetime
from django.conf import settings
from urllib.parse import urlencode
from background_task import background
from managr.utils.client import Variable_Client
from .utils import get_news_for_company, send_clips
from . import constants as comms_consts
from managr.core import constants as core_consts
from managr.core.models import User
from managr.core import exceptions as open_ai_exceptions
from managr.slack.helpers import requests as slack_requests
from managr.slack.helpers import block_builders


logger = logging.getLogger("managr")


def emit_process_news_summary(payload, context, schedule=datetime.datetime.now()):
    return _process_news_summary(payload, context, schedule=schedule)


@background()
def _process_news_summary(payload, context):
    state = payload["view"]["state"]["values"]
    user = User.objects.get(id=context.get("u"))
    company = state["COMPANY_INPUT"]["plain_input"]["value"]
    while True:
        try:
            url = core_consts.OPEN_AI_CHAT_COMPLETIONS_URI
            prompt = core_consts.OPEN_AI_NEWS_BOOLEAN_CONVERSION(company)
            body = core_consts.OPEN_AI_CHAT_COMPLETIONS_BODY(
                user.email, prompt, token_amount=500, top_p=0.1,
            )
            with Variable_Client() as client:
                r = client.post(url, data=json.dumps(body), headers=core_consts.OPEN_AI_HEADERS,)
                r = open_ai_exceptions._handle_response(r)
                query_input = r.get("choices")[0].get("message").get("content")
                break
        except Exception as e:
            logger.exception(e)
            break
    query = urlencode({"q": query_input})
    news_res = get_news_for_company(query)
    articles = news_res["articles"]
    send_clips(user, news_res, company)

    descriptions = [article["description"] for article in articles]
    attempts = 1
    token_amount = 500
    timeout = 60.0
    while True:
        url = core_consts.OPEN_AI_CHAT_COMPLETIONS_URI
        prompt = comms_consts.OPEN_AI_NEWS_CLIPS_SUMMARY(
            datetime.datetime.now().date(), descriptions, company
        )
        body = core_consts.OPEN_AI_CHAT_COMPLETIONS_BODY(
            user.email,
            prompt,
            "You are a VP of Communications",
            token_amount=token_amount,
            top_p=0.1,
        )
        with Variable_Client(timeout) as client:
            r = client.post(url, data=json.dumps(body), headers=core_consts.OPEN_AI_HEADERS,)
        try:
            r = open_ai_exceptions._handle_response(r)
            message = r.get("choices")[0].get("message").get("content")

            break
        except open_ai_exceptions.StopReasonLength:
            logger.exception(
                f"Retrying again due to token amount, amount currently at: {token_amount}"
            )
            if token_amount <= 2000:
                message = "Token amount error"
                break
            else:
                token_amount += 500
                continue
        except httpx.ReadTimeout as e:
            timeout += 30.0
            if timeout >= 120.0:
                message = "Read timeout issue"
                logger.exception(f"Read timeout from Open AI {e}")
                break
            else:
                attempts += 1
                continue
        except Exception as e:
            message = f"Unknown exception: {e}"
            logger.exception(e)
            break
    try:
        blocks = [
            block_builders.simple_section(f"*Summary for {company}*", "mrkdwn"),
            block_builders.divider_block(),
            block_builders.simple_section(message, "mrkdwn"),
        ]
        if not settings.IN_PROD:
            blocks.extend(
                [
                    block_builders.divider_block(),
                    block_builders.context_block(
                        f"*AI Generated Search Terms:* {query_input}", "mrkdwn"
                    ),
                ]
            )
        slack_res = slack_requests.update_channel_message(
            user.slack_integration.channel,
            context.get("ts"),
            user.organization.slack_integration.access_token,
            block_set=blocks,
        )
    except Exception as e:
        logger.exception(
            f"ERROR sending update channel message for chat submission because of <{e}>"
        )
    return
