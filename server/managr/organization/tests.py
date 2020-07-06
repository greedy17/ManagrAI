from django.test import TestCase
from faker import Faker
from .models import Organization, Account
from .serializers import AccountSerializer
from .factories import AccountFactory, OrganizationFactory
# Create your tests here.


class OrganizationTestCase(TestCase):

    def setUp(self):
        self.org = OrganizationFactory()

    def test_org_has_no_users(self):
        # check that an org has been created with 0 users
        self.assertEqual(self.org.users.all().count(), 0,)


class AccountTestCase(TestCase):

    def setUp(self):
        self.org = OrganizationFactory()

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
        serializer = AccountSerializer(data=accounts, many=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        # get org accounts
        self.assertGreaterEqual(self.org.accounts.all().count(), 30,)
