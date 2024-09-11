import logging
import json
import uuid
import httpx
import datetime
import re
import html
from dateutil import parser
from django.conf import settings
from background_task import background
from managr.utils.client import Variable_Client
from managr.utils.misc import custom_paginator
from rest_framework.exceptions import ValidationError
from managr.slack.helpers.block_sets.command_views_blocksets import custom_clips_paginator_block
from . import constants as comms_consts
from .models import Search, NewsSource, AssistAlert, Journalist, JournalistContact, EmailTracker
from .models import Article as InternalArticle
from .serializers import (
    SearchSerializer,
    NewsSourceSerializer,
    JournalistSerializer,
    JournalistContactSerializer,
    EmailTrackerSerializer,
)
from managr.core.models import TaskResults
from managr.core import constants as core_consts
from managr.core.models import User, TaskResults
from managr.core import exceptions as open_ai_exceptions
from managr.slack.helpers import requests as slack_requests
from managr.slack.helpers import block_builders
from managr.slack.helpers.utils import action_with_params, send_to_error_channel
from managr.slack import constants as slack_const
from managr.slack.models import UserSlackIntegration
from newspaper import Article
from managr.slack.helpers.utils import block_finder
from managr.comms.utils import (
    generate_config,
    extract_base_domain,
    normalize_newsapi_to_model,
    normalize_article_data,
    separate_weeks,
)
from managr.api.emails import send_html_email

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


def emit_share_client_summary(summary, clips, title, user_email):
    logger.info("emit function")
    return _share_client_summary(summary, clips, title, user_email)


def emit_get_meta_account_info(user_id):
    return _get_meta_account_info(user_id)


def emit_process_user_hashtag_list(user_id):
    return _process_user_hashtag_list(user_id)


def emit_process_contacts_excel(user_id, data, result_id):
    return _process_contacts_excel(user_id, data, result_id)


def emit_process_regenerate_pitch_slack(payload, context):
    return _process_regenerate_pitch_slack(payload, context)


def emit_process_bulk_draft(data, user_id, task_id):
    return _process_bulk_draft(data, user_id, task_id)


def emit_send_social_summary(news_alert_id, schedule):
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
def _process_website_domain(url, organization_name):
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
        clips = alert.search.get_clips(boolean, end_time, start_time)["articles"]
        if len(clips):
            try:
                clips = [article for article in clips if article["title"] != "[Removed]"]
                normalized_clips = normalize_newsapi_to_model(clips)
                descriptions = [clip["description"] for clip in normalized_clips]
                res = Search.get_summary(
                    alert.user,
                    2000,
                    60.0,
                    descriptions,
                    alert.search.search_boolean,
                    alert.search.instructions,
                    False,
                )
                email_list = [alert.user.email]

                if "@outlook" in email_list[0]:
                    message = html.escape(res.get("choices")[0].get("message").get("content"))
                    message = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", message)
                    for i in range(6, 0, -1):
                        message = re.sub(
                            rf'^{"#" * i} (.*?)$', rf"<h{i}>\1</h{i}>", message, flags=re.MULTILINE
                        )
                    message = re.sub(
                        r"\[(.*?)\]\((.*?)\)|<([^|>]+)\|([^>]+)>",
                        r'<a href="\2\3">\1\4</a>',
                        message,
                    )

                else:
                    message = res.get("choices")[0].get("message").get("content")
                    message = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", message)
                    for i in range(6, 0, -1):
                        message = re.sub(
                            rf'^{"#" * i} (.*?)$', rf"<h{i}>\1</h{i}>", message, flags=re.MULTILINE
                        )
                    message = re.sub(
                        r"\[(.*?)\]\((.*?)\)|<([^|>]+)\|([^>]+)>",
                        r'<a href="\2\3">\1\4</a>',
                        message,
                    )

                clip_short_list = normalized_clips[:5]
                for clip in clip_short_list:
                    if clip["author"] is None:
                        clip["author"] = "N/A"
                    clip["publish_date"] = clip["publish_date"][:10]
                content = {
                    "summary": message,
                    "clips": clip_short_list,
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
            except Exception as e:
                send_to_error_channel(str(e), alert.email, "send news alert")
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
    alert.save()
    return


@background()
def _send_social_summary(news_alert_id):
    alert = AssistAlert.objects.get(id=news_alert_id)
    boolean = alert.search.search_boolean
    tweet_res = alert.user.twitter_account.get_tweets(boolean)
    if len(tweet_res):
        tweet_list = []
        tweets = tweet_res.get("data", None)
        includes = tweet_res.get("includes", None)
        user_data = includes.get("users")
        for tweet in tweets:
            if len(tweet_list) > 5:
                break
            for user in user_data:
                if user["id"] == tweet["author_id"]:
                    if user["public_metrics"]["followers_count"] > 1000:
                        tweet["tweet_link"] = (
                            f"https://twitter.com/{user['username']}/status/{tweet['id']}"
                        )
                        tweet["user"] = user
                        tweet_list.append(tweet)
                    break
        search_tweets = [
            f"Name:{tweet['user']['username']} Tweet: {tweet['text']} Follower count: {tweet['user']['public_metrics']['followers_count']} Date: {tweet['created_at']}"
            for tweet in tweet_list
        ]
        res = alert.user.twitter_account.get_summary(
            alert.user,
            2000,
            60.0,
            search_tweets,
            alert.search.search_boolean,
            alert.search.instructions,
            False,
        )
        message = res.get("choices")[0].get("message").get("content").replace("**", "*")
        content = {
            "summary": message,
            "tweets": tweet_list,
            "website_url": f"{settings.MANAGR_URL}/login",
        }
        send_html_email(
            f"ManagrAI Digest: {alert.search.name}",
            "core/email-templates/social-email.html",
            settings.DEFAULT_FROM_EMAIL,
            [alert.user.email],
            context=content,
        )
        if "sent_count" in alert.meta_data.keys():
            alert.meta_data["sent_count"] += 1
        else:
            alert.meta_data["sent_count"] = 1
        alert.save()
    return


@background()
def _share_client_summary(summary, clips, title, user_email):
    for clip in clips:
        if clip["author"] is None:
            clip["author"] = "N/A"
        clip["publish_date"] = clip["publish_date"][:10]
    content = {
        "summary": summary,
        "clips": clips,
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


@background()
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
        domains = NewsSource.get_stopped_sources()
    if not len(domains):
        domains = [f"No {report_type} domains"]
    try:
        blocks = [
            block_builders.simple_section(f"Report type: {report_type}"),
            block_builders.simple_section(f"{','.join(domains)}"),
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


@background(schedule=2)
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


@background()
def test_database_pull(date_to, date_from, search, result_id):
    date_to = parser.parse(date_to)
    date_from = parser.parse(date_from)
    dates = separate_weeks(date_from, date_to)
    articles = []
    task_ids = []
    print(datetime.datetime.now())
    for date_set in dates:
        try:
            result = TaskResults.objects.create()
            task = get_article_by_week(str(result.id), search, str(date_set[0]), str(date_set[1]))
            result.task = task
            result.save()
            task_ids.append(str(result.id))
        except Exception as e:
            print(e)
    while True:
        for task_id in task_ids:
            task = TaskResults.objects.get(id=task_id)
            if TaskResults.ready(task):
                articles.append(task.json_result)
                task_ids = task_ids.remove(task_id)
        if not task_ids:
            break
        all_data = TaskResults.objects.get(id=result_id)
        all_data.json_result = articles
        all_data.save()
    print(datetime.datetime.now())
    return


def create_contacts_from_file(journalist_ids, user_id):
    user = User.objects.get(id=user_id)
    s = 0
    journalists = Journalist.objects.filter(id__in=journalist_ids).values_list("id", flat=True)
    for journalist_id in journalists:
        try:
            serializer = JournalistContactSerializer(
                data={"journalist": journalist_id, "user": user.id}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            s += 1
        except Exception as e:
            continue
    return


@background()
def _process_contacts_excel(user_id, data, result_id):
    data_length = len(data["email"])
    contacts_to_create = []
    failed_list = []
    succeeded = 0
    for idx in range(data_length):
        try:
            journalist_data = {
                "outlet": data["publication"][idx],
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
    response_data = create_contacts_from_file(contacts_to_create, user_id)
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
        contact = JournalistContact.objects.get(user=user, journalist__email=email)
        if not contact.bio:
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
                    token_amount=token_amount,
                    top_p=0.1,
                    response_format={"type": "json_object"},
                )
                with Variable_Client(timeout) as client:
                    r = client.post(
                        url,
                        data=json.dumps(body),
                        headers=core_consts.OPEN_AI_HEADERS,
                    )
                r = open_ai_exceptions._handle_response(r)
                r = r.get("choices")[0].get("message").get("content")
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


@background()
def test_send_pitch():
    user = User.objects.get(email="zach@mymanagr.com")
    pitch = "Hi [Journalist first name],\n\nYour insightful coverage on aerospace technology advancements has been noted. An exclusive story about SpaceX's latest achievements might pique your interest.\n\nRecently, the Starship prototype was launched by SpaceX, marking a significant stride in space exploration. This development is poised to revolutionize interplanetary travel and aligns with the trend of private companies leading space missions, as highlighted in recent industry reports.\n\nAn exclusive opportunity is offered to explore the technical innovations and strategic vision driving SpaceX's success. Detailed insights and access to key experts can be provided to discuss the implications of these advancements for the future of space exploration.\n\nWould a collaboration on a feature exploring these groundbreaking developments interest you? Your expertise and perspective would bring a unique angle to this story.\n\nLooking forward to your thoughts.\n\nThanks,"
    prompt = "Craft a short media pitch for Space X"
    detail_id = None
    writing_style_id = None
    channel_id = False
    params = [f"u={str(user.id)}"]
    if detail_id:
        params.append(f"d={detail_id}")
    if writing_style_id:
        params.append(f"ws={writing_style_id}")
    try:
        blocks = [
            block_builders.context_block(f"{prompt}", "mrkdwn"),
            block_builders.header_block("Answer:"),
            block_builders.simple_section(f"{pitch}\n", "mrkdwn", "PITCH"),
            block_builders.actions_block(
                [
                    block_builders.simple_button_block(
                        "Edit",
                        "EDIT",
                        action_id=action_with_params(
                            slack_const.PROCESS_ADD_EDIT_FIELD,
                            params,
                        ),
                    )
                ]
            ),
        ]
        channel = channel_id if channel_id else user.slack_integration.channel
        slack_res = slack_requests.send_channel_message(
            channel,
            user.organization.slack_integration.access_token,
            block_set=blocks,
        )
    except Exception as e:
        print(e)
    return


@background()
def test_pitch():
    user = User.objects.get(email="zach@mymanagr.com")
    pitch = """Dear [Recipient's Name],

    We are pleased to introduce a groundbreaking technology designed to enhance rainforest conservation efforts. This innovative solution leverages advanced data analytics and remote sensing to provide real-time monitoring and actionable insights.

    Our technology integrates satellite imagery with machine learning algorithms to detect deforestation activities with unprecedented accuracy. By analyzing high-resolution images, it can identify illegal logging, land-use changes, and other threats to rainforest ecosystems. This allows for timely intervention and more effective enforcement of conservation policies.

    Additionally, the system offers predictive analytics to forecast potential areas of deforestation, enabling proactive measures to protect vulnerable regions. The platform is user-friendly and can be accessed by conservationists, policymakers, and researchers through a secure web interface.

    We believe this technology will significantly contribute to preserving the biodiversity and ecological integrity of rainforests worldwide. For further details or to schedule a demonstration, please do not hesitate to contact us.

    Thank you for your attention to this important matter.

    Sincerely,[Your Name][Your Position][Your Organization]"""

    has_error = False
    attempts = 1
    token_amount = 3000
    timeout = 60.0
    while True:
        try:
            contacts = JournalistContact.objects.filter(user=user)
            contact_list = [
                f"Name:{contact.journalist.full_name}, Outlet:{contact.journalist.outlet}"
                for contact in contacts
            ]
            url = core_consts.OPEN_AI_CHAT_COMPLETIONS_URI
            prompt = comms_consts.OPEN_AI_PITCH_JOURNALIST_LIST(contact_list, pitch)
            body = core_consts.OPEN_AI_CHAT_COMPLETIONS_BODY(
                user.email,
                prompt,
                "You are a VP of Communications",
                token_amount=token_amount,
                top_p=0.1,
                response_format={"type": "json_object"},
            )
            with Variable_Client(timeout) as client:
                r = client.post(
                    url,
                    data=json.dumps(body),
                    headers=core_consts.OPEN_AI_HEADERS,
                )
            res = open_ai_exceptions._handle_response(r)
            res_content = res.get("choices")[0].get("message").get("content")
            journalists = json.loads(res_content).get("journalists")
            print(journalists)
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
        return message

    return journalists
