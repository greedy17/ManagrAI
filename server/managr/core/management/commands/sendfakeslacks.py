from django.core.management.base import BaseCommand, CommandError
from managr.salesforce.background import _process_resource_sync
from managr.core.models import User


class Command(BaseCommand):
    help = "Helper for dev to send slack messages"

    def handle(self, *args, **options):
        u = User.objects.get(email="pari@thinknimble.com")
        _process_resource_sync.now(str(u.id), "test", "Opportunity", 300, 0)

