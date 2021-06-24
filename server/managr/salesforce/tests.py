import json
import uuid

from django.utils import timezone
from django.test import TestCase

from background_task.models import CompletedTask, Task

from managr.core import factories as core_factories
from managr.organization import factories as org_factories
from managr.salesforce.models import SalesforceAuthAccount, SFResourceSync, SObjectField
from managr.salesforce.adapter.exceptions import CannotRetreiveObjectType
from managr.slack.models import OrgCustomSlackForm, FormField
from managr.slack import constants as slack_consts


# Create your tests here.


class SfSyncTestCase(TestCase):
    def setUp(self):
        self.admin_user = core_factories.UserFactory(
            is_admin=True, user_level="MANAGER", organization=org_factories.OrganizationFactory()
        )

        self.salesforce_account = SalesforceAuthAccount.objects.create(
            user=self.admin_user,
            sobjects={"Account": True, "Contact": True, "Lead": True, "Opportunity": True},
        )

        self.resource_sync = SFResourceSync.objects.create(
            operations_list=["test", "test"], user=self.admin_user
        )

    def test_reconciles_less_100(self):
        for i in range(0, 4):
            resource_sync = self.resource_sync
            task_params = [
                [
                    "7cfd2353-942d-4ff7-a0ff-47be5ebde745",
                    f"{str(self.resource_sync.id)}",
                    "Lead",
                    200,
                    0,
                ],
                {},
            ]
            t = Task.objects.create(
                task_params=json.dumps(task_params),
                run_at=timezone.now(),
                task_name="managr.salesforce.background._process_resource_sync",
                queue="SALESFORCE_RESOURCE_SYNC",
                task_hash=str(uuid.uuid4()),
            )

            t_dict = t.__dict__
            del t_dict["_state"]
            t_dict["attempts"] = 1
            c = CompletedTask.objects.create(**t_dict)
            if i != 3:
                resource_sync.completed_operations.append(c.task_hash)

            resource_sync.operations.append(t.task_hash)
            resource_sync.save()

        self.assertEquals(self.resource_sync.progress, 75)
        self.resource_sync.reconcile()
        self.assertEquals(self.resource_sync.progress, 100)

    def test_reconciles_more_100(self):
        for i in range(0, 4):
            resource_sync = self.resource_sync
            task_params = [
                [
                    "7cfd2353-942d-4ff7-a0ff-47be5ebde745",
                    f"{str(self.resource_sync.id)}",
                    "Lead",
                    200,
                    0,
                ],
                {},
            ]
            t = Task.objects.create(
                task_params=json.dumps(task_params),
                run_at=timezone.now(),
                task_name="managr.salesforce.background._process_resource_sync",
                queue="SALESFORCE_RESOURCE_SYNC",
                task_hash=str(uuid.uuid4()),
            )

            t_dict = t.__dict__
            del t_dict["_state"]
            t_dict["attempts"] = 1
            c = CompletedTask.objects.create(**t_dict)

            resource_sync.completed_operations.append(c.task_hash)
            if i != 3:
                resource_sync.operations.append(t.task_hash)
            resource_sync.save()

        self.assertEquals(self.resource_sync.progress, 133)
        self.resource_sync.reconcile()
        self.assertEquals(self.resource_sync.progress, 100)

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

    def test_generates_forms_with_public_fields(self):
        for form in slack_consts.INITIAL_FORMS:
            resource, form_type = form.split(".")

            f = OrgCustomSlackForm.objects.create(
                form_type=form_type, resource=resource, organization=self.admin_user.organization
            )

            public_fields = SObjectField.objects.filter(
                is_public=True,
                id__in=slack_consts.DEFAULT_PUBLIC_FORM_FIELDS.get(resource, {}).get(form_type, []),
            )
            for i, field in enumerate(public_fields):
                f.fields.add(field, through_defaults={"order": i})
            f.save()

            self.assertEquals(
                f.formfield_set.count(),
                len(slack_consts.DEFAULT_PUBLIC_FORM_FIELDS.get(resource, {}).get(form_type, [])),
            )
