import json
import uuid

from django.utils import timezone
from django.test import TestCase

from background_task.models import CompletedTask, Task

from managr.core import factories as core_factories
from managr.organization import factories as org_factories
from managr.salesforce.models import SFResourceSync


# Create your tests here.


class SfSyncTestCase(TestCase):
    def setUp(self):
        self.admin_user = core_factories.UserFactory(
            is_admin=True, user_level="MANAGER", organization=org_factories.OrganizationFactory()
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

            resource_sync.completed_operations.append(c.task_hash)
            if i != 3:
                resource_sync.operations.append(t.task_hash)
            resource_sync.save()

        self.assertEquals(self.resource_sync.progress, 133)
        self.resource_sync.reconcile()
        self.assertEquals(self.resource_sync.progress, 100)
