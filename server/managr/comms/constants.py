from django.conf import settings

USE_NEWS_API = settings.USE_NEWS_API
NEWS_API_KEY = settings.NEWS_API_KEY if USE_NEWS_API else None

USE_TWITTER_API = settings.USE_TWITTER_API
TWITTER_CLIENT_ID = settings.TWITTER_CLIENT_ID if USE_TWITTER_API else None
TWITTER_REDIRECT_URI = settings.TWITTER_REDIRECT_URI if USE_TWITTER_API else None
TWITTER_ACCESS_TOKEN = settings.TWITTER_ACCESS_TOKEN if USE_TWITTER_API else None
TWITTER_BASE_URI = "https://api.twitter.com/"
TWITTER_REQUEST_TOKEN_URI = "oauth/request_token"
TWITTER_RECENT_TWEETS_URI = "2/tweets/search/recent"
TWITTER_AUTHORIZATION_URI = "https://twitter.com/i/oauth2/authorize"
TWITTER_ACCESS_TOKEN_URI = TWITTER_BASE_URI + "2/oauth2/token"
TWITTER_SCOPES = ["tweet.read", "offline.access", "users.read"]
if settings.IN_DEV:
    TWITTER_FRONTEND_REDIRECT = "http://localhost:8080/settings/integrations"
elif settings.IN_STAGING:
    TWITTER_FRONTEND_REDIRECT = "https://staging.managr.ai/settings/integrations"
else:
    TWITTER_FRONTEND_REDIRECT = "https://app.managr.ai/settings/integrations"
TWITTER_API_HEADERS = {"Authorization": f"Bearer {TWITTER_ACCESS_TOKEN}"}

NEWS_API_HEADERS = {
    "Authorization": f"Bearer {NEWS_API_KEY}",
}

NEW_API_URI = "https://newsapi.org/v2"

NEW_API_EVERYTHING_QUERY_URI = (
    lambda query: f"everything?{query}&language=en&sortBy=publishedAt&pageSize=40"
)

NEW_API_EVERYTHING_DATE_URI = (
    lambda date_from, date_to: f"everything?from={date_from}&to={date_to}&language=en&sortBy=publishedAt&pageSize=20"
)

SEARCH_TYPE_CHOICES = (("NEWS", "News"), ("SOCIAL_MEDIA", "Social Media"), ("MIXED", "Mixed"))

DEFAULT_INSTRUCTIONS = """*Executive summary:*\n Highlighting 5 key points from today's clips.\n
*Sentiment*\n Evaluate the overall tone or sentiment of the coverage. Is it primarily positive, neutral, or negative and why.\n
*Key Messages:*\n Determine whether the coverage communicates the company's key messages effectively."""

DEFAULT_TWITTER_INSTRUCTIONS = """*Executive summary:*\n Highlighting 5 key points from today's clips.\n
*Sentiment*\n Evaluate the overall tone or sentiment of the coverage. Is it primarily positive, neutral, or negative and why.\n
*Influencers:*\n Identify key influencers based on follower count"""

DEFAULT_CLIENT_INSTRUCTIONS = "Summary: Summarize the news in paragraph format, in less than 600 characters. \n Top Sources: List top 10 sources (based on popularity and size, no newswire sources)"


DEFAULT_TWITTER_CLIENT_INSTRUCTIONS = """<strong>Summary of the Tweets:</strong>\n
<strong>Sentiment:</strong>\n
<strong>Top Influencers:</strong>\n Identify key influencers based on follower count"""

DEFAULT_WRITING_STYLE = "Aim for a professional, informative, yet concise style, bypassing formalities, such as Dear, Sir, Best regards, etc. Get right to the point"


def OPEN_AI_NEWS_CLIPS_SUMMARY(date, clips, search, instructions=False, for_client=False):
    if not instructions:
        instructions = DEFAULT_CLIENT_INSTRUCTIONS
    body = f"""Today's date is {date}. Read the news coverage below and carefully follow these instructions, output has to be less than 1000 characters: \n Here are the instructions:{instructions}. \n Here is the news coverage: {clips}.
    """
    # if instructions:
    #     body += instructions
    # else:
    #     default = DEFAULT_CLIENT_INSTRUCTIONS if for_client else DEFAULT_INSTRUCTIONS
    #     body += default
    return body


def OPEN_AI_TWITTER_SUMMARY(date, tweets, search, instructions, for_client=False):
    if not instructions:
        instructions = DEFAULT_TWITTER_CLIENT_INSTRUCTIONS
    body = f"""Today's date is {date}.Summarize the twitter coverage based on these tweets.\n Tweets: {tweets}\n
    You must follow these instructions: {instructions}. Summary cannot be longer than 1,000 characters.
    """
    return body


OPEN_AI_TWITTER_SEARCH_CONVERSION = (
    lambda search: f"""Convert the Search Term below into a valid Twitter API query.
    Follow these steps in order to create the best possible search:
    1: Concentrate on the primary keywords or key concepts of the search term. For example, from 'why is Michael Jordan trending', extract just 'Michael Jordan'.
    2:Only use hashtag terms when given
    3: Only do user search when instructed
    Search Term: {search}"""
)

DEFAULT_ARTICLE_INSTRUCTIONS = (
    lambda search: f"*Context: \n Sentiment: \n Impact: as it pertains to {search}.* Output can not exceed 400 characters"
)
DEFAULT_CLIENT_ARTICLE_INSTRUCTIONS = (
    lambda boolean: f"Summary: summarize the article and its relation to any of these terms {boolean} in under 250 characters. \n Sentiment: what is the sentiment of any of these terms {boolean} within the article, keep under 200 characters"
)


def OPEN_AI_WEB_SUMMARY(
    date,
    article,
    instructions,
):
    body = f"Today's date is {date}. Summarize this news article:\n {article}. \nOutput format must be:\n {instructions}. It cannot be longer than 1500 characters."
    return body


def OPEN_AI_ARTICLE_SUMMARY(date, article, search, length, instructions=False, for_client=False):
    if not instructions:
        instructions = DEFAULT_CLIENT_ARTICLE_INSTRUCTIONS(search)
    if not search:
        body = f"Today's date is {date}. Read the article below, then follow these instructions: {instructions}. Output cannot exceed 800 characters.\n Article: {article} \n"
    else:
        body = f"Today's date is {date}. At least one of the terms in the boolean search were mentioned in the provided news article. Follow the instructions carefully.\nBoolean Search: {search} \n Instructions: {instructions} \n News Article: {article}"
    return body


def OPEN_AI_PITCH(date, type, output, persona, chars, style=False):
    if not style:
        style = "Begin with a precise introduction, without informal salutations. Be clear, concise, and informative, avoiding metaphors. Offer coherent data without persuasion. Aim for depth, not sensationalism and avoid commercial bias."
    body = f"""Today's date is {date}. As the VP of Communications, generate content following these instructions carefully: {output}. \n You must Mirror this writing style: {style}. \n Lastly, this content must adhere to a strict {chars} word limit."""
    return body


def OPEN_AI_GENERATE_CONTENT(date, article, style, instructions):
    if not style:
        style = "Begin with a precise introduction, without informal salutations. Be clear, concise, and informative, avoiding metaphors. Offer coherent data without persuasion. Aim for depth, not sensationalism and avoid commercial bias."
    body = f"""Today's date is {date}. Read the news article below and generate content in less than 800 characters, mirroring a custom writing style. Here are the instructions: {instructions}. Here is the writing style {style}. \n Here is the news article {article}.
    """
    return body


OPEN_AI_PTICH_DRAFT_WITH_INSTRUCTIONS = (
    lambda pitch, instructions: f"""
Adjust and rewrite the content per the instructions, while maintaining the existing writing style.\n
Content: {pitch}\n
Instructions: {instructions}"""
)

OPEN_AI_LEARN_WRITING_STYLE_PROMPT = (
    lambda sample: f"""Perform a detailed analysis of {sample}, focusing on discerning the author's unique style apart from content. Evaluate tone, formality, structure, and linguistic idiosyncrasies, ensuring an objective stance. Investigate the mechanisms used for establishing credibility, engaging readers informatively, avoiding persuasive or sales-oriented language. Task: Formulate concise guidelines capturing the essence of the author's style, enabling its replication across various themes. Emphasize a clear, informative, non-promotional communication style, highlighting specific stylistic techniques contributing to effective and trustworthy discourse. Output cannot exceed 1,200 characters."""
)

OPEN_AI_REGENERATE_ARTICLE = (
    lambda article, content, instructions: f"""Adjust the content below following these instructions carefully:{instructions}. Output must be less than 1000 characters. \n
    here is the content:{content}
    """
)

DO_NOT_TRACK_LIST = [
    "https://www.wsj.com",
    "https://www.nytimes.com",
    "https://www.bizjournals.com",
    "https://www.tiktok.com",
    "https://www.instagram.com",
    "https://www.facebook.com",
]


DO_NOT_INCLUDE_WORDS = ["photos", "sex", "review", "linkedin"]

EXCLUDE_DOMAINS = [
    "globenewswire.com",
    "marketscreener.com",
    "zacjohnson.com",
    "allafrica.com",
    "prnewswire.com",
    "prnewswire.co.uk",
    "gov.uk",
    "pulse.ug",
    "timesofindia.indiatimes.com",
    "indiatimes.com",
    "ibtimes.com.au",
    "etfdailynews.com",
    "dealnews.com",
    "slickdeals.net",
    "prtimes.jp",
]
