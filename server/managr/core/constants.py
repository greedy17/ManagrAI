from django.conf import settings

from managr.utils.misc import get_site_url


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

if settings.USE_OPEN_AI:
    OPEN_AI_SECRET = settings.OPEN_AI_SECRET
    OPEN_AI_HEADERS = {
        "Content-type": "application/json",
        "Authorization": f"Bearer {OPEN_AI_SECRET}",
    }
OPEN_AI_COMPLETIONS_URI = "https://api.openai.com/v1/completions"

OPEN_AI_SUMMARY_PROMPT = (
    lambda object: f"""Summarize the meetings notes below in the most concise way (300 characters max) as if you are reporting back to a VP of Sales, tone is casual yet professional.
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
    lambda meeting_comments: f"""You are a salesperson who just had a meeting with a prospect or customer. Your job is to now send a follow-up email. You must follow these instructions:
    1) The email must include the desired command outlined "in the follow up email". This request supersedes any other instruction. Use the data from the meeting_comments to craft the email.
    2) writing style must be this (unless otherwise specified in the meeting comments):
    A casual and friendly tone, using informal salutations and contractions.
    Concise and to-the-point sentences that focus on the value proposition.
    Frequent paragraph breaks to enhance readability.
    Use of a question. Limit to one question, at the end, a clear call-to-action (no P.S. at the end)
    3) The email cannot be more than 1000 characters.
    Meeting Notes: {meeting_comments}"""
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
    lambda transcript: f"""You are a VP of Sales reviewing a sales rep's call via transcript. These transcripts are typically between 20-60 minutes long. Below is just a 5 minute section of the call transcript. Follow these instructions carefully:
1) Summarize this section in paragraph form. The summary needs to be 500 to 800 characters.
2) The summary must include the following (if discussed): customer pain, observations, objections, objection handling, competitors mentioned, timeline, decision process and next steps. The tone of the summary needs to be casual, conversational, and slightly witty.
3) Desired format:\n Summary: <summary>\n
    Transcript: {transcript}
    """
)

OPEN_AI_TRANSCRIPT_UPDATE_PROMPT = (
    lambda fields, summaries: f"""Below are short summaries, summarizing parts of a sales call transcript. These summaries are in chronological order. Put these summaries together, and follow the instructions below:
1) You are VP of Sales. Create one summary, in paragraph of how this call went. Include relevant data regarding: customer pain, customer objections, objection handling by salesperson, competitors mentioned, timeline to close, decision process, the next steps and overall tone of the meeting.
2) The summary must be no less than 1,500 characters and no greater than 2,000 characters.
3) Write the summary using casual, engaging, conversational, and slightly witty tone.
4) Based on the summary, update the CRM fields below. For field "meeting_comments" fill in a very short casual version of the summary. Fill in the remaining CRM fields based on information from the summary.\n
5) The output must be a python dictionary. The summary must be added to the dictionary using a key called 'summary'.\n
    CRM fields:{fields}\nSummaries: {summaries}"""
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


# OAuth permission scopes to request from Nylas
SCOPE_EMAIL_CALENDAR = "calendar"


ALL_SCOPES = [SCOPE_EMAIL_CALENDAR]
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
    (NOTIFICATION_CLASS_ALERT, "ALERT",),
    (NOTIFICATION_CLASS_EMAIL, "EMAIL",),
    (NOTIFICATION_CLASS_SLACK, "SLACK",),
)


NOTIFICATION_RESOURCE_ACCOUNT = "ACCOUNT"
NOTIFICATION_RESOURCE_ORGANIZATION = "ORGANIZATION"

NOTIFICATION_RESOURCE_REPORT = "REPORT"
NOTIFICATION_RESOURCE_OPPORTUNITY = "OPPORTUNITY"
NOTIFICATION_RESOURCE_USER = "USER"
NOTIFICATION_RESOURCES = (
    (NOTIFICATION_RESOURCE_ACCOUNT, "Account",),
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
MORNING_DIGEST = "MORNING_DIGEST"
NON_ZOOM_MEETINGS = "NON_ZOOM_MEETINGS"
CALENDAR_CHECK = "CALENDAR_CHECK"
WORKFLOW_CONFIG_CHECK = "WORKFLOW_CONFIG_CHECK"
MORNING_REFRESH = "MORNING_REFRESH"
MEETING_REMINDER = "MEETING_REMINDER"
TRIAL_STATUS = "TRIAL_STATUS"
# These times should be a half hour before the intended time
REMINDER_CONFIG = {
    WORKFLOW_REMINDER: {"HOUR": 7, "MINUTE": 00},
    MORNING_DIGEST: {"HOUR": 7, "MINUTE": 30},
    REMINDER_MESSAGE_REP: {"HOUR": 17, "MINUTE": 30},
    REMINDER_MESSAGE_MANAGER: {"HOUR": 18, "MINUTE": 00},
}

TIMEZONE_TASK_TIMES = {
    NON_ZOOM_MEETINGS: {"HOUR": 7, "MINUTE": 30},
    CALENDAR_CHECK: {"HOUR": 5, "MINUTE": 30},
    MEETING_REMINDER: {"HOUR": 17, "MINUTE": 30},
    TRIAL_STATUS: {"HOUR": 5, "MINUTE": 30},
}


def REMINDERS():
    return {
        WORKFLOW_REMINDER: True,
        MORNING_DIGEST: False,
        REMINDER_MESSAGE_REP: True,
        REMINDER_MESSAGE_MANAGER: True,
    }

