from django.conf import settings

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
    SCRAPER_API_WEBHOOK = "https://managr-zach.ngrok.io/api/scraper-webhook"
elif settings.IN_STAGING:
    TWITTER_FRONTEND_REDIRECT = "https://staging.managr.ai/pr-integrations"
    SCRAPER_API_WEBHOOK = "https://staging.managr.ai/api/scraper-webhook"
else:
    TWITTER_FRONTEND_REDIRECT = "https://app.managr.ai/pr-integrations"
    SCRAPER_API_WEBHOOK = "https://app.managr.ai/api/scraper-webhook"
TWITTER_API_HEADERS = {"Authorization": f"Bearer {TWITTER_ACCESS_TOKEN}"}
TWITTER_USER_HEADERS = lambda user_token: {"Authorization": f"Bearer {user_token}"}

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

GOOGLE_SEARCH_URI = "https://www.googleapis.com/customsearch/v1"
GOOGLE_SEARCH_KEY = settings.GOOGLE_SEARCH_API_KEY
GOOGLE_SEARCH_ID = settings.GOOGLE_SEARCH_ID
YOUTUBE_SEARCH_URI = "https://www.googleapis.com/youtube/v3/search"
YOUTUBE_VIDEO_URI = "https://www.googleapis.com/youtube/v3/videos"
YOUTUBE_SEARCH_PARAMS = lambda query, max, from_date, to_date: {
    "part": "snippet",
    "q": query,
    "order": "relevance",
    "relevanceLanguage": "en",
    "type": "video",
    "maxResults": max,
    "key": GOOGLE_SEARCH_KEY,
    "publishedAfter": from_date,
    "publishedBefore": to_date,
}

YOUTUBE_VIDEO_PARAMS = lambda video_id: {
    "part": "statistics",
    "id": video_id,
    "key": GOOGLE_SEARCH_KEY,
}

SCRAPER_API_KEY = settings.SCRAPER_API_KEY
SCRAPER_BATCH_URI = "https://async.scraperapi.com/batchjobs"


def SCRAPER_BATCH_BODY(urls, include_webhook=False, is_article=False):
    body = {
        "urls": urls,
        "render": "true",
        "apiKey": SCRAPER_API_KEY,
    }
    if include_webhook:
        body["callback"] = {
            "type": "webhook",
            "url": f"{SCRAPER_API_WEBHOOK}?isArticle={is_article}",
        }
    return body


SEMRUSH_TRAFFIC_URI = "https://api.semrush.com/analytics/ta/api/v3/summary"

BUZZSUMO_API_KEY = settings.BUZZSUMO_API_KEY
BUZZSUMO_SEARCH_URI = "https://api.buzzsumo.com/search/articles.json"
BUZZSUMO_TRENDS_URI = "https://api.buzzsumo.com/search/trends.json"

BLUESKY_SEARCH_URI = "https://api.bsky.app/xrpc/app.bsky.feed.searchPosts"

BLUESKY_PROFILE_URI = "https://api.bsky.app/xrpc/app.bsky.actor.getProfile"


def SEMRUSH_PARAMS(urls):
    return {"key": settings.SEMRUSH_API_KEY, "targets": ",".join(urls)}


def GOOGLE_SEARCH_PARAMS(query, number_of_results):
    params = {
        "q": query,
        "key": GOOGLE_SEARCH_KEY,
        "cx": GOOGLE_SEARCH_ID,
        "num": number_of_results,
    }
    return params


def OPEN_AI_GET_INSIGHTS(notes, activity, bio, instructions):
    prompt = f"""
    You are a proactive and detail-oriented VP of Communications. A data-driven leader who champions collaboration and technological innovation. 
    Excellent communicator focused on strategic management, team accountability, and continuously enhancing PR processes. Here is your task: Review all the notes, bio, and user engagement activity related to a contact, most likely a journalist. Then follow the instructions.
    
    Here's the bio, if any: {bio}
    \n
    Here are the contact notes: {notes}
    \n
    Here's the user engagement activity, if any: {activity}
    \n
    Here are the instructions: {instructions}


    Output should not exceed 1,000 characters. Use <strong> tags for bold text. Use <h2> tags for headings. Always use a heading.
    
    """
    return prompt


def OPEN_AI_TRACKER_INSIGHTS(bio, instructions):
    prompt = f"""
    You are a proactive and detail-oriented VP of Communications. A data-driven leader who champions collaboration and technological innovation. Excellent communicator focused on strategic management, team accountability, and continuously enhancing PR processes. Here is your task: Review all the email pitching activities done by users that are pitching journalist, podcasters, or bloggers. Then follow these instructions.
    
    Here's the activity: {bio}
    \n
    Here are the instructions: {instructions}


    Output should not exceed 1,000 characters. Use <strong> tags for bold text. Use <h2> tags for headings. Always use a heading. All dates and Numbers need to be in strong tags. All dates returned must be in the mm/dd/yyyy format. Never return the message id 
    
    """
    return prompt


def OPEN_AI_RESULTS_PROMPT(journalist, results, company, text):
    prompt = f"""Here are the top 5 search results for {journalist}:

    Results: {results}

    Additional info on the person from a publisher site: {text}.

    Using the information from the search results and publisher site, create a bio for {journalist}. 
    In the bio, be sure to include the name of the most recent company the person is affiliated with. To ensure accuracy, check for mentions of the company across both the search results and publisher information, using the most widely recognized name version of the company. If the information says that the person worked at a company previously, it means they're no longer there so look carefully for their new company.
    Then, provide 3 brief, relevant pitching tips for {company} based on what you know about the person.
    Finally, include all available contact details for the person, such as social media handles and email. If an email address is found, use it; if none is mentioned, omit this detail. Check the name provided to make sure it is spelled correctly and not missing any parts of the name. You must return the correct name

    Output must be JSON with bio, company,name, and email as keys:
    bio: '
    <h2>Bio:</h2>
    [Bio content]
    <h2>3 Pitching Tips:</h2>
    [Pitching tips]
    <h2>Contact Details:</h2>
    [Contact details]
    ',
    company: [Company name],
    email: '[EMAIL IF FOUND]'
    name: [Journalist Name]

    Structure your resposne in the following format:
    **Heading** in `<h2>` tags,
    Sections with `<strong>` subheadings, 
    Ordered or unordered lists using `<ol>` or `<ul>`, 
    Paragraphs with `<p>`, and 
    Line breaks `<br>` between main points for clarity.
    All links must be anchor tags with target="_blank" so that they open in a new window.

    Make sure to:
    1. Use descriptive headings for each section.
    2. Separate main points with line breaks or paragraphs.
    3. Keep responses structured and consistent for easy reading in a Vue.js app.
    4. Do not wrap the JSON in ```json```
    """
    return prompt


def OPEN_AI_DISCOVERY_RESULTS_PROMPT(journalist, results, content, text):
    prompt = f"""Here are the top 5 search results for {journalist}:

    Results: {results}

    Additional info on the person from a publisher site: {text}.

    Combine the data from the search results and publisher site to craft one bio for {journalist}.
    Include the company the person works for, make sure the company name is full version of the company name.
    Then offer 3 short pitching tips based on what you know of the person, tailored to the user's pitch: {content}.
    Lastly, list all available contact details for the person based on the provided data, including social handles and email address.
    If the email is mentioned in the provided information, use that email. If no email is found, guess their work email based on verified email patterns for their publication.
    Always return the email like this - email: guessed email

    Output must be JSON with bio, company, and email as keys:
    bio: '
    <h2>Bio:</h2>
    [Bio content]
    <h2>3 Pitching Tips:</h2>
    [Pitching tips]
    <h2>Contact Details:</h2>
    [Contact details]
    ',
    company: [Company name],
    email: '[EMAIL IF FOUND]'

    Do not wrap the JSON in ```json```

    Structure your resposne in the following format:
    **Heading** in `<h2>` tags,
    Sections with `<strong>` subheadings, 
    Ordered or unordered lists using `<ol>` or `<ul>`, 
    Paragraphs with `<p>`, and 
    Line breaks `<br>` between main points for clarity.
    All links must be anchor tags with target="_blank" so that they open in a new window.

    Make sure to:
    1. Use descriptive headings for each section.
    2. Separate main points with line breaks or paragraphs.
    3. Keep responses structured and consistent for easy reading in a Vue.js app.
    

    """
    return prompt


def OPEN_AI_SOCIAL_BIO(person, org, results, text):
    prompt = f"""
    Here are the top 5 search results for {person} on Twitter, Bluesky, or YouTube : \n Results: {results}\n And here is additional info on the person from a website: {text}. \n 
    Combine the data from search results and the website to craft one bio for {person}. Then offer 3 short relevant pitching tips for {org} based on what you know about the person. 
    Lastly, if available, list out journalist's additional social handles and email address. If email not available, exclude email details from the output. 
    Output must be JSON:
    bio: '
    <h2>Social Media Bio:</h2>
    [BIO WITHOUT ANY LINKS]
    <h2>Pitching Tips:</h2>
    [PITCHING TIPS]
    <h2>Contact Details:</h2>
    [CONTACT DETAILS]
    ',
    email: '[EMAIL IF FOUND]'

    Structure your resposne in the following format:
    **Heading** in `<h2>` tags,
    Sections with `<strong>` subheadings, 
    Ordered or unordered lists using `<ol>` or `<ul>`, 
    Paragraphs with `<p>`, and 
    Line breaks `<br>` between main points for clarity.
    Do not include ```html in your response.

    Make sure to:
    1. Use descriptive headings for each section.
    2. Separate main points with line breaks or paragraphs.
    3. Keep responses structured and consistent for easy reading in a Vue.js app.
    4. Do not wrap the JSON in ```json```
    5. All links must be anchor tags with target="_blank" so that they open in a new window.
    6. NEVER include any additional text next to the email. example: instead of email@email.com (guessed email based on typical email patterns), simply return email@email.com, Instead of email@email.com (guessed email), simply return email@email.com. This is very important, do not ignore
    """
    return prompt


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

NEW_API_EVERYTHING_QUERY_URI = lambda query: f"everything?{query}&language=en&sortBy=publishedAt"

NEW_API_EVERYTHING_DATE_URI = (
    lambda date_from, date_to: f"everything?from={date_from}&to={date_to}&language=en&sortBy=publishedAt&pageSize=40"
)

SEARCH_TYPE_CHOICES = (("NEWS", "News"), ("SOCIAL_MEDIA", "Social Media"), ("MIXED", "Mixed"))
COVERAGE_TYPE_CHOICES = (("NATIONAL", "National"), ("LOCAL", "Local"), ("BOTH", "Both"))
ALERT_TYPES = (("EMAIL", "Email"), ("SLACK", "Slack"), ("BOTH", "Both"))
MESSAGE_TYPES = (("USER", "User"), ("SYSTEM", "System"))

DEFAULT_INSTRUCTIONS = """*Executive summary:*\n Highlighting 5 key points from today's clips.\n
*Sentiment*\n Evaluate the overall tone or sentiment of the coverage. Is it primarily positive, neutral, or negative and why.\n
*Key Messages:*\n Determine whether the coverage communicates the company's key messages effectively."""

DEFAULT_TWITTER_INSTRUCTIONS = """*Executive summary:*\n Highlighting 5 key points from today's clips.\n
*Sentiment*\n Evaluate the overall tone or sentiment of the coverage. Is it primarily positive, neutral, or negative and why.\n
*Influencers:*\n Identify key influencers based on follower count"""

DEFAULT_CLIENT_INSTRUCTIONS = "Summarize the news in paragraph format. list the top 3 sources (based on popularity and size, no newswire sources). Be concise, keep the output short."


DEFAULT_TWITTER_CLIENT_INSTRUCTIONS = """<strong>Summary of the Tweets: No more than 400 characters long </strong>\n
<strong>Sentiment: No more than 200 characters long</strong>\n
<strong>Top Influencers:</strong>\n Identify key influencers based on follower count"""


DEFAULT_INSTAGRAM_CLIENT_INSTRUCTIONS = """<strong>Summary of the Posts: No more than 400 characters long </strong>\n
<strong>Sentiment: No more than 200 characters long</strong>\n
"""

DEFAULT_WRITING_STYLE = "Aim for a professional, informative, yet concise style, bypassing formalities, such as Dear, Sir, Best regards, etc. Get right to the point"

OPEN_AI_QUERY_STRING = (
    lambda search, project: f"""
    Generate a boolean search query for NewsAPI based on user input and Projects details (if provided). Follow these guidelines:

    1. If a specific search term is provided, use it directly in the query (e.g., Supply chain shortage, Florida State University, "Commercial Real-estate", Nike AND football).

    2. If a user submits a long conversational request or uses chat-like phrasing, identify the **core topic, entity, or beat** by distilling their input into 2-3 keywords or a concise phrase likely to generate news coverage, prioritizing terms or topics with a high likelihood of media interest. 
       - Avoid including extraneous context or unrelated words. 
       - Example: "Top storylines covering Lululemon" should just come back as "Lululemon."
       - Example 2: "Find journalists covering Electric vehicles" should return "Electric Vehicles."

    3. If the user provides project details (e.g., a media pitch, campaign, or product launch), scan it prior to building a search:

       - Example 1: User requests, "What are my competitor's up to ?" for a project about Lululemon's pitch on sustainable fashion, return: `"Nike" OR "Under Armour" OR "Athleta"
 
       - Example 2: User requests, "Find journalists interested in this pitch", for a project about Lululemon's pitch on sustainable fashion, return relevant topics or beats such as : `"Sustainable fashion" OR "Recycled materials".

    Boolean Formatting:
    1. Use quotes around exact phrases as needed.
    2. Use only AND and OR operators, avoiding them within quotes unless part of an official name.
    3. For negative qualifiers, use NOT (e.g., "not stock-related" becomes NOT stocks).
    4. Focus on only the **core topic, beat, or industry**. Avoid extraneous terms or unrelated context. Exclude date references (like "yesterday" or "recent").
    5. Use no more than one AND in the query to keep it concise.
    6. Only return the boolean, no explanations or extra context are necessary.

    User Request: {search}
    Project details (campaign, media pitch, etc): {project}
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


def JOURNALIST_INSTRUCTIONS(company):
    return f"Summarize the articles the journalist wrote, then you must provide a factual background on the journalist (important: do not make it up). Lastly, provide pitching tips for user who works for {company}"


def TWITTER_USERNAME_INSTRUCTIONS(company):
    return f"Summarize the tweets from the author, then you must provide a factual background on the author (important: do not make it up). Lastly, provide pitching tips for user who works for {company} "


def OPEN_AI_NEWS_CLIPS_SUMMARY(
    date, clips, search, project, elma, trending, instructions=False, for_client=False
):
    if not trending:

        body = f"""
                {elma}.
                Today is {date}. Please provide a concise and accurate response based on the trending news coverage below. User may provide additional instructions, make sure to follow them. If the instructions don't ask for anything specific, just provide a brief summary of the news coverage as it pertains to their search term. For additional context, user may provide their project details (pitch, product launch, company boiler plate).
                Cite your sources by enclosing the citationIndex of the article in a set of square brackets at the end of the corresponding sentence, without a space between the last word and the citation. For example: 'Paris is the capital of France[0].' Only use this format to cite the news coverage.
                Do not use more than 2 citations in one sentence. Do not include a references section at the end of your answer. Never make an entire list item a link.
                Input Format:
                User Request: {search}
                News Coverage: {clips}
                Project details (campaign, media pitch, etc): {project}
                Output format:
                **Heading** in `<h2>` tags,
                Sections with `<strong>` subheadings,
                Ordered or unordered lists using `<ol>` or `<ul>`,
                Paragraphs with `<p>`, and
                Line breaks `<br>` between main points for clarity.
                Do not include ```html in your response.
                Keep responses structured and consistent for easy reading in a Vue.js app.
                """
    else:

        body = f"""

        {elma}.

        Today is {date}. Please provide a concise and accurate response based on the trending news coverage below. User may provide additional instructions, make sure to follow them. If the instructions don't ask for anything specific, just provide a brief summary of the news coverage as it pertains to their search term. For additional context, user may provide their project details (pitch, product launch, company boiler plate).
        Cite your sources by enclosing the citationIndex of the article in a set of square brackets at the end of the corresponding sentence, without a space between the last word and the citation. For example: 'Paris is the capital of France[0].' Only use this format to cite the news coverage.
        Do not use more than 2 citations in one sentence. Do not include a references section at the end of your answer. Never make an entire list item a link.
        
        Input Format:

        User Request: {search}
        News Coverage: {clips}
        Project details (campaign, media pitch, etc): {project}
    
        Output format:

        **Heading** in `<h2>` tags,
        Sections with `<strong>` subheadings,
        Ordered or unordered lists using `<ol>` or `<ul>`,
        Paragraphs with `<p>`, and
        Line breaks `<br>` between main points for clarity.
        Do not include ```html in your response.

        Keep responses structured and consistent for easy reading in a Vue.js app.
        """

    return body


def SUMMARY_FOLLOW_UP(date, clips, previous, project, elma, instructions, trending):
    if not trending:

        body = f"""

        {elma}.

        Today is {date}. User is asking a follow up question. Please provide an output per the users request (see below) based on the previous response and the news coverage below. Also, if a user provides project details (check below) reference those as well, they are applicable to the request.
        Cite your sources by enclosing the citationIndex of the article in a set of square brackets at the end of the corresponding sentence, without a space between the last word and the citation. For example: 'Paris is the capital of France[0].' Only use this format to cite the news coverage.
        Do not use more than 2 citations in one sentence. Do not include a references section at the end of your answer. Never make an entire list item a link.
        
        Follow these instructions carefully:
        
        1. The user is most likely asking a follow up question (query) based on the previous response and the news coverage. Also assume the user's follow up is related to the current topic, event, entity, or company.
        2. If the answer can not be provided using the previous response or news coverage below, or the user introduces a new entity/company/topic (e.g. from lululemon to Nike or from fashion to finance), or the user tells you to "run a new search", then create a new search term to find the required information. Make sure the search term is simple, fairly broad, likely to get media coverage. Use an AND or OR if needed. Example: Original search is about Lululemon, in the previous response there is nothing about Peloton. User asks a follow up, "top storylines about Peloton" -- new search should be Top storylines covering Peloton.
        3. The output should just be the answer to their question / request. Example 1: "List top journalist covering this news" = return a list of journalist. Example 2: "What's being said about Joe Smith" = an concise answer about Joe smith.
        4. Only return "new search term" followed by the term, in square brackets with no explanations or other information. Example: "New Search Term: [Term is here]
        
        Input Format:
        Previous response: {previous}
        User Request: {instructions}
        News Coverage: {clips}
        Project details (campaign, media pitch, etc): {project}
        
        Output format:
        **Heading** in `<h2>` tags,
            Sections with `<strong>` subheadings,
            Ordered or unordered lists using `<ol>` or `<ul>`,
            Paragraphs with `<p>`, and
            Line breaks `<br>` between main points for clarity.
            Do not include ```html in your response.
        Keep responses structured and consistent for easy reading in a Vue.js app.
        """

    else:

        body = f"""

        {elma}.
        Today is {date}. User is asking a follow up question. Please provide an output per the users request (see below) based on the previous response and the trending news coverage below. Also, if a user provides project details (check below) reference those as well, they are applicable to the request.
        Cite your sources by enclosing the citationIndex of the article in a set of square brackets at the end of the corresponding sentence, without a space between the last word and the citation. For example: 'Paris is the capital of France[0].' Only use this format to cite the news coverage.
        Do not use more than 2 citations in one sentence. Do not include a references section at the end of your answer. Never make an entire list item a link.
       
        Follow these instructions carefully:
        1. The user is most likely asking a follow up question (query) based on the previous response and the trending news coverage. Also assume the user's follow up is related to the current topic, event, entity, or company.
        2. If the answer can not be provided using the previous response or trending news coverage below, or the user introduces a new entity/company/topic (e.g. from lululemon to Nike or from fashion to finance), or the user tells you to "run a new search", then create a new keyword From the user input, extract the **either the single most relevant keyword or up to 2 keywords separated by a comma ** related to the topic while excluding brand names, locations (e.g., country, state, etc.), or generic terms like 'top' or 'headlines'.
        3. The output should just be the answer to their question / request. Example 1: "List top journalist covering this news" = return a list of journalist. Example 2: "What's being said about Joe Smith" = an concise answer about Joe smith.
        4. Only return "new search term" followed by the keyword, in square brackets with no explanations or other information. Example: "New Search Term: [keyword is here]
        
        Input Format:
        Previous response: {previous}
        User Request: {instructions}
        News Coverage: {clips}
        Project details (campaign, media pitch, etc): {project}

        Output format:
        **Heading** in `<h2>` tags,
            Sections with `<strong>` subheadings,
            Ordered or unordered lists using `<ol>` or `<ul>`,
            Paragraphs with `<p>`, and
            Line breaks `<br>` between main points for clarity.
            Do not include ```html in your response.
        Keep responses structured and consistent for easy reading in a Vue.js app.
        """

    return body


def OPEN_AI_NEWS_CLIPS_SUMMARY_EMAIL(
    date, clips, search, elma, project, instructions=False, for_client=False
):

    body = f"""

        {elma}.

        Today is {date}. User is asking a question based on recent media coverage. Please provide an output per the users request (see below) based on the news coverage below (see below). Also, if a user provides project details (check below) reference those as well, they are applicable to the request. If the instructions don't ask for anything specific, just provide a brief summary of the news coverage as it pertains to their search term. Example: “Top storylines covering Lululemon” = List top stories covering Lululemon. Example 2: "List top journalist covering Lululemon” = return a list of journalist. Example 3: Lululemon = List top headlines about Lululemon along with any additional insights (sentiment, key messages)
        Cite your sources by enclosing the citationIndex of the article in a set of square brackets at the end of the corresponding sentence, without a space between the last word and the citation. For example: 'Paris is the capital of France[0].' Only use this format to cite the news coverage.
        Do not use more than 2 citations in one sentence. Do not include a references section at the end of your answer. Never make an entire list item a link.
        
        Input Format:

        User Request: {search}
        Media Coverage: {clips}
        Project details (campaign, media pitch, etc): {project}
    
        Output format:

        **Heading** in `<h2>` tags,
        Sections with `<strong>` subheadings,
        Ordered or unordered lists using `<ol>` or `<ul>`,
        Paragraphs with `<p>`, and
        Line breaks `<br>` between main points for clarity.
        Do not include ```html in your response.

        Keep responses structured and consistent for easy reading in a Vue.js app.
        """

    return body


def OPEN_AI_NEWS_CLIPS_SLACK_SUMMARY(date, clips, search, instructions=False, for_client=False):
    if not instructions:
        instructions = DEFAULT_CLIENT_INSTRUCTIONS
    body = f"""Today's date is {date}. Please provide a concise and accurate response per my instructions, using the given news coverage. If the instructions don't ask for anything specific, just provide a brief summary of the news in 250 words or less.
    Cite the most relevant sources by enclosing the index of the search result in a Slack hyperlink with the index at the end of the corresponding sentence, without a space between the last word and the citation. Example: <URL|[INDEX]>.
    Never cite more than 3 sources in a row. Do not include a references section at the end of your answer. Never make an entire list item a link. If the search results are insufficient or irrelevant, answer the query to the best of your ability using existing knowledge.
    Keep the output under 1000 characters. All URLs must be formatted as Slack hyperlinks. Do NOT insert only a URL into the text. Make sure that your response is properly formatted Slack markdown with good spacing. For headers, only use this format *HEADER TEXT*.

    Here is the news coverage:
    {clips}

    Here are the instructions:
    {instructions}
    """
    return body


def OPEN_AI_TWITTER_SUMMARY(date, tweets, search, project, elma, for_client=False):
    body = f"""

    {elma}.

    Today is {date}. Please provide a concise and accurate response based on the social media coverage below. User may provide additional instructions, make sure to follow them. If the instructions don't ask for anything specific, just provide a brief summary of the the coverage as it pertains to their search term and identify top influencers from all channels - X (formally Twitter), Bluesky, and Youtube. For additional context, user may provide their project details (pitch, product launch, company boiler plate).
    Cite your sources by enclosing the citationIndex of the article in a set of square brackets at the end of the corresponding sentence, without a space between the last word and the citation. For example: 'Paris is the capital of France[0].' Only use this format to cite the news coverage.
    Do not use more than 2 citations in one sentence. Do not include a references section at the end of your answer. Never make an entire list item a link.
    
    Input Format:

    User Request: {search}
    Social media coverage: {tweets}
    Project details (campaign, media pitch, etc): {project}
   
    Output format:

    **Heading** in `<h2>` tags,
    Sections with `<strong>` subheadings,
    Ordered or unordered lists using `<ol>` or `<ul>`,
    Paragraphs with `<p>`, and
    Line breaks `<br>` between main points for clarity.
    Do not include ```html in your response.

    Keep responses structured and consistent for easy reading in a Vue.js app.
    """
    return body


def TWITTER_SUMMARY_FOLLOW_UP(date, tweets, previous, project, elma, instructions):
    body = f"""

    {elma}.

    Today is {date}. Please provide a concise and accurate answer to the query based on the previous response and the social media coverage below. It is most likely a follow up question. User provides project details for additional context.
    Cite your sources by enclosing the citationIndex of the article in a set of square brackets at the end of the corresponding sentence, without a space between the last word and the citation. For example: 'Paris is the capital of France[0].' Only use this format to cite the news coverage.
    Do not use more than 2 citations in one sentence. Do not include a references section at the end of your answer. Never make an entire list item a link.
    
    Follow these instructions carefully:
    
    1. The user is most likely asking a follow up question (query) based on the previous response and the tweets / clips. Also assume the user's follow up is related to the current topic, event, entity, or company.
    2. If the answer can not be provided using the previous response or news coverage below, or the user introduces a new entity/company/topic (e.g. from lululemon to Nike or from fashion to finance), or the user tells you to "run a new search", then create a new search term to find the required information. Make sure the search term is simple, fairly broad, likely to get media coverage. Use an AND or OR if needed. Example: Original search is about Lululemon, in the previous response there is nothing about Peloton. User asks a follow up, "top storylines about Peloton" -- new search should be Top storylines covering Peloton.
    3. Focus on only answering the query. No need to regurgitate other/irrelevant parts of the previous response.
    4. Only return "new search term" followed by the term, in square brackets with no explanations or other information. Example: "New Search Term: [Term is here]
    
    Input Format:
    Previous response: {previous}
    User Request: {instructions}
    Tweets, Posts, and clips: {tweets}
    Project details (campaign, media pitch, etc): {project}
    
    Output format:
    **Heading** in `<h2>` tags,
        Sections with `<strong>` subheadings,
        Ordered or unordered lists using `<ol>` or `<ul>`,
        Paragraphs with `<p>`, and
        Line breaks `<br>` between main points for clarity.
        Do not include ```html in your response.
    Keep responses structured and consistent for easy reading in a Vue.js app.
    """

    return body


def OPEN_AI_INSTAGRAM_SUMMARY(date, posts, instructions, for_client=False):
    if not instructions:
        instructions = DEFAULT_INSTAGRAM_CLIENT_INSTRUCTIONS
    body = f"""Today's date is {date}.Summarize the instagram coverage based on these posts.\n Posts: {posts}\n
    You must follow these instructions: {instructions}. Summary cannot be longer than 1,000 characters. 
    """
    return body


OPEN_AI_TWITTER_SEARCH_CONVERSION = (
    lambda search, project: f"""
    Generate a valid Twitter API query based on user input and Projects details (if provided). Follow these guidelines:

    1. If a specific search term is provided, use it directly in the query (e.g., Supply chain shortage, Florida State University, "Commercial Real-estate", Nike AND football).

    2. If a user submits a long conversational request or uses chat-like phrasing, identify the **core topic, entity, or beat** by distilling their input into 2-3 keywords or a concise phrase likely to generate news coverage, prioritizing terms or topics with a high likelihood of media interest. 
       - Avoid including extraneous context or unrelated words. 
       - Example: "Top storylines covering Lululemon" should just come back as "Lululemon."
       - Example 2: "Find journalists covering Electric vehicles" should return "Electric Vehicles."

    3. If the user provides project details (e.g., a media pitch, campaign, or product launch), scan it prior to building a search:

       - Example 1: User requests, "What are my competitor's up to ?" for a project about Lululemon's pitch on sustainable fashion, return: `"Nike" OR "Under Armour" OR "Athleta"
 
       - Example 2: User requests, "Find journalists interested in this pitch", for a project about Lululemon's pitch on sustainable fashion, return relevant topics or beats such as : `"Sustainable fashion" OR "Recycled materials".

    Boolean Formatting:
    1. Use quotes around exact phrases as needed.
    2. Use only AND and OR operators, avoiding them within quotes unless part of an official name.
    3. For negative qualifiers, use NOT (e.g., "not stock-related" becomes NOT stocks).
    4. Focus on only the core entity or topic. Exclude date references (like "yesterday" or "latest" or "recent") and general terms like "News" or "Coverage" or "journalist".
    5. Use no more than one AND in the query to keep it concise.
    6. Only return the boolean, no explanataions or extra context is neccessary
   

    User Request: {search}
    Project details (campaign, media pitch, etc): {project}
"""
)

DEFAULT_ARTICLE_INSTRUCTIONS = (
    lambda search: f"*Context: \n Sentiment: \n Impact: as it pertains to {search}.* Output can not exceed 400 characters"
)
DEFAULT_CLIENT_ARTICLE_INSTRUCTIONS = (
    lambda boolean: f"Summary: summarize the article and its relation to any of these terms {boolean} . \n Sentiment: what is the sentiment of any of these terms {boolean} within the article"
)


def OPEN_AI_ARTICLE_SUMMARY(date, article, search, instructions=False, for_client=False):
    if not instructions:
        instructions = DEFAULT_CLIENT_ARTICLE_INSTRUCTIONS(search)
    if not search:
        body = f"""
        Today's date is {date}. Read the article below, then provide a summary and the sentiment of the article below.

        Here's the Article: {article}

        Output format must be:

        <strong>Summary:</strong>
        summary here


        <strong>Sentiment:</strong>
        sentiment here

        Keep responses structured and consistent for easy reading in a Vue.js app.   

      
    """
    else:
        body = f"""Today's date is {date}. At least one of the terms in the boolean search were mentioned in the provided news article. Follow the instructions carefully. 
        
        Boolean Search: {search} \n 
        
        Instructions: {instructions}
        
        News Article: {article}

        Output format must be:

        <strong>Summary:</strong>
        summary here

        <strong>Sentiment:</strong>
        sentiment here

        Keep responses structured and consistent for easy reading in a Vue.js app.
"""
    return body


def OPEN_AI_PITCH(date, type, instructions, elma, style=False):
    body = f"""
    {elma}.
    
    Today's date is {date}. Generate a response per the user's instructions below.
    
    Input Format:

    User Request: {type}
    Project details (campaign, media pitch, etc): {instructions}
    Writing style instructions: {style}

    Keep responses structured and consistent for easy reading in a Vue.js app.
    Use Paragraphs with `<p>`, and Line breaks `<br>` between paragraphs for clarity.
    Do not include ```html in your response.
    """
    return body


OPEN_AI_PTICH_DRAFT_WITH_INSTRUCTIONS = (
    lambda elma, pitch, instructions, style, details: f"""

    {elma}.
    
    Generate a response per the user's instructions below.

    Input Format:

    Previous Response {pitch}
    User Request: {instructions}
    Project details (campaign, media pitch, etc): {details}
    Writing style instructions: {style}

    Make sure to Keep responses structured and consistent for easy reading in a Vue.js app.
    Use Paragraphs with `<p>`, and Line breaks `<br>` between paragraphs for clarity.
    Do not include ```html in your response.

    """
)


OPEN_AI_PTICH_SLACK_DRAFT_WITH_INSTRUCTIONS = (
    lambda pitch, instructions, style, details: f"""
    Adjust and rewrite the content per the instructions below, adhering to the desired writing style guidelines. The content should be a format to display in markdown with proper spacing and separate paragraphs for each section (greeting, introduction, closing, etc). Do not include ```markdown``` in your response.\n
    
    Content: {pitch}\n
    Instructions: {instructions}\n
    Writing Style: {style}
    Additional details {details}
    """
)


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


def OPEN_AI_REWRITE_PTICH(original, bio, style, with_style, journalist, name):
    if not with_style:
        prompt = f"""
        Craft a personalized media pitch, following the instructions below:
        1. Write a short, 100 word email to the journalist from: {name}
        2. You must use this writing style: {style}
        3. Subject line: email subject line must be 2-3 words.
        4. Open with "Hi {journalist}," . The name here is passed via parameter from a JS function and sometimes it includes an email, ONLY include the first name in the opening line.
        5. Here is either a generic pitch or company/product/campaign details {original}. Using that data, craft a personalized email based on this information about the journalist: {bio}
        6. Check to see if their email is listed in the journalist bio above. The email is sometimes attached to the name, if so you must use that. If no email can be found, then you must guess their work email. Make sure to base it on verified email patterns associated with their respective publication. Always return the email like this - email: (guessed email)
        7. Do not bold any of the text in the response.

        Personalize the original pitch pitch (see below) to the journalist based on the data from their bio (see below). You must maintain the existing writing style from the original pitch. Also, include a short, basic subject line; no more than 3 words. DO NOT BOLD ANY TEXT IN YOUR RESPONSE, EVER!
        Original Pitch: {original}
        Journalist's bio and pitching tips: {bio}
        My name: {name}
        Provide journalist's email: Check to see if their email is listed in the journalist bio above. If so, you must use that email. If no email can be found, then you must guess their work email. When guessing, you must base it on verified email patterns associated with their respective publication. Always return the email like this - email: email
        """
    else:
        prompt = f"""
        Adjust and rewrite the original media pitch, adhering to the writing style guidelines below.

        original pitch: {original}
        writing style: {style}
        """
    prompt += """
    * DO NOT INCLUDE ```json``` in the output. Use backslash n for all new lines. Enclose keys in in double quotes.
    OUTPUT JSON OBJECT:
    {body: REWRITTEN PITCH,
    subject: SUBJECT,
    email: EMAIL}
    """
    return prompt


def OPEN_AI_WEB_SUMMARY(query, results, text, instructions, summary, elma, project):
    if not instructions:
        prompt = f"""
        {elma}.

        Please provide a concise and accurate response to my query, using the given search results. For additional context, user may provide their project details (pitch, product launch, company boiler plate) - if they do, offer creative suggestions on how they can leverage the search results for their project. 
        Cite your sources by enclosing the citationIndex of the article in a set of square brackets at the end of the corresponding sentence, without a space between the last word and the citation. For example: 'Paris is the capital of France[0].' Only use this format to cite the news coverage.
        Do not use more than 2 citations in one sentence. Do not include a references section at the end of your answer. If the search results are insufficient or irrelevant, answer the query to the best of your ability using existing knowledge. 
        
        query: {query}
        search results: {results}
        full text from the top result: {text}
        Project details (campaign, media pitch, etc): {project}

        Structure your resposne in the following format:
        **Heading** in `<h2>` tags,
        Sections with `<strong>` subheadings, 
        Ordered or unordered lists using `<ol>` or `<ul>`, 
        Paragraphs with `<p>`, and 
        Line breaks `<br>` between main points for clarity.
        Do not include ```html in your response.

        Make sure to:
        1. Separate main points with line breaks or paragraphs.
        2. Keep responses structured and consistent for easy reading in a Vue.js app.
        """
    elif summary:
        prompt = f"""
        {elma}.

        Based on the initial summary and the additional search results, please provide a concise and accurate response to the follow-up question. Use the given search results and the initial summary to ensure the response is comprehensive. Also, if a user provides project details (check below) offer creative suggestions on how they can leverage the search results for their project.  Cite your sources by enclosing the citationIndex of the search result in a set of square brackets at the end of the corresponding sentence, without a space between the last word and the citation. For example: 'Paris is the capital of France[0].' Only use this format to cite the news coverage.
        Do not use more than 2 citations in one sentence. Do not include a references section at the end of your answer. If the search results are insufficient or irrelevant, answer the query to the best of your ability using existing knowledge and the initial summary.
        Make sure that your response is properly formatted simple html with good spacing and easy to read. No padding on the body since it will be going into a container that already has it.
        
        Follow these instructions carefully:

        1. The user is most likely asking a follow up question (query) based on the previous response and the news coverage. Also assume the user's follow up is related to the current topic, event, entity, or company.
        2. Only if the answer can not be provided using the previous response or news coverage below, or the user introduces a new entity/company/topic (e.g. from lululemon to Nike or from fashion to finance),  or the user tells you to "run a new search", then create a new search term to find the required information. Make sure the search term is simple, fairly broad, likely to get media coverage. Use an AND or OR if needed. Example: Original search is about Lululemon, in the previous response there is nothing about Peloton. User asks a follow up, "top storylines about Peloton" -- new search should be Top storylines covering Peloton.
        3. Focus on only answering the query. No need to regurgitate other/irrelevant parts of the previous response.
        4. Only return "new search term" followed by the term, in square brackets with no explanations or other information. Example: "New Search Term: [Term is here]

        initial summary: {summary}
        follow-up question: {instructions}
        search results: {results}
        Project details (campaign, media pitch, etc): {project}

        Structure your resposne in the following format:
        **Heading** in `<h2>` tags,
        Sections with `<strong>` subheadings, 
        Ordered or unordered lists using `<ol>` or `<ul>`, 
        Paragraphs with `<p>`, and 
        Line breaks `<br>` between main points for clarity.
        Do not include ```html in your response.

        Make sure to:
        1. Separate main points with line breaks or paragraphs.
        2. Keep responses structured and consistent for easy reading in a Vue.js app.
        """
    else:
        prompt = f"""
        {elma}.

        Please provide a concise and accurate response to my query, using the given search results. Cite your sources by enclosing the citationIndex of the search result in a set of square brackets at the end of the corresponding sentence, without a space between the last word and the citation. For example: 'Paris is the capital of France[0].' Only use this format to cite the news coverage.
        Do not use more than 2 citations in one sentence. Do not include a references section at the end of your answer. If the search results are insufficient or irrelevant, answer the query to the best of your ability using existing knowledge. 
        Make sure that your response is properly formatted simple html with good spacing and easy to read. No padding on the body since it will be going into a container that already has it.
        
        query: {instructions}
        search results: {results}
        full text from the top result: {text}

        Structure your resposne in the following format:
        **Heading** in `<h2>` tags,
        Sections with `<strong>` subheadings, 
        Ordered or unordered lists using `<ol>` or `<ul>`, 
        Paragraphs with `<p>`, and 
        Line breaks `<br>` between main points for clarity.
        Do not include ```html in your response.

        Make sure to:
        1. Separate main points with line breaks or paragraphs.
        2. Keep responses structured and consistent for easy reading in a Vue.js app.
        """

    return prompt


OPEN_AI_LEARN_WRITING_STYLE_PROMPT = (
    lambda sample: f"""Perform a detailed analysis of {sample}, focusing on discerning the author's unique style apart from content. Evaluate tone, formality, structure, and linguistic idiosyncrasies, ensuring an objective stance. Investigate the mechanisms used for establishing credibility, engaging readers informatively, avoiding persuasive or sales-oriented language. Task: Formulate concise guidelines capturing the essence of the author's style, enabling its replication across various themes. Emphasize a clear, informative, non-promotional communication style, highlighting specific stylistic techniques contributing to effective and trustworthy discourse. Output cannot exceed 1,200 characters."""
)

OPEN_AI_REGENERATE_ARTICLE = (
    lambda article, content, instructions: f"""Adjust the content below following these instructions carefully:{instructions}. Output must be less than 1000 characters. \n
    here is the content:{content}
    """
)

OPEN_AI_FIND_JOURNALISTS = (
    lambda type, beat, location, content: f"""List 10 real, active journalists and their respective publications that would be interested in writing about the content provided below. Sort by order of relevance, most relevant at the top. Provide pitching tips based on what you know about the journalists, relevant to the user's content. User will specify whether they want journalists or influencers. Follow these instructions very carefully:
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
    lambda content, info: f"""
   List up to 10 real, active people would be interested in this pitch: {content}. Here is more information regarding who they are looking for: {info}.
   Now, you must follow the instructions below very carefully:

    * Rule #1: Ensure that all people are real, currently active professionals. Do not include fake names such as Jane Doe or John Smith.

    * Rule #2: Only list people that you have the highest confidence (90% or above) in that they still work there. If you lack confidence do not list all 10, just the ones you're most confident in

    Content output, 3 rows:
    Name:
    Company:
    Reason for Selection:
    View Updated Bio

    "View Updated Bio" MUST be returned in a button tag!
    "Name", "Company", and "Reason for Selection" MUST be returned in a strong tag!
    You MUST wrap each individual journalists/influencer selection in a span tag!
    Do not add any additional text to the response. ONLY return with what I asked for.
"""
)


def OPEN_AI_DISCOVER_JOURNALIST(info, journalists, content):
    if content:
        two = f"2. Based on the most recent data, do these journalist still fit this criteria: {info} and would be interested in the provided pitch. If journalist does not meet the criteria, do not list in the output. It is Important that you only list journalist that fit the criteria."
        three = f"3. Reason why the journalist would be interested in this: {info}"
    else:
        two = f"2. List up to 15 journalist from the data below that are still active and currently writing for a recognizable news publication. Do not include in the list: inactive, former, or retired Journalists."
        three = f"3. Reason why the journalist would be interested in this: {info}"
    prompt = f"""
    Follow these steps carefully based on the object data below
    1. Identify which publication the journalist currently works for (label "freelancer" if applicable) ? Only use the full name of the publication and do not include two names with a slash.
    {two}
    {three}
    JSON OUTPUT FORMAT: {'{'}'journalists':[{'{'}
        'name': NAME,
        'publication': CURRENT EMPLOYER,
        'reason': REASON FOR SELECTION{'}'}] {'}'}
    Journalists data:
    {journalists}
    """
    if content:
        prompt += f"\nPitch:\n{content}"
    return prompt


def OPEN_AI_GET_JOURNALIST_LIST(info, content, list):
    initial_sentence = (
        f"List 20 real, active journalists, podcasters, or bloggers based on this criteria: {info}"
    )
    if content:
        initial_sentence += f" and would be interested in this pitch: {content}"
    prompt = f"""
    {initial_sentence}.\n
    
    Always Reference my current list of journalist (if any) before responding in case I need something based on that list.

    Current list, if any: {list}

    You must follow the instructions below very carefully:
    * Ensure that all journalists, podcasters, or bloggers are real and currently active. 
    * Do not include fake names such as Jane Doe or John Smith or make names up.
    * Output format must a ONLY JSON object:
    journalists: [LIST OF JOURNALIST NAMES]
    """
    return prompt


def OPEN_AI_PITCH_JOURNALIST_LIST(journalists, pitch):
    prompt = f"""
    From the list of journalists I provided, list 20 who would be interested in this pitch: {pitch}.
    Give the reason each journalist would be interested individually to the pitch.
    * Output format must a ONLY JSON object:
    journalists: journalists:[{'{'}
        'name': NAME,
        'outlet': OUTLET,
        'reason': REASON FOR SELECTION{'}'}]

    journalists:\n
    {journalists}    
    """
    return prompt


OPEN_AI_EMAIL_JOURNALIST = (
    lambda user, org, style, bio, author, outlet, headline, description, date,: f"""
    {author} from {outlet} wrote this article, "{headline}", heres the article description: {description}. The date of the article is {date}. Now, here is what I need you to do:    
    1. Write a short, 100 word email to the journalist from: {user}    
    2. You must use this writing style: {style}    
    3. Subject line: email subject line must be 2-3 words.    
    4. Open with "Hey {author}," . The name here is passed via parameter from a JS function and sometimes it includes an email, ONLY include the first name in the opening line.
    5. Make an observation about their article and use this opportunity to make a tailored pitch for {org}. Apply relevant pitching tips based on the information you have about the journalist found in their bio here: {bio}
    6. Check to see if their email is listed in the journalist bio above. The email is sometimes attached to the name, if so you must use that. If no email can be found, then you must guess their work email. Make sure to base it on verified email patterns associated with their respective publication. Always return the email like this - email: (guessed email)    
    7. Do not bold any of the text in the response.
     """
)

OPEN_AI_RELEVANT_ARTICLES = (
    lambda term, clips: f"""
    List the top 5 most relevant stories pertaining to {term}, sort by most relevant at the top. Output must be: 4-5 word summary of the headline (Source: outlet, mm/dd/yy) in an a tag that opens in a new page using the link. Here are the news clips: \n {clips}:
     """
)

OPEN_AI_RELEVANT_POSTS = (
    lambda term, clips: f"""
    List the top 5 most relevant posts pertaining to {term}, sort by most relevant at the top. Output must be: 4-5 word summary of the post (Source: outlet, mm.dd) in an a tag that opens in a new page using the link. Here are the posts: \n {clips}:
     """
)

OPEN_AI_TOP_JOURNALISTS = (
    lambda term, clips: f"""
    List the top 10 Journalists from top news outlets writing about {term}. Sort by order of influence (most influential at the 
    top) Output must be: Journalist name, (Outlet), 4-5 word headline summary using quotes, - date using mm.dd format. 
    Name must be a strong tag. Here are the news clips: \n {clips}:
     """
)

OPEN_AI_TOP_INFLUENCERS = (
    lambda tweets: f"""
    List the top 5 influencers. Sort by follower count, highest at the top. Output must be : Name, (follower count), 4-5 word post summary using quotes, - date using mm.dd format. Here are the tweets: \n {tweets}:
     """
)

OPEN_AI_RELATED_TOPICS = (
    lambda clips: f"""
    Generate up to 5 related, interesting, diverse questions or topics for further exploration based on the news clips below. Focus on most interesting, impactful and engaging stories. Output must be capped at 4 words per suggestion, no numbering, and no punctuation. Format the output must be as follows:
    Search1:
    Search2:
    Search3:
    Search4:
    Search5:
     
    Here are the news clips / tweets: \n {clips}:
     """
)

OPEN_AI_GOOGLE_SEARCH = (
    lambda search, results, text: f"""
    Answer this question based on all the information below: {search}. You must site your sources (outlet name and date).
    Here are the top 5 search results:{results}
    And here is the top article: {text}  
    """
)


def OPEN_AI_GOOGLE_QUERY(date, question):
    prompt = f"""Today is {date}. Given the user's question, extract a search query that captures the essential information needed to find relevant results from the google search API.
    question: {question}
    """

    return prompt


OPEN_AI_EMPTY_SEARCH_SUGGESTIONS = (
    lambda search: f"""Using NewsAPI to search for '{search}' returned no results. Suggest 3 boolean searches that are likely to get news coverage. 
    The first version should be a slightly modified to make it more broad. The second should be even more broad using an AND between terms, and the third version should be a broad, related topic.
    Return the result as a JSON object in the following format: {{ "boolean": [suggestion1, suggestion2, suggestion3] }}
    """
)


# def REPORT_SUMMARY(brand, clips):
#     prompt = f"""
#     You are the VP of Communications at {brand}. Your task is to create a concise executive overview of the earned media report based on the news clips below. The summary should focus on the following key takeaways and be broken into sections, capped at 1,000 words:

#     1. Total volume of media coverage, what stories drove coverage spikes, and trends in mentions over time.
#     2. Key recognizable publications and influential journalists who covered the brand.
#     3. Key metrics, such as total reach, potential impressions, and engagement rates.
#     4. A brief analysis of media sentiment and its impact on [brand.name]'s brand image.
#     5. Highlight recurring themes or key messages across the media coverage.

#     Your response must be properly formatted html. Do not include any styling and/or <meta> tags. Do not include ```html in your response.

#     Here are the news clips:

#     {clips}
#     """

#     return prompt


def OPEN_AI_NO_RESULTS(boolean):
    prompt = f"""
    No results were found for the search term: {boolean}. You must generate alternative search suggestions using common variations and related terms that may increase the likelihood of finding relevant content. 
    Provide a brief message explaining that these alternative suggestions broaden the search to include common variations and related terms, increasing the chances of finding relevant news coverage.  You can also suggest that they try running a Social or Web search. If they run a web search (vs news search which is what they just ran), suggest using "latest news on {boolean}"" to view most recent articles.
    Follow these guidelines in your response:
    
    1. Create 2–3 alternative search phrases using related terms for {boolean}, separated by 'OR'. Each phrase should be 2–3 words long.
    2. Use synonyms, industry terms, or descriptive phrases commonly used in news coverage of similar topics.
   
    For Example, if the term is 'Supply chain shortage' some good alternative suggestions may be the following:
    "supply chain disruptions" OR "logistics delays" OR "labor shortages"
    "supply issues" OR "supply chain delays" OR "distribution challenges"

    Structure your resposne in the following format:
    **Heading** in `<h2>` tags,
    Sections with `<strong>` subheadings, 
    Ordered or unordered lists using `<ol>` or `<ul>`, 
    Paragraphs with `<p>`, and 
    Line breaks `<br>` between main points for clarity.
    Do not include ```html in your response.

    Make sure to:
    1. Use descriptive headings for each section.
    2. Separate main points with line breaks or paragraphs.
    3. Keep responses structured and consistent for easy reading in a Vue.js app.

    """

    return prompt


REGENERATE_REPORT_SUMMARY = (
    lambda content, instructions, clips: f"""
    The content below is an executive overview of the earned media report that was generated based on the news clips below. Rewrite this report based on the instructions provided below the report. Use the clips for reference when neccessary:

    Here's the report:
    {content}

    Instructions: 
    {instructions}

    clips: 
    {clips}
    """
)


DO_NOT_TRACK_LIST = [
    "https://www.bizjournals.com",
    "https://www.tiktok.com",
    "https://www.instagram.com",
    "https://www.facebook.com",
    "https://www.x.com",
    "https://www.linkedin.com",
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
    "x.com",
    ".png",
    ".jpeg",
    "category",
    "podcast",
    "author",
    ".jpeg",
]

NON_VIABLE_CLASSES = ["menu", "nav"]

EXCLUDE_DOMAINS = [
    "bringatrailer.com",
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
    "dealcatcher.com",
    "dansdeals.com",
    "superpunch.net",
    "securityaffairs.com",
    "fuckingyoung.es",
    "pypi.org",
    "biztoc.com",
    "kicksonfire.com",
    "memeorandum.com",
    "sostav.ru",
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


def REPORT_SUMMARY(elma, brand, clips):
    prompt = f"""

    {elma}.

    Your task is to create a concise executive overview of media coverage based on the news clips below for the following brand or topic: {brand}. The summary should focus on the following key takeaways and be broken into sections, capped at 1,000 words:
   
    1. Total volume of media coverage, what stories drove coverage spikes, and trends in mentions over time.
    2. Key recognizable publications and influential journalists who covered the brand.
    3. Key metrics, such as total reach, potential impressions, and engagement rates.
    4. A brief analysis of media sentiment and its impact on [brand.name]'s brand image.
    5. Highlight recurring themes or key messages across the media coverage.

    Here are the news clips:
    {clips}
    """
    return prompt


def SOCIAL_REPORT_SUMMARY(elma, brand, clips):
    prompt = f"""

    {elma}.

    Your task is to create a concise executive overview of media coverage based on the social posts (tweets, bluesky posts, and youtube videos) below for the following brands or topic: {brand}. The summary should focus on the following key takeaways and be broken into sections, capped at 1,000 words:
    1. Total volume of media coverage, what stories drove coverage spikes, and trends in mentions over time.
    2. Identify key recognizable publications and influencers
    3. Key metrics, such as audience engagement and reach.
    4. A brief analysis of media sentiment and its impact on [brand.name]'s brand image.
    5. Highlight recurring themes or key messages across the media coverage.
    
    Here are the social posts:
    {clips}

    """
    return prompt


def GENERATE_TREND_BOOLEAN(search):
    prompt = f"""
    From the user input, extract the **either the single most relevant keyword or up to 2 keywords separated by a comma ** related to the topic while excluding brand names, locations (e.g., country, state, etc.), or generic terms like 'top' or 'headlines'.
   
    Example 1: user input: "Top news covering AI and healthcare" should return: AI, Healthcare.
    Example 2: user input: "Whats happening in sports" should return: Sports
    Example 3: user input: "Whats trending would be relevant to Florida State University" should return: "Higher Education"

    User input: {search}
    * Output format must a ONLY JSON object:
    keywords : [LIST OF KEYWORDS]
    """

    return prompt
