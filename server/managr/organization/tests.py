from django.test import TestCase

from .models import Organization
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
