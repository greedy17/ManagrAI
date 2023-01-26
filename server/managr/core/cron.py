import logging
import re
import uuid
import kronos
import datetime

from django.utils import timezone
from django.db.models import Q

from managr.slack.helpers import block_builders, block_sets
from managr.alerts.models import AlertConfig
from managr.core import constants as core_consts
from managr.core.models import NylasAuthAccount, User, MeetingPrepInstance
from managr.core.nylas.auth import revoke_access_token
from managr.core.background import (
    check_for_time,
    check_workflows_count,
    emit_process_send_workflow_reminder,
    check_for_uncompleted_meetings,
)

from managr.slack.helpers import requests as slack_requests
from managr.slack.helpers.block_sets import get_block_set
from managr.organization.models import Contact
from managr.salesforce.adapter.models import ContactAdapter
from managr.zoom.background import _split_first_name, _split_last_name
from managr.core.serializers import MeetingPrepInstanceSerializer
from managr.opportunity.models import Lead, Opportunity
from managr.organization.models import Account
from managr.slack.models import OrgCustomSlackForm, OrgCustomSlackFormInstance
from managr.slack import constants as slack_consts
from managr.salesforce.models import MeetingWorkflow


NOTIFICATION_TITLE_STALLED_IN_STAGE = "Opportunity Stalled in Stage"
NOTIFICATION_TITLE_INACTIVE = "Opportunity Inactive"


NOTIFICATION_TITLE_LAPSED_1 = "Opportunity expected close date lapsed by at least 1 day"
NOTIFICATION_TITLE_LAPSED_14 = "Opportunity expected close date lapsed by at least 14 days"
NOTIFICATION_TITLE_LAPSED_30 = "Opportunity expected close date lapsed by at least 30 days"


logger = logging.getLogger("managr")


def to_date_string(date):
    if not date:
        return "n/a"
    d = datetime.datetime.strptime(date, "%Y-%m-%d")
    return d.strftime("%a, %B %d, %Y")


def meeting_prep(processed_data, user_id, invocation=1, send_slack=True):
    def get_domain(email):
        """Parse domain out of an email"""
        return email[email.index("@") + 1 :]

    user = User.objects.get(id=user_id)
    ignore_emails = user.organization.ignore_emails
    meeting = {}
    # Getting all participants from meetings and all their emails
    all_participants = processed_data.get("participants")
    all_emails = []
    for participant in all_participants:
        participants_email = participant.get("email")
        all_emails.append(participants_email)

    meeting = {}

    # all emails are now in participant_emails

    # Gather Meeting Participants from Zoom and Calendar
    # Gather unique emails from the Zoom Meeting participants
    participants = []
    user = User.objects.get(id=user_id)

    org_email_domain = get_domain(user.email)
    remove_users_with_these_domains_regex = r"(@[\w.]+calendar.google.com)|({})".format(
        org_email_domain
    )
    for email in ignore_emails:
        remove_users_with_these_domains_regex = (
            remove_users_with_these_domains_regex + r"|({})".format(email)
        )
    # re.search(remove_users_with_these_domains_regex, p.get("email", ""))
    #### first check if we care about this meeting before going forward

    should_register_this_meeting = [
        p
        for p in all_participants
        if not re.search(remove_users_with_these_domains_regex, p.get("email", ""))
    ]

    if not len(should_register_this_meeting):
        return

    memo = {}
    for p in all_participants:
        if p.get("email", "") not in ["", None, *memo.keys()] and not re.search(
            remove_users_with_these_domains_regex, p.get("email", "")
        ):
            memo[p.get("email")] = len(participants)
            participants.append(p)

    # If the user has their calendar connected through Nylas, find a
    # matching meeting and gather unique participant emails.
    # calendar_participants = calendar_participants_from_zoom_meeting(meeting, user)

    # Combine the sets of participants. Filter out empty emails, meeting owner, and any
    # emails with domains that match the owner, which are teammates of the owner.
    for p in all_participants:
        if not re.search(remove_users_with_these_domains_regex, p.get("email", "")) and p.get(
            "email", ""
        ) not in ["", None]:
            if p.get("email", "") in memo.keys():
                index = memo[p.get("email")]
                participants[index]["name"] = p.get("name", "")
            else:
                memo[p.get("email")] = len(participants)
                participants.append(p)

    contact_forms = []
    if len(participants):
        # Reduce to set of unique participant emails
        participant_emails = set([p.get("email") for p in participants])
        meeting_contacts = []
    # find existing contacts

    existing_contacts = Contact.objects.filter(
        email__in=participant_emails, owner__organization__id=user.organization.id
    ).exclude(email=user.email)
    # convert all contacts to model representation and remove from array
    for contact in existing_contacts:
        formatted_contact = contact.adapter_class.as_dict

        # create a form for each contact to save to workflow
        meeting_contacts.append(formatted_contact)
        for index, participant in enumerate(participants):
            if participant["email"] == contact.email or participant["email"] == User.email:
                del participants[index]
    new_contacts = list(
        filter(
            lambda x: len(x.get("secondary_data", dict())) or x.get("email"),
            list(
                map(
                    lambda participant: {
                        **ContactAdapter(
                            **dict(
                                email=participant["email"],
                                # these will only get stored if lastname and firstname are accessible from sf
                                external_owner=user.salesforce_account.salesforce_id,
                                secondary_data={
                                    "FirstName": _split_first_name(participant["name"]),
                                    "LastName": _split_last_name(participant["name"]),
                                    "Email": participant["email"],
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
    meeting_resource_data = dict(resource_id="", resource_type="")
    opportunity = Opportunity.objects.filter(
        contacts__email__in=participant_emails, owner__id=user.id
    ).first()
    if opportunity:
        meeting_resource_data["resource_id"] = str(opportunity.id)
        meeting_resource_data["resource_type"] = "Opportunity"
    else:
        account = Account.objects.filter(
            contacts__email__in=participant_emails, owner__id=user.id,
        ).first()
        if account:
            meeting_resource_data["resource_id"] = str(account.id)
            meeting_resource_data["resource_type"] = "Account"
        else:
            lead = Lead.objects.filter(email__in=participant_emails, owner__id=user.id).first()
            if lead:
                meeting_resource_data["resource_id"] = str(lead.id)
                meeting_resource_data["resource_type"] = "Lead"

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
            organization=user.organization,
        ).first()
        if not template:
            logger.exception(
                f"Unable to find Contact Form template for user {str(user_id)}, email {user.email} cannot create initial form for meeting review"
            )
            contact["_form"] = None
        else:
            # create instance
            form = OrgCustomSlackFormInstance.objects.create(
                user=user,
                template=template,
                resource_id="" if contact.get("id") in ["", None] else contact.get("id"),
            )
            contact_forms.append(form)
            contact["_form"] = str(form.id)
    event_data = processed_data
    processed_data.pop("participants")
    data = {
        "user": user.id,
        "participants": meeting_contacts,
        "event_data": event_data,
        "invocation": invocation,
    }
    resource_check = meeting_resource_data.get("resource_id", None)
    provider = processed_data.get("provider")

    if resource_check:
        data["resource_id"] = meeting_resource_data["resource_id"]
        data["resource_type"] = meeting_resource_data["resource_type"]

    # Creates Meeting Prep Instance
    serializer = MeetingPrepInstanceSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    serializer.save()

    meeting_prep_instance = (
        MeetingPrepInstance.objects.filter(user=user).order_by("-datetime_created").first()
    )

    # Conditional Check for Zoom meeting or Non-Zoom Meeting
    if provider != [None, "zoom"]:
        # Google Meet (Non-Zoom)
        meeting_workflow = MeetingWorkflow.objects.create(
            non_zoom_meeting=meeting_prep_instance, user=user,
        )

        # Sending end_times, workflow_id, and user values to emit function
        non_zoom_end_times = processed_data.get("times").get("end_time")
        workflow_id = str(meeting_workflow.id)
        user_id = str(user.id)
        user_tz = str(user.timezone)
        return emit_non_zoom_meetings(workflow_id, user_id, user_tz, non_zoom_end_times)


def process_current_alert_list(user_id):
    user = User.objects.get(id=user_id)
    configs = AlertConfig.objects.filter(Q(template__user=user.id, template__is_active=True))
    alert_blocks = [
        block_builders.simple_section(f":eyes: *Pipeline Monitor*", "mrkdwn"),
    ]
    if configs:
        for config in configs:
            channel_info = slack_requests.get_channel_info(
                user.organization.slack_integration.access_token, config.recipients[0]
            )
            name = channel_info.get("channel").get("name")
            alert_blocks = [
                *alert_blocks,
                block_builders.simple_section(f"{config.template.title}: #{name}", "mrkdwn"),
            ]
    else:
        alert_blocks.append(
            block_builders.simple_section("Your pipeline look good today :thumbsup: ", "mrkdwn")
        )
    return alert_blocks


@kronos.register("0 0 * * *")
def revoke_tokens():
    expire = timezone.now() + datetime.timedelta(days=5)
    """ revokes tokens for email auth accounts in state of sync_error, stopped, invalid """
    nylas_tokens = NylasAuthAccount.objects.filter(
        sync_status__in=core_consts.NYLAS_SYNC_STATUSES_FAILING, last_edited__gte=expire
    ).values_list("access_token", flat=True)
    for token in nylas_tokens:
        revoke_access_token(token)
