import json
import uuid
import random
import re

from django.utils import timezone
from django.test import TestCase

from background_task.models import CompletedTask, Task

from managr.core import factories as core_factories
from managr.organization import factories as org_factories
from managr.salesforce.models import SFResourceSync


def get_domain(email):
    """Parse domain out of an email"""
    return email[email.index("@") + 1 :]


class Meeting(TestCase):
    def setUp(self):
        self.admin_user = core_factories.UserFactory(
            is_admin=True, user_level="MANAGER", organization=org_factories.OrganizationFactory()
        )
        self.fake_meeting_participants_w_random = [
            {
                "name": "testertesty baker",
                "id": "",
                "user_email": f"{''.join([chr(random.randint(97, 122)) for x in range(random.randint(3,9))])}@{''.join([chr(random.randint(97, 122)) for x in range(random.randint(3,9))])}.com",
            },
            {
                "name": "another1 baker",
                "id": "",
                "user_email": f"{''.join([chr(random.randint(97, 122)) for x in range(random.randint(3,9))])}@{''.join([chr(random.randint(97, 122)) for x in range(random.randint(3,9))])}.com",
            },
        ]
        self.fake_meeting_participants_w_self = [
            {"name": "another1 baker", "id": "", "user_email": self.admin_user.email,},
        ]
        self.fake_meeting_participants_w_internal = [
            {
                "name": "another1 baker",
                "id": "",
                "user_email": f"{''.join([chr(random.randint(97, 122)) for x in range(random.randint(3,9))])}@{get_domain(self.admin_user.email)}",
            }
        ]
        self.fake_meeting_participants_w_resource_booking = [
            {
                "name": "another1 baker",
                "id": "",
                "user_email": f"{''.join([chr(random.randint(97, 122)) for x in range(random.randint(3,9))])}@resource.calendar.google.com",
            }
        ]

    def test_random_participants_joined_should_remove_self(self):
        participants = []
        zoom_participants = [
            *self.fake_meeting_participants_w_random,
            *self.fake_meeting_participants_w_self,
        ]
        org_email_domain = get_domain(self.admin_user.email)
        remove_users_with_these_domains_regex = r"(@[\w.]+calendar.google.com)|({})".format(
            org_email_domain
        )

        memo = {}
        for p in zoom_participants:
            if p.get("user_email", "") not in ["", None, *memo.keys()] and not re.search(
                remove_users_with_these_domains_regex, p.get("user_email", "")
            ):
                memo[p.get("user_email")] = len(participants)
                participants.append(p)
        self.assertEquals(len(participants), len(self.fake_meeting_participants_w_random))

    def test_random_participants_joined_should_remove_self_and_empty(self):
        participants = []
        zoom_participants = [
            *self.fake_meeting_participants_w_random,
            *self.fake_meeting_participants_w_self,
        ]
        zoom_participants[0]["user_email"] = ""
        org_email_domain = get_domain(self.admin_user.email)
        remove_users_with_these_domains_regex = r"(@[\w.]+calendar.google.com)|({})".format(
            org_email_domain
        )

        memo = {}
        for p in zoom_participants:
            if p.get("user_email", "") not in ["", None, *memo.keys()] and not re.search(
                remove_users_with_these_domains_regex, p.get("user_email", "")
            ):
                memo[p.get("user_email")] = len(participants)
                participants.append(p)
        self.assertEquals(len(participants), len(self.fake_meeting_participants_w_random) - 1)

    def test_random_participants_joined_should_remove_self_internal(self):
        participants = []
        zoom_participants = [
            *self.fake_meeting_participants_w_random,
            *self.fake_meeting_participants_w_self,
            *self.fake_meeting_participants_w_internal,
        ]

        org_email_domain = get_domain(self.admin_user.email)
        remove_users_with_these_domains_regex = r"(@[\w.]+calendar.google.com)|({})".format(
            org_email_domain
        )

        memo = {}
        for p in zoom_participants:
            if p.get("user_email", "") not in ["", None, *memo.keys()] and not re.search(
                remove_users_with_these_domains_regex, p.get("user_email", "")
            ):
                memo[p.get("user_email")] = len(participants)
                participants.append(p)
        self.assertEquals(len(participants), len(self.fake_meeting_participants_w_random))

    def test_random_participants_joined_should_remove_self_internal_duplicate_external(self):
        participants = []
        zoom_participants = [
            *self.fake_meeting_participants_w_random,
            *self.fake_meeting_participants_w_self,
            *self.fake_meeting_participants_w_internal,
        ]
        zoom_participants = [*zoom_participants, zoom_participants[0]]

        org_email_domain = get_domain(self.admin_user.email)
        remove_users_with_these_domains_regex = r"(@[\w.]+calendar.google.com)|({})".format(
            org_email_domain
        )

        memo = {}
        for p in zoom_participants:
            if p.get("user_email", "") not in ["", None, *memo.keys()] and not re.search(
                remove_users_with_these_domains_regex, p.get("user_email", "")
            ):
                memo[p.get("user_email")] = len(participants)
                participants.append(p)
        self.assertEquals(len(participants), len(self.fake_meeting_participants_w_random))

    def test_random_participants_joined_should_remove_self_internal_and_ignore_nylas_check(self):
        participants = []
        zoom_participants = [
            *self.fake_meeting_participants_w_self,
            *self.fake_meeting_participants_w_internal,
        ]
        nylas_participants = [
            {
                "name": "another1 baker",
                "id": "",
                "user_email": f"{''.join([chr(random.randint(97, 122)) for x in range(random.randint(3,9))])}@{''.join([chr(random.randint(97, 122)) for x in range(random.randint(3,9))])}.com",
            }
        ]

        org_email_domain = get_domain(self.admin_user.email)
        remove_users_with_these_domains_regex = r"(@[\w.]+calendar.google.com)|({})".format(
            org_email_domain
        )

        memo = {}
        for p in zoom_participants:
            if p.get("user_email", "") not in ["", None, *memo.keys()] and not re.search(
                remove_users_with_these_domains_regex, p.get("user_email", "")
            ):
                memo[p.get("user_email")] = len(participants)
                participants.append(p)
        if len(participants):
            for p in nylas_participants:
                if not re.search(
                    remove_users_with_these_domains_regex, p.get("user_email", "")
                ) and p.get("user_email", "") not in ["", None]:
                    if p.get("user_email", "") in memo.keys():
                        index = memo[p.get("user_email")]
                        participants[index]["name"] = p.get("name", "")
                    else:
                        memo[p.get("user_email")] = len(participants)
                        participants.append(p)

        self.assertEquals(len(participants), 0)

    def test_random_participants_joined_should_remove_self_include_nylas(self):
        participants = []
        zoom_participants = [
            *self.fake_meeting_participants_w_self,
            *self.fake_meeting_participants_w_random,
        ]
        nylas_participants = [
            {
                "name": "another1 baker",
                "id": "",
                "user_email": f"{''.join([chr(random.randint(97, 122)) for x in range(random.randint(3,9))])}@{''.join([chr(random.randint(97, 122)) for x in range(random.randint(3,9))])}.com",
            }
        ]
        org_email_domain = get_domain(self.admin_user.email)
        remove_users_with_these_domains_regex = r"(@[\w.]+calendar.google.com)|({})".format(
            org_email_domain
        )

        memo = {}
        for p in zoom_participants:
            if p.get("user_email", "") not in ["", None, *memo.keys()] and not re.search(
                remove_users_with_these_domains_regex, p.get("user_email", "")
            ):
                memo[p.get("user_email")] = len(participants)
                participants.append(p)
        if len(participants):
            for p in nylas_participants:
                if not re.search(
                    remove_users_with_these_domains_regex, p.get("user_email", "")
                ) and p.get("user_email", "") not in ["", None]:
                    if p.get("user_email", "") in memo.keys():
                        index = memo[p.get("user_email")]
                        participants[index]["name"] = p.get("name", "")
                    else:
                        memo[p.get("user_email")] = len(participants)
                        participants.append(p)

        self.assertEquals(
            len(participants),
            (len(self.fake_meeting_participants_w_random) + len(nylas_participants)),
        )

    def test_random_participants_joined_should_remove_self_and_nylas(self):
        participants = []
        zoom_participants = [
            *self.fake_meeting_participants_w_self,
            *self.fake_meeting_participants_w_random,
        ]
        nylas_participants = [*self.fake_meeting_participants_w_resource_booking]

        org_email_domain = get_domain(self.admin_user.email)
        remove_users_with_these_domains_regex = r"(@[\w.]+calendar.google.com)|({})".format(
            org_email_domain
        )

        memo = {}
        for p in zoom_participants:
            if p.get("user_email", "") not in ["", None, *memo.keys()] and not re.search(
                remove_users_with_these_domains_regex, p.get("user_email", "")
            ):
                memo[p.get("user_email")] = len(participants)
                participants.append(p)
        if len(participants):
            for p in nylas_participants:
                if not re.search(
                    remove_users_with_these_domains_regex, p.get("user_email", "")
                ) and p.get("user_email", "") not in ["", None]:
                    if p.get("user_email", "") in memo.keys():
                        index = memo[p.get("user_email")]
                        participants[index]["name"] = p.get("name", "")
                    else:
                        memo[p.get("user_email")] = len(participants)
                        participants.append(p)

        self.assertEquals(
            len(participants), len(self.fake_meeting_participants_w_random),
        )

    def test_random_participants_joined_should_remove_duplicates(self):
        participants = []
        zoom_participants = [
            *self.fake_meeting_participants_w_self,
            *self.fake_meeting_participants_w_random,
        ]
        nylas_participants = [
            *self.fake_meeting_participants_w_random,
        ]

        org_email_domain = get_domain(self.admin_user.email)
        remove_users_with_these_domains_regex = r"(@[\w.]+calendar.google.com)|({})".format(
            org_email_domain
        )

        memo = {}
        for p in zoom_participants:
            if p.get("user_email", "") not in ["", None, *memo.keys()] and not re.search(
                remove_users_with_these_domains_regex, p.get("user_email", "")
            ):
                memo[p.get("user_email")] = len(participants)
                participants.append(p)
        if len(participants):
            for p in nylas_participants:
                if not re.search(
                    remove_users_with_these_domains_regex, p.get("user_email", "")
                ) and p.get("user_email", "") not in ["", None]:
                    if p.get("user_email", "") in memo.keys():
                        index = memo[p.get("user_email")]
                        participants[index]["name"] = p.get("name", "")
                    else:
                        memo[p.get("user_email")] = len(participants)
                        participants.append(p)

        self.assertEquals(
            len(participants), len(self.fake_meeting_participants_w_random),
        )

    def test_random_participants_joined_should_fill_in_details(self):
        participants = []
        zoom_participants = [
            *self.fake_meeting_participants_w_self,
            *self.fake_meeting_participants_w_random,
        ]
        nylas_participants = [
            *self.fake_meeting_participants_w_random,
        ]
        nylas_participants[1]["name"] = "Change me"
        org_email_domain = get_domain(self.admin_user.email)
        remove_users_with_these_domains_regex = r"(@[\w.]+calendar.google.com)|({})".format(
            org_email_domain
        )

        memo = {}
        for p in zoom_participants:
            if p.get("user_email", "") not in ["", None, *memo.keys()] and not re.search(
                remove_users_with_these_domains_regex, p.get("user_email", "")
            ):
                memo[p.get("user_email")] = len(participants)
                participants.append(p)
        if len(participants):
            for p in nylas_participants:
                if not re.search(
                    remove_users_with_these_domains_regex, p.get("user_email", "")
                ) and p.get("user_email", "") not in ["", None]:
                    if p.get("user_email", "") in memo.keys():
                        index = memo[p.get("user_email")]
                        participants[index]["name"] = p.get("name", "")
                    else:
                        memo[p.get("user_email")] = len(participants)
                        participants.append(p)

        self.assertEquals(
            "Change me", participants[1]["name"],
        )

    def test_random_participants_joined_should_remove_resource_email(self):
        participants = []
        zoom_participants = [
            *self.fake_meeting_participants_w_self,
            *self.fake_meeting_participants_w_random,
        ]
        nylas_participants = [
            *self.fake_meeting_participants_w_resource_booking,
        ]

        org_email_domain = get_domain(self.admin_user.email)
        remove_users_with_these_domains_regex = r"(@[\w.]+calendar.google.com)|({})".format(
            org_email_domain
        )

        memo = {}
        for p in zoom_participants:
            if p.get("user_email", "") not in ["", None, *memo.keys()] and not re.search(
                remove_users_with_these_domains_regex, p.get("user_email", "")
            ):
                memo[p.get("user_email")] = len(participants)
                participants.append(p)
        if len(participants):
            for p in nylas_participants:
                if not re.search(
                    remove_users_with_these_domains_regex, p.get("user_email", "")
                ) and p.get("user_email", "") not in ["", None]:
                    if p.get("user_email", "") in memo.keys():
                        index = memo[p.get("user_email")]
                        participants[index]["name"] = p.get("name", "")
                    else:
                        memo[p.get("user_email")] = len(participants)
                        participants.append(p)

        self.assertEquals(len(participants), len(self.fake_meeting_participants_w_random))

