import os
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from managr.core.cron import generate_meeting_scores


class Command(BaseCommand):

    help = "Generate scores for closed meetings"

    def handle(self, *args, **kwargs):

        generate_meeting_scores()

        self.stdout.write(self.style.SUCCESS("Successfully sent notifications"))

