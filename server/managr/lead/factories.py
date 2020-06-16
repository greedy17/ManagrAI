import random
import factory
from factory.django import DjangoModelFactory

from .models import Lead, CallNote


class LeadFactory(DjangoModelFactory):
    """Generate a Lead with random attributes"""

    title = factory.Faker("sentence")
    amount = factory.LazyAttribute(lambda a: random.randint(1, 30) * 1000)
    primary_description = factory.Faker("text", max_nb_chars=150)
    secondary_description = factory.Faker("text", max_nb_chars=150)

    class Meta:
        model = Lead


class CallNoteFactory(DjangoModelFactory):
    title = factory.Faker("sentence")
    content = factory.Faker("sentence")

    class Meta:
        model = CallNote
