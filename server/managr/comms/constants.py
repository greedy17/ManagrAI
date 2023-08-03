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


def OPEN_AI_NEWS_CLIPS_SUMMARY(date, clips, company, instructions=False):
    body = f"""Today's date is {date} Prepare a daily news briefing for a public relations manager at {company}. 
Summarize the clips from today:\n Clips: {clips}\n
It cannot be longer than 1,000 characters. Writing style, analysis, observations and tone must mirror that of a VP of Communications. 
Output format must be:\n"""
    if instructions:
        body += instructions
    else:
        body += """1. Executive summary. Highlighting 5 key points from today's clips.\n
2. Sentiment. Evaluate the overall tone or sentiment of the coverage. Is it primarily positive, neutral, or negative and why.\n
3. Key Messages: Determine whether the coverage communicates the company's key messages effectively."""
    return body

def OPEN_AI_ARTICLE_SUMMARY(date, article, search, instructions=False):
    body = f"""Today's date is {date}  Summarize this news article:\n Article: {article}\n As it relates to {search}
It cannot be longer than 500 characters. Writing style, analysis, observations and tone must mirror that of a VP of Communications. 
Output format must be:\n"""
    if instructions:
        body += instructions
    else:
        body += """Provide a 3 bullet point summary.\n 
        * Was this a feature story or a mention.\n 
        * What was the sentiment around our brand vs the rest of the article.\n 
        * Where are the key messages\n
        * Highlight any mentions and sentiment our products or people\n
        * Highlight any mentions and sentiment of our competitors"""
    return body
