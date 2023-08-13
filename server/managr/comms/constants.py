from django.conf import settings

USE_NEWS_API = settings.USE_NEWS_API
NEWS_API_KEY = settings.NEWS_API_KEY if USE_NEWS_API else None

NEWS_API_HEADERS = {
    "Authorization": f"Bearer {NEWS_API_KEY}",
}
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


def OPEN_AI_ARTICLE_SUMMARY(date, article, search, instructions=False):
    body = f"Today's date is {date}  Summarize this news article:\n Article: {article}\n As it relates to {search} It cannot be longer than 500 characters. Output format must be:\n"
    if instructions:
        body += instructions
    else:
        body += f"""<strong>Was {search} featured or mentioned in this article. Briefly explain.</stong>\n
        <strong>{search} sentiment vs article sentiment</stong>\n"""
    return body
