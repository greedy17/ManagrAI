import random
import uuid
import factory
from django.utils import timezone
from factory.django import DjangoModelFactory

from .models import Opportunity


class OpportunityFactory(DjangoModelFactory):
    """Generate a Opportunity with random attributes"""

    name = factory.Faker("sentence")
    amount = factory.LazyAttribute(lambda a: random.randint(1, 30) * 1000)
    close_date = factory.LazyAttribute(
        lambda a: timezone.now() + timezone.timedelta(random.randint(1, 30))
    )
    integration_id = factory.LazyAttribute(lambda a: str(uuid.uuid4()))
    stage = factory.Faker("name")

    class Meta:
        model = Opportunity
