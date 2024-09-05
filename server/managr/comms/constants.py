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

GOOGLE_SEARCH_URI = "https://www.googleapis.com/customsearch/v1"
GOOGLE_SEARCH_KEY = settings.GOOGLE_SEARCH_API_KEY
GOOGLE_SEARCH_ID = settings.GOOGLE_SEARCH_ID

SCRAPER_API_KEY = settings.SCRAPER_API_KEY


def GOOGLE_SEARCH_PARAMS(query, number_of_results):
    params = {
        "q": query,
        "key": GOOGLE_SEARCH_KEY,
        "cx": GOOGLE_SEARCH_ID,
        "num": number_of_results,
    }
    return params


def OPEN_AI_RESULTS_PROMPT(journalist, results, company, text):
    prompt = f"""Here are the top 5 search results for {journalist}:

    Results: {results}

    Additional info on the person from a publisher site: {text}.

    Combine the data from the search results and publisher site to craft one bio for {journalist}. 
    Include the company the person works for, make sure the company name is the most widely used version of the company name. 
    Then offer 3 short relevant pitching tips for {company} based on what you know about the person. 
    Lastly, list all available contact details for the person based on the provided data, including social handles and email address. 
    If the email is mentioned in the provided information, use that email. If no email is found, exclude email details from the output.

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

    Output MUST follow these rules:
    1. Separate each section with one new line, no additional spacing or padding.
    2. Use <strong> tags for bold text.
    3. Use <h2> tags for headings, except for the company name, which should be inline with 'Company:'.
    4. If there are any links ensure that they are active and clickable in appropriate html tags. AND they must open in a new tab.
    5. Do not include additional text next to the email.
    6. Exclude domain extensions from company names.
    7. Do not add name : [name] and company: [company] at the top of the bio.
    8. Do not wrap the JSON in ```json```.
    """
    return prompt


def OPEN_AI_DISCOVERY_RESULTS_PROMPT(journalist, results, content, text):
    prompt = f"""Here are the top 5 search results for {journalist}:

    Results: {results}

    Additional info on the person from a publisher site: {text}.

    Combine the data from the search results and publisher site to craft one bio for {journalist}. 
    Include the company the person works for, make sure the company name is the most widely used version of the company name. 
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

    Output MUST follow these rules:
    1. Separate each section with one new line, no additional spacing or padding.
    2. Use <strong> tags for bold text.
    3. Use <h2> tags for headings, except for the company name, which should be inline with 'Company:'.
    4. If there are any links ensure that they are active and clickable in appropriate html tags. AND they must open in a new tab
    5. Do not include additional text next to the email.
    6. Exclude domain extensions from company names.
    7. Do not add name : [name] and company: [company] at the top of the bio
    8. Do not wrap the JSON in ```json```
    """
    return prompt


def OPEN_AI_SOCIAL_BIO(person, org, results, text):
    prompt = f"""
    Here are the top 5 search results for {person} on Twitter: \n Results: {results}\n And here is additional info on the person from a website: {text}. \n 
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

    Output MUST follow the following rules:
    1. All bold text MUST be returned in a strong tag instead of markdown!
    2. Add a <br> between sections.
    3. If there are any links ensure that they are active and clickable in appropriate html tags. AND they must open in a new tab.
    4. Do not wrap the JSON in ```json```
    5. NEVER include any additional text next to the email. example: instead of email@email.com (guessed email based on typical email patterns), simply return email@email.com, Instead of email@email.com (guessed email), simply return email@email.com. This is very important, do not ignore
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

NEW_API_EVERYTHING_QUERY_URI = (
    lambda query: f"everything?{query}&language=en&sortBy=publishedAt&pageSize=40"
)

NEW_API_EVERYTHING_DATE_URI = (
    lambda date_from, date_to: f"everything?from={date_from}&to={date_to}&language=en&sortBy=publishedAt&pageSize=40"
)

SEARCH_TYPE_CHOICES = (("NEWS", "News"), ("SOCIAL_MEDIA", "Social Media"), ("MIXED", "Mixed"))
COVERAGE_TYPE_CHOICES = (("NATIONAL", "National"), ("LOCAL", "Local"), ("BOTH", "Both"))
ALERT_TYPES = (("EMAIL", "Email"), ("SLACK", "Slack"), ("BOTH", "Both"))

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

OPEN_AI_EMPTY_SEARCH_SUGGESTIONS = (
    lambda search: f"""Using NewsAPI to search for '{search}' returned no results. Generate 3 alternative terms that are similar to what the user is trying to search for just much more broad, and more likely to get news coverage. 
    The goal is to create 3 different suggestions that will get the user news results. Use AND between select words to broaden the search term. Keep the search short, extract only the main subject or specific topic, ignoring any contextual details. 
    Only use quotes when two words or more. Format the output must be as follows:
    Search1:
    Search2:
    Search3:
    """
)

OPEN_AI_QUERY_STRING = (
    lambda search: f"""Extract the main topic, company, organization or entity from '{search}' for a NewsAPI boolean query. Follow these steps:
    1. When quotes are present, use the exact phrase
    2. Do not include AND or OR within quotes unless part of an entity name.
    3. Convert negative qualifiers to boolean operators, e.g., 'not stock related' becomes 'NOT stocks', 'NOT shares', 'NOT Nasdaq'.
    4. Ignore date references like 'last night', 'yesterday', 'latest', 'current', etc.
    5. Omit words like 'News', 'Coverage', 'Journalists', 'Sentiment', 'Newsjacking' or anything similar. Focus only on the entity or topic.
    6. Never use more than one AND in the boolean search
    7. Output must only be the boolean search
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

OPEN_AI_NO_RESULTS_SUGGESTION = (
    lambda boolean: f"""Using NewsAPI to search for '{boolean}' returned no results. 
    Generate 3 alternative terms that are similar to what the user is trying to search for just much more broad, and more likely to get news coverage. 
    The goal is to create 3 different suggestions that will get the user news results. Use AND between select words to broaden the search term. Keep the search short, extract only the main subject or specific topic, ignoring any contextual details. Only use quotes when two words or more. Format the output must be as follows:\nSuggestion 1:\nSuggestion 2:\nSuggestion 3:
    """
)


def JOURNALIST_INSTRUCTIONS(company):
    return f"Summarize the articles the journalist wrote, then you must provide a factual background on the journalist (important: do not make it up). Lastly, provide pitching tips for user who works for {company}"


def TWITTER_USERNAME_INSTRUCTIONS(company):
    return f"Summarize the tweets from the author, then you must provide a factual background on the author (important: do not make it up). Lastly, provide pitching tips for user who works for {company} "


def OPEN_AI_NEWS_CLIPS_SUMMARY(date, clips, search, instructions=False, for_client=False):
    if not instructions:
        instructions = DEFAULT_CLIENT_INSTRUCTIONS

    body = f"""
    Today is {date}. Please provide a concise and accurate response per my instructions, using the given news coverage. If the instructions don't ask for anything specific, just provide a brief summary of the news in 150 words or less. Cite the most relevant sources by enclosing the index of the search result in square brackets at the end of the corresponding sentence, without a space between the last word and the citation. 
        For example: 'Paris is the capital of France[1].' Only use this format to cite search results. Never cite more than 3 sources in a row. Do not include a references section at the end of your answer. Never make an entire list item a link. If the search results are insufficient or irrelevant, answer the query to the best of your ability using existing knowledge. 
        Make sure that your response is properly formatted simple html with good spacing. Do not include any styling and/or <meta> tags. Do not include ```html``` in your response.

    Here is the news coverage:
    {clips}

    Here are the instructions:
    {instructions}
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


def OPEN_AI_TWITTER_SUMMARY(date, tweets, search, instructions, for_client=False):
    if not instructions:
        instructions = DEFAULT_TWITTER_CLIENT_INSTRUCTIONS
    body = f"""Today's date is {date}. Summarize the twitter coverage based on the twets below. Cite the most relevant sources by enclosing the index of the search result in square brackets at the end of the corresponding sentence, without a space between the last word and the citation. 
    For example: 'Paris is the capital of France[1].' Only use this format to cite search results. Never cite more than 3 sources in a row. Do not include a references section at the end of your answer.
    You must follow these instructions: {instructions}. Make sure that your response is properly formatted simple html with good spacing. Do not include any styling and/or <meta> tags. Do not include ```html``` in your response. Keep it brief, The response should be under 800 characters.   

    Tweets: {tweets}
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


def OPEN_AI_ARTICLE_SUMMARY(date, article, search, length, instructions=False, for_client=False):
    if not instructions:
        instructions = DEFAULT_CLIENT_ARTICLE_INSTRUCTIONS(search)
    if not search:
        body = f"Today's date is {date}. Read the article below, then follow these instructions: {instructions}. Do not bold any text in your response. Output cannot exceed 800 characters.\n Article: {article} \n"
    else:
        body = f"Today's date is {date}. At least one of the terms in the boolean search were mentioned in the provided news article. Follow the instructions carefully. Do not bold any text in your response. \nBoolean Search: {search} \n Instructions: {instructions} \n News Article: {article}"
    return body


def OPEN_AI_PITCH(date, type, instructions, style=False):
    body = f"""Today's date is {date}. Generate the content below in HTML format with proper spacing and separate paragraphs for each section (greeting, introduction, closing, etc). Do not include ```html``` in your response.

    1. Here is what you are asked to generate: {type}
    2. If provided, generated content must be based on this information: {instructions}.
    3. Lastly, you must follow this Writing Style: {style}
    """
    return body


OPEN_AI_PTICH_DRAFT_WITH_INSTRUCTIONS = (
    lambda pitch, instructions, style, details: f"""
    Adjust and rewrite the content per the instructions below, adhering to the desired writing style guidelines. The content should be in HTML format with proper spacing and separate paragraphs for each section (greeting, introduction, closing, etc). Do not include ```html``` in your response.\n
    
    Content: {pitch}\n
    Instructions: {instructions}\n
    Writing Style: {style}
    Additional details {details}
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


OPEN_AI_REWRITE_PTICH = (
    lambda original, bio, name: f"""
    Rewrite the original media pitch incoporating pitching tips from the journalist's bio below. 
    Be sure to maintaining the existing writing style as the original pitch. 
    Include a short intriguing subject line; no more than 3 words. DO NOT BOLD ANY TEXT IN YOUR RESPONSE, EVER!

    Original Pitch: {original}
    Journalist's bio along with pitching tips: {bio}
    Provide journalist's email: Check to see if their email is listed in the journalist bio above. 
    If so, you must use that email. If no email can be found, then you must guess their work email. When guessing, you must base it on verified email patterns associated with their respective publication. 
    Always return the email like this - email: (guessed email)    
    My name: {name}

    OUTPUT JSON:
    body: REWRITTEN PITCH,
    subject: SUBJECT,
    email: EMAIL
    """
)


def OPEN_AI_WEB_SUMMARY(query, results, text, instructions, summary):
    if not instructions:
        prompt = f"""Please provide a concise and accurate response to my query, using the given search results. Cite the most relevant sources by enclosing the index of the search result in square brackets at the end of the corresponding sentence, without a space between the last word and the citation. 
        For example: 'Paris is the capital of France[1].' Only use this format to cite search results. Never cite more than 3 sources in a row. Do not include a references section at the end of your answer. If the search results are insufficient or irrelevant, answer the query to the best of your ability using existing knowledge. 
        Make sure that your response is properly formatted simple html with good spacing and easy to read. No padding on the body since it will be going into a container that already has it.
        
        query: {query}
        search results: {results}
        full text from the top result: {text}
        """
    elif summary:
        prompt = f"""Based on the initial summary and the additional search results, please provide a concise and accurate response to the follow-up question. Use the given search results and the initial summary to ensure the response is comprehensive. Cite the most relevant sources by enclosing the index of the search result in square brackets at the end of the corresponding sentence, without a space between the last word and the citation.
        For example: 'Paris is the capital of France[1].' Only use this format to cite search results. Never cite more than 3 sources in a row. Do not include a references section at the end of your answer. If the search results are insufficient or irrelevant, answer the query to the best of your ability using existing knowledge and the initial summary.
        Make sure that your response is properly formatted simple html with good spacing and easy to read. No padding on the body since it will be going into a container that already has it.
        
        initial summary: {summary}
        follow-up question: {instructions}
        search results: {results}
        """
    else:
        prompt = f"""Please provide a concise and accurate response to my query, using the given search results. Cite the most relevant sources by enclosing the index of the search result in square brackets at the end of the corresponding sentence, without a space between the last word and the citation. 
        For example: 'Paris is the capital of France[1].' Only use this format to cite search results. Never cite more than 3 sources in a row. Do not include a references section at the end of your answer. If the search results are insufficient or irrelevant, answer the query to the best of your ability using existing knowledge. 
        Make sure that your response is properly formatted simple html with good spacing and easy to read. No padding on the body since it will be going into a container that already has it.
        
        query: {instructions}
        search results: {results}
        full text from the top result: {text}
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


# OPEN_AI_TEST_JOURNALIST = (
#     lambda info, journalists, publicastion: f"""
#     Journalists is a dictionary of journalist names as a key and google results as the value based on this Info: {info}.
#     For each journalist tell me their currently employer based on the google results
#     Journalists:
#     {journalists}
# """
# )


def OPEN_AI_GET_JOURNALIST_LIST(info, content):
    initial_sentence = f"List 20 real, active journalists based on this information: {info}"
    if content:
        initial_sentence += f" and would be interested in this pitch: {content}"
    prompt = f"""
    {initial_sentence}.\n
   
    You must follow the instructions below very carefully:
    * Ensure that all journalists are real, currently active writers. 
    * Do not include fake names such as Jane Doe or John Smith or make names up.
    * Output format must a ONLY JSON object:
    {'{'}'journalists': [LIST OF NAMES]{'}'}
    """
    return prompt


def OPEN_AI_PITCH_JOURNALIST_LIST(journalists, pitch):
    initial_sentence = (
        f"From the list of journalists I provided who would be interested in this pitch: {pitch}"
    )
    prompt = f"""
    {initial_sentence}.\n
    * Output format must a ONLY JSON object:
    {'{'}'journalists': [LIST OF NAMES]{'}'}

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
    "x.com",
    ".png",
    ".jpeg",
]

NON_VIABLE_CLASSES = ["menu", "nav"]

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
    "dealcatcher.com",
    "dansdeals.com",
    "superpunch.net",
    "securityaffairs.com",
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
