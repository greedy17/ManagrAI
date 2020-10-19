import factory
from factory.django import DjangoModelFactory
from managr.utils.numbers import generate_random_numbers
from .models import User


# Factories go here


class UserFactory(DjangoModelFactory):
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    email = factory.Faker("email")
    phone_number = generate_random_numbers()
    password = factory.Faker("password", length=10)
    is_active = True
    is_invited = True

    class Meta:
        model = User
