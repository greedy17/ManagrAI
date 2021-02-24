import logging
import json
import pytz
from datetime import datetime

from background_task import background

from rest_framework.exceptions import ValidationError

from managr.core.calendars import calendar_participants_from_zoom_meeting

from managr.slack.helpers import requests as slack_requests
from managr.slack.helpers.block_sets import get_block_set
from managr.organization.models import Contact, Account
from managr.opportunity.models import Opportunity
from managr.salesforce.adapter.models import ContactAdapter


from .. import constants as zoom_consts
from ..zoom_helper.exceptions import TokenExpired
from ..models import ZoomAuthAccount, ZoomMeeting, MeetingReview
from ..serializers import ZoomMeetingSerializer

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


def emit_push_meeting_contacts(meeting_id):
    meeting_id = str(meeting_id)
    return _push_meeting_contacts(meeting_id)


def emit_refresh_zoom_token(zoom_account_id, schedule):
    # scedule can be seconds int or datetime string
    zoom_account_id = str(zoom_account_id)
    schedule = datetime.strptime(schedule, "%Y-%m-%dT%H:%M")
    return _refresh_zoom_token(zoom_account_id, schedule=schedule)


def emit_process_past_zoom_meeting(user_id, meeting_uuid, send_slack=True):
    return _get_past_zoom_meeting_details(user_id, meeting_uuid, send_slack)


def emit_kick_off_slack_interaction(user_id, managr_meeting_id):
    return _kick_off_slack_interaction(user_id, managr_meeting_id)


def emit_save_meeting_review_data(managr_meeting_id, data):
    return _save_meeting_review_data(managr_meeting_id, data)


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


@background(schedule=0)
def _push_meeting_contacts(meeting_id):
    """ After a meeting is reviewed this task will create contacts for whom we have and email or a lastName (required by sf)"""
    from managr.salesforce.background import emit_add_c_role_to_opp

    meeting = ZoomMeeting.objects.filter(id=meeting_id).first()
    if meeting:
        # find contacts and push them to sf
        contacts_not_in_sf = list(
            filter(lambda contact: not contact["from_integration"], meeting.participants)
        )
        contacts_in_sf = list(
            filter(lambda contact: contact["from_integration"], meeting.participants)
        )
        user = meeting.zoom_account.user
        if hasattr(user, "salesforce_account"):
            sf = user.salesforce_account
            # add the contacts with the details to sf place the id int source and user
            created_contacts = []
            not_created_contacts = []
            for index, contact in enumerate(contacts_not_in_sf):

                if not contact["email"] or not len(contact["email"]):
                    not_created_contacts.append(contact)
                    continue
                # if a contact doesnt have a last name append N/A so we can at least add them
                last_name = contact.get("secondary_data", {}).get("LastName")
                contact["secondary_data"]["LastName"] = last_name if last_name else "N/A"
                if meeting.meeting_resource == "Account":
                    # add the account external id
                    contact["external_account"] = str(meeting.linked_account.integration_id)

                contact = {**contact, **contact.get("secondary_data", {})}
                del contact["secondary_data"]
                while True:
                    attempts = 0
                    try:
                        res = ContactAdapter.create_new_contact(
                            contact,
                            sf.access_token,
                            sf.instance_url,
                            sf.object_fields.get("Contact", {}).get("fields", {}),
                        )
                        contact["integration_id"] = res["id"]
                        contact["integration_source"] = "SALESFORCE"
                        # contact from integration source is still False
                        # we use this to show a message that we created the contact
                        created_contacts.append(contact)
                        # meeting.participants
                        break
                    except TokenExpired:
                        if attempts >= 5:
                            logger.exception(
                                f"Failed to refresh user token for Salesforce operation add contact to sf failed {str(meeting.id)}"
                            )
                            break
                        else:
                            sf.regenerate_token()
                            attempts += 1

            if len(contacts_not_in_sf):
                meeting.participants = [
                    ### NOTE THE ORDER HERE IS IMPORTANT FOR REMOVING FROM MEETING
                    *not_created_contacts,
                    *created_contacts,
                    *meeting.participants[len(contacts_not_in_sf) :],
                ]
                meeting.save()
            if meeting.meeting_resource != "Account":
                "Leads and Opportunities need to have a contact role"
                for contact in [*created_contacts, *contacts_in_sf]:
                    emit_add_c_role_to_opp(
                        str(user.id), str(meeting.opportunity.id), contact["integration_id"]
                    )

            else:
                for contact in contacts_in_sf:
                    contact["account"] = str(meeting.linked_account.integration_id)
                    contact["external_account"] = contact["account"]

                    ContactAdapter.update_contact(
                        {
                            "account": contact["account"],
                            "external_acount": contact["external_account"],
                        },
                        sf.access_token,
                        sf.instance_url,
                        contact["integration_id"],
                        sf.object_fields.get("Contact", {}).get("fields", {}),
                    )

        block_set_context = {
            "m": str(meeting.id),
            "show_contacts": True,
        }
        ts, channel = meeting.slack_interaction.split("|")
        res = slack_requests.update_channel_message(
            channel,
            ts,
            user.organization.slack_integration.access_token,
            block_set=get_block_set("final_meeting_interaction", context=block_set_context),
        ).json()

        meeting.slack_interaction = f"{res['ts']}|{res['channel']}"
        meeting.save()

    # emit event to create contact role
    # save to the meeting
    # update the slack message

    return meeting


@background(schedule=0)
def _get_past_zoom_meeting_details(user_id, meeting_uuid, original_duration, send_slack=True):
    logger.info("Retrieving past Zoom meeting details...")

    # SEND SLACK IS USED FOR TESTING ONLY
    zoom_account = ZoomAuthAccount.objects.filter(user__id=user_id).first()
    if zoom_account and not zoom_account.is_revoked:
        # emit the process
        try:
            meeting = zoom_account.helper_class.get_past_meeting(meeting_uuid)
            meeting = meeting.get_past_meeting_participants(zoom_account.access_token)
        except TokenExpired:
            zoom_account.regenerate_token()
            return _get_past_zoom_meeting_details(user_id, meeting_uuid, original_duration)

        meeting.original_duration = original_duration

        #
        logger.info(f"    Got Meeting: {meeting} with ID: {meeting.id}")
        logger.info(f"    Meeting Start: {meeting.start_time}")
        logger.info(f"    Meeting End: {meeting.end_time}")

        # Gather Meeting Participants from Zoom and Calendar
        logger.info("Gathering meeting participants...")
        zoom_participants = meeting.as_dict.get("participants", None)

        logger.info(f"    Zoom Participants: {zoom_participants}")

        # Gather unique emails from the Zoom Meeting participants
        participants = []
        user = zoom_account.user
        for participant in zoom_participants:
            if participant not in participants and participant.get("user_email") != user.email:
                participants.append(participant)

        # If the user has their calendar connected through Nylas, find a
        # matching meeting and gather unique participant emails.
        calendar_participants = calendar_participants_from_zoom_meeting(meeting, user)

        # Combine the sets of participants. Filter out empty emails and the meeting owner
        participants = [
            p
            for p in [*zoom_participants, *calendar_participants]
            if p.get("user_email") not in [None, "", user.email]
        ]

        logger.info(f"    Got list of participants: {participants}")

        if len(participants):
            # Reduce to set of unique participant emails
            participant_emails = set([p.get("user_email") for p in participants])

            meeting_contacts = []

            # find existing contacts

            existing_contacts = Contact.objects.filter(
                email__in=participant_emails, owner__organization__id=user.organization.id
            ).exclude(email=user.email)
            # convert all contacts to model representation and remove from array
            for contact in existing_contacts:
                formatted_contact = contact.adapter_class.as_dict
                formatted_contact["from_integration"] = True
                meeting_contacts.append(formatted_contact)
                for index, participant in enumerate(participants):
                    if (
                        participant["user_email"] == contact.email
                        or participant["user_email"] == user.email
                    ):
                        del participants[index]

            meeting_contacts = [
                *list(
                    filter(
                        lambda x: len(x.get("secondary_data", dict())) or x.get("email"),
                        list(
                            map(
                                lambda participant: {
                                    **ContactAdapter(
                                        **dict(
                                            email=participant["user_email"],
                                            # these will only get stored if lastname and firstname are accessible from sf
                                            external_owner=user.salesforce_account.salesforce_id,
                                            secondary_data={
                                                "FirstName": _split_first_name(participant["name"]),
                                                "LastName": _split_last_name(participant["name"]),
                                            },
                                        )
                                    ).as_dict,
                                    "from_integration": False,
                                },
                                participants,
                            ),
                        ),
                    )
                ),
                *meeting_contacts,
            ]

            opportunity = Opportunity.objects.filter(
                contacts__email__in=participant_emails, owner__organization__id=user.organization.id
            ).first()
            if opportunity:
                meeting.opportunity = opportunity.id
                if opportunity.account:
                    meeting.linked_account = opportunity.account.id
            else:
                account = Account.objects.filter(
                    contacts__email__in=participant_emails,
                    owner__organization__id=user.organization.id,
                ).first()
                if account:
                    meeting.linked_account = account.id

            meeting.participants = meeting_contacts
            serializer = ZoomMeetingSerializer(data=meeting.as_dict)

            try:
                serializer.is_valid(raise_exception=True)
                serializer.save()
            except ValidationError as e:
                logger.exception(
                    f"Unable to save and initiate slack for meeting with uuid "
                    f"{meeting_uuid} because of error {json.dumps(e.detail)}"
                )
                return e

            # emit the event to start slack interaction
            if send_slack:
                emit_kick_off_slack_interaction(user_id, str(serializer.instance.id))
            return serializer.instance


@background(schedule=0)
def _kick_off_slack_interaction(user_id, managr_meeting_id):
    # get meeting
    meeting = ZoomMeeting.objects.filter(id=managr_meeting_id).first()
    if meeting:
        # get user
        user = meeting.zoom_account.user

        if hasattr(user, "slack_integration"):
            user_slack_channel = user.slack_integration.channel
            slack_org_access_token = user.organization.slack_integration.access_token
            block_set = get_block_set("initial_meeting_interaction", {"m": managr_meeting_id,},)
            res = slack_requests.send_channel_message(
                user_slack_channel, slack_org_access_token, block_set=block_set
            ).json()

            # save slack message ts and channel id to remove if the meeting is deleted before being filled
            meeting.slack_interaction = f"{res['ts']}|{res['channel']}"
            meeting.save()


@background(schedule=0)
def _save_meeting_review_data(managr_meeting_id, data):
    data = json.loads(data)

    meeting = ZoomMeeting.objects.filter(id=managr_meeting_id).first()
    meeting.interaction_status = zoom_consts.MEETING_INTERACTION_STATUS_COMPLETE
    meeting.is_closed = True
    meeting.save()
    if not hasattr(meeting, "meeting_review"):
        date = data.get("close_date", None)
        if date:
            ## make it aware by adding utc
            date = datetime.strptime(date, "%Y-%m-%d")
            date = pytz.utc.localize(date)
        obj = dict()
        obj["meeting"] = meeting
        obj["meeting_type"] = data.get("meeting_type", None)
        obj["forecast_category"] = data.get("forecast_category", None)
        obj["stage"] = data.get("stage", None)
        obj["description"] = data.get("description", None)
        obj["next_step"] = data.get("next_step", None)
        obj["close_date"] = date
        obj["sentiment"] = data.get("sentiment", None)
        obj["amount"] = data.get("amount", None)

        return MeetingReview.objects.create(**obj)


# same method as _save_meeting_review_data but not as a task
