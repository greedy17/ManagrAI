import re
import json
from managr.core.utils import Variable_Client
from newspaper import Config
from django.db.models import Q
from .constants import DO_NOT_TRACK_LIST
from dateutil import parser

user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.1234.567 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.1234.567 Safari/537.36 OPR/100.0.1234.567"
    # add more User-Agents if you want
]


def generate_config():
    config = Config()
    # config.browser_user_agent = random.choice(user_agents)
    config.browser_user_agent = (
        "Mozilla/5.0 (compatible; managr-webcrawler/1.0; +https://managr.ai/documentation)"
    )
    config.request_timeout = 10
    return config


def extract_base_domain(article_link):
    pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\.edu\b"

    edu_search = re.search(pattern, article_link)
    if edu_search:
        return None
    match = re.search(r"https?://([^/]+)", article_link)
    if match:
        if match.group(1) in DO_NOT_TRACK_LIST:
            return None
        return match.group(1)
    return None


def boolean_search_to_query(search_string):
    terms = search_string.split()
    query = Q()
    current_query = Q()
    is_negative = False
    for term in terms:
        if term == "AND":
            query &= current_query
            current_query = Q()
        elif term == "OR":
            pass
        elif term == "NOT":
            is_negative = True
        else:
            term = term.replace('"', "")
            term_query = Q(search_vector_field__icontains=term)
            if is_negative:
                current_query &= ~term_query
                is_negative = False
            else:
                current_query |= term_query
    query &= current_query
    return query


def get_search_boolean(search):
    from managr.core import exceptions as open_ai_exceptions
    from managr.core import constants as core_consts

    url = core_consts.OPEN_AI_CHAT_COMPLETIONS_URI
    prompt = core_consts.OPEN_AI_NEWS_BOOLEAN_CONVERSION(search)
    body = core_consts.OPEN_AI_CHAT_COMPLETIONS_BODY(
        "dev",
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
    return query_input


def normalize_newsapi_to_model(api_data):
    normalized_data = [
        dict(
            title=article.get("title", ""),
            description=article.get("description", ""),
            author=article.get("author", ""),
            publish_date=article.get("publishedAt", ""),
            link=article.get("url", ""),
            image_url=article.get("urlToImage"),
            source=article.get("source", {}).get("name", ""),
        )
        for article in api_data
    ]
    return normalized_data


def normalize_article_data(api_data, article_models):
    normalized_list = []
    normalized_api_list = normalize_newsapi_to_model(api_data)
    normalized_list.extend(normalized_api_list)
    normalized_model_list = [article.fields_to_dict() for article in article_models]
    normalized_list.extend(normalized_model_list)
    return normalized_list


def merge_sort_dates(arr):
    if len(arr) > 1:
        mid = len(arr) // 2
        sub_array1 = arr[:mid]
        sub_array2 = arr[mid:]
        merge_sort_dates(sub_array1)
        merge_sort_dates(sub_array2)
        i = j = k = 0
        while i < len(sub_array1) and j < len(sub_array2):
            parsed_value1 = parser.parse(sub_array1[i]["publish_date"])
            parsed_value2 = parser.parse(sub_array2[j]["publish_date"])
            if parsed_value1 < parsed_value2:
                arr[k] = sub_array1[i]
                i += 1
            else:
                arr[k] = sub_array2[j]
                j += 1
            k += 1
        while i < len(sub_array1):
            arr[k] = sub_array1[i]
            i += 1
            k += 1
        while j < len(sub_array2):
            arr[k] = sub_array2[j]
            j += 1
            k += 1
    return arr
