import logging
import uuid
import time
import random

from django.conf import settings
from background_task import background
from rest_framework.exceptions import ValidationError

from ..exceptions import TokenExpired, InvalidRequest
from ..models import (
    SalesloftAuthAccount,
    SLAccount,
    Cadence,
    People,
    PeopleAdapter,
)
from managr.organization.models import Contact
from background_task.models import CompletedTask

from ..helpers.class_functions import (
    process_person,
    sync_current_slaccount_page,
    sync_current_person_page,
    sync_current_cadence_page,
    sync_current_account_page,
)

logger = logging.getLogger("managr")


def emit_sync_accounts(auth_account_id, verbose_name):
    return sync_accounts(auth_account_id, verbose_name=verbose_name)


def emit_sync_cadences(auth_account_id, verbose_name):
    return sync_cadences(auth_account_id, verbose_name=verbose_name)


def emit_sync_slaccounts(auth_account_id, verbose_name):
    return sync_slaccounts(auth_account_id, verbose_name=verbose_name)


def emit_sync_people(auth_account_id, verbose_name):
    return sync_people(auth_account_id, verbose_name=verbose_name)


def emit_add_cadence_membership(people_id, cadence_id):
    return add_cadence_membership(people_id, cadence_id)


@background()
def sync_accounts(auth_account_id):
    auth_account = SalesloftAuthAccount.objects.get(id=auth_account_id)
    while True:
        attempts = 1
        try:
            success = 0
            failed = 0
            res = auth_account.helper_class.get_users()
            initial_page = sync_current_account_page(res["data"], auth_account.id)
            success += initial_page["success"]
            failed += initial_page["failed"]
            if res["metadata"]["paging"]["total_pages"] > 1:
                count = 2
                while count <= res["metadata"]["paging"]["total_pages"] and count <= 20:
                    page_res = auth_account.helper_class.get_users(count)
                    curr_page = sync_current_account_page(page_res["data"], auth_account.id)
                    success += curr_page["success"]
                    failed += curr_page["failed"]
                    count += 1
            break
        except TokenExpired:
            if attempts >= 5:
                return logger.exception(
                    f"Failed to sync salesloft users for account {auth_account.id}"
                )
            else:
                auth_account.regenerate_token()
                attempts += 1
        except Exception as e:
            return logger.exception(f"Salesloft account exception: {e}")
    return logger.info(f"Synced {success}/{success+failed} users for {auth_account}")


@background()
def sync_cadences(auth_account_id):
    auth_account = SalesloftAuthAccount.objects.get(id=auth_account_id)
    while True:
        attempts = 1
        try:
            success = 0
            failed = 0
            res = auth_account.helper_class.get_cadences()
            initial_page = sync_current_cadence_page(res["data"])
            success += initial_page["success"]
            failed += initial_page["failed"]
            if res["metadata"]["paging"]["total_pages"] > 1:
                count = 2
                while count <= res["metadata"]["paging"]["total_pages"] and count <= 20:
                    page_res = auth_account.helper_class.get_cadences(count)
                    curr_page = sync_current_cadence_page(page_res["data"])
                    success += curr_page["success"]
                    failed += curr_page["failed"]
                    count += 1
            break
        except TokenExpired:
            if attempts >= 5:
                return logger.exception(
                    f"Failed to sync salesloft cadences for account {auth_account.id}"
                )
            else:
                auth_account.regenerate_token()
                attempts += 1
        except Exception as e:
            return logger.exception(f"Salesloft cadence exception: {e}")
    return logger.info(f"Synced {success}/{success+failed} cadences for {auth_account}")


@background()
def sync_slaccounts(auth_account_id):
    auth_account = SalesloftAuthAccount.objects.get(id=auth_account_id)
    while True:
        attempts = 1
        try:
            success = 0
            failed = 0
            res = auth_account.helper_class.get_accounts()
            initial_page = sync_current_slaccount_page(res["data"])
            success += initial_page["success"]
            failed += initial_page["failed"]
            if res["metadata"]["paging"]["total_pages"] > 1:
                count = 2
                while count <= res["metadata"]["paging"]["total_pages"] and count <= 20:
                    page_res = auth_account.helper_class.get_accounts(count)
                    curr_page = sync_current_slaccount_page(page_res["data"])
                    success += curr_page["success"]
                    failed += curr_page["failed"]
                    count += 1
            break
        except TokenExpired:
            if attempts >= 5:
                return logger.exception(
                    f"Failed to sync salesloft accounts for account {auth_account}"
                )
            else:
                auth_account.regenerate_token()
                attempts += 1
        except Exception as e:
            return logger.exception(f"Salesloft slaccount exception: {e}")
    return logger.info(f"Synced {success}/{success+failed} accounts for {auth_account}")


@background()
def sync_people(auth_account_id):
    auth_account = SalesloftAuthAccount.objects.get(id=auth_account_id)
    while True:
        attempts = 1
        try:
            success = 0
            failed = 0
            res = auth_account.helper_class.get_people()
            initial_page = sync_current_person_page(res["data"])
            success += initial_page["success"]
            failed += initial_page["failed"]
            if res["metadata"]["paging"]["total_pages"] > 1:
                count = 2
                while count <= res["metadata"]["paging"]["total_pages"] and count <= 20:
                    page_res = auth_account.helper_class.get_people(count)
                    curr_page = sync_current_person_page(page_res["data"])
                    success += curr_page["success"]
                    failed += curr_page["failed"]
                    count += 1
            break
        except TokenExpired:
            if attempts >= 5:
                return logger.exception(
                    f"Failed to sync salesloft accounts for account {auth_account}"
                )
            else:
                auth_account.regenerate_token()
                attempts += 1
        except Exception as e:
            return logger.exception(f"Salesloft people exception: {e}")
    return logger.info(f"Synced {success}/{success+failed} people for {auth_account}")


def add_cadence_membership(person_id, cadence_id):
    cadence = Cadence.objects.get(id=cadence_id)
    auth_account = SalesloftAuthAccount.objects.get(id=cadence.owner.auth_account.id)
    contact = Contact.objects.get(id=person_id)
    person = People.objects.filter(email=contact.email).first()
    slaccount = SLAccount.objects.get(name=contact.account.name)
    owner = slaccount.owner.salesloft_id
    people_id = person.people_id if person else None
    created = False
    while True:
        attempts = 1
        try:
            if not person:
                data = {
                    "first_name": contact.secondary_data["FirstName"],
                    "last_name": contact.secondary_data["LastName"],
                    "email_address": contact.email,
                    "owner_id": owner,
                    "account_id": slaccount.account_id,
                }
                create_res = PeopleAdapter.create_in_salesloft(auth_account.access_token, data)
                process_person(create_res["data"])
                people_id = create_res["data"]["id"]
                created = True

            res = cadence.helper_class.add_membership(people_id, auth_account.access_token)
            break
        except TokenExpired:
            if attempts >= 5:
                return logger.exception(
                    f"Failed to add Person with id {people_id} to Cadence {cadence.name}, could not regenerate token"
                )
            else:
                auth_account.regenerate_token()
                attempts += 1
        except InvalidRequest:
            return {"status": "Failed"}
        except ValidationError as e:
            logger.exception(f"Error adding cadence: {e}")
            return {"status": "Failed"}
        except Exception as e:
            logger.exception(f"Exception adding cadence: {e}")
            return {"status": "Failed"}
    logger.info(f"Person with id {people_id} added to cadence {cadence.id}")
    if created:
        return {"status": "Created"}
    return {"status": "Success"}


@background()
def sync_helper(auth_id):
    sync_steps = [emit_sync_accounts, emit_sync_slaccounts, emit_sync_people, emit_sync_cadences]
    sl_account = SalesloftAuthAccount.objects.get(id=auth_id)
    v_name = str(uuid.uuid4())
    has_error = False
    current_task = None
    for step in sync_steps:
        if has_error:
            logger.exception(f"SALESLOFT SYNC ERROR ON TASK: {current_task}")
            break
        logger.info(f"Scheduling task {step} for {sl_account}")
        attempts = 1
        sync_step = step(str(sl_account.id), f"{step.__name__}_{v_name}")
        current_task = sync_step.verbose_name
        while True:
            if attempts >= 10:
                has_error = True
                break
            try:
                task = (
                    CompletedTask.objects.filter(task_hash=sync_step.task_hash)
                    .order_by("-run_at")
                    .first()
                )
                if task and task.verbose_name == f"{step.__name__}_{v_name}":
                    logger.info(f"COMPLETED SALESLOFT SYNC TASK:{task}")
                    break
                else:
                    attempts += 1
                    sleep = 1 * 2 ** attempts + random.uniform(0, 1)
                    time.sleep(sleep)
            except Exception as e:
                logger.exception(f"Salesloft sync helper: {e}")
                attempts += 1
    return
