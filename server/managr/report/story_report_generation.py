import logging

from django.utils import timezone
from rest_framework.exceptions import ValidationError

from managr.core.models import EmailAuthAccount
from managr.core.nylas.emails import send_new_email_legacy
from managr.lead import constants as lead_constants
from managr.lead.models import ActionChoice, Action, Lead
from managr.organization.models import Contact
from managr.organization.serializers import ContactSerializer
from managr.utils.sites import get_site_url

from .models import StoryReport

logger = logging.getLogger("managr")


def generate_story_report_data(story_report_id, generated_by_id):
    """
    Given a StoryReport UUID, generate the report's
    data and update the instance with the generated data.
    Finally, trigger email regarding report availability to
    user that triggered this story_report to be generated.
    """
    story_report = StoryReport.objects.get(
        generated_by=generated_by_id,
        pk=story_report_id
    )

    lead = story_report.lead
    if lead.status.title != lead_constants.LEAD_STATUS_CLOSED:
        logger.exception(f"Attempted to generate story report for open lead {lead.id}")
        raise ValidationError(f"Attempted to generate story report for open lead {lead.id}")

    # generate report's data
    story_report.data['lead'] = LeadDataGenerator(lead).as_dict
    story_report.data['representative'] = RepresentativeDataGenerator(lead).as_dict
    story_report.data['organization'] = OrganizationDataGenerator(lead).as_dict
    story_report.datetime_generated = timezone.now()
    story_report.save()

    # send email to user that generated report
    send_email(story_report)


def send_email(report):
    recipient = report.generated_by

    try:
        ea = EmailAuthAccount.objects.filter(user__is_serviceaccount=True).first()
    except EmailAuthAccount.DoesNotExist:
        # currently passing if there is an error, when we are ready we will require this
        pass
    if ea:
        token = ea.access_token
        sender = {"email": ea.email_address, "name": "Managr"}
        recipient = [
            {"email": recipient.email, "name": recipient.full_name}
        ]
        message = {
            "subject": f"Story Report Generated for {report.lead.title}",
            "body": f"The report is available at {report.client_side_url}."
        }
        try:
            send_new_email_legacy(token, sender, recipient, message)
        except Exception as e:
            """ this error is most likely going to be an error on our set
            up rather than the user_token """
            pass


class BaseGenerator:
    def __init__(self, lead):
        self._lead = lead
        self._representative = lead.claimed_by
        self._organization = self._representative.organization


class LeadDataGenerator(BaseGenerator):
    """
    Generates lead-level metrics for StoryReport.
    Final output is the self.as_dict method.
    """

    @property
    def lead_activity_logs(self):
        """
        Only include the actions logged from last time this rep claimed the lead,
        though to the closing of the lead.
        """
        return self._lead.activity_logs.filter(
            action_timestamp__gte=self.claimed_timestamp,
            action_timestamp__lte=self._lead.expected_close_date,
            action_taken_by=self._representative,
        )

    @property
    def claimed_timestamp(self):
        """
        Given lead, return timestamp for latest claim-event.
        """
        # NOTE (Bruno 8-11-20): currently, a claim-event does not
        # take place on lead creation. Hence conditional herein.
        claimed_event = self._lead.activity_logs.filter(
            activity=lead_constants.LEAD_CLAIMED
        ).first()
        if claimed_event:
            return claimed_event.action_timestamp
        return self._lead.datetime_created

    @property
    def ready_timestamp(self):
        """
        Find newest READY, because this salesperson may have picked it more than once.
        """
        logged_ready = self.lead_activity_logs.filter(
            activity=lead_constants.LEAD_UPDATED,
            meta__extra__status_update=True,
            meta__extra__new_status=lead_constants.LEAD_STATUS_READY,
        ).first()
        if logged_ready:
            return logged_ready.action_timestamp

    @property
    def booked_timestamp(self):
        """
        Find first BOOKED, because this salesperson may have picked it more than once.
        """
        logged_booked = self.lead_activity_logs.filter(
            activity=lead_constants.LEAD_UPDATED,
            meta__extra__status_update=True,
            meta__extra__new_status=lead_constants.LEAD_STATUS_BOOKED,
        ).last()
        if logged_booked:
            return logged_booked.action_timestamp

    @property
    def demo_timestamp(self):
        """
        Find first DEMO, because this salesperson may have picked it more than once.
        """
        logged_demo = self.lead_activity_logs.filter(
            activity=lead_constants.LEAD_UPDATED,
            meta__extra__status_update=True,
            meta__extra__new_status=lead_constants.LEAD_STATUS_DEMO,
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
        calls = self.lead_activity_logs.filter(activity=lead_constants.CALL_NOTE_CREATED)
        texts = self.lead_activity_logs.filter(activity=lead_constants.MESSAGE_SENT)
        emails = self.lead_activity_logs.filter(activity=lead_constants.EMAIL_SENT)
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

        if not bool(contact_map):
            return None
        # NOTE (Bruno): if more than one contact have same count of comms.
        # actions, the first one is returned.
        primary_contact_id = max(contact_map, key=lambda key: contact_map[key])
        primary_contact = Contact.objects.get(pk=primary_contact_id)
        return ContactSerializer(primary_contact).data

    @property
    def call_count(self):
        return self.lead_activity_logs.filter(activity=lead_constants.CALL_NOTE_CREATED).count()

    @property
    def text_count(self):
        return self.lead_activity_logs.filter(activity=lead_constants.MESSAGE_SENT).count()

    @property
    def email_count(self):
        return self.lead_activity_logs.filter(activity=lead_constants.EMAIL_SENT).count()

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
    def action_count(self):
        """
        Generate count of actions for lead, performed by representative that closed the lead.
        """
        return self.lead_activity_logs.filter(activity=lead_constants.ACTION_CREATED).count()

    @property
    def days_to_closed(self):
        if self.ready_timestamp:
            return (self.closed_timestamp - self.ready_timestamp).days
        return (self.closed_timestamp - self.claimed_timestamp).days

    @property
    def days_ready_to_booked(self):
        if not self.ready_timestamp or not self.booked_timestamp:
            return None
        if self.ready_timestamp > self.booked_timestamp:
            return None
        return (self.booked_timestamp - self.ready_timestamp).days

    @property
    def days_booked_to_demo(self):
        if not self.booked_timestamp or not self.demo_timestamp:
            return None
        if self.booked_timestamp > self.demo_timestamp:
            return None
        return (self.demo_timestamp - self.booked_timestamp).days

    @property
    def days_to_demo(self):
        if not self.demo_timestamp:
            return None
        if self.ready_timestamp and not (self.ready_timestamp > self.demo_timestamp):
            return (self.demo_timestamp - self.ready_timestamp).days
        return (self.demo_timestamp - self.claimed_timestamp).days

    @property
    def days_demo_to_closed(self):
        if not self.demo_timestamp:
            return None
        return (self.closed_timestamp - self.demo_timestamp).days

    @property
    def contract_value(self):
        return self._lead.closing_amount

    @property
    def as_dict(self):
        return {
            'contract_value': self.contract_value,
            'days_to_closed': self.days_to_closed,
            'days_ready_to_booked': self.days_ready_to_booked,
            'days_booked_to_demo': self.days_booked_to_demo,
            'days_to_demo': self.days_to_demo,
            'days_demo_to_closed': self.days_demo_to_closed,
            'primary_contact': self.primary_contact,
            'call_count': self.call_count,
            'text_count': self.text_count,
            'email_count': self.email_count,
            'custom_action_counts': self.custom_action_counts,
            'action_count': self.action_count,
        }


class RepresentativeDataGenerator(BaseGenerator):
    """
    Generates representative-level metrics for StoryReport.
    Final output is the self.as_dict method.
    """
    @property
    def leads(self):
        closed_leads = Lead.objects.filter(
            claimed_by=self._representative,
            status__title=lead_constants.LEAD_STATUS_CLOSED,
        )
        return [LeadDataGenerator(lead).as_dict for lead in closed_leads]

    def average_for(self, property, rounding_places=0, as_integer=True):
        total = 0
        count = 0
        for lead in self.leads:
            if lead.get(property):
                total += lead[property]
                count += 1
        if count == 0:
            return None
        if as_integer:
            return int(round(total / count, rounding_places))
        return round(total / count, rounding_places)

    @property
    def average_custom_action_counts(self):
        totals = {}
        counts = {}
        for lead in self.leads:
            for action_choice_title, count in lead['custom_action_counts'].items():
                if totals.get(action_choice_title):
                    totals[action_choice_title] += count
                    counts[action_choice_title] += 1
                else:
                    totals[action_choice_title] = count
                    counts[action_choice_title] = 1

        averages = {}
        for action_choice_title, aggregate in totals.items():
            averages[action_choice_title] = int(round(aggregate / counts[action_choice_title]))
        return averages

    @property
    def as_dict(self):
        return {
            'average_contract_value': self.average_for('contract_value', rounding_places=2, as_integer=False),
            'average_days_to_closed': self.average_for('days_to_closed'),
            'average_days_ready_to_booked': self.average_for('days_ready_to_booked'),
            'average_days_booked_to_demo': self.average_for('days_booked_to_demo'),
            'average_days_to_demo': self.average_for('days_to_demo'),
            'average_days_demo_to_closed': self.average_for('days_demo_to_closed'),
            'average_call_count': self.average_for('call_count'),
            'average_text_count': self.average_for('text_count'),
            'average_email_count': self.average_for('email_count'),
            'average_custom_action_counts': self.average_custom_action_counts,
            'average_action_count': self.average_for('action_count'),
        }


class OrganizationDataGenerator(BaseGenerator):
    """
    Generates organization-level metrics for StoryReport.
    Final output is the self.as_dict method.
    """

    @property
    def representatives(self):
        return self._organization.users.all()

    def generate_representative_leads(self, representative):
        closed_leads = Lead.objects.filter(
            claimed_by=representative,
            status__title=lead_constants.LEAD_STATUS_CLOSED,
        )
        return [LeadDataGenerator(lead).as_dict for lead in closed_leads]

    def average_for(self, property, rounding_places=0):
        total = 0
        count = 0
        for representative in self.representatives:
            leads = self.generate_representative_leads(representative)
            for lead in leads:
                if lead.get(property):
                    total += lead[property]
                    count += 1
        if count == 0:
            return None
        return int(round(total / count, rounding_places))

    @property
    def as_dict(self):
        return {
            'average_call_count': self.average_for('call_count'),
            'average_text_count': self.average_for('text_count'),
            'average_email_count': self.average_for('email_count'),
            'average_action_count': self.average_for('action_count'),
        }
