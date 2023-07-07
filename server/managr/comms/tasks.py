import logging
import math
from urllib.parse import urlencode
import json
import httpx
import datetime
from background_task import background
from managr.utils.client import Variable_Client
from .utils import get_news_for_company
from . import constants as comms_consts
from managr.core import constants as core_consts
from managr.core.models import User
from managr.core import exceptions as open_ai_exceptions
from managr.slack.helpers import requests as slack_requests
from managr.slack.helpers import block_builders


logger = logging.getLogger("managr")


def emit_process_news_summary(payload, context, schedule=datetime.datetime.now()):
    return _process_news_summary(payload, context, schedule=schedule)


def article_list_seperator(articles_list):
    new_list = []
    if len(",".join(articles_list)) > 3000:
        half_index = math.floor(len(articles_list) / 2)
        first_half = articles_list[:half_index]
        second_half = articles_list[half_index:]
        if len(",".join(first_half)) > 3000:
            new_list.append(article_list_seperator(first_half))
        else:
            new_list.append(",".join(first_half))
        if len(",".join(second_half)) > 3000:
            new_list.append(article_list_seperator(second_half))
        else:
            new_list.append(",".join(second_half))
    return new_list


def send_clips(user, news_res, company):
    articles = news_res["articles"]
    articles_list = [
        f"Published: {article['publishedAt']}\nTitle: {article['title']} \n Clip: {article['description']}\n\n"
        for article in articles
    ]
    news_list = article_list_seperator(articles_list)
    for index, message in enumerate(news_list):
        try:
            article_blocks = [
                block_builders.header_block(
                    f"Articles used for summary {company} {index + 1}/{len(news_list)}"
                ),
                block_builders.divider_block(),
                block_builders.simple_section(message, "mrkdwn"),
            ]
            article_res = slack_requests.send_channel_message(
                user.slack_integration.channel,
                user.organization.slack_integration.access_token,
                block_set=article_blocks,
            )
        except Exception as e:
            logger.exception(
                f"ERROR sending update channel message for chat submission because of <{e}>"
            )
    return


@background()
def _process_news_summary(payload, context):
    state = payload["view"]["state"]["values"]
    user = User.objects.get(id=context.get("u"))
    company = state["COMPANY_INPUT"]["plain_input"]["value"]
    query = urlencode({"q": company})
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
            user.email, prompt, token_amount=token_amount, top_p=0.1
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
            block_builders.header_block(f"Summary for {company}"),
            block_builders.divider_block(),
            block_builders.simple_section(message, "mrkdwn"),
        ]
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
