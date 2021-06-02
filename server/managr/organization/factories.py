import random
import factory
from factory.django import DjangoModelFactory

from managr.core.models import User

from managr.utils.numbers import generate_random_numbers

from .models import Account, Contact, Organization


# Factories go here


class AccountFactory(DjangoModelFactory):
    name = factory.Faker("company")
    url = factory.Faker("url")
    type = "NEW"

    class Meta:
        model = Account


class ContactFactory(DjangoModelFactory):
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    title = "Employee"
    email = factory.Faker("email")
    phone_number_1 = generate_random_numbers()
    phone_number_2 = generate_random_numbers()

    class Meta:
        model = Contact


class OrganizationFactory(DjangoModelFactory):
    name = factory.Faker("company")
    state = "ACTIVE"

    class Meta:
        model = Organization
