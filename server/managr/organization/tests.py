import copy
import json
from django.test import TestCase
from faker import Faker
from django.test import RequestFactory

from managr.core.models import User

from .models import Organization, Account
from .serializers import AccountSerializer
from .factories import AccountFactory, OrganizationFactory


# Create your tests here.


class MockRequest:
    def __init__(self, user):
        self.user = user


class OrganizationTestCase(TestCase):
    def setUp(self):
        self.org = OrganizationFactory()

    def test_org_has_no_users(self):
        # check that an org has been created with 0 users
        self.assertEqual(
            self.org.users.all().count(), 0,
        )


class AccountTestCase(TestCase):
    fixtures = ["dev.json"]

    def setUp(self):
        self.org = Organization.objects.first()
        self.user = self.org.users.first()
        self.request = MockRequest(self.user)

    def test_account_created_to_org(self):
        # test to see if an account was created and set to an org
        acc = AccountFactory(organization=self.org)
        self.assertEqual(acc.organization, self.org)

    def test_account_bulk_create(self):
        # create random fake accounts to add in bulk
        accounts = []
        for i in range(30):
            faker = Faker()
            acc = dict(name=faker.name(), url=faker.url())
            accounts.append(acc)
        serializer = AccountSerializer(
            data=accounts, context={"request": self.request}, many=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        # get org total accounts number

        self.assertGreaterEqual(
            self.org.accounts.all().count(), 30,
        )

    def test_account_bulk_update(self):
        faker = Faker()
        acc = AccountFactory(organization=self.org)
        updated_acc = {"id": acc.id, "name": faker.name(), "url": acc.url}

        serializer = AccountSerializer(
            acc, data=updated_acc, context={"request": self.request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        self.assertEqual(serializer.data["name"], updated_acc["name"])
