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
TWITTER_RECENT_TWEETS_URI = "2/tweets/search/recent"


NEWS_API_HEADERS = {
    "Authorization": f"Bearer {TWITTER_ACCESS_TOKEN}",
}

TWITTER_API_HEADERS = {"Authorization": f"Bearer {TWITTER_ACCESS_TOKEN}"}
NEW_API_URI = "https://newsapi.org/v2"

NEW_API_EVERYTHING_URI = (
    lambda query: f"everything?{query}&language=en&sortBy=publishedAt&pageSize=20"
)

DEFAULT_INSTRUCTIONS = """*Executive summary:*\n Highlighting 5 key points from today's clips.\n
*Sentiment*\n Evaluate the overall tone or sentiment of the coverage. Is it primarily positive, neutral, or negative and why.\n
*Key Messages:*\n Determine whether the coverage communicates the company's key messages effectively."""

DEFAULT_CLIENT_INSTRUCTIONS = """<strong>Executive summary:</strong>\n Highlighting 5 key points from today's clips.\n
<strong>Sentiment:</stong>\n Evaluate the overall tone or sentiment of the coverage. Is it primarily positive, neutral, or negative and why.\n
<strong>Key Messages:</strong>\n Determine whether the coverage communicates the company's key messages effectively."""


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
        default = DEFAULT_CLIENT_INSTRUCTIONS if for_client else DEFAULT_INSTRUCTIONS
        body += default
    return body


OPEN_AI_TWITTER_SEARCH_CONVERSION = (
    lambda search: f"""Convert the Search Term below into a boolean query to be used for Twitter search API.
    Follow these steps in order to create the best possible search:
    1: Only use hashtag terms when given
    2: Only do user search when instructed
    Search Term: {search}"""
)


def OPEN_AI_ARTICLE_SUMMARY(date, article, search, instructions=False):
    body = f"Today's date is {date}  Summarize this news article:\n Article: {article}\n As it relates to {search} It cannot be longer than 500 characters. Output format must be:\n"
    if instructions:
        body += instructions
    else:
        body += f"""<strong>Was {search} featured or mentioned in this article. Briefly explain.</stong>\n
        <strong>{search} sentiment vs article sentiment</stong>\n"""
    return body

def OPEN_AI_PITCH(date, name, type, brand, persona, briefing, style):
    body = f"Today is {date}. You are a VP of Communications tasked by {name} with generating {type} about company: {brand}. Tailor the content to this target persona: {persona}. Here is the briefing: {briefing}. Here are the output instructions: {style}"
    return body