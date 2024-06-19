from django.conf import settings
from datetime import datetime
import time

USE_NEWS_API = settings.USE_NEWS_API
NEWS_API_KEY = settings.NEWS_API_KEY if USE_NEWS_API else None

USE_TWITTER_API = settings.USE_TWITTER_API
TWITTER_API_KEY = settings.TWITTER_API_KEY
TWITTER_API_SECRET = settings.TWITTER_API_SECRET
TWITTER_CLIENT_ID = settings.TWITTER_CLIENT_ID if USE_TWITTER_API else None
TWITTER_REDIRECT_URI = settings.TWITTER_REDIRECT_URI if USE_TWITTER_API else None
TWITTER_ACCESS_TOKEN = settings.TWITTER_ACCESS_TOKEN if USE_TWITTER_API else None
TWITTER_BASE_URI = "https://api.twitter.com/"
TWITTER_REQUEST_TOKEN_URI = TWITTER_BASE_URI + "oauth/request_token"
TWITTER_RECENT_TWEETS_URI = "2/tweets/search/recent"
TWITTER_AUTHORIZATION_URI = TWITTER_BASE_URI + "oauth/authorize"
TWITTER_ACCESS_TOKEN_URI = TWITTER_BASE_URI + "oauth/access_token"
TWITTER_REFRESH_TOKEN_URI = TWITTER_BASE_URI + "oauth/token"
TWITTER_SCOPES = ["tweet.read", "offline.access", "users.read"]
HUNTER_VERIFY_URI = "https://api.hunter.io/v2/email-verifier"
HUNTER_FINDER_URI = "https://api.hunter.io/v2/email-finder"
HUNTER_API_KEY = settings.HUNTER_API_KEY
if settings.IN_DEV:
    TWITTER_FRONTEND_REDIRECT = "http://localhost:8080/pr-integrations"
elif settings.IN_STAGING:
    TWITTER_FRONTEND_REDIRECT = "https://staging.managr.ai/pr-integrations"
else:
    TWITTER_FRONTEND_REDIRECT = "https://app.managr.ai/pr-integrations"
TWITTER_API_HEADERS = {"Authorization": f"Bearer {TWITTER_ACCESS_TOKEN}"}

USE_INSTAGRAM_API = settings.USE_INSTAGRAM_API
if USE_INSTAGRAM_API:
    INSTAGRAM_APP_KEY = settings.INSTAGRAM_APP_KEY
    INSTAGRAM_APP_SECRET = settings.INSTAGRAM_APP_SECRET
    INSTAGRAM_REDIRECT_URI = settings.INSTAGRAM_REDIRECT_URI

INSTAGRAM_BASE_URI = "https://www.facebook.com/v19.0/"
INSTAGRAM_GRAPH_BASE_URL = "https://graph.facebook.com/v19.0/"
INSTAGRAM_AUTHORIZATION_URI = INSTAGRAM_BASE_URI + "dialog/oauth"
INSTAGRAM_ACCESS_TOKEN_URI = INSTAGRAM_GRAPH_BASE_URL + "oauth/access_token"
INSTAGRAM_ACCOUNTS_URI = INSTAGRAM_GRAPH_BASE_URL + "me/accounts"
INSTAGRAM_HASHTAG_SEARCH_URI = INSTAGRAM_GRAPH_BASE_URL + "ig_hashtag_search"
INSTAGRAM_SCOPES = (
    "public_profile,email,instagram_basic,business_management,pages_show_list,pages_read_engagement"
)
if settings.IN_DEV:
    INSTAGRAM_FRONTEND_REDIRECT = "http://localhost:8080/pr-integrations"
elif settings.IN_STAGING:
    INSTAGRAM_FRONTEND_REDIRECT = "https://staging.managr.ai/pr-integrations"
else:
    INSTAGRAM_FRONTEND_REDIRECT = "https://app.managr.ai/pr-integrations"

TWITTER_AUTHORIZATION_QUERY_PARAMS = {
    "oauth_callback": TWITTER_REDIRECT_URI,
    "oauth_consumer_key": TWITTER_API_KEY,
}


def TWITTER_AUTHENTICATION_PARAMS(token, verifier):
    params = {
        "oauth_consumer_key": TWITTER_API_KEY,
        "oauth_token": token,
        "oauth_verifier": verifier,
    }
    return params


def TWITTER_TOKEN_PARAMS(token):
    params = {
        "oauth_token": token,
        "oauth_callback": TWITTER_REDIRECT_URI,
    }
    return params


def INSTAGRAM_MEDIA_PARAMS(instagram_id, until, since):
    params = {
        "fields": "id,caption,permalink,children{media_url, media_type},comments_count,media_type,media_url,timestamp,like_count",
        "user_id": instagram_id,
        "limit": "30",
        "language": "en",
        "until": until,
        "since": since,
    }
    return params


def INSTAGRAM_TOP_MEDIA_URI(hashtag_id):
    url = INSTAGRAM_GRAPH_BASE_URL + hashtag_id + "/top_media"
    return url


NEWS_API_HEADERS = {
    "Authorization": f"Bearer {NEWS_API_KEY}",
}

NEW_API_URI = "https://newsapi.org/v2"

NEW_API_EVERYTHING_QUERY_URI = (
    lambda query: f"everything?{query}&language=en&sortBy=publishedAt&pageSize=40"
)

NEW_API_EVERYTHING_DATE_URI = (
    lambda date_from, date_to: f"everything?from={date_from}&to={date_to}&language=en&sortBy=publishedAt&pageSize=40"
)

SEARCH_TYPE_CHOICES = (("NEWS", "News"), ("SOCIAL_MEDIA", "Social Media"), ("MIXED", "Mixed"))
COVERAGE_TYPE_CHOICES = (("NATIONAL", "National"), ("LOCAL", "Local"), ("BOTH", "Both"))

DEFAULT_INSTRUCTIONS = """*Executive summary:*\n Highlighting 5 key points from today's clips.\n
*Sentiment*\n Evaluate the overall tone or sentiment of the coverage. Is it primarily positive, neutral, or negative and why.\n
*Key Messages:*\n Determine whether the coverage communicates the company's key messages effectively."""

DEFAULT_TWITTER_INSTRUCTIONS = """*Executive summary:*\n Highlighting 5 key points from today's clips.\n
*Sentiment*\n Evaluate the overall tone or sentiment of the coverage. Is it primarily positive, neutral, or negative and why.\n
*Influencers:*\n Identify key influencers based on follower count"""

DEFAULT_CLIENT_INSTRUCTIONS = "Summary: Summarize the news in paragraph format, in less than 600 characters. \n Top Sources: List top 10 sources (based on popularity and size, no newswire sources)"


DEFAULT_TWITTER_CLIENT_INSTRUCTIONS = """<strong>Summary of the Tweets: No more than 400 characters long </strong>\n
<strong>Sentiment: No more than 200 characters long</strong>\n
<strong>Top Influencers:</strong>\n Identify key influencers based on follower count"""


DEFAULT_INSTAGRAM_CLIENT_INSTRUCTIONS = """<strong>Summary of the Posts: No more than 400 characters long </strong>\n
<strong>Sentiment: No more than 200 characters long</strong>\n
"""

DEFAULT_WRITING_STYLE = "Aim for a professional, informative, yet concise style, bypassing formalities, such as Dear, Sir, Best regards, etc. Get right to the point"

OPEN_AI_QUERY_STRING = (
    lambda search: f"""From the search query '{search}', extract only the main subject or specific topic, ignoring any contextual details about professions, actions, or additional requests. The output must be a concise key subject that can be used for a boolean query in NewsAPI. Avoid including terms that describe professions (like 'journalists') or actions (like 'providing pitching tips'), focusing only on the core subject matter (like 'CPR'). The output must be a valid boolean query that can be used by NewsAPI following the steps below:
    1. If quotes are being used around the query then always search the exact phrase. Example: "optimized supply chain management" should return as "optimized supply chain management".
    2. Do not include AND or OR within quotes, unless it's part of an entity name. Example: 'AI and farming' should return as 'AI' AND 'farming'.
    3. If the query includes negative qualifiers like 'not', transform them into appropriate boolean operators like 'NOT'. Replace general concepts with specific key terms relevant for NewsAPI boolean queries. For instance, 'not stock related' should be translated into 'NOT stocks', 'NOT shares', 'NOT Nasdaq'
    4. When asked to write content on behalf of an organization or entity, omit the organization or entity name. Example: "Write a media pitch for Mayo Clinic about AI and Cancer" should return "AI and Cancer"
    5. Disregard any reference to a date, like 'last night', 'yesterday', etc.
    """
)

OPEN_AI_SEARCH_SUGGESTIONS = (
    lambda name, company: f"""Given the following user details:
    - Company: {company}
    - Name: {name}
    Please generate three initial search suggestions to help the user get started with monitoring relevant news. First search should be the company name - ex: "Coca-Cola" -- IF its a PR agency make an educated guess on who their top 5 clients are, use those as the search suggestions (do not search for the PR firm). Second search should be industry topics that are hyper relevant to the brand - if its a university, provide a topics that the school has research expertise in (vs generic industry topics), be as specific as possible - ex:"CPR", "Climate Change", "Cancer Research", Fashion AND Tiktok . Third Search, provide top 2-3 competitors using a OR in between.
    Output instructions for Non PR firms: Start with "Hi {name}, here are some search suggestions to get you started."
    - "Brand" (just the brand name)
    - "Industry Topic" (up to 5,  Must be 2-3 words max, use AND in between words to broaden search, if needed.) -- ex: "Climate Change", AI AND Research, DEI AND Campus
    - Competitors: Competitor 1 OR Competitor 2 OR Competitor 3 (if its a brand) - just the brand name.
    Output instructions for PR firms: Start with "Hi {name}, here are some search suggestions to get you started."
    - "Brands" (guess which brands they may work with based on location of agency and their niche, list just the brand name)
    - "Industry Topic" (relevent to the PR agency's niche, up to 5, Must be 2-3 words max, use AND in between words to broaden search, if needed.) -- ex: if the agency is focused on fashion clients: AI and Fashion, GenZ and Tiktok. If the agency is focused on B2b: Embedded Finance, Commercial real-estate 
    """
)


def OPEN_AI_NEWS_CLIPS_SUMMARY(date, clips, search, instructions=False, for_client=False):
    if not instructions:
        instructions = DEFAULT_CLIENT_INSTRUCTIONS
    body = f"""Today's date is {date}. Read the news coverage below and carefully follow these instructions, output has to be less than 1000 characters. Do not bold any text in your response. \n Here are the instructions:{instructions}. \n Here is the news coverage: {clips}.
    """
    return body


def OPEN_AI_TWITTER_SUMMARY(date, tweets, search, instructions, for_client=False):
    if not instructions:
        instructions = DEFAULT_TWITTER_CLIENT_INSTRUCTIONS
    body = f"""Today's date is {date}.Summarize the twitter coverage based on these tweets.\n Tweets: {tweets}\n
    You must follow these instructions: {instructions}. Summary cannot be longer than 1,000 characters. Do not bold any text in your response.
    """
    return body


def OPEN_AI_INSTAGRAM_SUMMARY(date, posts, instructions, for_client=False):
    if not instructions:
        instructions = DEFAULT_INSTAGRAM_CLIENT_INSTRUCTIONS
    body = f"""Today's date is {date}.Summarize the instagram coverage based on these posts.\n Posts: {posts}\n
    You must follow these instructions: {instructions}. Summary cannot be longer than 1,000 characters. Do not bold any text in your response.
    """
    return body


OPEN_AI_TWITTER_SEARCH_CONVERSION = (
    lambda search: f"""Convert the Search Term below into a valid Twitter API query.
    Follow these steps in order to create the best possible search:
    1: Concentrate on the primary keywords or key concepts of the search term. For example, from 'why is Michael Jordan trending', extract just 'Michael Jordan'.
    2:Only use hashtag terms when given
    3: Only do user search when instructed
    4: only return the converted search term
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
        body = f"Today's date is {date}. Read the article below, then follow these instructions: {instructions}. Do not bold any text in your response. Output cannot exceed 800 characters.\n Article: {article} \n"
    else:
        body = f"Today's date is {date}. At least one of the terms in the boolean search were mentioned in the provided news article. Follow the instructions carefully. Do not bold any text in your response. \nBoolean Search: {search} \n Instructions: {instructions} \n News Article: {article}"
    return body


def OPEN_AI_PITCH(date, type, instructions, style=False):
    if not style:
        style = "Begin with a precise introduction, without informal salutations. Be clear, concise, and informative, avoiding metaphors. Offer coherent data without persuasion. Aim for depth, not sensationalism and avoid commercial bias."
    body = f"""Today's date is {date}. You are tasked with generating content. You must follow the instructions below. Strictly adhere to any specified word count in the instructions:
    1. Here are the instructions: {type}.
    2. If provided, generate content must be based on this information: {instructions}.
    3. You must Mirror this writing style: {style}.
    4. Again, please adhere to the specified word count.
    """
    return body


def OPEN_AI_GENERATE_CONTENT(date, article, style, instructions):
    if not style:
        style = "Begin with a precise introduction, without informal salutations. Be clear, concise, and informative, avoiding metaphors. Offer coherent data without persuasion. Aim for depth, not sensationalism and avoid commercial bias."
    body = f"""Today's date is {date}. Read the news article below and generate content in less than 800 characters, mirroring a custom writing style. Here are the instructions: {instructions}. Here is the writing style {style}. \n Here is the news article {article}.
    """
    return body


def OPEN_AI_IMAGE_CONTENT(images, instructions, tokens):
    messages = {"role": "user"}
    content = [{"type": "text", "text": instructions}]
    for image in images:
        image_dict = {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image}"}}
        content.append(image_dict)
    messages["content"] = content
    body = {"model": "gpt-4-vision-preview", "messages": [messages], "max_tokens": tokens}
    return body


OPEN_AI_PTICH_DRAFT_WITH_INSTRUCTIONS = (
    lambda pitch, instructions: f"""
Adjust and rewrite the content per the instructions, while maintaining the existing writing style.\n
Content: {pitch}\n
Instructions: {instructions}"""
)

OPEN_AI_REWRITE_PTICH = (
    lambda original, tip, name: f"""
Adjust and rewrite this pitch per the pitching tip, while maintaining the existing writing style. This pitch will be sent via email so you must include a short intriguing subject line; no more than 3 words. Do not bold any text.\n
pitch: {original}\n
tip: {tip}
my name: {name}"""
)

OPEN_AI_LEARN_WRITING_STYLE_PROMPT = (
    lambda sample: f"""Perform a detailed analysis of {sample}, focusing on discerning the author's unique style apart from content. Evaluate tone, formality, structure, and linguistic idiosyncrasies, ensuring an objective stance. Investigate the mechanisms used for establishing credibility, engaging readers informatively, avoiding persuasive or sales-oriented language. Task: Formulate concise guidelines capturing the essence of the author's style, enabling its replication across various themes. Emphasize a clear, informative, non-promotional communication style, highlighting specific stylistic techniques contributing to effective and trustworthy discourse. Output cannot exceed 1,200 characters."""
)

OPEN_AI_REGENERATE_ARTICLE = (
    lambda article, content, instructions: f"""Adjust the content below following these instructions carefully:{instructions}. Output must be less than 1000 characters. \n
    here is the content:{content}
    """
)

OPEN_AI_FIND_JOURNALISTS = (
    lambda type, beat, location, content: f"""List up to 10 real, active journalists and their respective publications that would be interested in writing about the content provided below. Provide pitching tips based on what you know about the journalists, relevant to the user's content. User will specify whether they want journalists or influencers. Follow these instructions very carefully:
    Rule #1: Ensure that all journalists listed are real, currently active professionals. Do not include fake names such as Jane Doe or John Smith.
    Rule #2: Only list journalists that have written for the publication in the past 12 months.
    Rule #3: Email addresses need to be accurate, guess the correct emails based on verified patterns.
    Rule #4: Do NOT bold any of the text in the response.
    Journalist Type: The journalists or influencers must be: {type}.
    Journalistic Beat: The journalists or influencers must cover this specific beat or topic: {beat}.
    Location: The journalists or influencers must be based in or primarily cover {location}.
    User’s Content: {content}.
    """
)

OPEN_AI_GENERATE_FEEDBACK = (
    lambda type, audience, objective, feedback, content: f"""
    Analyze the content along with the post details below from the perspective of a Social Media Manager and provide short, blunt, direct feedback in order to help optimize the content. Output must be as follows: Score: 1-10 (10 being best), Score details: 3-4 bullet points outlining score reasoning, Feedback: 1-2 sentences providing additional feedback.
    Post Type: {type}
    Target Audience: {audience}
    Post Objective: {objective}
    Specific Feedback: {feedback}
    Content: {content}
    """
)

REGENERATE_CONTENT_WITH_FEEDBACK = (
    lambda content, feedback: f"""
    Rewrite the content below based on this feedback.
    Content: {content}
    Feedback: {feedback}
    """
)

OPEN_AI_GENERATE_PDF_SUMMARY = (
    lambda date, instructions, text: f"""
    Today's date is {date}. Read the content below and carefully follow the instructions, output has to be less than 1500 characters: 
    \n Here are the instructions:{instructions}. \n Here is the content: {text}.
"""
)


RUN_PROCESS = (
    lambda date, type, summary, details, style: f""""
    Today is {date}. You are tasked with creating content based on the latest news which is provided below, along with other important details. You must adhere to the writing style provided. For context, user may have also provided additional details about themselves, their company, or their intent for the content being written.
    a. Content Instructions: {type}
    b. Content cannot exceed 2,000 characters
    c. News Summary: {summary}
    d. Additional Details: {details}
    e. Writing Style: {style}
    """
)


OPEN_AI_CONTENT_ASSIST = (
    lambda date, style, instructions, clips: f"""Today's date is {date}. Follow the instructions below carefully:
    Read all the news clips provided below.
    Based on the news coverage do this: {instructions}
    The output must adhere to this writing style: {style}
    Output must not exceed 2500 characters
    Here are the news clips: {clips}"""
)


DISCOVER_JOURNALIST = (
    lambda type, beat, location, content: f"""
    List up to 10 real, active journalists and their respective publications that would be interested in writing about the content provided below. Provide pitching tips based on what you know about the journalists, relevant to the user's content. User will specify whether they want journalists or influencers. Follow these instructions very carefully:
    Rule #1: Ensure that all journalists listed are real, currently active professionals. Do not include fake names such as Jane Doe or John Smith.
    Rule #2: Only list journalists that have written for the publication in the past 12 months.
    Rule #3: Email addresses need to be accurate, guess the correct emails based on verified patterns.
    Here is the Journalist Type: The journalists or influencers must be: {type}.
    Here is the Journalistic Beat: The journalists or influencers must cover this specific beat or topic: {beat}.
    Here is the Location: The journalists or influencers must be based in or primarily cover {location}.
    Here is the User’s Content: {content}.
    Important Output instructions:
    1. DO NOT bold any text in the response
    2. Wrap each journalist/tip in a SPAN tag
    3. Always respond in this format: Journalist: [journalist]
    Publication: [publication/podcast/etc.]
    Email: [email]
    Pitching Tip: [pitching tip]
    """
)

OPEN_AI_EMAIL_JOURNALIST = (
    lambda user, org, style, author, outlet, headline, description, date,: f"""
    {author} from {outlet} wrote this article, "{headline}", heres the article description: {description}. The date of the article is {date}. Now, here is what I need you to do:
    1. Write a short, 100 word email to the journalist from: {user}
    2. Make an observation about their article and use this opportunity to make a tailored pitch for {org}. Use any specific information or pitching tips you have about the journalist (e.g., how they like to be pitched, what they usually cover, their interests). If the company name seems to be a PR agency, assume it's on behalf of the agency's clients.
    3. You must use this writing style: {style}
    4. Open with "Hey {author}," . The name here is passed via parameter from a JS function and sometimes it includes an email, ONLY include the first name in the opening line.
    5. Subject line: email subject line must be 2-3 words.
    6. Guess their email. You must guess their work email address. Make sure to base it on verified email patterns associated with their respective publication. The email is sometimes attached to the name, if so you must use that. Always return the email like this - email: (guessed email)
    7. Do not bold any of the text in the response.  
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


DO_NOT_INCLUDE_WORDS = [
    "photos",
    "sex",
    "review",
    "linkedin",
    ".pdf",
    "facebook",
    "instagram",
    ".jpg",
    "/video",
]

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
    "doctorofcredit.com",
    "ozbargain.com.au",
    "politicalwire.com",
    "freerepublic.com",
    "blogger.com",
    "slashdot.org",
    "theflightdeal.com",
    "fly4free.com",
    "antaranews.com",
    "investorsobserver.com",
]

JOURNALIST_CHOICES = [
    ("ACTIVE", "Active"),
    ("INACTIVE", "Inactive"),
    ("NOT_WITH", "No longer with outlet"),
    ("FREE", "Freelancer"),
    ("CON", "Contributor"),
    ("OPT", "Opt out"),
    ("OTHER", "Other"),
]
