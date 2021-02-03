import json
import pdb
import logging

from managr.organization.models import Organization, Stage
from managr.opportunity.models import Opportunity, OpportunityScore
from managr.zoom.models import ZoomMeeting
from managr.slack import constants as slack_const
from managr.opportunity import constants as opp_consts
from managr.slack.helpers import requests as slack_requests
from managr.slack.helpers.utils import process_action_id, NO_OP, processor
from managr.slack.helpers.block_sets import get_block_set
from managr.slack.helpers import block_builders


logger = logging.getLogger("managr")


@processor(required_context=["o", "u", "opp", "sentiment"])
def process_meeting_sentiment(payload, context):
    url = slack_const.SLACK_API_ROOT + slack_const.VIEWS_OPEN
    trigger_id = payload["trigger_id"]
    access_token = (
        Organization.objects.select_related("slack_integration")
        .get(pk=context["o"])
        .slack_integration.access_token
    )
    private_metadata = {
        "original_message_channel": payload["channel"]["id"],
        "original_message_timestamp": payload["message"]["ts"],
    }

    private_metadata.update(context)
    data = {
        "trigger_id": trigger_id,
        "view": {
            "type": "modal",
            "callback_id": slack_const.ZOOM_MEETING__PROCESS_MEETING_SENTIMENT,
            "title": {"type": "plain_text", "text": "Log Meeting"},
            "blocks": get_block_set("zoom_meeting_complete_form", context=context),
            "submit": {"type": "plain_text", "text": "Submit"},
            "private_metadata": json.dumps(private_metadata),
        },
    }
    res = slack_requests.generic_request(url, data, access_token=access_token)


@processor(required_context=["o", "u", "opp", "m"])
def process_zoom_meeting_different_opportunity(payload, context):
    url = slack_const.SLACK_API_ROOT + slack_const.VIEWS_OPEN
    trigger_id = payload["trigger_id"]
    access_token = (
        Organization.objects.select_related("slack_integration")
        .get(pk=context["o"])
        .slack_integration.access_token
    )

    private_metadata = {
        "original_message_channel": payload["channel"]["id"],
        "original_message_timestamp": payload["message"]["ts"],
    }
    private_metadata.update(context)

    data = {
        "trigger_id": trigger_id,
        "view": {
            "type": "modal",
            "callback_id": slack_const.ZOOM_MEETING__DIFFERENT_OPPORTUNITY,
            "title": {"type": "plain_text", "text": "Change Opportunity"},
            "blocks": get_block_set("select_different_opportunity", context=context),
            "submit": {"type": "plain_text", "text": "Submit"},
            "private_metadata": json.dumps(private_metadata),
        },
    }
    slack_requests.generic_request(url, data, access_token=access_token)


@processor(required_context=["r"])
def process_get_contacts(payload, context):
    url = slack_const.SLACK_API_ROOT + slack_const.VIEWS_OPEN
    trigger_id = payload["trigger_id"]
    reminder = Reminder.objects.filter(id=context.get("r")).first()
    org = reminder.created_by.organization
    access_token = org.slack_integration.access_token
    blocks = [
        get_block_set("reminder_contact_block_set", {"contact": contact})
        for contact in reminder.linked_contacts.all()
    ]
    private_metadata = {
        "original_message_channel": payload["channel"]["id"],
        "original_message_timestamp": payload["message"]["ts"],
    }
    empty_block = [{"type": "section", "text": {"type": "mrkdwn", "text": "No Contacts Attached"},}]

    data = {
        "trigger_id": trigger_id,
        "view": {
            "type": "modal",
            "callback_id": slack_const.SHOW_REMINDER_CONTACTS,
            "title": {"type": "plain_text", "text": "Contacts"},
            "blocks": blocks if len(blocks) else empty_block,
            "private_metadata": json.dumps(private_metadata),
        },
    }

    private_metadata.update(context)

    slack_requests.generic_request(url, data, access_token=access_token)


@processor(required_context=["l"])
def process_get_lead_contacts(payload, context):
    url = slack_const.SLACK_API_ROOT + slack_const.VIEWS_OPEN
    trigger_id = payload["trigger_id"]
    lead = Lead.objects.filter(id=context.get("l")).first()
    org = lead.claimed_by.organization
    access_token = org.slack_integration.access_token
    blocks = [
        get_block_set("reminder_contact_block_set", {"contact": contact})
        for contact in lead.linked_contacts.all()
    ]
    private_metadata = {
        "original_message_channel": payload["channel"]["id"],
        "original_message_timestamp": payload["message"]["ts"],
    }
    empty_block = [{"type": "section", "text": {"type": "mrkdwn", "text": "No Contacts Attached"},}]

    data = {
        "trigger_id": trigger_id,
        "view": {
            "type": "modal",
            "callback_id": slack_const.SHOW_LEAD_CONTACTS,
            "title": {"type": "plain_text", "text": "Contacts"},
            "blocks": blocks if len(blocks) else empty_block,
            "private_metadata": json.dumps(private_metadata),
        },
    }

    private_metadata.update(context)

    slack_requests.generic_request(url, data, access_token=access_token)


@processor(required_context=["l"])
def process_get_lead_logs(payload, context):
    url = slack_const.SLACK_API_ROOT + slack_const.VIEWS_OPEN
    trigger_id = payload["trigger_id"]
    lead = Lead.objects.filter(id=context.get("l")).first()
    org = lead.claimed_by.organization
    access_token = org.slack_integration.access_token
    blocks = [
        get_block_set("show_lead_logs", {"activity": activity})
        for activity in lead.activity_logs.all()
    ]
    private_metadata = {
        "original_message_channel": payload["channel"]["id"],
        "original_message_timestamp": payload["message"]["ts"],
    }
    empty_block = [{"type": "section", "text": {"type": "mrkdwn", "text": "No Logs to show"},}]

    data = {
        "trigger_id": trigger_id,
        "view": {
            "type": "modal",
            "callback_id": slack_const.SHOW_LEAD_LOGS,
            "title": {"type": "plain_text", "text": "Logs"},
            "blocks": blocks if len(blocks) else empty_block,
            "private_metadata": json.dumps(private_metadata),
        },
    }

    private_metadata.update(context)

    slack_requests.generic_request(url, data, access_token=access_token)


@processor(required_context=["m"])
def process_show_meeting_contacts(payload, context):
    url = slack_const.SLACK_API_ROOT + slack_const.VIEWS_OPEN
    trigger_id = payload["trigger_id"]
    # view_id = payload["view"]["id"]
    meeting = ZoomMeeting.objects.filter(id=context.get("m")).first()
    org = meeting.zoom_account.user.organization

    access_token = org.slack_integration.access_token
    blocks = get_block_set("show_meeting_contacts", context,)

    data = {
        "trigger_id": trigger_id,
        # "view_id": view_id,
        "view": {
            "type": "modal",
            "callback_id": slack_const.ZOOM_MEETING__VIEW_MEETING_CONTACTS,
            "title": {"type": "plain_text", "text": "Contacts"},
            # "submit": {"type": "plain_text", "text": "Submit"},
            "blocks": blocks,
            # "private_metadata": json.dumps(private_metadata),
        },
    }

    # private_metadata.update(context)

    res = slack_requests.generic_request(url, data, access_token=access_token)


@processor(required_context=["m"])
def process_get_meeting_score_components(payload, context):
    try:
        url = slack_const.SLACK_API_ROOT + slack_const.VIEWS_OPEN
        trigger_id = payload["trigger_id"]
        meeting = ZoomMeeting.objects.filter(id=context.get("m")).first()
        org = meeting.zoom_account.user.organization
        access_token = org.slack_integration.access_token

        # order as per mike

        # new line
        # stage
        # forecast
        # close date
        # new line
        # attendees
        # new line
        # duration
        sentiment = ""
        stage = ""
        forecast = ""
        close_date = ""
        attendance = ""
        duration = ""

        for comp in meeting.meeting_score_components:
            if comp["type"] == "sentiment":
                sentiment = comp.get("message", "N/A")
            if comp["type"] == "stage":
                stage = comp.get("message", "N/A")
            if comp["type"] == "forecast_category":
                forecast = comp.get("message", "N/A")
            if comp["type"] == "close_date":
                close_date = comp.get("message", "N/A")
            if comp["type"] == "attendance":
                attendance = comp.get("message", "N/A")
            if comp["type"] == "duration":
                duration = comp.get("message", "N/A")

        paragraph = f"{sentiment} \n {stage} {forecast} {close_date} \n {attendance} {duration}"

        private_metadata = {
            "original_message_channel": payload["channel"]["id"],
            "original_message_timestamp": payload["message"]["ts"],
        }
        empty_block = [
            {"type": "section", "text": {"type": "mrkdwn", "text": "No Scoring Data to show"},}
        ]
        blocks = [get_block_set("show_meeting_score_description", {"score_paragraph": paragraph})]

        data = {
            "trigger_id": trigger_id,
            "view": {
                "type": "modal",
                "callback_id": slack_const.SHOW_MEETING_SCORE_COMPONENTS,
                "title": {"type": "plain_text", "text": "Summary"},
                "blocks": blocks if len(blocks) else empty_block,
                "private_metadata": json.dumps(private_metadata),
            },
        }

        private_metadata.update(context)

        slack_requests.generic_request(url, data, access_token=access_token)
    except Exception as e:
        logger.warning(e)
        pass


@processor(required_context=["ls"])
def process_get_lead_score_components(payload, context):
    url = slack_const.SLACK_API_ROOT + slack_const.VIEWS_OPEN
    trigger_id = payload["trigger_id"]
    lead_score = LeadScore.objects.select_related("lead").filter(id=context.get("ls")).first()
    lead = lead_score.lead

    org = lead.claimed_by.organization
    access_token = org.slack_integration.access_token
    lead_score_components = [
        {
            "label": "Action Score",
            "score": lead_score.actions_score,
            "insight": lead_score.actions_insight,
        },
        {
            "label": "Incoming Messages Score",
            "score": lead_score.incoming_messages_score,
            "insight": lead_score.incoming_messages_insight,
        },
        {
            "label": "Days In Stage Score",
            "score": lead_score.days_in_stage_score,
            "insight": lead_score.days_in_stage_insight,
        },
        {
            "label": "Forecast Score",
            "score": lead_score.forecast_table_score,
            "insight": lead_score.forecast_table_insight,
        },
        {
            "label": "Expected Close Date Score",
            "score": lead_score.expected_close_date_score,
            "insight": lead_score.expected_close_date_insight,
        },
    ]
    blocks = [
        get_block_set("show_lead_score_description", {"score_components": comp})
        for comp in lead_score_components
    ]
    private_metadata = {
        "original_message_channel": payload["channel"]["id"],
        "original_message_timestamp": payload["message"]["ts"],
    }
    empty_block = [{"type": "section", "text": {"type": "mrkdwn", "text": "No Logs to show"},}]

    data = {
        "trigger_id": trigger_id,
        "view": {
            "type": "modal",
            "callback_id": slack_const.SHOW_LEAD_SCORE_COMPONENTS,
            "title": {"type": "plain_text", "text": "Score Components"},
            "blocks": blocks if len(blocks) else empty_block,
            "private_metadata": json.dumps(private_metadata),
        },
    }

    private_metadata.update(context)

    slack_requests.generic_request(url, data, access_token=access_token)


@processor(required_context=["m", "contact_index"])
def process_edit_meeting_contact(payload, context):
    url = slack_const.SLACK_API_ROOT + slack_const.VIEWS_OPEN
    trigger_id = payload["trigger_id"]
    meeting = ZoomMeeting.objects.filter(id=context.get("m")).first()
    contact = meeting.participants[int(context.get("contact_index"))]

    org = meeting.zoom_account.user.organization

    access_token = org.slack_integration.access_token

    salesforce_account = meeting.zoom_account.user.salesforce_account

    blocks = get_block_set("edit_meeting_contacts", {"meeting": meeting, "contact": contact},)

    data = {
        "trigger_id": trigger_id,
        "view": {
            "type": "modal",
            "callback_id": slack_const.ZOOM_MEETING__EDIT_MEETING_CONTACT,
            "title": {"type": "plain_text", "text": "Edit Contact"},
            "blocks": blocks,
        },
    }

    res = slack_requests.generic_request(url, data, access_token=access_token)


@processor(required_context=["o"])
def process_update_forecast_category_option(payload, context):
    url = slack_const.SLACK_API_ROOT + slack_const.VIEWS_UPDATE
    org = Organization.objects.get(id=context["o"])
    access_token = org.slack_integration.access_token
    trigger_id = payload["trigger_id"]
    view_id = payload["view"]["id"]
    # check actions for specific select action
    select_action = list(filter(lambda x: x["block_id"] == "stage", payload["actions"]))
    if select_action:
        blocks = payload["view"]["blocks"]
        selected_value = select_action[0]["selected_option"]["value"]
        forecast_block = list(
            filter(
                lambda x: x[1]["block_id"] == "forecast_category",
                enumerate(payload["view"]["blocks"]),
            )
        )[0]
        # grab the suggested block message if it exists and remove it
        suggestion_block = list(
            filter(
                lambda x: x[1]["block_id"] == "forecast_suggestion",
                enumerate(payload["view"]["blocks"]),
            )
        )
        if len(suggestion_block):
            del blocks[suggestion_block[0][0]]

        stage = Stage.objects.get(pk=selected_value)
        fc_to_return = None  # forecast_block[1]["accessory"]["initial_option"]["value"]
        if stage.forecast_category:
            fc_to_return = stage.forecast_category
        if fc_to_return:
            # get label to show as recommended value
            # create new text block
            # show recommendation
            # slice and add in position
            label = (
                list(
                    filter(
                        lambda category: category[0] == fc_to_return, opp_consts.FORECAST_CHOICES,
                    )
                ),
            )
            if len(label):

                text = f"The recommended forecast for this stage is *{label[0][0][1]}*, Would you like to override the Forecast Category ?"
                suggestion_block = block_builders.simple_section(
                    text, "mrkdwn", "forecast_suggestion"
                )
                blocks = [
                    *blocks[: forecast_block[0] + 1],
                    suggestion_block,
                    *blocks[forecast_block[0] + 1 :],
                ]

        """
        new_fc_option = block_builders.option(
            *list(
                map(
                    lambda x: (x[1], x[0]),
                    list(
                        filter(
                            lambda category: category[0] == fc_to_return,
                            opp_consts.FORECAST_CHOICES,
                        )
                    ),
                )
            )[0]
        )
      
        blocks.append(
            block_builders.external_select(
                "*Forecast Category1*",
                slack_const.GET_OPPORTUNITY_FORECASTS,
                initial_option=new_fc_option,
                block_id="forecast_category1",
            )
        )
        """

    data = {
        "trigger_id": trigger_id,
        "view_id": view_id,
        "view": {
            "submit": {"type": "plain_text", "text": "Submit"},
            "callback_id": slack_const.ZOOM_MEETING__PROCESS_MEETING_SENTIMENT,
            "type": "modal",
            "title": {"type": "plain_text", "text": "Log Meeting"},
            "blocks": blocks,
            "private_metadata": payload["view"]["private_metadata"],
        },
    }

    res = slack_requests.generic_request(url, data, access_token=access_token)


def handle_block_actions(payload):
    """
    This takes place when user completes a general interaction,
    such as clicking a button.
    """
    switcher = {
        slack_const.ZOOM_MEETING__PROCESS_MEETING_SENTIMENT: process_meeting_sentiment,
        slack_const.ZOOM_MEETING__DIFFERENT_OPPORTUNITY: process_zoom_meeting_different_opportunity,
        slack_const.SHOW_REMINDER_CONTACTS: process_get_contacts,
        slack_const.SHOW_LEAD_CONTACTS: process_get_lead_contacts,
        slack_const.SHOW_LEAD_LOGS: process_get_lead_logs,
        slack_const.SHOW_MEETING_SCORE_COMPONENTS: process_get_meeting_score_components,
        slack_const.SHOW_LEAD_SCORE_COMPONENTS: process_get_lead_score_components,
        slack_const.ZOOM_MEETING__VIEW_MEETING_CONTACTS: process_show_meeting_contacts,
        slack_const.ZOOM_MEETING__EDIT_MEETING_CONTACT: process_edit_meeting_contact,
        slack_const.GET_ORGANIZATION_STAGES: process_update_forecast_category_option,
    }
    action_query_string = payload["actions"][0]["action_id"]
    processed_string = process_action_id(action_query_string)
    action_id = processed_string.get("true_id")
    action_params = processed_string.get("params")
    print(f"ID: {action_query_string}")
    return switcher.get(action_id, NO_OP)(payload, action_params)
