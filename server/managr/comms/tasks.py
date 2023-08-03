import logging
import json
import httpx
import datetime
from urllib.parse import urlencode
from background_task import background
from managr.utils.client import Variable_Client
from .utils import get_news_for_company
from managr.utils.misc import custom_paginator
from managr.slack.helpers.block_sets.command_views_blocksets import custom_clips_paginator_block
from . import constants as comms_consts
from managr.core import constants as core_consts
from managr.core.models import User
from managr.core import exceptions as open_ai_exceptions
from managr.slack.helpers import requests as slack_requests
from managr.slack.helpers import block_builders
from managr.slack.helpers.utils import action_with_params
from managr.slack import constants as slack_const
from managr.slack.models import UserSlackIntegration
from newspaper import Article

logger = logging.getLogger("managr")


def emit_process_news_summary(payload, context, schedule=datetime.datetime.now()):
    return _process_news_summary(payload, context, schedule=schedule)


def emit_process_send_clips(payload, context):
    return _process_send_clips(payload, context)

def emit_process_article_summary(payload, context):
    return _process_article_summary(payload, context)


@background()
def _process_news_summary(payload, context):
    state = payload["view"]["state"]["values"]
    user = User.objects.get(id=context.get("u"))
    search = state["SEARCH"]["plain_input"]["value"]
    try:
        instructions = state["OUTPUT_INSTRUCTIONS"]["plain_input"]["value"]
    except KeyError:
        instructions = False
    while True:
        try:
            url = core_consts.OPEN_AI_CHAT_COMPLETIONS_URI
            prompt = core_consts.OPEN_AI_NEWS_BOOLEAN_CONVERSION(search)
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
    descriptions = [article["description"] for article in articles]
    attempts = 1
    token_amount = 500
    timeout = 60.0
    while True:
        url = core_consts.OPEN_AI_CHAT_COMPLETIONS_URI
        prompt = comms_consts.OPEN_AI_NEWS_CLIPS_SUMMARY(
            datetime.datetime.now().date(), descriptions, user.organization.name, instructions
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
            message = r.get("choices")[0].get("message").get("content").replace("**", "*")

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
            block_builders.simple_section(
                f"*Summary for {search}*", "mrkdwn", block_id="NEWS_SUMMARY"
            ),
            block_builders.context_block(f"AI-generated search: {query_input}", "mrkdwn"),
            block_builders.divider_block(),
            block_builders.simple_section(message, "mrkdwn"),
            block_builders.divider_block(),
            block_builders.actions_block(
                [
                    block_builders.simple_button_block(
                        "Regenerate",
                        "REGENERATE",
                        action_id=slack_const.PROCESS_SHOW_REGENERATE_NEWS_SUMMARY_FORM,
                    ),
                    block_builders.simple_button_block(
                        "Show Clips", "SHOW_CLIPS", action_id=slack_const.PROCESS_SEND_CLIPS
                    ),
                ]
            ),
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


@background()
def _process_send_clips(payload, context):
    slack_account = UserSlackIntegration.objects.get(slack_id=payload["user"]["id"])
    user = slack_account.user
    access_token = user.organization.slack_integration.access_token
    blocks = payload["message"]["blocks"]
    title_text = blocks[0]["text"]["text"].split("for ")[1].replace("*", "")
    context_text = blocks[1]["elements"][0]["text"]
    boolean_text = context_text.split("search: ")[1]
    news_res = get_news_for_company(f"q={boolean_text}")
    paginated_articles = custom_paginator(
        news_res["articles"], count=10, page=context.get("new_page", 1)
    )
    paginated_article_blocks = [
        block_builders.simple_section(f"*Articles summarized for {title_text}*", "mrkdwn"),
        block_builders.context_block(f"AI-generated search: {context_text}", "mrkdwn"),
        block_builders.divider_block(),
    ]
    for article in paginated_articles["results"]:
        text = f"*{article['title']}*\n{article['description']}"
        source_text = f"*Date:* {article['publishedAt'][:10]} (<{article['url']}|{article['source']['name']}> | {article['author']})"
        article_blocks = [
            block_builders.simple_section(text, "mrkdwn"),
            block_builders.context_block(source_text, "mrkdwn"),
            block_builders.actions_block(
                [
                    block_builders.simple_button_block(
                        "Article Summary",
                        "SUMMARIZE_ARTICLE",
                        action_id=action_with_params(
                            slack_const.PROCESS_SUMMARIZE_ARTICLE, [f"url={article['url']}"]
                        ),
                    )
                ]
            ),
            block_builders.divider_block(),
        ]
        paginated_article_blocks.extend(article_blocks)
    paginated_article_blocks.extend(custom_clips_paginator_block(paginated_articles, str(user.id)))
    try:
        article_res = slack_requests.update_channel_message(
            user.slack_integration.channel,
            context.get("ts"),
            access_token,
            block_set=paginated_article_blocks,
        )
    except Exception as e:
        logger.exception(
            f"ERROR sending update channel message for chat submission because of <{e}>"
        )
    return


@background()
def _process_article_summary(payload,context):
    slack_account = UserSlackIntegration.objects.get(slack_id=payload["user"]["id"])
    user = slack_account.user
    url = context.get("url")
    article_res = Article(url)
    article_res.download()
    article_res.parse()
    blocks = payload["message"]["blocks"]
    title_text = blocks[0]["text"]["text"].split("for ")[1].replace("*", "")
    text = article_res.text
    attempts = 1
    token_amount = 500
    timeout = 60.0
    while True:
        url = core_consts.OPEN_AI_CHAT_COMPLETIONS_URI
        prompt = comms_consts.OPEN_AI_ARTICLE_SUMMARY(
            datetime.datetime.now().date(), text, title_text
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
            message = r.get("choices")[0].get("message").get("content").replace("**", "*")

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
    blocks = [block_builders.simple_section("*Article Summary*", "mrkdwn"),block_builders.context_block(article_res.title, "mrkdwn"), block_builders.divider_block(), block_builders.simple_section(message, "mrkdwn")]
    try:
        article_res = slack_requests.update_channel_message(
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