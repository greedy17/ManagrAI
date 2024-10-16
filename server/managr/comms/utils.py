import re
import json
import boto3
import csv
import fitz
import tempfile
import requests
import pytz
import io
import base64
from datetime import datetime, timezone, timedelta
from newspaper import Article, ArticleException
from functools import reduce
from managr.core.utils import Variable_Client
from newspaper import Config
from django.db.models import Q
from . import constants as comms_consts
from dateutil import parser
from django.conf import settings
from urllib.parse import urlparse, urlunparse
from collections import OrderedDict
from .exceptions import _handle_response
from .models import NewsSource, Journalist, JournalistContact
from botocore.exceptions import ClientError
from django.contrib.postgres.search import SearchQuery
from managr.core import constants as core_consts
from managr.core import exceptions as open_ai_exceptions
from managr.core.models import User

s3 = boto3.client("s3")

user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.1234.567 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.1234.567 Safari/537.36 OPR/100.0.1234.567",
]


def extract_email_address(text):
    match = re.search(r"<([^<>]+)>", text)
    if match:
        return match.group(1)
    return None


def get_domain(url, full_netloc=False):
    parsed_url = urlparse(url)
    netloc = parsed_url.netloc
    domain_parts = netloc.split(".")
    if "www" in domain_parts:
        domain_parts.remove("www")
    if full_netloc:
        return ".".join(domain_parts)
    return domain_parts[0]


def extract_date_from_text(text):
    if "Published" in text and "Updated" in text:
        text = text.split("Updated")
        text[0] = text[0].replace("Published:", "")
    if isinstance(text, list):
        if len(text) > 0:
            text = text[0]
        else:
            return None
    try:
        parsed_date = parser.parse(text)
        return str(parsed_date)
    except parser.ParserError:
        pass
    text = text.replace("\n", "").replace("\t", "").strip()
    patterns = [
        r"(\d{1,2} [A-Za-z]+ \d{4})",
        r"([A-Za-z]+(?: \d{1,2},)? \d{4})",
        r"([A-Za-z]{3}\. \d{1,2}, \d{4} \d{1,2}:\d{2} [apAP]\.m\.)",
        r"(\w+\s\d+,\s\d{4})",
        r"(?P<date>\w+ \d{1,2}, \d{4}) at (?P<time>\d{1,2}:\d{2} \w{2})",
        r"(\d{1,2}:\d{2} [ap]\.m\. ET [A-Za-z]{3}\. \d{1,2}, \d{4})",
        r"(\w+ \d{1,2}, \d{4}) at (\d{1,2}:\d{2}[ap]m)(?: \w{3})?",
        r"\b[A-Za-z]+\s\d{1,2},\s\d{4}\b",
    ]
    date_str = text
    strptime_formats = [
        "%d %B %Y",
        "%B %d, %Y",
        "%b %d, %Y",
        "%b. %d, %Y %I:%M %p",
        "%Y-%m-%dT%H:%M:%S%z",
        "%B %d, %Y at %I:%M %p",
        "%I:%M %p ET %b. %d, %Y",
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            date_str = match.group()
            if ":" in date_str:
                colon_idx = date_str.index(":")
                start_index = colon_idx - 2 if colon_idx >= 2 else 0
                hour = date_str[start_index:colon_idx]
                if int(hour) < 10 and " " in hour:
                    hour = " 0" + str(int(hour))
                    date_str = date_str[: colon_idx - 2] + hour + date_str[colon_idx:]
            if "a.m." in date_str:
                date_str = date_str.replace("a.m.", "AM")
            if "p.m." in date_str:
                date_str = date_str.replace("p.m.", "PM")
    for format in strptime_formats:
        try:
            date_obj = datetime.strptime(date_str, format)
        except ValueError:
            continue
        except Exception:
            continue
        return str(date_obj)
    return None


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
        if match.group(1) in ",".join(comms_consts.DO_NOT_TRACK_LIST):
            return None
        return match.group(1)
    return None


def split_and_combine_terms(string):
    terms = string.replace('"', "").replace("(", "").replace(")", "").split()
    corrected_terms = []
    current_term = ""
    for idx, term in enumerate(terms):
        if term in ["AND", "OR", "NOT"]:
            corrected_terms.append(current_term)
            current_term = ""
            corrected_terms.append(term)
        elif idx == len(terms) - 1:
            if len(current_term):
                current_term += f" {term}"
            else:
                current_term = term
            corrected_terms.append(current_term)
        else:
            if len(current_term):
                current_term += f" {term}"
            else:
                current_term = term
    return corrected_terms


def boolean_search_to_query(search_string):
    term_list = split_and_combine_terms(search_string)
    query = Q()
    current_q_objects = []
    current_query = None
    is_negative = False
    for idx, term in enumerate(term_list):
        if idx == len(term_list) - 1:
            current_query = Q(content__iregex=r"\m{}\M".format(term))
            if len(current_q_objects):
                if current_query is not None:
                    current_q_objects.append(current_query)
                current_query = reduce(lambda q1, q2: q1 | q2, current_q_objects)
                current_q_objects = []
            if is_negative:
                query &= ~current_query
            else:
                query &= current_query
        elif term == "AND":
            if len(current_q_objects):
                current_query = reduce(lambda q1, q2: q1 | q2, current_q_objects)
                current_q_objects = []
            query &= current_query
            current_query = None
            is_negative = False
        elif term == "OR":
            if current_query is not None:
                current_q_objects.append(current_query)
            current_query = None
        elif term == "NOT":
            if len(current_q_objects):
                if current_query is not None:
                    current_q_objects.append(current_query)
                current_query = reduce(lambda q1, q2: q1 | q2, current_q_objects)
                current_q_objects = []
            if current_query:
                if is_negative:
                    query &= ~current_query
                else:
                    query &= current_query
            current_query = None
            is_negative = True
        else:
            current_query = Q(content__iregex=r"\m{}\M".format(term))

    return query


def boolean_search_to_searchquery(search_string):
    term_list = split_and_combine_terms(search_string)
    search_query = None
    current_search_queries = []
    current_query = None
    is_negative = False
    for idx, term in enumerate(term_list):
        if idx == len(term_list) - 1:
            current_query = SearchQuery(term, search_type="plain")
            if current_search_queries:
                if current_query is not None:
                    current_search_queries.append(current_query)
                current_query = reduce(lambda q1, q2: q1 | q2, current_search_queries)
                current_search_queries = []
            if is_negative:
                if search_query:
                    search_query &= ~current_query
                else:
                    search_query = ~current_query
            else:
                if search_query:
                    search_query &= current_query
                else:
                    search_query = current_query
        elif term == "AND":
            if current_search_queries:
                current_query = reduce(lambda q1, q2: q1 | q2, current_search_queries)
                current_search_queries = []
            if search_query:
                print(search_query)
                search_query &= current_query
            else:
                search_query = current_query
            current_query = None
            is_negative = False
        elif term == "OR":
            if current_query is not None:
                current_search_queries.append(current_query)
            current_query = None
        elif term == "NOT":
            if current_search_queries:
                if current_query is not None:
                    current_search_queries.append(current_query)
                current_query = reduce(lambda q1, q2: q1 | q2, current_search_queries)
                current_search_queries = []
            if current_query:
                if is_negative:
                    search_query &= ~current_query
                else:
                    search_query &= current_query
            current_query = None
            is_negative = True
        else:
            current_query = SearchQuery(term, search_type="plain")
    if search_query is None:
        search_query = current_query
    return search_query


def get_search_boolean(search):
    from managr.core import exceptions as open_ai_exceptions
    from managr.core import constants as core_consts

    url = core_consts.OPEN_AI_CHAT_COMPLETIONS_URI
    prompt = core_consts.OPEN_AI_NEWS_BOOLEAN_CONVERSION(search)
    tokens = 2000
    while True:
        body = core_consts.OPEN_AI_CHAT_COMPLETIONS_BODY(
            "dev",
            prompt,
            token_amount=tokens,
            top_p=0.1,
        )
        try:
            with Variable_Client() as client:
                r = client.post(
                    url,
                    data=json.dumps(body),
                    headers=core_consts.OPEN_AI_HEADERS,
                )
            r = open_ai_exceptions._handle_response(r)
            break
        except open_ai_exceptions.StopReasonLength:
            if token_amount <= 5000:
                has_error = True

                message = "Token amount error"
                break
            else:
                token_amount += 1000
                continue

    query_input = r.get("choices")[0].get("message").get("content")
    return query_input


def convert_html_to_markdown(summary, clips):
    from managr.core import exceptions as open_ai_exceptions
    from managr.core import constants as core_consts

    url = core_consts.OPEN_AI_CHAT_COMPLETIONS_URI
    prompt = core_consts.OPEN_AI_CONVERT_HTML(summary, clips)
    body = core_consts.OPEN_AI_CHAT_COMPLETIONS_BODY(
        "ManagrAI",
        prompt,
        token_amount=2000,
        top_p=0.1,
    )
    with Variable_Client() as client:
        r = client.post(
            url,
            data=json.dumps(body),
            headers=core_consts.OPEN_AI_HEADERS,
        )
    r = open_ai_exceptions._handle_response(r)
    new_summary = r.get("choices")[0].get("message").get("content")
    return new_summary


def convert_html_to_markdown(summary, clips):
    from managr.core import exceptions as open_ai_exceptions
    from managr.core import constants as core_consts

    url = core_consts.OPEN_AI_CHAT_COMPLETIONS_URI
    prompt = core_consts.OPEN_AI_CONVERT_HTML(summary, clips)
    body = core_consts.OPEN_AI_CHAT_COMPLETIONS_BODY(
        "ManagrAI",
        prompt,
        token_amount=1500,
        top_p=0.1,
    )
    with Variable_Client() as client:
        r = client.post(
            url,
            data=json.dumps(body),
            headers=core_consts.OPEN_AI_HEADERS,
        )
    r = open_ai_exceptions._handle_response(r)
    new_summary = r.get("choices")[0].get("message").get("content")
    return new_summary


def normalize_newsapi_to_model(api_data):
    normalized_data = [
        dict(
            title=article.get("title", ""),
            description=article.get("description", ""),
            author=article.get("author", ""),
            publish_date=article.get("publishedAt", ""),
            link=article.get("url", ""),
            image_url=article.get("urlToImage"),
            source=article.get("source", {}),
        )
        for article in api_data
    ]
    return normalized_data


def merge_sort_dates(arr, key="publish_date"):
    if len(arr) > 1:
        mid = len(arr) // 2
        sub_array1 = arr[:mid]
        sub_array2 = arr[mid:]
        merge_sort_dates(sub_array1, key)
        merge_sort_dates(sub_array2, key)
        i = j = k = 0
        while i < len(sub_array1) and j < len(sub_array2):
            parsed_value1 = parser.parse(sub_array1[i][key]).replace(tzinfo=timezone.utc)
            parsed_value2 = parser.parse(sub_array2[j][key]).replace(tzinfo=timezone.utc)
            if parsed_value1 > parsed_value2:
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


def normalize_article_data(api_data, article_models, for_test=False):
    normalized_list = []
    normalized_api_list = normalize_newsapi_to_model(api_data)
    normalized_list.extend(normalized_api_list)
    normalized_model_list = [article.fields_to_dict(for_test) for article in article_models]
    normalized_list.extend(normalized_model_list)
    sorted_arr = merge_sort_dates(normalized_list)
    ordered_dict = OrderedDict()
    for obj in sorted_arr:
        if obj["title"] not in ordered_dict.keys():
            ordered_dict[obj["title"]] = obj
    duplicates_removed_list = list(ordered_dict.values())[:50]
    return duplicates_removed_list


def create_and_upload_csv(data):
    file_name = "content_data.csv"
    s3 = boto3.client("s3")
    location = "staging" if settings.IN_STAGING else "prod"
    key = f"{location}/{file_name}"

    try:
        s3.head_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=key)
    except ClientError as e:
        if e.response["Error"]["Code"] == "404":
            with open(file_name, "w", newline="") as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow(
                    [
                        "Organization Name",
                        "User Email",
                        "Type",
                        "Content",
                        "Action Integer",
                        "Positive/Negative",
                    ]
                )
            s3.upload_file(file_name, settings.AWS_STORAGE_BUCKET_NAME, key)
        else:
            raise  # Re-raise the caught exception
    else:
        mode = "a" if data[0] != "Organization Name" else "w"
        with open(file_name, mode, newline="") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(data)

        s3.upload_file(file_name, settings.AWS_STORAGE_BUCKET_NAME, key)


def append_data_to_daily_file(data):
    bucket_name = settings.AWS_STORAGE_BUCKET_NAME
    today = datetime.now().strftime("%Y-%m-%d")
    file_name = f"{settings.ENVIRONMENT}/current week/data_{today}.csv"

    with open(file_name, "a", newline="") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(data)

    s3.upload_file(file_name, bucket_name, file_name)


def combine_weekly_data():
    bucket_name = settings.AWS_STORAGE_BUCKET_NAME
    prefix = f"{settings.ENVIRONMENT}/current week/"
    objects = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)

    combined_data = []

    for obj in objects.get("Contents", []):
        key = obj["Key"]
        response = s3.get_object(Bucket=bucket_name, Key=key)
        data = response["Body"].read().decode("utf-8").splitlines()
        combined_data.extend(data)

    # Append the combined data to the primary CSV file
    primary_file_key = "Content Data.csv"
    response = s3.get_object(Bucket=bucket_name, Key=primary_file_key)
    primary_data = response["Body"].read().decode("utf-8").splitlines()

    combined_data.extend(primary_data)

    # Upload the updated data to the primary CSV file
    s3.put_object(Bucket=bucket_name, Key=primary_file_key, Body="\n".join(combined_data))


def get_news_api_sources():
    news_url = comms_consts.NEW_API_URI + "/" + "sources"
    with Variable_Client() as client:
        new_res = client.get(news_url, headers=comms_consts.NEWS_API_HEADERS)
    return _handle_response(new_res)


def remove_api_sources():
    all_sources = NewsSource.objects.all()
    try:
        news_api_source_res = get_news_api_sources()
        r = news_api_source_res["sources"]
        source_list = [source["url"] for source in r]
    except Exception as e:
        print(str(e))
    for url in source_list:
        database_check = all_sources.filter(domain=url).first()
        if database_check:
            database_check.delete()
    return


def potential_link_check(href, website_url):
    parsed_url = urlparse(website_url)
    site_url = parsed_url.netloc
    if "https" in href:
        if site_url in href:
            return True
        else:
            return False
    return True


def complete_url(url, default_domain, default_scheme="https"):
    parsed_url = urlparse(url)
    parsed_source_domain = urlparse(default_domain)
    netloc = parsed_url.netloc if parsed_url.netloc else parsed_source_domain.netloc
    complete_url = urlunparse(
        (
            default_scheme,
            netloc,
            parsed_url.path,
            parsed_url.params,
            parsed_url.query,
            parsed_url.fragment,
        )
    )
    return complete_url


def images_extractor(pdf, page):
    import base64

    image_list = []
    images = page.get_images()
    if len(images):
        image = pdf.extract_image(images[0][0])
        image_base64 = base64.b64encode(image["image"]).decode("utf-8")
        image_list.append(image_base64)
    return image_list


def save_and_extract_text(file):
    text = ""
    image_list = []
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            temp_file.write(file.read())
            temp_filename = temp_file.name

        # Open the PDF file with PyMuPDF
        doc = fitz.open(temp_filename)
        for page_number in range(doc.page_count):
            page = doc.load_page(page_number)
            text += page.get_text()
            images = images_extractor(doc, page)
            image_list.extend(images)
        import os

        # Remove the temporary file
        os.remove(temp_filename)

        return text, image_list
    except Exception as e:
        print(str(e))
        return "", image_list


def extract_pdf_text(pdf_file):
    from django.core.files.uploadedfile import InMemoryUploadedFile

    text = ""
    image_list = []
    try:
        if isinstance(pdf_file, InMemoryUploadedFile):
            text, images = save_and_extract_text(pdf_file)
            image_list.extend(images)
        else:
            # Open the PDF file with PyMuPDF
            doc = fitz.open(pdf_file.temporary_file_path())
            for page_number in range(doc.page_count):
                page = doc.load_page(page_number)
                text += page.get_text()
                images = images_extractor(doc, page)
                image_list.extend(images)
        return text, image_list
    except Exception as e:
        print(str(e))
        return "", image_list


def convert_pdf_from_url(url):
    import os

    text = ""
    image_list = []
    try:
        r = requests.get(url)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            temp_file.write(r.content)
            temp_filename = temp_file.name

        # Open the PDF file with PyMuPDF
        doc = fitz.open(temp_filename)
        for page_number in range(doc.page_count):
            page = doc.load_page(page_number)
            text += page.get_text()
            images = images_extractor(doc, page)
            image_list.extend(images)
        # Remove the temporary file
        os.remove(temp_filename)

        return text, image_list
    except Exception as e:
        print(str(e))
        return "", image_list


def google_search(query, number_of_results=5, include_images=True):
    url = comms_consts.GOOGLE_SEARCH_URI
    params = comms_consts.GOOGLE_SEARCH_PARAMS(query, number_of_results)
    with Variable_Client() as client:
        res = client.get(url, params=params)
        if res.status_code == 200:
            results_list = []
            images = []
            res = res.json()
            # print('RESPONSE IS HERE -- >', res)
            results = res["items"]
            for item in results:
                result_data = {
                    "title": item["title"],
                    "snippet": item.get("snippet", "None"),
                    "link": item["link"],
                }
                if include_images:
                    try:
                        image = item.get("pagemap", {}).get("cse_image", None)
                        if image:
                            images.append(image[0]["src"])
                    except Exception as e:
                        print(e)
                        pass
                results_list.append(result_data)
            return {"images": images, "results": results_list}
        else:
            return {}


def alternate_google_search(query, number_of_results=5):
    url = comms_consts.GOOGLE_SEARCH_URI
    params = comms_consts.GOOGLE_SEARCH_PARAMS(query, number_of_results)
    with Variable_Client() as client:
        res = client.get(url, params=params)
        results_list = []
        if res.status_code == 200:
            res = res.json()
            results = res["items"]
            for index, item in enumerate(results):
                metatags = item["pagemap"]["metatags"][0]
                metatags_cse = item["pagemap"].get("cse_image", [])
                cse_img = metatags_cse[0] if metatags_cse else {}
                author = (
                    metatags.get("article:author")
                    if "article:author" in metatags
                    else metatags.get("author", "Unknown")
                )
                result_data = {
                    "id": index + 1,
                    "title": item["title"],
                    "snippet": item["snippet"],
                    "link": item["link"],
                    "source": metatags.get("og:site_name", "unknown"),
                    "source_img": metatags.get("og:image", ""),
                    # "description": metatags.get("og:description", ''),
                    "image": cse_img.get("src", ""),
                    "author": author,
                }
                results_list.append(result_data)
            return {"results": results_list}
        else:
            return {}


def check_journalist_validity(journalist, outlet, email):
    from managr.comms.serializers import JournalistSerializer

    data = {"email": email, "outlet": outlet}
    name_list = journalist.split(" ")
    db_check = []
    if len(journalist) > 2:
        first = name_list[0]
        last = name_list[len(name_list) - 1]
    else:
        first = name_list[0]
        last = name_list[1]
    try:
        email_check = Journalist.objects.filter(email=email)
        if len(email_check):
            db_check = email_check
        else:
            name_check = Journalist.objects.filter(first_name__iexact=first, last_name__iexact=last)
            if len(name_check):
                db_check = name_check
        if len(db_check):
            internal_journalist = db_check.first()
            return internal_journalist
        else:
            score = Journalist.verify_email(email)
            is_valid = True if score >= 85 else False
            if is_valid is False:
                r = Journalist.email_finder(first, last, False, outlet)
                if isinstance(r, dict) and "error" in r.keys():
                    return r
                score = r["score"]
                if score is None:
                    score = 0
                is_valid = True if score >= 85 else False
                if r["email"] is not None:
                    email = r["email"]
                    data["email"] = email
            data["accuracy_score"] = score
            data["first_name"] = first
        data["verified"] = is_valid
        data["last_name"] = last
        data["date_verified"] = datetime.now()
        if not len(data["email"]):
            data["email"] = f"{first}.{last}@domain.com"
        serializer = JournalistSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return serializer.instance
    except Exception as e:
        print(data, str(e))
        return {"error": "Could not create contact."}


def get_journalist_list(search, content):
    token_amount = 1000
    timeout = 60.0
    journalist_list = []
    while True:
        try:
            url = core_consts.OPEN_AI_CHAT_COMPLETIONS_URI
            if not journalist_list:
                prompt = comms_consts.OPEN_AI_GET_JOURNALIST_LIST(search, content)
                body = core_consts.OPEN_AI_CHAT_COMPLETIONS_BODY(
                    "zach@mymanagr.com",
                    prompt,
                    token_amount=token_amount,
                    temperature=0,
                    response_format={"type": "json_object"},
                )
                with Variable_Client(timeout) as client:
                    r = client.post(
                        url,
                        data=json.dumps(body),
                        headers=core_consts.OPEN_AI_HEADERS,
                    )
                r = open_ai_exceptions._handle_response(r)
                message = r.get("choices")[0].get("message").get("content")
                message = json.loads(message)
                message = message["journalists"]
                if len(message):
                    journalist_list = message
                break
        except open_ai_exceptions.StopReasonLength:
            if token_amount >= 6000:
                journalist_list = "Token amount error"
                break
            else:
                token_amount += 1000
                continue
        except Exception as e:
            journalist_list = str(e)
            break
    return journalist_list


def fill_journalist_info(search, journalists, content):
    token_amount = 1000
    timeout = 60.0
    journalist_data = []
    while True:
        try:
            url = core_consts.OPEN_AI_CHAT_COMPLETIONS_URI
            prompt = comms_consts.OPEN_AI_DISCOVER_JOURNALIST(search, journalists, content)
            body = core_consts.OPEN_AI_CHAT_COMPLETIONS_BODY(
                "zach@mymanagr.com",
                prompt,
                token_amount=token_amount,
                temperature=0,
                response_format={"type": "json_object"},
            )
            with Variable_Client(timeout) as client:
                r = client.post(
                    url,
                    data=json.dumps(body),
                    headers=core_consts.OPEN_AI_HEADERS,
                )
            r = open_ai_exceptions._handle_response(r)
            message = r.get("choices")[0].get("message").get("content")
            message = json.loads(message)
            journalist_data = message["journalists"]
            if len(journalist_data) > 15:
                journalist_data = journalist_data[:16]
            break
        except open_ai_exceptions.StopReasonLength:
            if token_amount >= 6000:
                journalist_data = "Token amount error"
                break
            else:
                token_amount += 1000
                continue
        except Exception as e:
            journalist_data = f"Unknown exception: {e}"
            break
    return journalist_data


def get_journalists(search, content):
    journalist_data = []
    while True:
        try:
            journalist_list = get_journalist_list(search, content)
            if isinstance(journalist_list, str):
                journalist_data = journalist_list
                break
            results = {}
            for j in journalist_list:
                res = google_search(f"{j} AND journalist AND 2024", 3)
                res = res["results"]
                str_list = [f"{r['title']},{r['snippet']}" for r in res]
                results[j] = str_list
            journalist_data = fill_journalist_info(search, results, content)
            break
        except Exception as e:
            journalist_data = str(e)
            break
    return journalist_data


def separate_weeks(start_date, end_date, delta=7):
    dates = []
    current_to = end_date
    while current_to > start_date:
        date_from = current_to - timedelta(days=delta)
        dates.append((date_from, current_to))
        current_to = date_from
    if dates[-1][0] > start_date:
        dates[-1] = (start_date, dates[-1][1])
    return dates


# def submit_job(url, id):
#     response = batch_client.submit_job(
#         jobName=f"crawler-{id}",
#         jobQueue="crawler-queue",
#         jobDefinition="web-scraper-prod",
#         containerOverrides={"command": ["server/manage.py", "crawl_spider.py", url]},
#     )
#     return response


def test_get_clips(search, boolean=False):
    from managr.comms.models import Article, Search
    from managr.core.constants import (
        OPEN_AI_CHAT_COMPLETIONS_URI,
        OPEN_AI_CHAT_COMPLETIONS_BODY,
        OPEN_AI_HEADERS,
    )
    from managr.core.exceptions import _handle_response

    try:
        today = datetime.now()
        date_to = str(datetime.now().date())
        date_from = str((today - timedelta(days=7)).date())
        if "journalist:" in search:
            internal_articles = Article.search_by_query(search, date_to, date_from, True)
            articles = normalize_article_data([], internal_articles)
            return {"articles": articles, "string": search}
        if not boolean:
            url = OPEN_AI_CHAT_COMPLETIONS_URI
            prompt = comms_consts.OPEN_AI_QUERY_STRING(search)
            body = OPEN_AI_CHAT_COMPLETIONS_BODY(
                "support@mymanagr.com",
                prompt,
                token_amount=500,
                top_p=0.1,
            )
            with Variable_Client() as client:
                r = client.post(
                    url,
                    data=json.dumps(body),
                    headers=OPEN_AI_HEADERS,
                )
            r = _handle_response(r)
            query_input = r.get("choices")[0].get("message").get("content")
            print("BOOLEAN:", query_input)
            print("---------------------------------------")
            news_res = Search.get_clips(query_input, date_to, date_from)
            articles = news_res["articles"]
            print("NEWSAPI CLIPS:", len(articles), articles)
            print("---------------------------------------")
        else:
            news_res = Search.get_clips(boolean, date_to, date_from)
            articles = news_res["articles"]
            query_input = boolean
        articles = [article for article in articles if article["title"] != "[Removed]"]
        internal_articles = Article.search_by_query(query_input, date_to, date_from)
        dict_articles = [article.fields_to_dict() for article in internal_articles]
        print("INTERNAL ARTICLES:", len(dict_articles), dict_articles)
        print("---------------------------------------")
        articles = normalize_article_data(articles, internal_articles, True)
        return {"articles": articles, "string": query_input}
    except Exception as e:
        return {"error": str(e)}


def test_prompt(pitch, user_id):
    user = User.objects.get(email="zach@mymanagr.com")
    token_amount = 4000
    timeout = 60.0
    while True:
        try:
            journalists_query = JournalistContact.objects.filter(user=user)
            journalists = [
                f"{journalist.journalist.full_name}-{journalist.journalist.outlet}"
                for journalist in journalists_query
            ]
            url = core_consts.OPEN_AI_CHAT_COMPLETIONS_URI
            prompt = comms_consts.OPEN_AI_PITCH_JOURNALIST_LIST(journalists, pitch)
            body = core_consts.OPEN_AI_CHAT_COMPLETIONS_BODY(
                "zach@mymanagr.com",
                prompt,
                token_amount=token_amount,
                temperature=0,
                response_format={"type": "json_object"},
            )
            with Variable_Client(timeout) as client:
                r = client.post(
                    url,
                    data=json.dumps(body),
                    headers=core_consts.OPEN_AI_HEADERS,
                )
            r = open_ai_exceptions._handle_response(r)
            message = r.get("choices")[0].get("message").get("content")
            message = json.loads(message)
            journalist_data = message["journalists"]
            break
        except open_ai_exceptions.StopReasonLength:
            if token_amount >= 6000:
                journalist_data = "Token amount error"
                break
            else:
                token_amount += 1000
                continue
        except Exception as e:
            journalist_data = f"Unknown exception: {e}"
            break
    return journalist_data


def generate_test_journalists(start, stop, email="zach@mymanagr.com"):
    from managr.comms.serializers import JournalistSerializer, JournalistContactSerializer

    user = User.objects.get(email=email)
    for i in range(start, stop):
        first = f"tfirst{i}"
        last = f"tlast{i}"
        email = f"t.{last}@testing.com"
        data = {"first_name": first, "last_name": last, "outlet": "Testing", "email": email}
        j_serializer = JournalistSerializer(data=data)
        j_serializer.is_valid(raise_exception=True)
        j_serializer.save()
        journalist = j_serializer.instance
        serializer = JournalistContactSerializer(
            data={"journalist": journalist.id, "user": user.id}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
    return


def convert_to_server_time(alert_time, user_timezone):
    user_timezone_obj = pytz.timezone(user_timezone)
    localized_datetime = user_timezone_obj.localize(alert_time, "%Y-%m-%dT%H:%M:%S.%f")
    server_timezone = settings.TIME_ZONE
    server_time = pytz.timezone(server_timezone)
    converted_datetime = localized_datetime.astimezone(server_time)
    return converted_datetime


def modify_href(match, id):
    original_href = match.group(1)
    new_href = (
        core_consts.TRACKING_PIXEL_LINK
        + "?redirect="
        + original_href
        + f"&id={id}"
        + "&type=clicked"
    )
    return f'href="{new_href}"'


def get_url_traffic_data(urls):
    domains = []
    data_dict = {}
    while True:
        try:
            for url in urls:
                domain = get_domain(url, True)
                domains.append(domain)
            domains = list(set(domains))
            url = comms_consts.SEMRUSH_TRAFFIC_URI
            params = comms_consts.SEMRUSH_PARAMS(domains)
            str_params = []
            for key in params.keys():
                str_params.append(f"{key}={params[key]}")
            str_params = "?" + "&".join(str_params)
            full_url = url + str_params
            with Variable_Client(30) as client:
                r = client.get(full_url)
            content = r._content
            decoded_content = content.decode("utf-8")
            csv_reader = csv.DictReader(io.StringIO(decoded_content), delimiter=";")

            for row in csv_reader:
                target = row["target"]
                data_dict[target] = row
            break
        except Exception as e:
            data_dict["error"] = str(e)
            break
    return data_dict


def get_article_data(urls):
    data = []
    for url in urls:
        try:
            article_res = Article(url, config=generate_config())
            article_res.download()
            article_res.parse()
            article_data = {
                "url": url,
                "title": article_res.title,
                "author": article_res.authors,
                "description": article_res.meta_description,
                "source": article_res.source_url,
                "image": article_res.top_image,
                "date": article_res.publish_date,
            }
            data.append(article_data)
        except ArticleException:
            continue
        except Exception as e:
            print(e)
            continue
    return data


def get_social_data(urls):
    headers = {"Accept": "application/json"}
    social_data = {}
    for url in urls:
        params = {"api_key": comms_consts.BUZZSUMO_API_KEY, "q": url}
        with Variable_Client(30) as client:
            res = client.get(comms_consts.BUZZSUMO_SEARCH_URI, params=params, headers=headers)
            if res.status_code == 200:
                res = res.json()
                results = res["results"]
                social_data[url] = results
            else:
                social_data[url] = {}
    return social_data
