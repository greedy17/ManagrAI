import random
import factory
from factory.django import DjangoModelFactory

from managr.core.models import User
from managr.lead.factories import LeadFactory
from managr.utils.numbers import generate_random_numbers

from .models import Account, Contact


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


def gen_random_test_data():
    """Quick script to generate random accounts, contacts, and leads."""
    u = User.objects.get(email="test@thinknimble.com")
    o = u.organization

    # Create 30 accounts
    for i in range(30):
        account = AccountFactory(organization=o)
        print(f"Created Account: '{account.name}'")

        # Create one to four contacts per account
        contacts = []
        for i in range(random.randint(1, 4)):
            contact = ContactFactory(account=account)
            print(f"    Created Contact: '{contact}'")
            contacts.append(contact)

        # Create one to three leads per account
        for i in range(random.randint(1, 3)):
            lead = LeadFactory(account=account)
            print(f"    Created Lead: '{contact}'")
            lead.linked_contacts.add(*contacts)
