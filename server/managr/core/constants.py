from django.conf import settings

USE_NYLAS = settings.USE_NYLAS
NYLAS_CLIENT_ID = settings.NYLAS_CLIENT_ID if USE_NYLAS else None
NYLAS_CLIENT_SECRET = settings.NYLAS_CLIENT_SECRET if USE_NYLAS else None
NYLAS_OAUTH_CALLBACK_URL = settings.NYLAS_OAUTH_CALLBACK_URL if USE_NYLAS else None
NYLAS_API_BASE_URL = "https://api.nylas.com"
EMAIL_AUTH_URI = "oauth/authorize"
EMAIL_AUTH_TOKEN_URI = "oauth/token"
EMAIL_AUTH_TOKEN_REVOKE_URI = "oauth/revoke"
EMAIL_ACCOUNT_URI = "account"
SEND_EMAIL_URI = "send"
CALENDAR_URI = "calendars"
EVENT_POST = "events"

STRIPE_API_BASE_URL = "https://api.stripe.com/v1"
STRIPE_CHECKOUT_SESSION = "/checkout/sessions"
STRIPE_SUBSCIPTIONS = "/subscriptions"
STRIPE_HEADERS = {
    "Authorization": f"Bearer {settings.STRIPE_API_KEY}",
    "Content-Type": "application/x-www-form-urlencoded",
}


if settings.USE_OPEN_AI:
    OPEN_AI_SECRET = settings.OPEN_AI_SECRET
    OPEN_AI_HEADERS = {
        "Content-type": "application/json",
        "Authorization": f"Bearer {OPEN_AI_SECRET}",
    }
OPEN_AI_COMPLETIONS_URI = "https://api.openai.com/v1/completions"
OPEN_AI_CHAT_COMPLETIONS_URI = "https://api.openai.com/v1/chat/completions"
OPEN_AI_EDIT_URI = "https://api.openai.com/v1/edits"

OPEN_AI_SUMMARY_PROMPT = (
    lambda object: f"""Summarize the meeting notes below in the most concise way (no less than 1,500 characters and no greater than 2,000 characters) as if you are reporting back to a VP of Sales, tone is casual yet professional.
    Highlight the most important information first like, the deal stage, next step and close date. 
    Also mention what kind of interaction it was - a call, meeting, or just an update. 
    Deliver message in sentence format
    \n Meeting notes:{object}
    """
)
OPEN_AI_UPDATE_PROMPT = (
    lambda labels, prompt, date: f"""Take the meeting note below and use it to update either Salesforce or HubSpot CRM fields below - 
    Some of CRM fields are labeled with the API name, so take that into account. 
    Desired output is a python dictionary, JSON.
    \nAssume CRM field labeled 'name' is always referring to either 'Company Name, 'Deal Name' or 'Opportunity Name' - 
    Do NOT include 'company' 'deal' or 'Opportunity' into the field data\n
    The entire meeting note should be pasted into 'meeting_comments', 
    then update all the relevant fields from the meeting note. Lastly, date format needs to be: year-month-day and use the date below as reference.
    \n Fields:{labels}\n text: {prompt}\n date: {date}"""
)

OPEN_AI_MEETING_EMAIL_DRAFT = (
    lambda crm_data: f"""You are a salesperson who just had a meeting with a prospect or customer. Your job is to now send a follow-up email. You must follow these instructions:
    1) Use the dictionary of crm fields and values below to craft the email.
    2) writing style must be this (unless otherwise specified in the meeting comments):
    A casual and friendly tone, using informal salutations and contractions.
    Concise and to-the-point sentences that focus on the value proposition.
    Frequent paragraph breaks to enhance readability.
    Use of a question. Limit to one question, at the end, a clear call-to-action (no P.S. at the end)
    3) The email cannot be more than 1000 characters.\n
    CRM Data: {crm_data}"""
)

OPEN_AI_NEXT_STEPS = (
    lambda data: f"Provide up to 3 listed out suggested next steps to take in order to close the prospect or move the deal forward based on meeting notes below, ranging from aggressive (close this month) to passive (close in the coming months)\n Meeting Notes: {data}"
)

OPEN_AI_DEAL_REVIEW = (
    lambda data, resource, date, crm: f"""You are my sales manager. I am a sales rep. 
    Imagine we are having a deal review (a weekly event) and your job is to go through my deal (or opportunity) and answer the questions below.
    Today's date is {date}.
    Base your answers around Todays date. Your response should be casual, yet professional.
    Assess each deal using one of the following sales frameworks: BANT, MEDDIC or MEDDPICC. Use a sales framework that aligns with CRM fields below.
    \n1) Highlight what information is missing from this deal based on one of the above sales frameworks.
    \n2) Check for data being up to date, do the following: Make sure the Close Date is not in the past, if so call it out. Do not include Last Activity here
    \n3) Show the Last Activity Date. If it exceeds 30 days from Todays date, then flag it. If its within the past 5 days, then it's a good sign.
    \n4) If they use a next step field then summarize the next step with a maximum character limit of 150 characters. 
    \n5) Write a very short email (300 character limit) for the prospect with the intent to move the deal forward. 
        Use the writing style below when crafting the email: A casual and friendly tone, using informal salutations and contractions. 
        Concise and to-the-point sentences that focus on the value proposition. 
        Use of a question and personal anecdotes to engage the recipient. 
        Limit to one question, asked at the end of the email. 
        Frequent paragraph breaks to enhance readability. 
        Clear call-to-action, suggesting specific dates or offering assistance.
    \nStart the email with Hi or Hey and do not use Best Regards in the sign off.
    \nHere is the format I want:
    \n{resource} Name:
    \n1) Missing Information: list out missing information in sentence format.
    \n2) Needs Updating: show data out of date in sentence format. If nothing is out of date, then say, 'Everything looks up to date'.
    \n3) Last Activity: show last activity date, comment as needed per the above.
    \n4) Next Step: summarize the next step with a maximum character limit of 150 characters. If blank, then say 'There is no next step'. If there is no next step field, then skip this.
    \n5) Suggested Email: write out the email
    \nUse the deal data below to make your assessment, data is coming from either Salesforce or HubSpot CRM. Account for labels being the API name. CRM Data: {data}"""
)

OPEN_AI_TRANSCRIPT_PROMPT = (
    lambda transcript: f"""'input': {transcript},'prompt': 'Analyze and summarize this section of a sales call transcript. 
Keep summary within 500-800 characters, capturing key sales-related details such as: identified pain, value proposition, 
product specifics, decision maker, decision process and criteria, internal champion, competitors, next steps, decision timeline, 
plus any budget and cost details. The summary must be in paragraph form. You must use this format: \nSummary: <summary>'"""
)

OPEN_AI_PR_TRANSCRIPT_SECTIONS_PROMPT = (
    lambda transcript: f"""
'input': {transcript},'prompt': 'You are a VP of PR Summarize key points of the Zoom call. Highlight objectives, challenges, strategies, action items, deadlines, stakeholders, and any miscellaneous notes
Present the summary in a concise and structured manner. You must use this format: \nSummary: <summary>'"""
)

OPEN_AI_TRANSCRIPT_UPDATE_PROMPT = (
    lambda input, crm_fields, user: f"""'input': {input}, 'prompt': 'Consolidate and analyze the provided sales call transcript summaries. The sales rep on this call is {user.first_name} from {user.organization.name}. You must complete the following tasks:
1) Fill in all the relevant data from the transcript into the appropriate CRM fields:\n CRM fields: {crm_fields}\n Leave any non-applicable fields empty, any date must be converted to year-month-day format, and do not include quotes in the values. 
2) Next, you will compose a concise and impactful summary of the sales call, as if you are the salesperson summarizing key takeaways for your team. Maintain relevance and sales-focused nuances. Make sure to Include what the next steps are at the end.
3) The output of fields and summary must be a single Python dictionary. Ensure the summary is included in the Python dictionary as the key summary.'"""
)

OPEN_AI_TRANSCRIPT_PR_PROMPT = (
    lambda input: f"""'input': {input}, 'prompt': 'You are a VP of PR. Consolidate the following summaries from the Zoom call into one comprehensive summary:
Ensure the final summary is structured, concise, and captures the overarching objectives, challenges, strategies, action items, deadlines, stakeholders, and any miscellaneous notes. End the summary with proposed and next steps'"""
)

OPEN_AI_CALL_ANALYSIS_PROMPT = (
    lambda summaries, date: f"""
As an experienced VP of Sales, analyze the call transcript summaries from {date} and provide insights. 
Identify high engagement instances and moments of disinterest. Note any expressed concerns or questions. 
Estimate deal closure probability and predict a closing date, if applicable. Output tone should be direct, concise, and conversational. 
Do not reference the summaries in the output. Structure your output as follows:\n
High Engagement:\n
Disinterest:\n
Questions or Concerns:\n
Sentiment:\n
Likelihood to Close:\n
Expected Closing Date:\n
Summaries: {summaries}"""
)

OPEN_AI_EMAIL_DRAFT_WITH_INSTRUCTIONS = (
    lambda email, instructions: f"""
Below is an AI generated email. Adjust and rewrite the email per instructions below:\n
Email: {email}\n
Instructions: {instructions}"""
)

OPEN_AI_ASK_MANAGR_WITH_INSTRUCTIONS = (
    lambda text, instructions, crm_data: f"""
Below is an AI generated response. Adjust and rewrite the response per instructions below, using the provided CRM data:\n
Response: {text}\n
CRM Data\n
Instructions: {instructions}"""
)


def OPEN_AI_COMPLETIONS_BODY(user_name, prompt, token_amount=500, temperature=False, top_p=False):
    body = {
        "model": "text-davinci-003",
        "prompt": prompt,
        "user": user_name,
    }
    if token_amount:
        body["max_tokens"] = token_amount
    if temperature:
        body["temperature"] = temperature
    if top_p:
        body["top_p"] = top_p
    return body


def OPEN_AI_CHAT_COMPLETIONS_BODY(
    user_name,
    prompt,
    system_role=False,
    token_amount=2000,
    temperature=False,
    top_p=False,
    model="gpt-4o",
):
    body = {
        "model": model,
        "messages": [
            {"role": "user", "content": prompt},
        ],
        "user": user_name,
    }
    if system_role:
        first_message = [{"role": "system", "content": system_role}]
        first_message.extend(body["messages"])
        body["messages"] = first_message
    if token_amount:
        body["max_tokens"] = token_amount
    if temperature:
        body["temperature"] = temperature
    if top_p:
        body["top_p"] = top_p
    return body


def OPEN_AI_EDIT_BODY(user_name, input, instructions, data, temperature=False, top_p=False):
    # instructions += f"use this data as context: {data}"
    body = {
        "model": "text-davinci-edit-001",
        "input": input,
        "instruction": instructions,
        "user": user_name,
    }
    if temperature:
        body["temperature"] = temperature
    if top_p:
        body["top_p"] = top_p
    return body


def OPEN_AI_ASK_MANAGR_PROMPT(user, date, prompt, data):
    body = f"""Today's date is {date}. Respond to {user.first_name}’s request using relevant CRM data provided.
\nCRM_data: {data}
\nRequest: {prompt}\n
Your response should be casual yet assertive, echoing the style of an experienced sales leader. 
The tone should be friendly and focused on value with succinct sentences. Output must be a regular message, not an email, unless specified. 
Limit your response to under 1,000 characters.
"""
    return body


OPEN_AI_NEWS_BOOLEAN_CONVERSION = (
    # lambda search: f"""Convert the Search Term below into a boolean query to be used for News API.
    # Follow these steps in order to create the best possible search:
    # 1: Concentrate on the primary keywords or key concepts of the search term. Example: 'Articles written or about Lululemon' should just be 'Lululemon'. Example 2: 'Apple, exclude stock related news' shoud be "apple" NOT (stock or Nasdaq or shares...).
    # 2: Do not make it a title search unless specifically instructed via the prompt.
    # 3: Do not use acronyms in your search unless specifically asked to.
    # 4: If the search term is a broad category such as "sports", ensure you include or exclude relevant subtopics (e.g., "football", "baseball", "basketball", "coaches", etc.), based on the nature of the query.
    # 5: Use logical operators judiciously to balance specificity and breadth. Employ 'AND' to combine terms that are closely related or typically reported together, ensuring relevance. Opt for 'OR' when connecting terms that are less frequently associated or when one term has a low probability of appearing in news contexts. This approach broadens the search scope while maintaining focus on the primary subject.
    # Search Term: {search}"""
    lambda search: f"""Convert the term below into a boolean query to be used for News API.
    term: {search}
    output must only be the boolean string.
    """
)

OPEN_AI_TRANSCRIPT_GENERATE_CONTENT = (
    lambda date, summary, instructions: f"""Today's date is {date}.
    Here is call summary {summary} from {date}. Generate content based on these instructions {instructions}."""
)

OPEN_AI_CONVERT_HTML = (
    lambda summary, clips: f"""
    Convert this html summary to markdown to use in Slack. The bolding and header format should only be one asterisk on each side of the text.
    For the citations, replace them with a slack hyperlink using the URL of the clip at the same index in the square brackets. Example: <URL|[INDEX]>.
    
    Summary:
    {summary}

    Clips:
    {clips}
    """
)


# OAuth permission scopes to request from Nylas
SCOPE_CALENDAR = "calendar"
# SCOPE_EMAIL = "email"

ALL_SCOPES = [
    SCOPE_CALENDAR,
    # SCOPE_EMAIL,
]
ALL_SCOPES_STR = ", ".join(ALL_SCOPES)


def EMAIL_REVOKE_ALL_TOKENS_URI(account_id):
    return f"a/{NYLAS_CLIENT_ID}/accounts/{account_id}/revoke-all/"


ACCOUNT_TYPE_MANAGER = "MANAGER"
ACCOUNT_TYPE_REP = "REP"

USER_LEVEL_MANAGER = "MANAGER"
USER_LEVEL_REP = "REP"
USER_LEVEL_SDR = "SDR"

USER_LEVELS = (
    (USER_LEVEL_MANAGER, "Manager"),
    (USER_LEVEL_REP, "Rep"),
    (USER_LEVEL_SDR, "SDR"),
)

CRM_SALESFORCE = "SALESFORCE"
CRM_HUBSPOT = "HUBSPOT"

CRM_CHOICES = ((CRM_SALESFORCE, "Salesforce"), (CRM_HUBSPOT, "Hubspot"))
NOTE_TYPE_STANDARD = "STANDARD"
NOTE_TYPE_CHAT = "CHAT"
NOTE_TYPES = ((NOTE_TYPE_STANDARD, "Standard"), (NOTE_TYPE_CHAT, "Chat"))
ACCOUNT_TYPES = (
    (ACCOUNT_TYPE_MANAGER, "MANAGER"),
    (ACCOUNT_TYPE_REP, "REP"),
)

STATE_ACTIVE = "ACTIVE"
STATE_INACTIVE = "INACTIVE"
STATE_INVITED = "INVITED"
STATE_CHOCIES = (
    (STATE_ACTIVE, "Active"),
    (STATE_INACTIVE, "Inactive"),
    (STATE_INVITED, "Invited"),
)


NYLAS_SYNC_STATUS_STOPPED = "stopped"
NYLAS_SYNC_STATUS_INVALID = "invalid"
NYLAS_SYNC_STATUS_SYNC_ERROR = "sync_error"
NYLAS_SYNC_STATUSES_FAILING = (
    NYLAS_SYNC_STATUS_STOPPED,
    NYLAS_SYNC_STATUS_INVALID,
    NYLAS_SYNC_STATUS_SYNC_ERROR,
)

NOTIFICATION_CLASS_ALERT = "ALERT"
NOTIFICATION_CLASS_EMAIL = "EMAIL"
NOTIFICATION_CLASS_SLACK = "SLACK"
NOTIFICATION_CLASS_CHOICES = (
    (
        NOTIFICATION_CLASS_ALERT,
        "ALERT",
    ),
    (
        NOTIFICATION_CLASS_EMAIL,
        "EMAIL",
    ),
    (
        NOTIFICATION_CLASS_SLACK,
        "SLACK",
    ),
)

NOTIFICATION_RESOURCE_ACCOUNT = "ACCOUNT"
NOTIFICATION_RESOURCE_ORGANIZATION = "ORGANIZATION"

NOTIFICATION_RESOURCE_REPORT = "REPORT"
NOTIFICATION_RESOURCE_OPPORTUNITY = "OPPORTUNITY"
NOTIFICATION_RESOURCE_USER = "USER"
NOTIFICATION_RESOURCES = (
    (
        NOTIFICATION_RESOURCE_ACCOUNT,
        "Account",
    ),
    (NOTIFICATION_RESOURCE_ORGANIZATION, "Organization"),
    (NOTIFICATION_RESOURCE_REPORT, "Report"),
    (NOTIFICATION_RESOURCE_OPPORTUNITY, "Opportunity"),
)

NOTIFICATION_OPTION_KEY_OPPORTUNITY_EMAIL_RECEIVED = "OPPORTUNITY_EMAIL_RECEIVED"
NOTIFICATION_OPTION_KEY_ORGANIZATION_STAGES = "ORGANIZATION_STAGES_UPDATE"
NOTIFICATION_OPTION_KEY_REPORT_GENERATED = "REPORT_GENERATED"
NOTIFICATION_OPTION_KEY_USER_UPDATE = "USER_UPDATE"
NOTIFICATION_OPTION_KEY_OPPORTUNITY_TEXT_RECEIVED = "OPPORTUNITY_TEXT_RECEIVED"
NOTIFICATION_OPTION_KEY_OPPORTUNITY_REMINDER = "OPPORTUNITY_REMINDER"
NOTIFICATION_OPTION_KEY_OPPORTUNITY_STALLED_IN_STAGE = "OPPORTUNITY_STALLED_IN_STAGE"
NOTIFICATION_OPTION_KEY_OPPORTUNITY_INACTIVE_90_DAYS = "OPPORTUNITY_INACTIVE_90_DAYS"
NOTIFICATION_OPTION_KEY_OPPORTUNITY_LAPSED_EXPECTED_CLOSE_DATE_1_DAY = (
    "OPPORTUNITY_LAPSED_CLOSE_DATE_1_DAY"
)
NOTIFICATION_OPTION_KEY_OPPORTUNITY_LAPSED_EXPECTED_CLOSE_DATE_14_DAYS = (
    "OPPORTUNITY_LAPSED_CLOSE_DATE_14_DAYS"
)
NOTIFICATION_OPTION_KEY_OPPORTUNITY_LAPSED_EXPECTED_CLOSE_DATE_30_DAYS = (
    "OPPORTUNITY_LAPSED_CLOSE_DATE_30_DAYS"
)
NOTIFICATION_OPTION_KEY_OPPORTUNITY_EMAIL_RECEIVED_ID = "004c41a0-11c2-4b33-bcec-4e10518d2fa3"


#### constants for testing grabbing id's from fixtures
NOTIFICATION_OPTION_STALLED_IN_STAGE_ID = "f9cc3934-f82b-442f-9d63-73de73d5d115"
NOTIFICATION_OPTION_INACTIVE_ID = "845c1d76-8743-4695-b6cf-9af7b0aaab14"
NOTIFICATION_OPTION_LAPSED_1_DAY_ID = "5d19b999-c0bf-429a-a8f5-17b9bc2efdc6"
NOTIFICATION_OPTION_LAPSED_14_DAYS_ID = "2bcddc82-305b-42a8-a295-99b76f418aac"
NOTIFICATION_OPTION_LAPSED_30_DAYS_ID = "0285c84d-10c5-41d8-8a97-d944cc373ad6"
NOTIFICATION_OPTION_STAGE_UPDATE_ID = "0e0a1e9d-f806-4807-8d09-58e90346edff"


NOTIFICATION_TYPE_REMINDER = "REMINDER"
NOTIFICATION_TYPE_EMAIL = "EMAIL"
NOTIFICATION_TYPE_SYSTEM = "SYSTEM"
NOTIFICATION_TYPE_OPPORTUNITY_STALLED_IN_STAGE = "OPPORTUNITY.STALLED_IN_STAGE"
NOTIFICATION_TYPE_OPPORTUNITY_LAPSED_EXPECTED_CLOSE_DATE_1 = (
    "OPPORTUNITY.LAPSED_EXPECTED_CLOSE_DATE_1"
)
NOTIFICATION_TYPE_OPPORTUNITY_LAPSED_EXPECTED_CLOSE_DATE_14 = (
    "OPPORTUNITY.LAPSED_EXPECTED_CLOSE_DATE_14"
)
NOTIFICATION_TYPE_OPPORTUNITY_LAPSED_EXPECTED_CLOSE_DATE_30 = (
    "OPPORTUNITY.LAPSED_EXPECTED_CLOSE_DATE_30"
)
NOTIFICATION_TYPE_OPPORTUNITY_INACTIVE = "OPPORTUNITY.INACTIVE"
NOTIFICATION_TYPE_EMAIL_OPENED = "EMAIL_OPENED"
NOTIFICATION_TYPE_CHOICES = (
    (NOTIFICATION_TYPE_REMINDER, "Reminder"),
    (NOTIFICATION_TYPE_EMAIL, "Email"),
    (NOTIFICATION_TYPE_SYSTEM, "System"),
    (NOTIFICATION_TYPE_EMAIL_OPENED, "Email Opened"),
    (NOTIFICATION_TYPE_OPPORTUNITY_INACTIVE, "Opportunity Inactive"),
    (NOTIFICATION_TYPE_OPPORTUNITY_STALLED_IN_STAGE, "Opportunity Stalled in Stage"),
    (
        NOTIFICATION_TYPE_OPPORTUNITY_LAPSED_EXPECTED_CLOSE_DATE_1,
        "Opportunity Lapsed Expected Close Date By 1 day or more",
    ),
    (
        NOTIFICATION_TYPE_OPPORTUNITY_LAPSED_EXPECTED_CLOSE_DATE_14,
        "Opportunity Lapsed Expected Close Date By 14 days or more",
    ),
    (
        NOTIFICATION_TYPE_OPPORTUNITY_LAPSED_EXPECTED_CLOSE_DATE_30,
        "Opportunity Lapsed Expected Close Date By 30 days or more",
    ),
)


NOTIFICATION_ACTION_SNOOZE = "SNOOZE"
NOTIFICATION_ACTION_VIEWED = "VIEWED"
NOTIFICATION_ACTION_CHOICES = (
    (NOTIFICATION_ACTION_SNOOZE, "Snooze"),
    (NOTIFICATION_ACTION_VIEWED, "Viewed"),
)

WORKFLOW_REMINDER = "WORKFLOW_REMINDER"
REMINDER_MESSAGE_REP = "REMINDER_MESSAGE_REP"
REMINDER_MESSAGE_MANAGER = "REMINDER_MESSAGE_MANAGER"
CALENDAR_REMINDER = "CALENDAR_REMINDER"
NON_ZOOM_MEETINGS = "NON_ZOOM_MEETINGS"
CALENDAR_CHECK = "CALENDAR_CHECK"
WORKFLOW_CONFIG_CHECK = "WORKFLOW_CONFIG_CHECK"
MORNING_REFRESH = "MORNING_REFRESH"
MEETING_REMINDER = "MEETING_REMINDER"
TRIAL_STATUS = "TRIAL_STATUS"
STRIPE_CHECKOUT_WEBHOOK = "checkout.session"
# These times should be a half hour before the intended time
REMINDER_CONFIG = {
    WORKFLOW_REMINDER: {"HOUR": 7, "MINUTE": 00},
    REMINDER_MESSAGE_REP: {"HOUR": 17, "MINUTE": 30},
    REMINDER_MESSAGE_MANAGER: {"HOUR": 18, "MINUTE": 00},
}

TIMEZONE_TASK_TIMES = {
    NON_ZOOM_MEETINGS: {"HOUR": 7, "MINUTE": 30},
    CALENDAR_CHECK: {"HOUR": 5, "MINUTE": 30},
    MEETING_REMINDER: {"HOUR": 17, "MINUTE": 30},
}


def REMINDERS():
    return {
        WORKFLOW_REMINDER: True,
        REMINDER_MESSAGE_REP: True,
        REMINDER_MESSAGE_MANAGER: True,
    }


GOOGLE_AUTHORIZATION_URI = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_AUTHENTICATION_URI = "https://oauth2.googleapis.com/token"
GOOGLE_SEND_EMAIL_URI = (
    lambda user_id: f"https://gmail.googleapis.com/gmail/v1/users/{user_id}/messages/send"
)

GOOGLE_CLIENT_ID = settings.GOOGLE_CLIENT_ID
GOOGLE_CLIENT_SECRET = settings.GOOGLE_CLIENT_SECRET
GOOGLE_REDIRECT_URI = settings.GOOGLE_REDIRECT_URI
GOOGLE_SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/gmail.send",
]


def GOOGLE_PARAMS():
    return {
        "response_type": "code",
        "state": "GOOGLE",
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "client_id": GOOGLE_CLIENT_ID,
        "access_type": "offline",
        "prompt": "consent",
    }


if settings.IN_DEV:
    GOOGLE_FRONTEND_REDIRECT = "http://localhost:8080/pr-integrations"
    TRACKING_PIXEL_LINK = "https://managr-zach.ngrok.io/api/users/google/email-tracking"
    MICROSOFT_FRONTEND_REDIRECT = "http://localhost:8080/pr-integrations"
elif settings.IN_STAGING:
    GOOGLE_FRONTEND_REDIRECT = "https://staging.managr.ai/pr-integrations"
    TRACKING_PIXEL_LINK = "https://staging.managr.ai/api/users/google/email-tracking"
    MICROSOFT_FRONTEND_REDIRECT = "https://staging.managr.ai/pr-integrations"
else:
    GOOGLE_FRONTEND_REDIRECT = "https://app.managr.ai/pr-integrations"
    TRACKING_PIXEL_LINK = "https://app.managr.ai/api/users/google/email-tracking"
    MICROSOFT_FRONTEND_REDIRECT = "https://app.managr.ai/pr-integrations"


def GOOGLE_HEADERS(access_token):
    return {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}


MICROSOFT_CLIENT_ID = settings.MICROSOFT_CLIENT_ID
MICROSOFT_CLIENT_SECRET = settings.MICROSOFT_CLIENT_SECRET
MICROSOFT_REDIRECT_URI = settings.MICROSOFT_REDIRECT_URI
MICROSOFT_AUTHORIZATION_URI = "https://login.microsoftonline.com/common/oauth2/v2.0/authorize"
MICROSOFT_AUTHENTICATION_URI = "https://login.microsoftonline.com/common/oauth2/v2.0/token"
MICROSOFT_SEND_MAIL = "https://graph.microsoft.com/v1.0/me/sendMail"
MICROSOFT_SCOPES = [
    "Mail.Send",
    "offline_access",
    "openid",
    "profile",
    "User.Read",
]


def MICROSOFT_AUTHORIZATION_PARAMS():
    return {
        "client_id": MICROSOFT_CLIENT_ID,
        "response_type": "code",
        "redirect_uri": MICROSOFT_REDIRECT_URI,
        "response_mode": "query",
        "prompt": "login",
    }


def MICROSOFT_AUTHENTICATE_PARAMS(code):
    return {
        "grant_type": "authorization_code",
        "redirect_uri": MICROSOFT_REDIRECT_URI,
        "client_secret": MICROSOFT_CLIENT_SECRET,
        "code": code,
        "client_id": MICROSOFT_CLIENT_ID,
    }


def MICROSOFT_REFRESH_PARAMS(refresh_token):
    return {
        "grant_type": "refresh_token",
        "redirect_uri": MICROSOFT_REDIRECT_URI,
        "client_secret": MICROSOFT_CLIENT_SECRET,
        "refresh_token": refresh_token,
        "client_id": MICROSOFT_CLIENT_ID,
    }


def MICROSOFT_HEADERS(access_token):
    return {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
