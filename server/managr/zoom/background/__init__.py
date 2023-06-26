import logging
from os import stat
import httpx
import json
import time
import re
import uuid
import random
from datetime import datetime
from django.utils import timezone
from django.conf import settings

from background_task import background
from managr.core.calendars import calendar_participants_from_zoom_meeting
from managr.slack.helpers import requests as slack_requests
from managr.slack.helpers.exceptions import (
    UnHandeledBlocksException,
    InvalidBlocksFormatException,
    InvalidBlocksException,
    InvalidAccessToken,
    CannotSendToChannel,
)
from managr.slack.helpers.block_sets import get_block_set
from managr.slack.helpers.utils import action_with_params
from managr.slack.helpers import block_builders
from managr.opportunity.models import Lead
from managr.salesforce.adapter.models import ContactAdapter
from managr.hubspot.adapter.models import HubspotContactAdapter
from managr.salesforce.models import MeetingWorkflow
from managr.slack.models import OrgCustomSlackForm, OrgCustomSlackFormInstance
from managr.slack import constants as slack_consts
from managr.crm.models import BaseAccount, BaseOpportunity, BaseContact
from .. import constants as zoom_consts
from ..zoom_helper.exceptions import TokenExpired, AccountSubscriptionLevel, RecordingNotFound
from managr.crm.exceptions import TokenExpired as CRMTokenExpired
from ..models import ZoomAuthAccount
from ..zoom_helper.models import ZoomAcct
from managr.core.exceptions import StopReasonLength, ServerError

logger = logging.getLogger("managr")


def _split_first_name(name):
    if name and len(name):
        name_parts = name.split(" ")
        if len(name_parts):
            return name_parts[0]


def _split_last_name(name):
    if name and len(name):
        name_parts = name.split(" ")
        if len(name_parts) > 1:

            return "".join(name_parts[1:])


def emit_refresh_zoom_token(zoom_account_id, schedule):
    # scedule can be seconds int or datetime string
    zoom_account_id = str(zoom_account_id)
    schedule = datetime.strptime(schedule, "%Y-%m-%dT%H:%M")
    return _refresh_zoom_token(zoom_account_id, schedule=schedule)


def emit_process_past_zoom_meeting(user_id, meeting_uuid, send_slack=True):
    return _get_past_zoom_meeting_details(user_id, meeting_uuid, send_slack)


def emit_kick_off_slack_interaction(user_id, managr_meeting_id, schedule=0):
    return _kick_off_slack_interaction(user_id, managr_meeting_id, schedule=schedule)


def emit_process_schedule_zoom_meeting(user, zoom_data):
    return _process_schedule_zoom_meeting(user, zoom_data)


def emit_process_get_transcript_and_update_crm(
    payload, context, summary_parts=[], viable_data=False, schedule=datetime.now()
):
    return _process_get_transcript_and_update_crm(
        payload, context, summary_parts, viable_data, schedule=schedule
    )


def _send_zoom_error_message(user, meeting_uuid):
    if hasattr(user, "slack_integration"):
        user_slack_channel = user.slack_integration.channel
        slack_org_access_token = user.organization.slack_integration.access_token

        try:
            slack_requests.send_channel_message(
                user_slack_channel,
                slack_org_access_token,
                text=f"Unable to log meeting",
                block_set=get_block_set(
                    "error_message",
                    {
                        "message": "Unfortunately we cannot gather meeting details for (basic) free level zoom accounts"
                    },
                ),
            )
        except InvalidBlocksException as e:
            return logger.exception(
                f"Failed to gather meeting for user {user.email} with uuid {meeting_uuid}"
            )
        except InvalidBlocksFormatException as e:
            return logger.exception(
                f"Failed to gather meeting for user {user.email} with uuid {meeting_uuid}"
            )
        except UnHandeledBlocksException as e:
            return logger.exception(
                f"Failed to gather meeting for user {user.email} with uuid {meeting_uuid}"
            )
        except InvalidAccessToken as e:
            return logger.exception(
                f"Failed to gather meeting for user {user.email} with uuid {meeting_uuid}"
            )


@background()
def _refresh_zoom_token(zoom_account_id):
    zoom_account = ZoomAuthAccount.objects.filter(id=zoom_account_id).first()
    if zoom_account and not zoom_account.is_revoked:
        try:
            zoom_account.regenerate_token()
        except TokenExpired:
            logger.exception(
                f"Failed to refresh zoom token for user {zoom_account.user.id},{zoom_account.user.email}"
            )
    elif zoom_account and zoom_account.is_revoked:
        logger.info(
            f"Did not attempt refresh for user because token was revoked, {zoom_account.user.id}, {zoom_account.user.email}"
        )
    return


def sync_contacts(contacts, user_id):
    from managr.crm.routes import model_routes

    zoom = ZoomAuthAccount.objects.get(user__id=user_id)
    user = zoom.user
    model_class = model_routes(user.crm)["Contact"]["model"]
    serializer_class = model_routes(user.crm)["Contact"]["serializer"]
    for item in contacts:
        existing = model_class.objects.filter(integration_id=item.integration_id).first()
        if existing:
            serializer = serializer_class(data=item.as_dict, instance=existing)
        else:
            serializer = serializer_class(data=item.as_dict)
        # check if already exists and update
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            logger.exception(f"Error saving contact in zoom flow: {e}")
            continue
        serializer.save()
        # if contact.secondary_data["associatedcompanyid"]
        if user.crm == "HUBSPOT":
            if (
                isinstance(item.secondary_data["num_associated_deals"], str)
                and len(item.secondary_data["num_associated_deals"]) > 0
            ):
                associated_deals = user.crm_account.adapter_class.get_associated_resource(
                    "Contact", "Deal", item.integration_id
                )["results"][0]["to"]
                filtered_ids = [deal["id"] for deal in associated_deals]
                synced_deals = BaseOpportunity.objects.filter(integration_id__in=filtered_ids)
                for deal in synced_deals:
                    deal.contacts.add(serializer.instance)
                    deal.save()
    return


def CONTACT_FILTERS(crm, emails):
    if crm == "HUBSPOT":
        return [{"propertyName": "email", "operator": "IN", "values": emails,}]
    else:
        email_string = "','".join(emails)
        return [f"AND Email IN ('{email_string}')"]


@background(schedule=0)
def _get_past_zoom_meeting_details(user_id, meeting_uuid, original_duration, send_slack=True):
    logger.info("Retrieving past Zoom meeting details...")

    def get_domain(email):
        """Parse domain out of an email"""
        return email[email.index("@") + 1 :]

    # SEND SLACK IS USED FOR TESTING ONLY
    zoom_account = ZoomAuthAccount.objects.filter(user__id=user_id).first()
    user = zoom_account.user
    ignore_emails = user.organization.ignore_emails
    meeting = {}
    if zoom_account and not zoom_account.is_revoked:
        while True:
            attempts = 1
            zoom_account = user.zoom_account
            try:
                meeting = zoom_account.helper_class.get_past_meeting(meeting_uuid)
                meeting.meta_data["original_duration"] = original_duration
                logger.info(f"{meeting.meta_data['original_duration']}")
                if meeting.meta_data["original_duration"] < 0:
                    # zoom weired bug where instance meetings get a random -1324234234 negative big int
                    meeting.meta_data["original_duration"] = 0
                # this will fail if a user has a free account
                meeting = meeting.get_past_meeting_participants(zoom_account.access_token)
                break
            except TokenExpired:
                if attempts >= 5:
                    return logger.exception(
                        f"Failed to retrieve meeeting data user zoom token is expired and we were unable to regenerate a new one {str(user.id)} email {user.email}"
                    )
                else:
                    zoom_account.regenerate_token()
                    attempts += 1
            except AccountSubscriptionLevel:
                logger.info(
                    f"failed to list participants from zoom because {zoom_account.user.email} has a free zoom account"
                )
                _send_zoom_error_message(user, meeting_uuid)
                return

        #
        logger.info(
            f"    Got Meeting: {meeting} with ID: {meeting_uuid} for user {user.email} with user_id {str(user.id)}"
        )
        logger.info(f"    Meeting Start: {meeting.start_time}")
        logger.info(f"    Meeting End: {meeting.end_time}")

        # Gather Meeting Participants from Zoom and Calendar
        logger.info("Gathering meeting participants...")
        zoom_participants = meeting.as_dict.get("participants", [])

        logger.info(f"    Zoom Participants: {zoom_participants}")

        # Gather unique emails from the Zoom Meeting participants
        participants = []
        user = zoom_account.user

        org_email_domain = get_domain(user.email)
        remove_users_with_these_domains_regex = r"(@[\w.]+calendar.google.com)|({})".format(
            org_email_domain
        )
        for email in ignore_emails:
            remove_users_with_these_domains_regex = (
                remove_users_with_these_domains_regex + r"|({})".format(email)
            )
        # re.search(remove_users_with_these_domains_regex, p.get("user_email", ""))
        #### first check if we care about this meeting before going forward
        should_register_this_meeting = [
            p
            for p in zoom_participants
            if not re.search(remove_users_with_these_domains_regex, p.get("user_email", ""))
        ]
        if not len(should_register_this_meeting):
            return

        memo = {}
        for p in zoom_participants:
            if p.get("user_email", "") not in ["", None, *memo.keys()] and not re.search(
                remove_users_with_these_domains_regex, p.get("user_email", "")
            ):
                memo[p.get("user_email")] = len(participants)
                participants.append(p)
        # If the user has their calendar connected through Nylas, find a
        # matching meeting and gather unique participant emails.
        calendar_participants = calendar_participants_from_zoom_meeting(meeting, user)

        # Combine the sets of participants. Filter out empty emails, meeting owner, and any
        # emails with domains that match the owner, which are teammates of the owner.
        logger.info(f"    Got list of participants: {participants}")
        for p in calendar_participants:
            if not re.search(
                remove_users_with_these_domains_regex, p.get("user_email", "")
            ) and p.get("user_email", "") not in ["", None]:
                if p.get("user_email", "") in memo.keys():
                    index = memo[p.get("user_email")]
                    participants[index]["name"] = p.get("name", "")
                else:
                    memo[p.get("user_email")] = len(participants)
                    participants.append(p)
        if settings.IN_STAGING:
            participants.append(
                {
                    "name": "maybe mike",
                    "id": "",
                    "user_email": f"{''.join([chr(random.randint(97, 122)) for x in range(random.randint(3,9))])}@{''.join([chr(random.randint(97, 122)) for x in range(random.randint(3,9))])}.com",
                }
            )
            participants.append(
                {
                    "name": "not",
                    "id": "",
                    "user_email": f"{''.join([chr(random.randint(97, 122)) for x in range(random.randint(3,9))])}@{''.join([chr(random.randint(97, 122)) for x in range(random.randint(3,9))])}.com",
                }
            )
        if settings.IN_DEV:
            participants.append(
                {
                    "name": "first",
                    "id": "",
                    "user_email": f"{''.join([chr(random.randint(97, 122)) for x in range(random.randint(3,9))])}@{''.join([chr(random.randint(97, 122)) for x in range(random.randint(3,9))])}.com",
                }
            )
            participants.append(
                {"name": "Zachary Bradley", "id": "", "user_email": "zachbradleydev@gmail.com",}
            )
        contact_forms = []
        if len(participants):
            # Reduce to set of unique participant emails
            participant_emails = set([p.get("user_email") for p in participants])
            attempts = 1
            while True:
                try:
                    crm_contacts = user.crm_account.adapter_class.list_resource_data(
                        "Contact", filter=CONTACT_FILTERS(user.crm, list(participant_emails)),
                    )
                    break
                except CRMTokenExpired:
                    if attempts >= 5:
                        break
                    else:
                        sleep = 1 * 2 ** attempts + random.uniform(0, 1)
                        time.sleep(sleep)
                        user.crm_account.regenerate_token()
                        attempts += 1
            sync_contacts(crm_contacts, str(user.id))
            meeting_contacts = []

            # find existing contacts

            existing_contacts = BaseContact.objects.filter(
                email__in=participant_emails,
                owner__organization__id=user.organization.id,
                integration_source=user.crm,
            ).exclude(email=user.email)
            meeting_resource_data = dict(resource_id="", resource_type="")
            opportunity = BaseOpportunity.objects.filter(
                contacts__email__in=participant_emails, owner__id=user.id
            ).first()
            if opportunity:
                meeting_resource_data["resource_id"] = str(opportunity.id)
                meeting_resource_data["resource_type"] = (
                    "Opportunity" if user.crm == "SALESFORCE" else "Deal"
                )
                existing_contacts = existing_contacts.filter(
                    opportunities__in=[str(opportunity.id)]
                )
            else:
                account = BaseAccount.objects.filter(
                    contacts__email__in=participant_emails, owner__id=user.id,
                ).first()
                if account:
                    meeting_resource_data["resource_id"] = str(account.id)
                    meeting_resource_data["resource_type"] = (
                        "Account" if user.crm == "SALESFORCE" else "Company"
                    )
                    existing_contacts = existing_contacts.filter(account=account.id)
                else:
                    lead = Lead.objects.filter(
                        email__in=participant_emails, owner__id=user.id
                    ).first()
                    if lead:
                        meeting_resource_data["resource_id"] = str(lead.id)
                        meeting_resource_data["resource_type"] = "Lead"
            # convert all contacts to model representation and remove from array
            for contact in existing_contacts:
                formatted_contact = contact.adapter_class.as_dict

                # create a form for each contact to save to workflow

                meeting_contacts.append(formatted_contact)
                for index, participant in enumerate(participants):
                    if (
                        participant["user_email"] == contact.email
                        or participant["user_email"] == user.email
                    ):
                        del participants[index]
            contact_adapter = ContactAdapter if user.crm == "SALESFORCE" else HubspotContactAdapter

            new_contacts = list(
                filter(
                    lambda x: len(x.get("secondary_data", dict())) or x.get("email"),
                    list(
                        map(
                            lambda participant: {
                                **contact_adapter(
                                    **dict(
                                        email=participant["user_email"],
                                        # these will only get stored if lastname and firstname are accessible from sf
                                        external_owner=user.crm_account.crm_id,
                                        secondary_data={
                                            f"{'FirstName' if user.crm == 'SALESFORCE' else 'FirstName'}": _split_first_name(
                                                participant["name"]
                                            ),
                                            f"{'LastName' if user.crm == 'SALESFORCE' else 'firstname'}": _split_last_name(
                                                participant["name"]
                                            ),
                                            f"{'Email' if user.crm == 'SALESFORCE' else 'email'}": participant[
                                                "user_email"
                                            ],
                                        },
                                    )
                                ).as_dict,
                            },
                            participants,
                        ),
                    ),
                )
            )
            meeting_contacts = [
                *new_contacts,
                *meeting_contacts,
            ]
            logger.info(f"PARTICIPANT EMAILS {participant_emails}")

            for contact in meeting_contacts:
                contact["_tracking_id"] = str(uuid.uuid4())
                form_type = (
                    slack_consts.FORM_TYPE_UPDATE
                    if contact["id"] not in ["", None]
                    else slack_consts.FORM_TYPE_CREATE
                )
                template = OrgCustomSlackForm.objects.filter(
                    form_type=form_type,
                    resource=slack_consts.FORM_RESOURCE_CONTACT,
                    team=user.team,
                ).first()
                if not template:
                    logger.exception(
                        f"Unable to find Contact Form template for user {str(user_id)}, email {user.email} cannot create initial form for meeting review"
                    )
                    contact["_form"] = None
                else:
                    # create instance
                    logger.info(f"contact_id: {contact['id']}")
                    form = OrgCustomSlackFormInstance.objects.create(
                        user=user,
                        template=template,
                        resource_id="" if contact.get("id") in ["", None] else contact.get("id"),
                    )
                    contact_forms.append(form)
                    contact["_form"] = str(form.id)
            meeting.participants = meeting_contacts
            meeting.save()
            logger.info(f"MEETING RESOURCE DATA {meeting_resource_data}")
            workflow = MeetingWorkflow.objects.create(
                user=user,
                meeting=meeting,
                operation_type=zoom_consts.MEETING_REVIEW_OPERATION,
                **meeting_resource_data,
            )
            workflow.forms.set(contact_forms)
            if send_slack:
                # sends false only for Mike testing
                workflow.begin_communication()
            return workflow


@background(schedule=0)
def _kick_off_slack_interaction(user_id, managr_meeting_id):
    # get meeting
    workflow = MeetingWorkflow.objects.filter(id=managr_meeting_id).first()
    if workflow:
        # get user
        user = workflow.user

        if hasattr(user, "slack_integration"):
            user_slack_channel = (
                user.slack_integration.zoom_channel
                if user.slack_integration.zoom_channel
                else user.slack_integration.channel
            )
            slack_org_access_token = user.organization.slack_integration.access_token
            block_set = [
                *get_block_set(
                    "direct_to_block_set",
                    context={
                        "slack": action_with_params(
                            slack_consts.SHOW_INITIAL_MEETING_INTERACTION,
                            params=[f"w={str(workflow.id)}"],
                        ),
                        "managr": f"{slack_consts.MANAGR_URL}/meetings",
                        "title": f"Log your meeting :calendar: *{workflow.meeting.topic}*",
                    },
                ),
                block_builders.context_block(f"Owned by {user.full_name}"),
            ]
            try:
                res = slack_requests.send_channel_message(
                    user_slack_channel,
                    slack_org_access_token,
                    text="Your Meeting just ended",
                    block_set=block_set,
                )
            except InvalidBlocksException as e:
                return logger.exception(
                    f"Failed To Generate Slack Workflow Interaction for user with workflow {str(workflow.id)} email {workflow.user.email} {e}"
                )
            except InvalidBlocksFormatException as e:
                return logger.exception(
                    f"Failed To Generate Slack Workflow Interaction for user with workflow {str(workflow.id)} email {workflow.user.email} {e}"
                )
            except UnHandeledBlocksException as e:
                return logger.exception(
                    f"Failed To Generate Slack Workflow Interaction for user with workflow {str(workflow.id)} email {workflow.user.email} {e}"
                )
            except InvalidAccessToken as e:
                return logger.exception(
                    f"Failed To Generate Slack Workflow Interaction for user with workflow {str(workflow.id)} email {workflow.user.email} {e}"
                )
            except CannotSendToChannel as e:
                res = slack_requests.send_channel_message(
                    user.slack_integration.channel,
                    slack_org_access_token,
                    text="Your Meeting just ended",
                    block_set=block_set,
                )
                return logger.exception(
                    f"Message redirected, failed to send to zoom channel in kick off slack interaction for workflow {str(workflow.id)} {e}"
                )
            except Exception as e:
                return logger.exception(
                    f"Kick off slack interaction error {e} for workflow {str(workflow.id)}"
                )

            # save slack message ts and channel id to remove if the meeting is deleted before being filled
            # user.activity.increment_untouched_count("meeting")
            workflow.slack_interaction = f"{res['ts']}|{res['channel']}"
            workflow.save()


def to_float(amount):
    if amount in ["", None]:
        return None
    try:
        return "{:.2f}".format(float(amount))
    except ValueError:
        return None


@background(schedule=0)
def _process_confirm_compliance(obj):
    """Sends Compliance verification on app deauth to zoom"""
    ZoomAcct.compliance_api(json.loads(obj))
    return


def _process_schedule_zoom_meeting(user, zoom_data):
    # get details of meeting
    hour = int(zoom_data["meeting_hour"])
    if zoom_data["meeting_time"] == "PM" and hour != 12:
        hour = hour + 12
    formatted_time = f"{str(hour)}:{zoom_data['meeting_minute']}"
    try:
        res = user.zoom_account.helper_class.schedule_meeting(
            zoom_data["meeting_topic"],
            zoom_data["meeting_date"],
            formatted_time,
            int(zoom_data["meeting_duration"]),
        )
        return res
    except Exception as e:
        logger.warning(f"Zoom schedule error: {e}")


def clean_prompt_string(prompt_string):
    cleaned_string = (
        prompt_string[prompt_string.index("{") : prompt_string.index("}") + 1]
        .replace("\n\n", "")
        .replace("\n ", "")
        .replace("\n", "")
        .replace("  ", "")
        .replace("', '", '", "')
        .replace("': '", '": "')
        .replace("{'", '{"')
        .replace("','", '","')
        .replace("':", '":')
        .replace(", '", ', "')
    )
    while "{  " in cleaned_string:
        cleaned_string = cleaned_string.replace("{  ", "{ ")
    cleaned_string = cleaned_string.replace("{ '", '{ "').replace("'}", '"}')
    return cleaned_string


WORD_TO_NUMBER = {
    "a": 1,
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
}

TIME_TO_NUMBER = {"week": 7, "weeks": 7, "month": 30, "months": 30, "year": 365, "tomorrow": 1}
DAYS_TO_NUMBER = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6,
}


def convert_date_string(date_string, value):
    from django.utils import timezone
    import calendar
    from dateutil.parser import parse

    if value is None:
        value = datetime.now()
    else:
        value = value.split("T")[0]
    split_date_string = date_string.lower().split(" ")
    time_key = None
    number_key = 1
    if any("push" in s for s in split_date_string) or any("move" in s for s in split_date_string):
        for key in split_date_string:
            if key in TIME_TO_NUMBER.keys():
                time_key = TIME_TO_NUMBER[key]
            if key in WORD_TO_NUMBER:
                number_key = WORD_TO_NUMBER[key]
    elif any(key in split_date_string for key in DAYS_TO_NUMBER.keys()):
        for key in split_date_string:
            if key in DAYS_TO_NUMBER.keys():
                current = datetime.now()
                start = current - timezone.timedelta(days=current.weekday())
                day_value = start + timezone.timedelta(days=DAYS_TO_NUMBER[key])
                if any("next" in s for s in split_date_string):
                    day_value = day_value + timezone.timedelta(days=7)
                return day_value
    elif any("end" in s for s in split_date_string):
        if any("week" in s for s in split_date_string):
            current = datetime.strptime(value, "%Y-%m-%d")
            start = current - timezone.timedelta(days=current.weekday())
            return start + timezone.timedelta(days=4)
        elif any("month" in s for s in split_date_string):
            current = datetime.strptime(value, "%Y-%m-%d")
            last_of_month = calendar.monthrange(current.year, current.month)[1]
            return current.replace(day=last_of_month)
    elif any("week" in s for s in split_date_string):
        current = datetime.strptime(value, "%Y-%m-%d")
        return current + timezone.timedelta(days=7)
    if "back" in date_string:
        new_value = datetime.strptime(value, "%Y-%m-%d") - timezone.timedelta(
            days=(time_key * number_key)
        )
    else:
        if time_key:
            new_value = datetime.strptime(value, "%Y-%m-%d") + timezone.timedelta(
                days=(time_key * number_key)
            )
        else:
            try:
                date_parsed = parse(date_string)
                new_value = date_parsed
            except Exception as e:
                print(e)
                new_value = value
    return new_value


def clean_prompt_return_data(data, fields, crm, resource=None):
    cleaned_data = dict(data)
    notes = cleaned_data.pop("meeting_comments", None)
    subject = cleaned_data.pop("meeting_type", None)
    for key in cleaned_data.keys():
        try:
            field = fields.get(api_name=key)
            if resource and field.api_name in ["Name", "dealname"]:
                cleaned_data[key] = resource.secondary_data[key]
            if cleaned_data[key] is None or cleaned_data[key] in [
                "",
                "TBD",
                "Unknown",
                "None",
                "N/A",
            ]:
                if resource:
                    cleaned_data[key] = resource.secondary_data[key]
                continue
            elif field.data_type == "TextArea":
                if resource and data[key] is not None:
                    current_value = (
                        resource.secondary_data[key]
                        if resource.secondary_data[key] is not None
                        else " "
                    )
                    cleaned_data[key] = f"{data[key]}\n\n{current_value}"
            elif field.data_type in ["Date", "DateTime"]:
                data_value = data[key]
                current_value = resource.secondary_data[key] if resource else None
                new_value = convert_date_string(data_value, current_value)
                if isinstance(new_value, str):
                    if resource:
                        cleaned_data[key] = resource.secondary_data[key]
                    else:
                        cleaned_data[key] = None
                else:
                    cleaned_data[key] = (
                        str(new_value.date())
                        if crm == "SALESFORCE"
                        else (str(new_value.date()) + "T00:00:00.000Z")
                    )
            elif field.api_name == "dealstage":
                if resource:
                    pipeline = field.options[0][resource.secondary_data["pipeline"]]
                    if pipeline:
                        stage_value = data[key].lower()
                        stage = [
                            stage
                            for stage in pipeline["stages"]
                            if stage["label"].lower() == stage_value
                        ]
                        if len(stage):
                            cleaned_data[key] = stage[0]["id"]
                        else:
                            cleaned_data[key] = resource.secondary_data["dealstage"]
            elif field.api_name in ["Amount", "amount"]:
                if isinstance(cleaned_data[key], int):
                    continue
                amount = cleaned_data[key]
                if "k" in amount:
                    amount = amount.replace("k", "000.0")
                if "$" in amount:
                    amount = amount.replace("$", "")
                cleaned_data[key] = amount
            elif field.data_type == "Picklist":
                if crm == "HUBSPOT":
                    options = field.options
                else:
                    options = field.crm_picklist_options.values
                value_found = False
                for value in options:
                    lowered_value = cleaned_data[key].lower()
                    current_value_label = value["label"].lower()
                    if lowered_value in current_value_label:
                        value_found = True
                        cleaned_data[key] = value["value"]
                if not value_found:
                    if resource:
                        cleaned_data[key] = resource.secondary_data[key]
                    else:
                        cleaned_data[key] = None
        except ValueError:
            continue
    cleaned_data["meeting_comments"] = notes
    cleaned_data["meeting_type"] = subject
    return cleaned_data


def swap_submitted_data_labels(data, fields):
    api_key_data = {}
    for label in data.keys():
        try:
            field_list = fields.filter(label__icontains=label)
            field = None
            for field_value in field_list:
                if len(field_value.label) == len(label):
                    field = field_value
                    break
            api_key_data[field.api_name] = data[label]
        except Exception as e:
            continue
    return api_key_data


def set_owner_field(resource, crm):
    if resource in ["Opportunity", "Account", "Contact"] and crm == "SALESFORCE":
        return "Owner ID"
    elif resource == "Company":
        return "Company owner"
    elif resource == "Contact" and crm == "HUBSPOT":
        return "Contact owner"
    elif resource == "Deal":
        return "Deal owner"
    return None


def process_transcript_to_summaries(transcript, user):
    from managr.core.exceptions import _handle_response
    from managr.core import constants as core_consts
    from managr.utils.client import Variable_Client

    summary_parts = []
    current_minute = 5
    start_index = 0
    current_hour = 0
    split_transcript = []
    while True:
        if current_minute == 60:
            current_minute = 0
            current_hour += 1
        check_time = (
            f"0{current_hour}:0{str(current_minute)}:"
            if (current_minute == 5 or current_minute == 0)
            else f"0{current_hour}:{str(current_minute)}:"
        )
        end_index = transcript.find(check_time)
        if end_index == -1 and len(split_transcript):
            split_transcript.append(transcript[start_index:])
            break
        elif end_index == -1 and not len(split_transcript):
            current_minute += 5
            continue
        else:
            split_transcript.append(transcript[start_index:end_index])
            start_index = end_index
            current_minute += 5
    if not len(summary_parts):
        for index, transcript_part in enumerate(split_transcript):
            if not settings.IN_PROD:
                print(index)

            transcript_body = core_consts.OPEN_AI_TRANSCRIPT_PROMPT(
                {"date": datetime.today(), "transcript": transcript_part,}
            )
            transcript_body = (
                transcript_body.replace("\r\n", "")
                .replace("\n", "")
                .replace("    ", "")
                .replace(" --> ", "-")
            )
            # if not settings.IN_PROD:
            #     token_check = max_token_calculator(transcript_body)
            #     print(f"MAX TOKEN CHECK: {len(transcript_body)}, {token_check}")
            attempts = 1
            timeout = 60.0
            tokens = 500
            while True:
                body = core_consts.OPEN_AI_COMPLETIONS_BODY(
                    user.email, transcript_body, tokens, top_p=0.9, temperature=0.7
                )
                url = core_consts.OPEN_AI_COMPLETIONS_URI
                with Variable_Client(timeout) as client:
                    try:
                        r = client.post(
                            url, data=json.dumps(body), headers=core_consts.OPEN_AI_HEADERS,
                        )
                        r = _handle_response(r)
                        summary = r.get("choices")[0].get("text")

                        summary = (
                            summary.replace(":\n\n", "").replace(".\n\n", "").replace("\n\n", "")
                        )
                        summary_split = summary.split("Summary:")
                        summary_parts.append(summary_split[1])
                        break
                    except StopReasonLength:
                        if tokens >= 2000:
                            break
                        else:
                            tokens += 500
                            continue
                    except IndexError:
                        continue
                    except ServerError:
                        if attempts >= 5:
                            return []
                        else:
                            attempts += 1
                            time.sleep(10.0)
                    except httpx.ReadTimeout:
                        logger.exception(
                            f"Read timeout to Open AI, trying again. TIMEOUT AT: {timeout}"
                        )
                        if timeout >= 120.0:
                            break
                        else:
                            timeout += 30.0
                    except Exception as e:
                        logger.exception(f"PROCESS TRANSCRIPT SUMMARIES EXCEPTION {e}")
                        break
    return summary_parts


@background()
def _process_get_transcript_and_update_crm(payload, context, summary_parts, viable_data):
    from managr.core.models import User
    from managr.salesforce.models import MeetingWorkflow
    from managr.crm.utils import CRM_SWITCHER
    from managr.utils.client import Variable_Client
    from managr.core import constants as core_consts
    from managr.core.exceptions import _handle_response
    from managr.core.background import emit_process_add_call_analysis

    pm = json.loads(payload["view"]["private_metadata"])
    user = User.objects.get(id=pm.get("u"))
    state = payload["view"]["state"]["values"]
    try:
        loading_res = slack_requests.send_channel_message(
            user.slack_integration.channel,
            user.organization.slack_integration.access_token,
            block_set=get_block_set(
                "loading",
                {"message": ":robot_face: Summarizing your call. This may take a few minutes..."},
            ),
        )
        ts = loading_res["message"]["ts"]
    except Exception as e:
        logger.exception(
            f"ERROR sending update channel message for chat submittion because of <{e}>"
        )
    selected_options = state["selected_object"]
    resource_type = context.get("resource_type")
    resource_list = [
        key for key in selected_options.keys() if "MEETING__PROCESS_TRANSCRIPT_TASK" in key
    ]
    value_key = "None"
    if len(resource_list):
        value_key = resource_list[0]
    selected_option = selected_options[value_key]["selected_option"]["value"]
    workflow = MeetingWorkflow.objects.get(id=pm.get("w"))
    resource = CRM_SWITCHER[user.crm][resource_type]["model"].objects.get(
        integration_id=selected_option
    )
    form_template = user.team.team_forms.get(form_type="UPDATE", resource=resource_type)
    fields = form_template.custom_fields.all()
    fields_list = list(fields.values_list("label", flat=True))
    workflow.resource_id = str(resource.id)
    workflow.resource_type = resource_type
    if slack_consts.MEETING__PROCESS_TRANSCRIPT_TASK not in workflow.operations:
        workflow.operations.append(slack_consts.MEETING__PROCESS_TRANSCRIPT_TASK)
    if slack_consts.MEETING__PROCESS_TRANSCRIPT_TASK not in workflow.operations_list:
        workflow.operations_list.append(slack_consts.MEETING__PROCESS_TRANSCRIPT_TASK)
    workflow.save()
    meeting = workflow.meeting
    has_error = False
    error_message = None
    try:
        if not settings.IN_PROD:
            logger.info("Retreiving meeting data...")
        meeting_data = meeting.meeting_account.helper_class.get_meeting_data(
            meeting.meeting_id, meeting.meeting_account.access_token
        )
        if not settings.IN_PROD:
            logger.info(f"Done! {meeting_data}")
        try:
            update_res = slack_requests.update_channel_message(
                user.slack_integration.channel,
                ts,
                user.organization.slack_integration.access_token,
                block_set=get_block_set(
                    "loading",
                    {"message": f":telephone_receiver: Transcript found for {meeting.topic}"},
                ),
            )
        except Exception as e:
            logger.exception(f"Could not update channel message because of {e} ts {ts}")
        recordings = meeting_data["recording_files"]
        filtered_recordings = [
            recording
            for recording in recordings
            if recording["recording_type"] == "audio_transcript"
        ]
        if len(filtered_recordings):
            if not len(summary_parts):
                recording_obj = filtered_recordings[0]
                download_url = recording_obj["download_url"]
                transcript = meeting.meeting_account.helper_class.get_transcript(
                    download_url, meeting.meeting_account.access_token
                )
                transcript = transcript.decode("utf-8")
                summary_parts = process_transcript_to_summaries(transcript, user)
            if len(summary_parts):
                timeout = 60.0
                tokens = 1500
                try:
                    update_res = slack_requests.update_channel_message(
                        user.slack_integration.channel,
                        ts,
                        user.organization.slack_integration.access_token,
                        block_set=get_block_set(
                            "loading",
                            {"message": f":robot_face: Processing transcript for {meeting.topic}"},
                        ),
                    )
                except Exception as e:
                    logger.exception(f"Could not update channel message because of {e} ts {ts}")
                attempts = 1
                while True:
                    summary_body = core_consts.OPEN_AI_TRANSCRIPT_UPDATE_PROMPT(
                        {
                            "date": workflow.datetime_created.date(),
                            "transcript_summaries": summary_parts,
                        },
                        fields_list,
                        workflow.datetime_created.date(),
                        user,
                    )
                    tokens = 1000
                    body = core_consts.OPEN_AI_COMPLETIONS_BODY(
                        user.email, summary_body, tokens, top_p=0.9
                    )
                    try:
                        if not settings.IN_PROD:
                            logger.info("Combining Summary parts")
                        if not viable_data:
                            with Variable_Client(timeout) as client:
                                url = core_consts.OPEN_AI_COMPLETIONS_URI
                                r = client.post(
                                    url, data=json.dumps(body), headers=core_consts.OPEN_AI_HEADERS,
                                )
                            r = _handle_response(r)
                            if not settings.IN_PROD:
                                logger.info(f"Summary response: {r}")
                            choice = r["choices"][0]["text"]
                            summary = clean_prompt_string(choice)
                            data = eval(summary)
                            viable_data = data
                        else:
                            data = viable_data
                        combined_summary = (
                            data.pop("summary", None)
                            if data.get("summary", None)
                            else data.pop("Summary", None)
                        )
                        owner_field = set_owner_field(resource_type, user.crm)
                        data[owner_field] = user.crm_account.crm_id
                        swapped_field_data = swap_submitted_data_labels(data, fields)
                        cleaned_data = clean_prompt_return_data(
                            swapped_field_data, fields, user.crm, resource
                        )

                        workflow.transcript_summary = combined_summary
                        workflow.save()
                        break
                    except StopReasonLength:
                        if tokens >= 2000:
                            break
                        else:
                            tokens += 500
                            continue
                    except ServerError:
                        if attempts >= 5:
                            has_error = True
                            error_message = ":no_entry_sign: There was a server error with Open AI"
                            break
                        else:
                            attempts += 1
                            time.sleep(10.0)
                    except ValueError as e:
                        print(e)
                        if str(e) == "substring not found":
                            continue
                        else:
                            has_error = True
                            error_message = (
                                ":no_entry_sign: Looks like we ran into an internal issue"
                            )
                            break
                    except SyntaxError as e:
                        print(e)
                        continue
                    except httpx.ReadTimeout:
                        logger.exception(
                            f"Read timeout to Open AI, trying again. TIMEOUT AT: {timeout}"
                        )
                        if timeout >= 120.0:
                            has_error = True
                            error_message = ":rocket: OpenAI servers are busy. No action needed, we'll try again in a few minutes..."
                            schedule = datetime.now() + timezone.timedelta(minutes=5)
                            emit_process_get_transcript_and_update_crm(
                                payload, context, summary_parts, viable_data, schedule
                            )
                            break
                        else:
                            timeout += 30.0
                    except Exception as e:
                        logger.exception(f"Exception combining summaries: <{e}>")
            else:
                has_error = True
                error_message = ":no_entry_sign: Unknown error"
        else:
            has_error = True
            error_message = ":no_entry_sign: We could not find a transcript for this meeting"
    except RecordingNotFound:
        has_error = True
        retry = context.get("retry_attempts", 0) + 1
        context.update(retry_attempts=retry)
        error_message = (
            f":rocket: Looks like you're transcript is not done processing, we'll try again in a bit!"
            if retry <= 3
            else "We could not find a recording for this meeting"
        )
        if retry < 3:
            emit_process_get_transcript_and_update_crm(
                payload, context, schedule=(datetime.now() + timezone.timedelta(minutes=30))
            )
    except Exception as e:
        logger.exception(e)
        has_error = True
        error_message = (
            f":no_entry_sign: We encountered an unknow error processing your transcript: {str(e)}"
        )
    # summary_parts = [
    #     " Colin and Michael were discussing the benefits of using an AI assistant for sales people. Colin had been using Chat Gbt and was looking for a free or low cost tool to help with emails and prioritization. They then discussed a meeting with Scratch Pad that an AE on Colin's team had booked and the benefits of using it for digital accessibility. Michael then asked Colin what kind of problems he had been running into with Chat Gbt.",
    #     " Colin O'Grady is a sales rep for a SaaS company who was reviewing the AI note taking software offered by Manager. He had already met with the CEO of another tool at 1.2, but the customer wasn't interested in having too many tools touch their system. Michael Gorodisher, the CEO of Manager, explained that they are a pass-through service that does not store any data and are listed in the Slack marketplace. He then asked Colin what got him to Manager's website, and Colin explained he found it after searching for AI sales tools. Michael then explained the features of Manager's software, including AI note taking, call summaries, and the ability to ask questions. Colin was interested in the AI note taking because it would help him with data entry and note taking.",
    #     " Michael and Colin discussed the benefits of using Wingman's AI to streamline customer interactions and replace scratch pad. They discussed the subscription terms and the 30 day free trial period. Colin mentioned that he wanted to use Wingman's AI to streamline his note taking and have a checklist to ensure he captures the necessary information from customer calls. They agreed to compare Wingman's summary with Michael's and discussed the next steps.",
    #     " In this section of the call transcript, Michael is demonstrating how to use Manager's AI-assisted solution to streamline the sales process. He goes over how the AI can fill out fields like customer pain, timeline, competitors, and decision process, and how the user can then generate a follow-up email, suggested next steps, and a summary to send to their executives. He also shows how the AI can be used to send a follow up email using a template as a poem and fill out fields quickly in Salesforce.",
    #     " In this section of the call, Michael and Colin discuss the AI automation features of the Manager app. Michael explains how it can help a salesperson log their notes, work faster, and enter data. Colin asks if they can also use the AI to draft a follow-up email that is short, funny, and provides bullet-point value. Michael confirms that they can, and demonstrates how the AI will automatically update the fields and tasks in the CRM. They also discuss how the AI can correct spelling mistakes.",
    #     " In this section of the call, Michael and Colin discussed the potential benefits of using the chat GPT software, including the AI note taking, automated follow up emails, and actionable alerts. They discussed the potential for Colin to demonstrate the tool to his leadership and the benefits of the tool for staying organized, timely, and accurate. They also discussed the potential to use the tool for deal reviews and the possibility of using the software without the AI note taking.",
    #     " Michael and Colin are discussing the value of Scratch Pad, a tool that adds AI call summaries, activity updating, and follow-up email suggestions to individual and group packages for an extra $15 per month. Colin is impressed with the tool and is looking forward to training with Michael on how to use it. He also wants to know how he can explain it to his buddy, who already uses Scratch Pad. Michael clarifies that the tool is not just a shortcut, but a much more efficient and better way to utilize Chat GPT as a superpower.",
    #     " Colin and Michael discussed how Manager, a tool to help salespeople work more efficiently, leveraged AI to do data entry and generate summaries. They discussed how this is different from their competitor, Scratch Pad, and how Manager’s AI-powered features could benefit executives, allowing them to see into deals more deeply and efficiently. They concluded by explaining that this was the perfect time for Manager to launch with its new AI engine, as executives are now more focused on value creation than time savings.",
    #     " Michael and Colin discussed how AI can help sales reps with data entry and other tasks to ensure nothing is forgotten during customer calls. Colin mentioned that some reps are better than others at taking notes during calls and that the AI can act as a back up to make sure nothing is missed. Michael suggested that Colin evaluate the company plan and business plan to get access to the AI. They decided to check in next week to see what Colin decides.",
    # ]
    # cleaned_data = {
    #     "call_recording__c": "Chorus",
    #     "champion__c": "Colin O’Grady\n\nColin O'Grady\n\nColin O'Grady\r\n\r\nNancy\r\r\r\r\n\r\r\r\r\nJerry\r\r\r\r\r\n\r\r\r\r\r\nJerry\r\r\r\r\r\r\n\r\r\r\r\r\r\nRon\r\r\r\r\r\r\r\n\r\r\r\r\r\r\r\nRon\r\r\r\r\r\r\r\n\r\r\r\r\r\r\r\nRon\r\r\r\r\r\r\r\n\r\r\r\r\r\r\r\nMichael Gorodisher\r\r\r\r\r\r\r\r\r\r\r\r\r\n\r\r\r\r\r\r\r\r\r\r\r\r\r\nStephen Russo\r\r\r\r\r\r\r\r\r\r\r\r\r\n\r\r\r\r\r\r\r\r\r\r\r\r\r\nJohn Miller\r\r\r\r\r\r\r\r\r\r\r\r\r\n\r\r\r\r\r\r\r\r\r\r\r\r\r\n ",
    #     "competitors__c": "Scratchpad",
    #     "crm__c": "Salesforce",
    #     "hs_manual_forecast_category": "COMMIT",
    #     "hs_next_step": "Submit follow up email\n\nTrialing Wingman, Signing up for individual access, Onboarding business accounts\n\nDecision Process\r\n\r\nFollow up\r\r\r\r\n\r\r\r\r\nEmail Jerry outlining our value proposition and why he needs to use Managr\r\r\r\r\r\n\r\r\r\r\r\nEmail Jerry\r\r\r\r\r\r\n\r\r\r\r\r\r\nFollow up call with his team to get buy in from the AEs\r\r\r\r\r\r\r\n\r\r\r\r\r\r\r\nDemonstrate the product\r\r\r\r\r\r\r\n\r\r\r\r\r\r\r\nFollow up with Ron in mid June\r\r\r\r\r\r\r\n\r\r\r\r\r\r\r\nFollow up with Ron in mid June\r\r\r\r\r\r\r\r\n\r\r\r\r\r\r\r\r\nMeeting with CFO\r\r\r\r\r\r\r\r\r\r\r\r\r\n\r\r\r\r\r\r\r\r\r\r\r\r\r\nEvaluate AI system\r\r\r\r\r\r\r\r\r\r\r\r\r\n\r\r\r\r\r\r\r\r\r\r\r\r\r\nMeeting with CFO for final approval\r\r\r\r\r\r\r\r\r\r\r\r\r\n\r\r\r\r\r\r\r\r\r\r\r\r\r\nUpdate Deal\r\r\r\r\r\r\r\r\r\r\r\r\r\r\r\r\n\r\r\r\r\r\r\r\r\r\r\r\r\r\r\r\r\nTEAM Demo\r\r\r\r\r\r\r\r\r\r\r\r\r\r\r\r\r\n\r\r\r\r\r\r\r\r\r\r\r\r\r\r\r\r\r\nTEAM Demo\r\r\r\r\r\r\r\r\r\r\r\r\r\r\r\r\r\n\r\r\r\r\r\r\r\r\r\r\r\r\r\r\r\r\r\nMove close date\r\r\r\r\r\r\r\r\r\r\r\r\r\r\r\r\r\n ",
    #     "next_step_date__c": "2023-06-07T00:00:00.000Z",
    #     "dealname": "Starbucks",
    #     "amount": "20K",
    #     "dealstage": "qualifiedtobuy",
    #     "closedate": "2023-06-14T00:00:00.000Z",
    #     "hubspot_owner_id": "153800017",
    #     "meeting_comments": "The sales call between Michael Gorodisher, a sales rep from Wingman, and Colin O’Grady, an AE for a SAS company, was successful. Michael was able to identify Colin’s pain points and present the advantages of Wingman’s AI-enabled software, which could help Colin streamline his sales process. Colin was interested in the 30-day free trial and the ability to opt-out if they’re not happy with it. Michael also discussed the value of Manager compared to Scratch Pad, which offers no additional value beyond a different view of Salesforce. Colin expressed his interest in the $29 individual package plus $15 a month to look like the best salesperson and be more efficient. At the end of the call, Colin and Michael agreed to keep in touch next week to see what Colin decides.",
    #     "meeting_type": "Sales Call Summary",
    # }
    # combined_summary = "The VP of Sales had a positive meeting with Colin O'Grady, a sales rep for a SaaS company, to discuss Manager's AI-assisted solution. Colin had previously used Chat Gbt and was looking for a low cost tool to help with emails and prioritization. Michael Gorodisher, the CEO of Manager, explained how their pass-through service was listed in the Slack Marketplace and discussed the features of their software, such as AI note taking, call summaries, and the ability to ask questions. Colin was interested in the AI note taking and the two discussed the benefits of using Wingman's AI to streamline customer interactions, the subscription terms, and the 30 day free trial period. They also discussed the potential to use the tool for deal reviews and the possibility of using the software without the AI note taking. Michael showed Colin how the AI can fill out fields like customer pain, timeline, competitors, and decision process and generate a follow-up email, suggested next steps, and a summary to send to their executives. He also showed how the AI can be used to send a follow up email using a template as a poem and fill out fields quickly in Salesforce. They discussed how the AI can help sales reps with data entry and other tasks to ensure nothing is forgotten during customer calls. They concluded by discussing the perfect time for Manager to launch with its new AI engine, as executives are now more focused on value creation than time savings. They decided to check in next week to see what Colin decides. Overall, the meeting had a positive tone and Michael and Colin are optimistic about the potential of Manager's AI-assisted solution."
    if not has_error:
        form_check = workflow.forms.all().filter(template=form_template).first()
        if form_check:
            new_form = form_check
        else:
            new_form = OrgCustomSlackFormInstance.objects.create(
                user=user,
                template=form_template,
                resource_id=str(resource.id),
                update_source="transcript",
                workflow=workflow,
            )
            new_form.save_form(cleaned_data, False)
        emit_process_add_call_analysis(str(workflow.id), summary_parts)
        blocks = [
            block_builders.header_block("AI Generated Call Summary"),
            block_builders.context_block(f"Meeting: {meeting.topic}"),
            block_builders.divider_block(),
            block_builders.simple_section(f"{resource_type}: {resource.display_value}"),
            block_builders.simple_section(combined_summary, "mrkdwn"),
            block_builders.divider_block(),
            block_builders.actions_block(
                [
                    block_builders.simple_button_block(
                        f"Review & Update {'Salesforce' if user.crm == 'SALESFORCE' else 'HubSpot'}",
                        "LAUNCH_REVIEW",
                        action_id=action_with_params(
                            slack_consts.CALL_LAUNCH_SUMMARY_REVIEW,
                            [f"form_id={str(new_form.id)}&u={str(user.id)}&w={str(workflow.id)}"],
                        ),
                        style="primary",
                    ),
                    block_builders.simple_button_block(
                        "Call Analysis",
                        "CALL_ANALYSIS",
                        action_id=action_with_params(
                            slack_consts.SEND_CALL_ANALYSIS_TO_DM,
                            [f"u={str(user.id)}&w={str(workflow.id)}"],
                        ),
                    ),
                ]
            ),
            block_builders.context_block(
                f"Your {'Salesforce' if user.crm == 'SALESFORCE' else 'HubSpot'} {'fields' if user.crm == 'SALESFORCE' else 'properties'} have been updated, please review."
            ),
        ]
    else:
        blocks = [
            block_builders.header_block("AI Generated Call Summary"),
            block_builders.context_block(f"Meeting: {meeting.topic}"),
            block_builders.simple_section(f"{error_message}", "mrkdwn"),
        ]
    try:
        slack_res = slack_requests.update_channel_message(
            user.slack_integration.channel,
            loading_res["message"]["ts"],
            user.organization.slack_integration.access_token,
            block_set=blocks,
        )
    except Exception as e:
        logger.exception(
            f"ERROR sending update channel message for chat submittion because of <{e}>"
        )
    return

