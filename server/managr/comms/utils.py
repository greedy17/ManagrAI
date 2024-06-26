import re
import json
import boto3
import csv
import fitz
import tempfile
import requests
from datetime import datetime, timezone
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
from .models import NewsSource
from botocore.exceptions import ClientError

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


def get_domain(url):
    parsed_url = urlparse(url)
    netloc = parsed_url.netloc
    domain_parts = netloc.split(".")
    if "www" in domain_parts:
        domain_parts.remove("www")
    return domain_parts[0]


def extract_date_from_text(text):
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
    text = text.replace("\n", "").strip()
    patterns = [
        r"(\d{1,2} [A-Za-z]+ \d{4})",
        r"([A-Za-z]+(?: \d{1,2},)? \d{4})",
        r"([A-Za-z]{3}\. \d{1,2}, \d{4} \d{1,2}:\d{2} [apAP]\.m\.)",
        r"(\w+\s\d+,\s\d{4})",
        r"(?P<date>\w+ \d{1,2}, \d{4}) at (?P<time>\d{1,2}:\d{2} \w{2})",
    ]
    date_str = text
    strptime_formats = [
        "%d %B %Y",
        "%B %d, %Y",
        "%b %d, %Y",
        "%b. %d, %Y %I:%M %p",
        "%Y-%m-%dT%H:%M:%S%z",
        "%B %d, %Y at %I:%M %p",
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            date_str = match.group(1)
            if ":" in date_str:
                colon_idx = date_str.index(":")
                hour = date_str[colon_idx - 2 : colon_idx]
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
        # escaped_term = re.escape(term)
        # print(escaped_term)
        if idx == len(term_list) - 1:
            current_query = Q(content__iregex=r"{}".format(term))
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
        merge_sort_dates(sub_array1)
        merge_sort_dates(sub_array2)
        i = j = k = 0
        while i < len(sub_array1) and j < len(sub_array2):
            parsed_value1 = parser.parse(sub_array1[i][key]).replace(tzinfo=timezone.utc)
            parsed_value2 = parser.parse(sub_array2[j][key]).replace(tzinfo=timezone.utc)
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


def normalize_article_data(api_data, article_models):
    normalized_list = []
    normalized_api_list = normalize_newsapi_to_model(api_data)
    normalized_list.extend(normalized_api_list)
    normalized_model_list = [article.fields_to_dict() for article in article_models]
    normalized_list.extend(normalized_model_list)
    sorted_arr = merge_sort_dates(normalized_list)
    ordered_dict = OrderedDict()
    sorted_arr.reverse()
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


def google_search(query):
    url = comms_consts.GOOGLE_SEARCH_URI
    params = comms_consts.GOOGLE_SEARCH_PARAMS(query)
    with Variable_Client() as client:
        res = client.get(url, params=params)
        if res.status_code == 200:
            results_list = []
            images = []
            res = res.json()
            results = res["items"][:5]
            for item in results:
                result_data = {
                    "title": item["title"],
                    "snippet": item["snippet"],
                    "link": item["link"],
                }
                try:
                    images.append(item["pagemap"]["cse_image"][0]["src"])
                except Exception:
                    pass
                results_list.append(result_data)
            return {"images": images, "results": results_list}
        else:
            return {}


def test_open(user, journalist, results, text):
    from managr.core import constants as core_consts
    from managr.core import exceptions as open_ai_exceptions
    import httpx

    has_error = False
    attempts = 1
    token_amount = 1000
    timeout = 60.0
    while True:
        try:
            url = core_consts.OPEN_AI_CHAT_COMPLETIONS_URI
            # prompt = comms_consts.OPEN_AI_RESULTS_PROMPT(journalist, results, "Visit Orlando", text)
            prompt = f"Create one summary based on the information from all the search results below. Ensure the summary encompasses a variety of topics mentioned in the results. You must include the source name and date to cite where you got the information from.\nHere are the top 5 search results:{results}\nAnd here is the top article: {text}"
            print(prompt)
            print("_______________________________")
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
            res = open_ai_exceptions._handle_response(r)

            message = res.get("choices")[0].get("message").get("content").replace("**", "*")
            print(message)
            break
        except open_ai_exceptions.StopReasonLength:
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
                break
            else:
                attempts += 1
                continue
        except Exception as e:
            has_error = True
            message = f"Unknown exception: {e}"
            break
    return message


def test_rewrite(details):
    from managr.core import constants as core_consts
    from managr.core import exceptions as open_ai_exceptions

    original = "Hi {Journalist first name},I admire your insightful coverage of cultural heritage. I'm reaching out to share a compelling story about the art of Gullah rag quilting. Sharon Cooper-Murray, 'The Gullah Lady,' can no longer teach this craft due to health reasons. However, Cookie Washington, an African American Quilter Artist, is dedicated to preserving this tradition. This technique, passed down through generations, combines feed and grain sacks with rag strips to create unique quilts. Would you be interested in exploring this rich cultural heritage and Cookie's efforts to honor Sharon's legacy?Thanks,[Your Name]"
    has_error = False
    attempts = 1
    token_amount = 1000
    timeout = 60.0

    while True:
        try:
            url = core_consts.OPEN_AI_CHAT_COMPLETIONS_URI
            prompt = comms_consts.OPEN_AI_REWRITE_PTICH(original, details, "Zachary")
            body = core_consts.OPEN_AI_CHAT_COMPLETIONS_BODY(
                "zach@mymanagr.com",
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
            print(pitch)
            break
        except open_ai_exceptions.StopReasonLength:
            if token_amount <= 2000:
                has_error = True

                message = "Token amount error"
                break
            else:
                token_amount += 500
                continue
        except Exception as e:
            has_error = True
            message = f"Unknown exception: {e}"
            break
    return


def test_flow():
    from managr.core.models import User
    from newspaper import Article

    user = User.objects.get(email="zach@mymanagr.com")
    journalist = "Kristin Corpuz"
    query = "Kristin Corpuz AND Allure"
    google_res = google_search(query)
    results = google_res["results"]
    images = google_res["images"]
    art = Article(results[0]["link"], config=generate_config())
    art.download()
    art.parse()
    text = art.text
    message = test_open(user, journalist, results, text)
    email = test_rewrite(message)
    return email


def dumb(query):
    from newspaper import Article
    from managr.core.models import User

    res = google_search(query)
    results = res["results"][:6]
    art = Article(results[0]["link"], config=generate_config())
    art.download()
    art.parse()
    text = art.text
    user = User.objects.get(email="zach@mymanagr.com")
    summary = test_open(user, "text", results, text)
    return summary
