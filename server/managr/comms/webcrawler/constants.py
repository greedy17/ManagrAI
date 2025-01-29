USER_AGENT_LIST = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 managr-crawler/1.0 (https://managr.ai/documentation)",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 managr-crawler/1.1 (https://managr.ai/documentation)",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/91.0.864.59 Safari/537.36 managr-crawler/1.2 (https://managr.ai/documentation)",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/89.0 Safari/537.36 managr-crawler/1.3 (https://managr.ai/documentation)",
    "Mozilla/5.0 (Linux; Android 9; Pixel 3 XL Build/PQ3A.190805.002) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36 managr-crawler/1.4 (https://managr.ai/documentation)",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36 managr-crawler/1.5 (https://managr.ai/documentation)",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:53.0) Gecko/20100101 Firefox/53.0 managr-crawler/1.6 (https://managr.ai/documentation)",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Safari/537.36 managr-crawler/1.7 (https://managr.ai/documentation)",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Safari/537.36 Edge/91.0.864.37 managr-crawler/1.8 (https://managr.ai/documentation)",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 managr-crawler/1.9 (https://managr.ai/documentation)",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36 managr-crawler/2.0 (https://managr.ai/documentation)",
    "Mozilla/5.0 (Windows NT 6.1; rv:53.0) Gecko/20100101 Firefox/53.0 managr-crawler/2.1 (https://managr.ai/documentation)",
    "Mozilla/5.0 (Linux; U; Android 10; en-US; Pixel 4 Build/QD2A.200305.003) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.101 Mobile Safari/537.36 managr-crawler/2.2 (https://managr.ai/documentation)",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:60.0) Gecko/20100101 Firefox/60.0 managr-crawler/2.3 (https://managr.ai/documentation)",
]

REFERER_LIST = [
    "https://www.google.com/",
    "https://www.bing.com/",
    "https://duckduckgo.com/",
    "https://www.yahoo.com/",
    "https://www.facebook.com/",
    "https://twitter.com/",
    "https://www.instagram.com/",
    "https://www.linkedin.com/",
    "https://www.npr.org/",
    "https://www.cnn.com/",
    "https://www.bbc.com/",
    "https://www.reuters.com/",
    "https://www.medium.com/",
    "https://www.quora.com/",
]

SCRAPPY_HEADERS = {
    "Cache-Control": "no-cache",
    "Pragma": "no-cache",
    "Connection": "keep-alive",
}

XPATH_STRING_OBJ = {
    "title": ["//title/text()"],
    "author": [
        "//meta[@name='author']/@content",
        "//*[contains(@class,'gnt_ar_by')]/a/text()",
        "//*[@class='article__author']/text()",
        "//meta[@name='twitter:data1']/@content",
        "//meta[@property='authors']/@content",
        "//meta[@property='article:author']/@content",
        "//meta[contains(@name,'author')]/@content",
        "//*[@rel='author']/text()",
        "//*[contains(@class,'author-name') and string-length() > 2]//text()",
    ],
    "description": [
        "//meta[contains(@property, 'description')]/@content",
        "//meta[contains(@name, 'description')]/@content",
    ],
    "publish_date": [
        "//*[contains(@class,'gnt_ar_dt')]/@aria-label",
        "//meta[@property='article:published_time']/@content",
        "//body//time/@datetime | //body//time/@dateTime | //body//time/text()",
        "//meta[contains(@itemprop,'date')]/@content",
        "//meta[contains(@name, 'date')]/@content",
    ],
    "image_url": ["//meta[@property='og:image']/@content"],
}

XPATH_TO_FIELD = {
    "title": "article_title_selector",
    "author": "author_selector",
    "description": "description_selector",
    "publish_date": "date_published_selector",
    "image_url": "image_url_selector",
    "content": "article_content_selector",
}

MONTH_DAY_TO_NAME = {
    1: "January",
    2: "February",
    3: "March",
    4: "April",
    5: "May",
    6: "June",
    7: "July",
    8: "August",
    9: "September",
    10: "October",
    11: "November",
    12: "December",
}

COMMON_SELECTORS = {
    "value": ["year.a", "/news/.a", "/article/.a", "article_.a", "/articles/.a"],
    "class": [
        "tnt-asset-link.a",
        "article-link.a",
        "entry-title.*,a",
        "td-image-wrap.a",
        "title.a",
        "title-link.a",
    ],
}

URL_DATE_PATTERN = r"(?i)\/([0-9]{2,4})(?:[-/_])([0-9]{1,2}|1[0-2]|[a-z]{3}|march|april)(?:[-/_])([0-9]{2,4})?(?:[-/_])?"

VALID_ARTICLE_WORDS = [
    "story",
    "article",
    "news",
]


EXCLUDE_WORDS = [
    "/about",
    "/section/",
    "/terms",
    "-policy",
    "/privacy",
    "/careers",
    "/accessibility",
    "/category",
    "/tag",
    "/author",
    "/videos",
    ".jpg",
    ".png",
    ".pdf",
    "/subscription",
    "/ads",
    "/ad",
]

EXCLUDE_CLASSES = ["menu", "nav", "footer", "header", "social"]
