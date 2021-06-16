from django.test import TestCase


from managr.core import factories as core_factories
from managr.organization import factories as org_factories
from managr.salesforce.models import SalesforceAuthAccount
from managr.salesforce.adapter.exceptions import CannotRetreiveObjectType

# Create your tests here.


class UserTestCase(TestCase):
    def setUp(self):
        self.admin_user = core_factories.UserFactory(
            is_admin=True, user_level="MANAGER", organization=org_factories.OrganizationFactory()
        )
        self.salesforce_account = SalesforceAuthAccount.objects.create(
            user=self.admin_user,
            sobjects={"Account": True, "Contact": True, "Lead": True, "Opportunity": True},
        )

    def test_resource_sync_opts(self):
        sobjects = {"Account": True, "Contact": True, "Lead": True, "Opportunity": True}
        self.assertEqual(
            self.salesforce_account.resource_sync_opts,
            list(map(lambda obj: obj if sobjects[obj] else False, sobjects)),
        )

    def test_resource_sync_opts_on_error(self):
        sf_acc = self.salesforce_account
        try:
            raise CannotRetreiveObjectType
        except CannotRetreiveObjectType:
            sobjects = {"Account": True, "Contact": True, "Lead": False, "Opportunity": True}
            pass
        sf_acc.sobjects = sobjects
        sf_acc.save()
        self.assertEqual(
            self.salesforce_account.resource_sync_opts,
            list(filter(lambda obj: obj if sobjects[obj] else None, sobjects)),
        )

    def test_field_sync_opts_admin(self):
        sobjects = {"Account": True, "Contact": True, "Lead": True, "Opportunity": True}
        self.assertEqual(
            self.salesforce_account.field_sync_opts,
            list(
                map(
                    lambda resource: f"OBJECT_FIELDS.{resource}",
                    filter(
                        lambda resource: resource
                        if sobjects.get(resource, None) not in ["", None, False]
                        else False,
                        sobjects,
                    ),
                )
            ),
        )

    def test_field_sync_opts_admin_on_error(self):
        sf_acc = self.salesforce_account
        try:
            raise CannotRetreiveObjectType
        except CannotRetreiveObjectType:
            sobjects = {"Account": True, "Contact": True, "Lead": False, "Opportunity": True}
            pass
        sf_acc.sobjects = sobjects
        sf_acc.save()

        self.assertEqual(
            self.salesforce_account.field_sync_opts,
            list(
                map(
                    lambda resource: f"OBJECT_FIELDS.{resource}",
                    filter(
                        lambda resource: resource
                        if sobjects.get(resource, None) not in ["", None, False]
                        else False,
                        sobjects,
                    ),
                )
            ),
        )

    def test_validation_sync_opts_admin(self):
        sf_acc = self.salesforce_account
        try:
            raise CannotRetreiveObjectType
        except CannotRetreiveObjectType:
            sobjects = {"Account": True, "Contact": True, "Lead": False, "Opportunity": True}
            pass
        sf_acc.sobjects = sobjects
        sf_acc.save()

        self.assertEqual(
            self.salesforce_account.validation_sync_opts,
            list(
                map(
                    lambda resource: f"VALIDATIONS.{resource}",
                    filter(
                        lambda resource: resource
                        if sobjects.get(resource, None) not in ["", None, False]
                        else False,
                        sobjects,
                    ),
                )
            ),
        )

    def test_non_validation_sync_opts(self):
        sf_acc = self.salesforce_account
        try:
            raise CannotRetreiveObjectType
        except CannotRetreiveObjectType:
            sobjects = {"Account": True, "Contact": True, "Lead": False, "Opportunity": True}
            pass
        sf_acc.sobjects = sobjects
        sf_acc.save()

        self.assertEqual(
            self.salesforce_account.validation_sync_opts,
            list(
                map(
                    lambda resource: f"VALIDATIONS.{resource}",
                    filter(
                        lambda resource: resource
                        if sobjects.get(resource, None) not in ["", None, False]
                        else False,
                        sobjects,
                    ),
                )
            ),
        )

