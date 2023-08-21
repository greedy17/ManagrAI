from django.conf import settings

USE_NEWS_API = settings.USE_NEWS_API
NEWS_API_KEY = settings.NEWS_API_KEY if USE_NEWS_API else None

USE_TWITTER_API = settings.USE_TWITTER_API
TWITTER_CLIENT_ID = settings.TWITTER_CLIENT_ID if USE_TWITTER_API else None
TWITTER_SECRET_KEY = settings.TWITTER_SECRET_KEY if USE_TWITTER_API else None
TWITTER_REDIRECT_URI = settings.TWITTER_REDIRECT_URI if USE_TWITTER_API else None
TWITTER_API_KEY = settings.TWITTER_API_KEY if USE_TWITTER_API else None
TWITTER_ACCESS_TOKEN = settings.TWITTER_ACCESS_TOKEN if USE_TWITTER_API else None
TWITTER_BASE_URI = "https://api.twitter.com/"
TWITTER_REQUEST_TOKEN_URI = "oauth/request_token"
TWITTER_RECENT_TWEETS_URI = "2/tweets/search/recent"
TWITTER_AUTHORIZATION_URI = "https://twitter.com/i/oauth2/authorize"
TWITTER_ACCESS_TOKEN_URI = TWITTER_BASE_URI + "2/oauth2/token"
TWITTER_SCOPES = ["tweets.read", "offline.access", "users.read"]

TWITTER_API_HEADERS = {"Authorization": f"Bearer {TWITTER_ACCESS_TOKEN}"}

NEWS_API_HEADERS = {
    "Authorization": f"Bearer {NEWS_API_KEY}",
}

NEW_API_URI = "https://newsapi.org/v2"

NEW_API_EVERYTHING_URI = (
    lambda query: f"everything?{query}&language=en&sortBy=publishedAt&pageSize=20"
)

SEARCH_TYPE_CHOICES = (("NEWS", "News"), ("SOCIAL_MEDIA", "Social Media"), ("MIXED", "Mixed"))

DEFAULT_INSTRUCTIONS = """*Executive summary:*\n Highlighting 5 key points from today's clips.\n
*Sentiment*\n Evaluate the overall tone or sentiment of the coverage. Is it primarily positive, neutral, or negative and why.\n
*Key Messages:*\n Determine whether the coverage communicates the company's key messages effectively."""

DEFAULT_TWITTER_INSTRUCTIONS = """*Executive summary:*\n Highlighting 5 key points from today's clips.\n
*Sentiment*\n Evaluate the overall tone or sentiment of the coverage. Is it primarily positive, neutral, or negative and why.\n
*Influencers:*\n Identify key influencers based on follower count"""

DEFAULT_CLIENT_INSTRUCTIONS = """<strong>Executive summary:</strong>\n Highlighting 5 key points from today's clips.\n
<strong>Sentiment:</stong>\n Evaluate the overall tone or sentiment of the coverage. Is it primarily positive, neutral, or negative and why.\n
<strong>Key Messages:</strong>\n Determine whether the coverage communicates the company's key messages effectively."""

DEFAULT_TWITTER_CLIENT_INSTRUCTIONS = """<strong>Executive summary:</strong>\n Highlighting 5 key points from today's clips.\n
<strong>Sentiment:</stong>\n Evaluate the overall tone or sentiment of the coverage. Is it primarily positive, neutral, or negative and why.\n
<strong>Influencers:</strong>\n Identify key influencers based on follower count"""


def OPEN_AI_NEWS_CLIPS_SUMMARY(date, clips, search, instructions=False, for_client=False):
    body = f"""Today's date is {date}.Summarize the news coverage for {search} based on these news clips.\n Clips: {clips}\n
Summary cannot be longer than 1,000 characters.
Output format must be:\n"""
    if instructions:
        body += instructions
    else:
        default = DEFAULT_CLIENT_INSTRUCTIONS if for_client else DEFAULT_INSTRUCTIONS
        body += default
    return body


def OPEN_AI_TWITTER_SUMMARY(date, tweets, search, instructions, for_client=False):
    body = f"""Today's date is {date}.Summarize the twitter coverage for {search} based on these tweets.\n Tweets: {tweets}\n
    Summary cannot be longer than 1,000 characters.
    Output format must be:\n"""
    if instructions:
        body += instructions
    else:
        default = (
            DEFAULT_TWITTER_CLIENT_INSTRUCTIONS if for_client else DEFAULT_TWITTER_INSTRUCTIONS
        )
        body += default
    return body


OPEN_AI_TWITTER_SEARCH_CONVERSION = (
    lambda search: f"""Convert the Search Term below into a valid Twitter search string.
    Follow these steps in order to create the best possible search:
    1: Only use hashtag terms when given
    2: Only do user search when instructed
    Search Term: {search}"""
)

DEFAULT_ARTICLE_INSTRUCTIONS = (
    lambda search: f"*Context and Sentiment pertaining to {search}:*\n*Relevance and Impact pertaining to {search}:*"
)
DEFAULT_CLIENT_ARTICLE_INSTRUCTIONS = (
    lambda search: f"<strong>Context and Sentiment pertaining to {search}:</strong>\n<strong>Relevance and Impact pertaining to {search}:</strong>"
)


def OPEN_AI_ARTICLE_SUMMARY(date, article, search, instructions=False, for_client=False):
    body = f"Today's date is {date}  Summarize this news article:\n Article: {article}\n As it relates to {search} It cannot be longer than 500 characters. Output format must be:\n"
    if instructions:
        body += instructions
    else:
        default = (
            DEFAULT_CLIENT_ARTICLE_INSTRUCTIONS(search)
            if for_client
            else DEFAULT_ARTICLE_INSTRUCTIONS(search)
        )
        body += default
    return body


def OPEN_AI_PITCH(date, type, output, persona, briefing):
    body = f"Today is {date}. You are a VP of Communications tasked to generate a {type}, targeting {persona}. Reference briefing: {briefing} , and follow these output instructions: {output}."
    return body


OPEN_AI_PTICH_DRAFT_WITH_INSTRUCTIONS = (
    lambda pitch, instructions: f"""
Below is an AI generated pitch. Adjust and rewrite the pitch per instructions below:\n
Pitch: {pitch}\n
Instructions: {instructions}"""
)
