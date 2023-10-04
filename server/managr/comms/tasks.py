import logging
import json
import uuid
import httpx
import datetime
from background_task import background
from managr.utils.client import Variable_Client
from managr.utils.misc import custom_paginator
from managr.slack.helpers.block_sets.command_views_blocksets import custom_clips_paginator_block
from . import constants as comms_consts
from .models import Search, NewsSource
from .serializers import SearchSerializer, NewsSourceSerializer
from managr.core import constants as core_consts
from managr.core.models import User
from managr.core import exceptions as open_ai_exceptions
from managr.slack.helpers import requests as slack_requests
from managr.slack.helpers import block_builders
from managr.slack.helpers.utils import action_with_params
from managr.slack import constants as slack_const
from managr.slack.models import UserSlackIntegration
from newspaper import Article
from managr.slack.helpers.utils import block_finder
from managr.comms.utils import generate_config, extract_base_domain

logger = logging.getLogger("managr")


def emit_process_news_summary(payload, context, schedule=datetime.datetime.now()):
    return _process_news_summary(payload, context, schedule=schedule)


def emit_process_send_clips(payload, context):
    return _process_send_clips(payload, context)


def emit_process_article_summary(payload, context):
    return _process_article_summary(payload, context)


def emit_process_website_domain(url, organization_name):
    return _process_website_domain(url, organization_name)


def create_new_search(payload, user_id):
    state = payload["view"]["state"]["values"]
    input_text = state["SEARCH"]["plain_input"]["value"]
    try:
        instructions = state["OUTPUT_INSTRUCTIONS"]["plain_input"]["value"]
    except KeyError:
        instructions = False
    while True:
        try:
            data = {"input_text": input_text, "user": user_id, "name": input_text[:70]}
            if instructions:
                data["instructions"] = instructions
            serializer = SearchSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            search = serializer.instance
            search.update_boolean()
            break
        except Exception as e:
            logger.exception(e)
            search = False
            break
    return search


def update_search(payload, context):
    update_boolean = False
    state = payload["view"]["state"]["values"]
    input_text = state["SEARCH"]["plain_input"]["value"]
    try:
        instructions = state["OUTPUT_INSTRUCTIONS"]["plain_input"]["value"]
    except KeyError:
        instructions = False
    while True:
        try:
            search = Search.objects.get(id=context.get("search_id"))
            if instructions:
                search.instructions = instructions
            if search.input_text != input_text:
                update_boolean = True
            search.input_text = input_text
            search.save()
            if update_boolean:
                search.update_boolean()
            break
        except Exception as e:
            logger.exception(e)
            search = False
            break
    return search


@background()
def _process_news_summary(payload, context):
    user = User.objects.get(id=context.get("u"))
    while True:
        try:
            search = (
                update_search(payload, context)
                if context.get("search_id", False)
                else create_new_search(payload, str(user.id))
            )
            news_res = Search.get_clips(search.search_boolean)
            articles = news_res["articles"]
            descriptions = [article["description"] for article in articles]
            break
        except Exception as e:
            logger.exception(e)
            break
    attempts = 1
    token_amount = 500
    timeout = 60.0
    while True:
        try:
            instructions = search.instructions if search.instructions else False
            res = Search.get_summary(
                user, token_amount, timeout, descriptions, search.input_text, instructions
            )
            message = res.get("choices")[0].get("message").get("content").replace("**", "*")
            user.add_meta_data("news_summaries")
            user.save()
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
                f"*Summary for {search.input_text}*", "mrkdwn", block_id="NEWS_SUMMARY"
            ),
            block_builders.context_block(f"AI-generated search: {search.search_boolean}", "mrkdwn"),
            block_builders.divider_block(),
            block_builders.simple_section(message, "mrkdwn"),
            block_builders.divider_block(),
            block_builders.actions_block(
                [
                    block_builders.simple_button_block(
                        "Regenerate",
                        "REGENERATE",
                        action_id=action_with_params(
                            slack_const.PROCESS_SHOW_REGENERATE_NEWS_SUMMARY_FORM,
                            params=[f"search_id={str(search.id)}"],
                        ),
                    ),
                    block_builders.simple_button_block(
                        "Show Clips",
                        "SHOW_CLIPS",
                        action_id=action_with_params(
                            slack_const.PROCESS_SEND_CLIPS, params=[f"search_id={str(search.id)}"]
                        ),
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
    search = Search.objects.get(id=context.get("search_id"))
    news_res = Search.get_clips(search.search_boolean)
    paginated_articles = custom_paginator(
        news_res["articles"], count=10, page=context.get("new_page", 1)
    )
    paginated_article_blocks = [
        block_builders.simple_section(f"*Clips for {search.input_text}*", "mrkdwn"),
        block_builders.context_block(f"AI-generated search: {search.search_boolean}", "mrkdwn"),
        block_builders.divider_block(),
    ]
    for article in paginated_articles["results"]:
        text = f"*{article['title']}*\n{article['description']}"
        source_text = f"*Date:* {article['publishedAt'][:10]} (<{article['url']}|{article['source']['name']}> | {article['author']})"
        block_id = str(uuid.uuid4())
        article_blocks = [
            block_builders.simple_section(text, "mrkdwn"),
            block_builders.context_block(source_text, "mrkdwn", block_id),
            block_builders.actions_block(
                [
                    block_builders.simple_button_block(
                        "Article Summary",
                        "SUMMARIZE_ARTICLE",
                        action_id=action_with_params(
                            slack_const.PROCESS_SUMMARIZE_ARTICLE, [f"block_id={block_id}"]
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
def _process_article_summary(payload, context):
    slack_account = UserSlackIntegration.objects.get(slack_id=payload["user"]["id"])
    blocks = payload["message"]["blocks"]
    try:
        index, block = block_finder(context.get("block_id"), blocks)
    except ValueError:
        # did not find the block
        block = None
        pass
    block_text = block["elements"][0]["text"]
    url = block_text[(block_text.find("<") + 1) : block_text.find("|")]
    user = slack_account.user
    attempts = 1
    token_amount = 500
    timeout = 60.0
    while True:
        config = generate_config()
        article_res = Article(url, config=config)
        article_res.download()
        article_res.parse()
        title_text = blocks[0]["text"]["text"].split("for ")[1].replace("*", "")
        text = article_res.text
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
            r = client.post(
                url,
                data=json.dumps(body),
                headers=core_consts.OPEN_AI_HEADERS,
            )
        try:
            r = open_ai_exceptions._handle_response(r)
            message = r.get("choices")[0].get("message").get("content").replace("**", "*")
            user.add_meta_data("article_summaries")
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
    blocks = [
        block_builders.simple_section("*Article Summary*", "mrkdwn"),
        block_builders.context_block(article_res.title, "mrkdwn"),
        block_builders.divider_block(),
        block_builders.simple_section(message, "mrkdwn"),
    ]
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


@background()
def _process_website_domain(url, organization_name):
    base_domain = extract_base_domain(url)
    if base_domain:
        try:
            database_check = NewsSource.objects.get(domain=base_domain)
            if organization_name in database_check.access_count.keys():
                database_check.access_count[organization_name] += 1
            else:
                database_check.access_count[organization_name] = 1
            database_check.save()
        except NewsSource.DoesNotExist:
            try:
                serializer = NewsSourceSerializer(
                    data={"domain": base_domain, "access_count": {organization_name: 1}}
                )
                serializer.is_valid(raise_exception=True)
                serializer.save()
            except Exception as e:
                logger.exception(
                    f"Failed to save new NewsSource for domain: {base_domain} because of {e}"
                )
    return
