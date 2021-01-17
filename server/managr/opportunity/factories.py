import random
import factory
from django.utils import timezone
from factory.django import DjangoModelFactory

from .models import Opportunity


class LeadFactory(DjangoModelFactory):
    """Generate a Opportunity with random attributes"""

    title = factory.Faker("sentence")
    amount = factory.LazyAttribute(lambda a: random.randint(1, 30) * 1000)
    primary_description = factory.Faker("text", max_nb_chars=150)
    secondary_description = factory.Faker("text", max_nb_chars=150)

    class Meta:
        model = Opportunity
