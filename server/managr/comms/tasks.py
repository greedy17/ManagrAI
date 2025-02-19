import datetime
import json
import logging
import math
import re
import uuid
from copy import copy
from urllib.parse import urlparse

import httpx
from background_task import background
from dateutil import parser
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from newspaper import Article
from rest_framework.exceptions import ValidationError
from scrapy.selector import Selector

from managr.api.emails import send_html_email
from managr.comms.utils import (
    alternate_google_search,
    check_article_validity,
    complete_url,
    extract_base_domain,
    generate_config,
    get_bluesky_data,
    get_domain,
    get_tweet_data,
    get_youtube_data,
    merge_sort_dates,
    normalize_article_data,
    send_url_batch,
)
from managr.core import constants as core_consts
from managr.core import exceptions as open_ai_exceptions
from managr.core.models import TaskResults, User
from managr.slack import constants as slack_const
from managr.slack.helpers import block_builders
from managr.slack.helpers import requests as slack_requests
from managr.slack.helpers.block_sets.command_views_blocksets import custom_clips_paginator_block
from managr.slack.helpers.utils import action_with_params, block_finder, send_to_error_channel
from managr.slack.models import UserSlackIntegration
from managr.utils.client import Variable_Client
from managr.utils.misc import custom_paginator

from . import constants as comms_consts
from .models import ArchivedArticle
from .models import Article as InternalArticle
from .models import (
    AssistAlert,
    Journalist,
    JournalistContact,
    NewsSource,
    Search,
    Thread,
    TwitterAccount,
)
from .serializers import (
    EmailTrackerSerializer,
    JournalistContactSerializer,
    JournalistSerializer,
    NewsSourceSerializer,
    SearchSerializer,
)
from .webcrawler.constants import XPATH_STRING_OBJ, XPATH_TO_FIELD

logger = logging.getLogger("managr")


def emit_process_slack_news_summary(payload, context, schedule=datetime.datetime.now()):
    return _process_slack_news_summary(payload, context, schedule=schedule)


def emit_process_send_clips(payload, context):
    return _process_send_clips(payload, context)


def emit_process_article_summary(payload, context):
    return _process_article_summary(payload, context)


def emit_process_website_domain(url, organization_name):
    return _process_website_domain(url, organization_name)


def emit_send_news_summary(news_alert_id, schedule=datetime.datetime.now()):
    return _send_news_summary(news_alert_id, schedule={"run_at": schedule})


def emit_send_omni_summary(news_alert_id, schedule=datetime.datetime.now()):
    return _send_omni_summary(news_alert_id, schedule={"run_at": schedule})


def emit_share_client_summary(link, title, user_email):
    logger.info("emit function")
    return _share_client_summary(link, title, user_email)


def emit_get_meta_account_info(user_id):
    return _get_meta_account_info(user_id)


def emit_process_user_hashtag_list(user_id):
    return _process_user_hashtag_list(user_id)


def emit_process_contacts_excel(user_id, data, result_id, tags):
    return _process_contacts_excel(user_id, data, result_id, tags)


def emit_process_regenerate_pitch_slack(payload, context):
    return _process_regenerate_pitch_slack(payload, context)


def emit_process_bulk_draft(data, user_id, task_id):
    return _process_bulk_draft(data, user_id, task_id)


def emit_send_social_summary(news_alert_id, schedule=datetime.datetime.now()):
    return _send_social_summary(news_alert_id, schedule={"run_at": schedule})


def create_new_search(payload, user_id):
    state = payload["view"]["state"]["values"]
    input_text = state["SEARCH"]["plain_input"]["value"]
    while True:
        try:
            data = {"input_text": input_text, "user": user_id, "name": input_text[:70]}
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


def get_clips(user, search, date_to, date_from):
    try:
        if "journalist:" in search:
            internal_articles = InternalArticle.search_by_query(search, date_to, date_from, True)
            articles = normalize_article_data([], internal_articles)
            return {"articles": articles, "string": search}
        else:
            url = core_consts.OPEN_AI_CHAT_COMPLETIONS_URI
            prompt = comms_consts.OPEN_AI_QUERY_STRING(search)
            body = core_consts.OPEN_AI_CHAT_COMPLETIONS_BODY(
                user.email,
                prompt,
                token_amount=500,
                top_p=0.1,
            )
            with Variable_Client() as client:
                r = client.post(
                    url,
                    data=json.dumps(body),
                    headers=core_consts.OPEN_AI_HEADERS,
                )
            r = open_ai_exceptions._handle_response(r)
            query_input = r.get("choices")[0].get("message").get("content")
            news_res = Search.get_clips(query_input, date_to, date_from)
            articles = news_res["articles"]
    except Exception as e:
        print(str(e))
    articles = [article for article in articles if article["title"] != "[Removed]"]
    internal_articles = InternalArticle.search_by_query(query_input, date_to, date_from)
    articles = normalize_article_data(articles, internal_articles)
    return {"articles": articles, "string": search}


def get_summary(user, clips, search, instructions=" "):
    if "journalist:" in search:
        instructions = comms_consts.JOURNALIST_INSTRUCTIONS(user.organization.name)
    has_error = False
    attempts = 1
    token_amount = 1000
    timeout = 60.0
    clip_strings = [
        f"Content: {clip['description']}, Date: {clip['publish_date']} , Source:{clip['source']}, Author:{clip['author']}, Link:{clip['link']}"
        for clip in clips
    ]
    while True:
        try:
            res = Search.get_summary(
                user, token_amount, timeout, clip_strings, search, instructions
            )
            message = res.get("choices")[0].get("message").get("content").replace("**", "*")
            user.add_meta_data("news_summaries")
            break
        except open_ai_exceptions.StopReasonLength:
            logger.exception(
                f"Retrying again due to token amount, amount currently at: {token_amount}"
            )
            if token_amount <= 2000:
                has_error = True
                message = "Token amount error"
                break
            else:
                token_amount += 500
                continue
        except httpx.ReadTimeout as e:
            timeout += 30.0
            if timeout >= 120.0:
                has_error = True
                message = "Read timeout issue"
                logger.exception(f"Read timeout from Open AI {e}")
                break
            else:
                attempts += 1
                continue
        except Exception as e:
            has_error = True
            message = f"Unknown exception: {e}"
            logger.exception(e)
            break
    if has_error:
        return {"has_error": has_error, "summary": message}

    return {"has_error": has_error, "summary": message}


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
def _process_slack_news_summary(payload, context):
    state = payload["view"]["state"]["values"]
    if context.get("ts", False):
        title = "Answer"
    else:
        title = "ManagrAI Digest"
    if "INSTRUCTIONS" in state.keys():
        instructions = state["INSTRUCTIONS"]["plain_input"]["value"]
        search = context.get("s")
        start_date = context.get("sd")
        end_date = context.get("ed")
    elif context.get("search_id", False):
        saved_search = Search.objects.get(id=context.get("search_id"))
        instructions = saved_search.instructions
        search = saved_search.input_text
        start_date = state["START_DATE"][list(state["START_DATE"].keys())[0]]["selected_date"]
        end_date = state["STOP_DATE"][list(state["STOP_DATE"].keys())[0]]["selected_date"]
    else:
        search = state["SEARCH"]["plain_input"]["value"]
        instructions = search
        start_date = state["START_DATE"][list(state["START_DATE"].keys())[0]]["selected_date"]
        end_date = state["STOP_DATE"][list(state["STOP_DATE"].keys())[0]]["selected_date"]
    user = User.objects.get(id=context.get("u"))
    attempts = 1
    token_amount = 1000
    timeout = 60.0
    articles = []
    while True:
        try:
            clips_res = get_clips(user, search, start_date, end_date)
            articles = clips_res["articles"]
            if len(articles):
                input_text = clips_res["string"]
                summary_res = get_summary(user, articles, search, instructions)
                message = summary_res["summary"]
                user.add_meta_data("news_summaries_slack")
                user.save()
            else:
                message = "No results found. Try a new search…"
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
        if len(articles):
            blocks = [
                block_builders.context_block(f"{search}", "mrkdwn"),
                block_builders.header_block(title),
                block_builders.simple_section(f"{message}\n", "mrkdwn", "SUMMARY"),
                block_builders.actions_block(
                    [
                        block_builders.simple_button_block(
                            "Ask Follow-Up",
                            "FOLLOWUP",
                            action_id=action_with_params(
                                slack_const.PROCESS_SHOW_REGENERATE_NEWS_SUMMARY_FORM,
                                [f"sd={start_date}", f"ed={end_date}", f"s={search}"],
                            ),
                        )
                    ]
                ),
                block_builders.divider_block(),
                block_builders.header_block("Clips:"),
            ]
        else:
            blocks = [
                block_builders.simple_section(f"{message}\n", "mrkdwn", "SUMMARY"),
                block_builders.actions_block(
                    [
                        block_builders.simple_button_block(
                            "New Search",
                            "FOLLOWUP",
                            action_id=slack_const.PROCESS_SHOW_SEARCH_MODAL,
                        )
                    ]
                ),
            ]

        if len(articles):
            end_index = 5 if len(articles) > 5 else len(articles)
            for i in range(0, end_index):
                article = articles[i]
                date = article["publish_date"][:10]
                fixed_date = f"{date[5:7]}/{date[8:]}/{date[0:4]}"
                author = (
                    article["author"].replace("_", "") if article["author"] is not None else "N/A"
                )
                article_text = f"{article['source']['name']}\n*{article['title']}*\n<{article['link']}|Read More>\n_{author}_ - {fixed_date}"
                blocks.append(block_builders.simple_section(article_text, "mrkdwn"))
                blocks.append(block_builders.divider_block())
        if context.get("ts", False):
            channel = context.get("channel")
            slack_res = slack_requests.update_channel_message(
                channel,
                context.get("ts"),
                user.organization.slack_integration.access_token,
                block_set=blocks,
            )
        else:
            channels = context.get("r").split("|")
            for channel in channels:
                slack_res = slack_requests.send_channel_message(
                    channel,
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
def _process_website_domain(urls, organization_name):
    for url in urls:
        base_domain = extract_base_domain(url)
        full_domain = f"https://{base_domain}"
        if base_domain:
            try:
                database_check = NewsSource.objects.get(domain=full_domain)
                if database_check.access_count is None:
                    database_check.access_count = {organization_name: 1}
                elif organization_name in database_check.access_count.keys():
                    database_check.access_count[organization_name] += 1
                else:
                    database_check.access_count[organization_name] = 1
                database_check.save()
            except NewsSource.DoesNotExist:
                try:
                    serializer = NewsSourceSerializer(
                        data={
                            "domain": full_domain,
                            "access_count": {organization_name: 1},
                        }
                    )
                    serializer.is_valid(raise_exception=True)
                    serializer.save()
                except Exception as e:
                    logger.exception(
                        f"Failed to save new NewsSource for domain: {base_domain} because of {e}"
                    )
    return


@background()
def _send_news_summary(news_alert_id):
    alert = AssistAlert.objects.get(id=news_alert_id)
    thread = None
    project = None
    link = "{settings.MANAGR_URL}/login"
    if alert.thread:
        thread = Thread.objects.get(id=alert.thread.id)
        project = thread.meta_data.get("project", "")
        link = thread.generate_url()

    boolean = alert.search.search_boolean
    end_time = datetime.datetime.now()
    start_time = end_time - datetime.timedelta(hours=24)

    context = {"search_id": str(alert.search.id), "u": str(alert.user.id)}
    payload = {
        "view": {
            "state": {
                "values": {
                    "START_DATE": {"start": {"selected_date": str(start_time.date())}},
                    "STOP_DATE": {"stop": {"selected_date": str(start_time.date())}},
                }
            }
        }
    }
    if alert.type in ["EMAIL", "BOTH"]:
        try:
            clips = alert.search.get_clips(boolean, end_time, start_time)["articles"]
            clips = [article for article in clips if article["title"] != "[Removed]"]
            internal_articles = InternalArticle.search_by_query(
                boolean, str(end_time), str(start_time)
            )
            normalized_clips = normalize_article_data(clips, internal_articles, False)
            if len(normalized_clips):
                descriptions = [clip["description"] for clip in normalized_clips]
                res = Search.get_summary(
                    alert.user,
                    2000,
                    60.0,
                    descriptions,
                    alert.search.instructions,
                    False,
                    False,
                    project,
                    False,
                    alert.search.instructions,
                    True,
                )

                email_list = [alert.user.email]

                message = res.get("choices")[0].get("message").get("content").replace("**", "*")
                message = re.sub(r"\*(.*?)\*", r"<strong>\1</strong>", message)
                message = re.sub(
                    r"\[(.*?)\]\((.*?)\)", r'<a href="\2" target="_blank">\1</a>', message
                )
                if thread:
                    thread.meta_data["articlesFiltered"] = normalized_clips
                    thread.meta_data["filteredArticles"] = normalized_clips
                    thread.meta_data["summary"] = message
                    thread.meta_data["summaries"] = []
                    thread.save()

                content = {
                    "thread_url": link,
                    "website_url": f"{settings.MANAGR_URL}/login",
                    "title": f"{alert.search.name}",
                }
                send_html_email(
                    f"ManagrAI Digest: {alert.search.name}",
                    "core/email-templates/news-email.html",
                    settings.DEFAULT_FROM_EMAIL,
                    email_list,
                    context=content,
                )
            else:
                return
        except Exception as e:
            print(str(e))
            send_to_error_channel(str(e), alert.user.email, "send news alert")
        if type == "BOTH":
            recipients = "|".join(alert.recipients)
            context.update(r=recipients)
            emit_process_slack_news_summary(payload, context)
    else:
        recipients = "|".join(alert.recipients)
        context.update(r=recipients)
        emit_process_slack_news_summary(payload, context)
    if "sent_count" in alert.meta_data.keys():
        alert.meta_data["sent_count"] += 1
    else:
        alert.meta_data["sent_count"] = 1
    alert.meta_data["last_sent"] = datetime.datetime.now().strftime("%m/%d/%Y %H:%M")
    alert.save()
    return


@background()
def _send_social_summary(news_alert_id):
    alert = AssistAlert.objects.get(id=news_alert_id)
    user = alert.user
    thread = alert.thread
    link = thread.generate_url()
    search_boolean = alert.search_boolean
    social_switcher = {
        "youtube": get_youtube_data,
        "twitter": get_tweet_data,
        "bluesky": get_bluesky_data,
    }
    max = 0
    social_values = ["youtube", "bluesky"]
    if user.has_twitter_integration:
        max = 20
        social_values.append("twitter")
    else:
        max = 25
    date_now = datetime.datetime.now(datetime.timezone.utc)
    date_to = str(date_now.date())
    date_from = str((date_now - datetime.timedelta(hours=24)).date())
    email_data = {}
    social_data_list = []
    for value in social_values:
        data_func = social_switcher[value]
        social_data = data_func(
            search_boolean, max=max, user=user, date_from=date_from, date_to=date_to
        )
        if "error" in social_data.keys():
            continue
        else:
            social_data_list.extend(social_data["data"])
    sorted_social_data = merge_sort_dates(social_data_list, "created_at")
    res = TwitterAccount.get_summary(
        alert.user,
        2000,
        60.0,
        sorted_social_data,
        search_boolean,
        alert.instructions,
        False,
    )
    message = res.get("choices")[0].get("message").get("content").replace("**", "*")
    message = re.sub(r"\*(.*?)\*", r"<strong>\1</strong>", message)
    message = re.sub(r"\[(.*?)\]\((.*?)\)", r'<a href="\2" target="_blank">\1</a>', message)
    thread.meta_data["tweets"] = sorted_social_data
    thread.meta_data["summary"] = message
    thread.meta_data["summaries"] = []
    if user.has_twitter_integration:
        if "tweetMedia" in email_data.keys():
            thread.meta_data["tweetMedia"] = email_data["media"]
        if "includes" in email_data.keys():
            thread.meta_data["includes"] = email_data["includes"]
    thread.save()

    content = {
        "thread_url": link,
        "website_url": f"{settings.MANAGR_URL}/login",
        "title": f"{alert.title}",
    }
    send_html_email(
        f"ManagrAI Digest: {alert.title}",
        "core/email-templates/social-email.html",
        settings.DEFAULT_FROM_EMAIL,
        [alert.user.email],
        context=content,
    )
    if "sent_count" in alert.meta_data.keys():
        alert.meta_data["sent_count"] += 1
    else:
        alert.meta_data["sent_count"] = 1
    alert.meta_data["last_sent"] = datetime.datetime.now().strftime("%m/%d/%Y %H:%M")
    alert.save()
    return


@background()
def _share_client_summary(link, title, user_email):

    content = {
        "thread_url": link,
        "website_url": f"{settings.MANAGR_URL}/login",
        "title": f"{title}",
    }
    try:
        send_html_email(
            "ManagrAI Digest",
            "core/email-templates/news-preview.html",
            settings.DEFAULT_FROM_EMAIL,
            [user_email],
            context=content,
        )
    except Exception as e:
        logger.exception(e)
    return


@background()
def _get_meta_account_info(user_id):
    user = User.objects.get(id=user_id)
    ig_account = user.instagram_account
    account_id = ig_account.get_account_id()
    instagram_id = ig_account.get_instagram_account_id(account_id)
    ig_account.instagram_id = instagram_id
    ig_account.save()
    return


@background()
def _process_user_hashtag_list(user_id):
    user = User.objects.get(id=user_id)
    ig = user.instagram_account
    new_hashtag_list = []
    today = datetime.datetime.now().date()
    for tag in ig.hashtag_list:
        hashtag, date, hashtag_id = tag.split(".")
        date_obj = parser.parse(date).date()
        if date_obj == today:
            continue
        else:
            new_hashtag_list.append(tag)
    logger.info(
        f"""
        HASHTAG PROCESSER REPORT:
        USER: {user.email}
        USER_HASHTAG_LIST ({len(ig.hashtag_list)}): {ig.hashtag_list}
        -----------------------------------------
        PROCESSED_LIST ({len(new_hashtag_list)}): {new_hashtag_list}
    """
    )
    ig.hashtag_list = new_hashtag_list
    ig.save()
    return


@background(queue="CRAWLER")
def _run_spider_batch(urls):
    from subprocess import Popen

    try:
        # Run the spider
        command = ["server/manage.py", "crawl_spider", urls]
        process = Popen(command)
        process.wait()
    except Exception as e:
        logger.exception(str(e))


@background
def _add_journalist_to_db(data, verified):
    data["verified"] = verified
    publication = data.pop("publication")
    full_name = data.pop("journalist").strip()
    name_split = full_name.split(" ")
    first = name_split[0]
    last = name_split[len(name_split) - 1]
    data["first_name"] = first
    data["last_name"] = last
    data["outlet"] = publication
    data["date_verified"] = datetime.datetime.now()
    serializer = JournalistSerializer(data=data)
    try:
        serializer.is_valid(raise_exception=True)
        serializer.save()
    except Exception as e:
        logger.exception(str(e))
    return


@background()
def news_source_report(report_type):
    user = User.objects.get(email="zach@mymanagr.com")
    if report_type == "problem":
        domains = NewsSource.problem_urls()
    elif report_type == "stopped":
        domains = NewsSource.objects.stopped()
    if not len(domains):
        domains = [f"No {report_type} domains"]
    for i in range(0, len(domains), 50):
        domain_batch = domains[i : i + 50]
        try:
            blocks = [
                block_builders.simple_section(f"Report type: {report_type}"),
                block_builders.simple_section(f"{','.join(domain_batch)}"),
            ]
            slack_res = slack_requests.send_channel_message(
                user.slack_integration.channel,
                user.organization.slack_integration.access_token,
                block_set=blocks,
            )
        except Exception as e:
            blocks = [
                block_builders.simple_section(f"Report type: {report_type}"),
                block_builders.simple_section(str(e)),
            ]
            slack_res = slack_requests.send_channel_message(
                user.slack_integration.channel,
                user.organization.slack_integration.access_token,
                block_set=blocks,
            )


@background(schedule=2, queue="DEFAULT")
def get_article_by_week(result_id, search, date_from, date_to):

    articles = InternalArticle.search_by_query(search, date_to, date_from)
    article_data = [article.fields_to_dict() for article in articles]
    try:
        result = TaskResults.objects.get(id=result_id)
        result.json_result = article_data
        result.save()
    except Exception as e:
        print(e)
    return


def create_contacts_from_file(journalist_ids, user_id, tags):
    user = User.objects.get(id=user_id)
    s = 0
    journalists = Journalist.objects.filter(id__in=journalist_ids).values_list("id", flat=True)
    for journalist_id in journalists:
        data = {"journalist": journalist_id, "user": user.id}
        if tags:
            data["tags"] = tags
        try:
            serializer = JournalistContactSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            s += 1
        except Exception as e:
            print(e)
            continue
    return


@background()
def _process_contacts_excel(user_id, data, result_id, tags):
    print(tags)
    data_length = len(data["email"])
    contacts_to_create = []
    failed_list = []
    succeeded = 0
    for idx in range(data_length):
        try:
            outlet_list = data["publication"][idx].split(",")
            journalist_data = {
                "outlet": outlet_list[0],
                "email": data["email"][idx],
                "first_name": data["first_name"][idx],
                "last_name": data["last_name"][idx],
                "verified": True,
                "accuracy_score": 100,
            }
            if all(value is None for value in journalist_data.values()):
                pass
            serializer = JournalistSerializer(data=journalist_data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            succeeded += 1
            contacts_to_create.append(str(serializer.instance.id))
        except ValidationError as e:
            if "unique" in str(e):
                succeeded += 1
                journalist = Journalist.objects.filter(email=journalist_data["email"]).first()

                if journalist:
                    contacts_to_create.append(str(journalist.id))
            else:
                email = journalist_data["email"]
                if email:
                    failed_list.append(email)
        except Exception as e:
            continue
    contacts_to_create = list(set(contacts_to_create))
    response_data = create_contacts_from_file(contacts_to_create, user_id, tags)
    result = TaskResults.objects.get(id=result_id)
    result.json_result = {"success": succeeded, "failed": failed_list}
    result.save()
    return


def _process_regenerate_pitch_slack(payload, context):
    user = User.objects.get(id=context.get("u"))
    params = [f"{key}={context[key]}" for key in context.keys()]
    state = payload["state"]["values"]
    instructions = state["EDIT_TEXT"]["plain_input"]["value"]
    style = context.get("ws", None)
    details = context.get("d", None)
    blocks = payload["message"]["blocks"]
    pitch = None
    try:
        pitch_index, pitch_block = block_finder("PITCH", blocks)
        input_index, input_block = block_finder("EDIT_TEXT", blocks)
    except ValueError:
        # did not find the block
        pitch_block = None
        input_block = None
        pass
    pitch = pitch_block["text"]["text"]
    blocks = blocks[:input_index]
    has_error = False
    attempts = 1
    token_amount = 1000
    timeout = 60.0

    while True:
        try:
            url = core_consts.OPEN_AI_CHAT_COMPLETIONS_URI
            prompt = comms_consts.OPEN_AI_PTICH_SLACK_DRAFT_WITH_INSTRUCTIONS(
                pitch, instructions, style, details
            )
            body = core_consts.OPEN_AI_CHAT_COMPLETIONS_BODY(
                user.email,
                prompt,
                token_amount=token_amount,
                top_p=0.1,
            )
            with Variable_Client(timeout) as client:
                r = client.post(
                    url,
                    data=json.dumps(body),
                    headers=core_consts.OPEN_AI_HEADERS,
                )
            r = open_ai_exceptions._handle_response(r)
            pitch = r.get("choices")[0].get("message").get("content")
            blocks[pitch_index] = block_builders.simple_section(pitch, "mrkdwn", "PITCH")
            blocks.append(
                block_builders.actions_block(
                    [
                        block_builders.simple_button_block(
                            "Make Edits",
                            "EDIT",
                            action_id=action_with_params(
                                slack_const.PROCESS_ADD_EDIT_FIELD,
                                params,
                            ),
                        )
                    ]
                )
            )
            user.add_meta_data("pitch_slack")
            slack_res = slack_requests.update_channel_message(
                payload["container"]["channel_id"],
                payload["container"]["message_ts"],
                user.organization.slack_integration.access_token,
                block_set=blocks,
            )
            break
        except open_ai_exceptions.StopReasonLength:
            logger.exception(
                f"Retrying again due to token amount, amount currently at: {token_amount}"
            )
            if token_amount <= 2000:
                has_error = True

                message = "Token amount error"
                break
            else:
                token_amount += 500
                continue
        except httpx.ReadTimeout as e:
            print(e)
            timeout += 30.0
            if timeout >= 120.0:
                has_error = True
                message = "Read timeout issue"
                logger.exception(f"Read timeout from Open AI {e}")
                break
            else:
                attempts += 1
                continue
        except Exception as e:
            has_error = True
            message = f"Unknown exception: {e}"
            logger.exception(e)
            break
    if has_error:
        send_to_error_channel(message, user.email, "regenerate pitch (platform)")
        return
    return


@background()
def _process_bulk_draft(data, user_id, task_id):
    user = User.objects.get(id=user_id)
    task = TaskResults.objects.get(id=task_id)
    emails = data.get("emails")
    original = data.get("original")
    style = data.get("style")
    failed_emails = []
    for email in emails:
        attempts = 1
        has_error = False
        token_amount = 2000
        timeout = 60.0
        try:
            contact = JournalistContact.objects.filter(user=user, journalist__email=email).first()
        except JournalistContact.DoesNotExist:
            continue
        if contact and not contact.bio:
            res = contact.generate_bio()
            if not res:
                failed_emails.append(email)
                continue
        while True:
            try:
                url = core_consts.OPEN_AI_CHAT_COMPLETIONS_URI
                prompt = comms_consts.OPEN_AI_REWRITE_PTICH(
                    original, contact.bio, style, False, "Journalist first name", user.first_name
                )
                body = core_consts.OPEN_AI_CHAT_COMPLETIONS_BODY(
                    user.email,
                    prompt,
                    model="o1-mini",
                )
                with Variable_Client(timeout) as client:
                    r = client.post(
                        url,
                        data=json.dumps(body),
                        headers=core_consts.OPEN_AI_HEADERS,
                    )
                r = open_ai_exceptions._handle_response(r)
                r = r.get("choices")[0].get("message").get("content")
                r = r.replace("```", "").replace("json", "")
                r = json.loads(r)
                serializer_data = {
                    "subject": r["subject"],
                    "recipient": contact.journalist.email,
                    "user": user.id,
                    "body": r["body"],
                    "name": contact.journalist.full_name,
                }
                serializer = EmailTrackerSerializer(data=serializer_data)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                serializer.instance.add_activity("draft_created")
                user.add_meta_data("pitches")
                break
            except open_ai_exceptions.StopReasonLength:
                logger.exception(
                    f"Retrying again due to token amount, amount currently at: {token_amount}"
                )
                if token_amount >= 3000:
                    has_error = True

                    message = "Token amount error"
                    break
                else:
                    token_amount += 1000
                    continue
            except httpx.ReadTimeout as e:
                timeout += 30.0
                if timeout >= 120.0:
                    has_error = True
                    message = "Read timeout issue"
                    logger.exception(f"Read timeout from Open AI {e}")
                    break
                else:
                    attempts += 1
                    continue
            except Exception as e:
                has_error = True
                message = f"Unknown exception: {e}"
                logger.exception(e)
                break
    task.json_result = {"failed": failed_emails}
    task.save()
    return


@background(queue="CRAWLER")
def parse_homepage(domain, body):
    selector = Selector(text=body)
    try:
        source = NewsSource.objects.get(domain=domain)
    except NewsSource.DoesNotExist:
        print(f"Could not find source with domain {domain}")
        return
    source = source.initialize(selector)
    source.save()
    if source.article_link_attribute is not None:
        regex = source.article_link_regex
        article_links = selector.xpath(regex)
        if len(article_links) < 1:
            source.is_crawling = False
            source.save()
        do_not_track_str = ",".join(comms_consts.DO_NOT_TRACK_LIST)
        if source.last_scraped and source.article_link_attribute:
            article_batch = []
            for anchor in article_links:
                article_url = anchor.xpath("@href").extract_first()
                valid = check_article_validity(anchor)
                if not valid:
                    continue
                article_domain = get_domain(article_url)
                if (len(article_domain) and article_domain not in do_not_track_str) or not len(
                    article_domain
                ):
                    article_url = complete_url(article_url, source.domain)
                    article_batch.append(article_url)
            article_check = list(
                InternalArticle.objects.filter(link__in=article_batch, source=source).values_list(
                    "link", flat=True
                )
            )
            new_articles = list(set(article_batch).difference(set(article_check)))
            if len(new_articles):
                send_url_batch(new_articles, False, True)
            print(f"Finished scrapping {domain} and found {len(new_articles)} articles to scrape.")
    else:
        print(f"No article link attribute for {domain}")
    current_datetime = datetime.datetime.now()
    source.last_scraped = timezone.make_aware(current_datetime, timezone.get_current_timezone())
    return source.save()


@background(queue="CRAWLER")
def parse_article(status_url):
    from managr.comms.utils import get_domain
    from managr.comms.webcrawler.extractor import ArticleExtractor

    try:
        with Variable_Client() as client:
            res = client.get(status_url, headers={"Content-Type": "application/json"})
            res = res.json()
        if res.get("status") == "finished":
            response = res.get("response")
            url = res.get("url")
            body = response.get("body")
            domain = get_domain(url, True)
        else:
            parse_article(status_url, schedule=60)
            return
    except json.JSONDecodeError as e:
        print(res)
        print(e)
    parsed_url = urlparse(url).netloc
    try:
        source = NewsSource.objects.get(domain__contains=parsed_url)
    except NewsSource.DoesNotExist:
        print(f"Could not find instance matching {url} ({domain})")
        return
    except NewsSource.MultipleObjectsReturned:
        print(f"Multiple instances matching {url} ({domain})")
        return
    html = Selector(text=body)
    instance = None
    if source is False:
        try:
            instance = Article.objects.get(link=url)
            source = instance.source
        except Article.DoesNotExist:
            try:
                domain = get_domain(url, True)
                source = NewsSource.objects.get(domain__contains=domain)
            except NewsSource.DoesNotExist:
                logger.exception(f"Failed to find source with domain: {domain}")
                return
    source, article_selectors = source.get_selectors(html)
    if source.selectors_defined:
        extractor = ArticleExtractor(source, html, article_selectors, url, instance)
        if not extractor.saved:
            logger.info("Failed to save {}|{}".format(url, extractor.error))
        else:
            source.crawling
            logger.info("Successfully saved {}".format(url))
    return


@background()
def bg_archive_articles(months=6, weeks=0, count_only=False, auto=False):
    """
    Archives articles older than a given date and deletes them from the original table.

    Args:
        months (int) - sets month_date to this many months back from current date, defaults to 6 months
        count_only (bool) - if True prints the count of the queryset the function would be working with.
                            Useful when there's a lot of articles within the timeframe so breaking up
                            archiving articles into smaller groups would be better.
    """
    # Get all articles older than the specified date
    current_date = timezone.now()
    if auto:
        counter = 1
        target = 50000
        while True:
            if counter >= 25:
                print(f"No date with a close article count")
                break
            month_date = current_date - relativedelta(
                months=counter,
            )
            test_count = InternalArticle.objects.filter(publish_date__lt=month_date).count()
            if math.isclose(target, test_count, abs_tol=20000):
                print(f"Closest date: {month_date} || Count: {test_count}")
                break
            print(f"Date ({month_date}) does not meet criteria ({test_count})")
            counter += 1
        return
    else:
        month_date = current_date - relativedelta(months=months, weeks=weeks)
        print(f"Archiving publish dates older than {month_date}")
        if count_only:
            articles_to_archive = InternalArticle.objects.filter(
                publish_date__lt=month_date
            ).count()
            print(f"{articles_to_archive} articles older than {month_date}")
            return
        articles_to_archive = InternalArticle.objects.filter(publish_date__lt=month_date)
        print(f"Found {len(articles_to_archive)} articles to archive")
        print(f"Attempting to archive {len(articles_to_archive)} articles")
        if articles_to_archive:
            for i in range(0, len(archived_articles), int(10000)):
                archived_articles = []
                # Prepare archived articles for bulk creation
                batch = articles_to_archive[i : i + 10000]
                for article in batch:
                    archived_articles.append(
                        ArchivedArticle(
                            title=article.title,
                            description=article.description,
                            author=article.author,
                            publish_date=article.publish_date,
                            link=article.link,
                            image_url=article.image_url,
                            source=article.source,
                            content=article.content,
                        )
                    )
                with transaction.atomic():
                    batch = archived_articles[i : i + 10000]
                    successful_arts = ArchivedArticle.objects.bulk_create(
                        batch, 1000, ignore_conflicts=True
                    )
                    print(f"Successfully archived {len(successful_arts)}/{len(batch)} articles.")
        articles_to_archive.delete()
        return


@background()
def _send_omni_summary(news_alert_id):
    alert = AssistAlert.objects.get(id=news_alert_id)
    user = alert.user
    thread = alert.thread
    link = thread.generate_url()
    search_boolean = alert.search_boolean
    social_switcher = {
        "youtube": get_youtube_data,
        "twitter": get_tweet_data,
        "bluesky": get_bluesky_data,
    }
    max = 0
    social_values = ["youtube", "bluesky"]
    if user.has_twitter_integration:
        max = 20
        social_values.append("twitter")
    else:
        max = 25
    date_now = datetime.datetime.now(datetime.timezone.utc)
    date_to = str(date_now.date())
    date_from = str((date_now - datetime.timedelta(hours=24)).date())
    social_data_dict = {"twitter": []}
    for value in social_values:
        data_func = social_switcher[value]
        social_data = data_func(
            search_boolean, max=max, user=user, date_from=date_from, date_to=date_to
        )
        print("{}, {}".format(value, social_data))
        if "error" in social_data.keys():
            social_data_dict[value] = []
            continue
        else:
            social_data_dict[value] = social_data["data"]
    internal_articles = InternalArticle.search_by_query(
        search_boolean, str(date_to), str(date_from)
    )
    normalized_clips = normalize_article_data([], internal_articles, False)[:31]
    google_results = alternate_google_search(search_boolean, 5, True)["results"]
    url = core_consts.OPEN_AI_CHAT_COMPLETIONS_URI
    prompt = comms_consts.OPEN_AI_OMNI_SUMMARY(
        date_now,
        alert.search.input_text,
        normalized_clips,
        social_data_dict["twitter"][:5],
        social_data_dict["youtube"][:6],
        social_data_dict["bluesky"][:7],
        google_results,
        thread.meta_data["project"],
    )

    body = core_consts.OPEN_AI_CHAT_COMPLETIONS_BODY(
        user.email,
        prompt,
        "You are a VP of Communications",
        top_p=0.1,
    )
    with Variable_Client(30) as client:
        r = client.post(
            url,
            data=json.dumps(body),
            headers=core_consts.OPEN_AI_HEADERS,
        )
    res = open_ai_exceptions._handle_response(r)
    sorted_social_data = []
    sorted_social_data.extend(social_data_dict["twitter"][:5])
    sorted_social_data.extend(social_data_dict["bluesky"][:7])
    sorted_social_data.extend(social_data_dict["youtube"][:6])
    sorted_social_data = merge_sort_dates(sorted_social_data, "created_at")
    message = res.get("choices")[0].get("message").get("content").replace("**", "*")
    message = re.sub(r"\*(.*?)\*", r"<strong>\1</strong>", message)
    message = re.sub(r"\[(.*?)\]\((.*?)\)", r'<a href="\2" target="_blank">\1</a>', message)
    thread.meta_data["omniSocial"] = sorted_social_data
    thread.meta_data["omniNews"] = normalized_clips
    thread.meta_data["omniWeb"] = google_results
    thread.meta_data["omniResults"] = [*sorted_social_data, *normalized_clips, *google_results]
    thread.save()
    content = {
        "thread_url": link,
        "website_url": f"{settings.MANAGR_URL}/login",
        "title": f"{alert.title}",
    }
    send_html_email(
        f"ManagrAI Digest: {alert.title}",
        "core/email-templates/social-email.html",
        settings.DEFAULT_FROM_EMAIL,
        [alert.user.email],
        context=content,
    )
    if "sent_count" in alert.meta_data.keys():
        alert.meta_data["sent_count"] += 1
    else:
        alert.meta_data["sent_count"] = 1
    alert.meta_data["last_sent"] = datetime.datetime.now().strftime("%m/%d/%Y %H:%M")
    alert.save()
    return
