from django.core.management.base import BaseCommand, CommandError
from managr.lead.lead_score_generation import generate_lead_scores


class Command(BaseCommand):
    """ manage.py service to create service accounts """

    help = "Generate scores for all open leads"

    def handle(self, *args, **kwargs):
        generate_lead_scores()
        self.stdout.write(self.style.SUCCESS("Successfully generated scores"))
