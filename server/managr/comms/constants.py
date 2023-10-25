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
    lambda query: f"everything?{query}&language=en&sortBy=publishedAt&pageSize=20"
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

DEFAULT_CLIENT_INSTRUCTIONS = """<strong>Executive summary:</strong>\n Highlighting 5 key points from today's clips.\n
<strong>Sentiment:</stong>\n Evaluate the overall tone or sentiment of the coverage. Is it primarily positive, neutral, or negative and why.\n
<strong>Key Messages:</strong>\n Determine whether the coverage communicates the company's key messages effectively."""

DEFAULT_TWITTER_CLIENT_INSTRUCTIONS = """<strong>Executive summary:</strong>\n Highlighting 5 key points from today's clips.\n
<strong>Sentiment:</stong>\n Evaluate the overall tone or sentiment of the coverage. Is it primarily positive, neutral, or negative and why.\n
<strong>Influencers:</strong>\n Identify key influencers based on follower count"""

DEFAULT_WRITING_STYLE = "Aim for a professional, informative, yet concise style, bypassing formalities, such as Dear, Sir, Best regards, etc. Get right to the point"


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
    lambda search: f"""Convert the Search Term below into a valid Twitter API query.
    Follow these steps in order to create the best possible search:
    1: Only use hashtag terms when given
    2: Only do user search when instructed
    Search Term: {search}"""
)

DEFAULT_ARTICLE_INSTRUCTIONS = (
    lambda search: f"*Context: \n Sentiment: \n Impact: as it pertains to {search}.* Output can not exceed 400 characters"
)
DEFAULT_CLIENT_ARTICLE_INSTRUCTIONS = (
    lambda search: f"<strong>Context: \n Sentiment: \n Impact: as it pertains to {search}</strong>. Output can not exceed 400 characters"
)


def OPEN_AI_WEB_SUMMARY(
    date,
    article,
    instructions,
):
    body = f"Today's date is {date}. Summarize this news article:\n {article}. \nOutput format must be:\n {instructions}. It cannot be longer than 1500 characters."
    return body


def OPEN_AI_ARTICLE_SUMMARY(date, article, search, length, instructions=False, for_client=False):
    body = f"Today's date is {date}. Summarize this news article {article}, as it relates to {search}. \n Output format must be:\n"
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


def OPEN_AI_PITCH(date, type, output, persona, chars, style=False):
    if not style:
        style = "Maintain an objective and factual tone throughout. Begin with a precise introduction, without informal salutations. Establish authority using a formal style and cite reputable sources where relevant. Strive for clear and succinct communication, avoiding metaphors and ornate language. Present information in a coherent manner, providing necessary context and reliable data, while refraining from persuasive elements. Focus on depth of content to engage readers, rather than using sensationalism. The goal is to inform and respect the reader’s intelligence, suitable for educational or professional environments. Refrain from commercial commentary or emotional bias. Conclude without relying on standard transition phrases like 'In conclusion' or 'In summary'."
    body = f"""Today's {date}. As the VP of Communications, generate content follow these instructions carefully {output}. You must Mirror this writing {style}. Lastly, this content must adhere to a strict {chars} character limit."""
    print(body)
    return body


def OPEN_AI_GENERATE_CONTENT(date, article, style, instructions):
    if not style:
        style = "Maintain an objective and factual tone throughout. Begin with a precise introduction, without informal salutations. Establish authority using a formal style and cite reputable sources where relevant. Strive for clear and succinct communication, avoiding metaphors and ornate language. Present information in a coherent manner, providing necessary context and reliable data, while refraining from persuasive elements. Focus on depth of content to engage readers, rather than using sensationalism. The goal is to inform and respect the reader’s intelligence, suitable for educational or professional environments. Refrain from commercial commentary or emotional bias. Conclude without relying on standard transition phrases like 'In conclusion' or 'In summary'."
    body = f"Today's date is {date}. Generate the following content:\n {instructions},\n based on this news article:\n {article}\n. Use this writing stye:\n {style}. Output cannot exceed 1,500 characters."
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
    lambda article, content, instructions: f"""Adjust and rewrite this content:\n Content: {content}\n per these Instructions: {instructions}.
     No longer than 1,500 characters. For reference, here is the article the content is based on: Article: {article}."""
)

DO_NOT_TRACK_LIST = ["www.wsj.com", "www.nytimes.com", "www.bizjournals.com"]
