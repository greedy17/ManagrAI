from django.utils import timezone

from managr.lead import constants
from managr.lead.models import ActionChoice, Action
from managr.organization.models import Contact
from managr.organization.serializers import ContactSerializer

def generate_story_report_data(story_report):
    """
    Given an instance of StoryReport, generate the report's
    data and update the instance with the generated data.
    Finally, trigger email regarding report generation to
    user that triggered this story_report to be generated.
    """
    # NOTE: lead/account/organization DB data is to be added into Response
    # as part of the serialization step, not here.
    story_report.data['lead'] = LeadDataGenerator(story_report).as_dict
    story_report.data['representative'] = RepresentativeDataGenerator(story_report).as_dict
    story_report.data['organization'] = OrganizationDataGenerator(story_report).as_dict
    story_report.datetime_generated = timezone.now()
    story_report.save()
    # trigger email


# lead ref
# account ref

# lead-level statistics:
# -x- comms. calls/texts/emails/actions for deal
# -x- primary contact
# -x- number of actions to close the deal
# -x- custom actions for deal:
#       -- all custom actions, sorted by count (tie-breaker by alphabetical)
# -x- READY to CLOSED (backup is CLAIMED to CLOSED)
# -x- days to first demo
# -x- days post demo
# -x- days ready to booked
# -x- days booked to demo
# -x- days from demo to closed

# rep-level statistics:
# -- average closing time for a lead
# -- average contract value
# -- average days ready to booked
# -- average days booked to demo
# -- average actions to close the deal
# -- average days from demo to closed
# -- average 'days in entire sales cycle` (READY to CLOSED or backup CLAIMED to CLOSED)
# -- average calls/texts/emails/actions per deal

# org-level statistics:
# -- average calls/texts/emails/actions per deal

class LeadDataGenerator:
    """
    Generates lead-level metrics for StoryReport.
    Final output is the self.as_dict method.

    Lead/account/organization DB data is to be added into Response
    as part of the serialization step, not here.
    """
    def __init__(
        self,
        story_report,
    ):
        self._story_report = story_report
        self._lead = story_report.lead
        self._representative = self._lead.claimed_by
        self._organization = self._representative.organization

    @property
    def lead_activity_logs(self):
        """
        Only include the actions logged from last time this rep claimed the lead,
        though to the closing of the lead.
        """
        return self._lead.activity_logs.filter(
            action_timestamp__gte=self.claimed_timestamp
            action_timestamp__lte=self._lead.expected_close_date,
            action_taken_by=self._representative,
        )

    @property
    def claimed_timestamp(self):
        """
        Given lead, return timestamp for latest claim-event.
        """
        # can assume that there has been at least one claim-event for lead.
        return self._lead.activity_logs.filter(
            activity=lead_constants.LEAD_CLAIMED
        ).first().action_timestamp

    @property
    def ready_timestamp(self):
        """
        Find newest READY, because this salesperson may have picked it more than once.
        """
        logged_ready = self.lead_activity_logs.filter(
            activity=constants.LEAD_UPDATED,
            meta__extra__status_update=True,
            meta__extra__new_status=constants.LEAD_STATUS_READY,
        ).first()
        if logged_ready:
            return logged_ready.action_timestamp

    @property
    def booked_timestamp(self):
        """
        Find first BOOKED, because this salesperson may have picked it more than once.
        """
        logged_booked = self.lead_activity_logs.filter(
            activity=constants.LEAD_UPDATED,
            meta__extra__status_update=True,
            meta__extra__new_status=constants.LEAD_STATUS_BOOKED,
        ).last()
        if logged_booked:
            return logged_booked.action_timestamp

    @property
    def demo_timestamp(self):
        """
        Find first DEMO, because this salesperson may have picked it more than once.
        """
        logged_demo = self.lead_activity_logs.filter(
            activity=constants.LEAD_UPDATED,
            meta__extra__status_update=True,
            meta__extra__new_status=constants.LEAD_STATUS_DEMO,
        ).last()
        if logged_demo:
            return logged_demo.action_timestamp

    @property
    def closed_timestamp(self):
        return self._lead.expected_close_date

    @property
    def primary_contact(self):
        """
        Based on communications (calls/texts/emails), which contact associated
        with lead was most contacted.
        Returns Contact instance.
        """
        calls = self.lead_activity_logs.filter(activity=constants.CALL_NOTE_CREATED)
        texts = self.lead_activity_logs.filter(activity=constants.MESSAGE_SENT)
        emails = self.lead_activity_logs.filter(activity=constants.EMAIL_SENT)
        contact_map = {}
        for call in calls:
            if call.meta.get('linked_contacts'):
                for contact in call.meta['linked_contacts']:
                    if contact_map.get(contact):
                        contact_map[contact] += 1
                    else:
                        contact_map[contact] = 1

        for text in texts:
            if text.meta.get('linked_contacts'):
                for contact in text.meta['linked_contacts']:
                    if contact_map.get(contact):
                        contact_map[contact] += 1
                    else:
                        contact_map[contact] = 1

        for email in emails:
            if email.meta.get('linked_contacts'):
                for contact in email.meta['linked_contacts']:
                    if contact_map.get(contact):
                        contact_map[contact] += 1
                    else:
                        contact_map[contact] = 1

        # NOTE (Bruno): if more than one contact have same count of comms.
        # actions, the first one is returned.
        primary_contact_id = max(contact_map, key=lambda key: contact_map[key])
        return Contact.objects.get(pk=primary_contact_id)

    @property
    def communication_counts(self):
        """
        Generate count of communications (calls/texts/email) for lead.
        """
        call_count = self.lead_activity_logs.filter(activity=constants.CALL_NOTE_CREATED).count()
        text_count = self.lead_activity_logs.filter(activity=constants.MESSAGE_SENT).count()
        email_count = self.lead_activity_logs.filter(activity=constants.EMAIL_SENT).count()
        return {
            'call_count': call_count,
            'text_count': text_count,
            'email_count': email_count,
        }

    @property
    def custom_action_counts(self):
        """
        Generate count of custom (org-level) actions for lead.
        """
        action_count_map = {}
        custom_actions = self._organization.action_choices
        for action_choice in custom_actions.all():
            action_count_map[action_choice.title] = action_choice.action_set.filter(
                lead=self._lead,
                created_by=self._representative,
                datetime_created__gte=self.claimed_timestamp,
                datetime_created__lte=self._lead.expected_close_date,
            ).count()
        return action_count_map

    # NOTE (Bruno): not sure how relevant this property is, since self.custom_action_counts
    # may cover it. Keeping it here for further testing once we have real data.
    @property
    def actions_count(self):
        """
        Generate count of actions for lead, performed by representative that closed the lead.
        """
        return self.lead_activity_logs.filter(activity=constants.ACTION_CREATED).count()

    @property
    def as_dict(self):
        return {
            'timestamps': {
                'claimed': self.claimed_timestamp,
                'ready': self.ready_timestamp,
                'booked': self.booked_timestamp,
                'demo': self.demo_timestamp,
                'closed': self.closed_timestamp,
            }
            'primary_contact': ContactSerializer(self.primary_contact).data
            'communication_counts': self.communication_counts,
            'custom_action_counts': self.custom_action_counts,
            'actions_count': self.actions_count,
        }
