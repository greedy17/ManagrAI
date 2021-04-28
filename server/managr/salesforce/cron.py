import logging
import kronos
from datetime import datetime
import logging
import math

from django.conf import settings
from django.template.loader import render_to_string
from django.utils import timezone
from django.db.models import Q, F, Func, IntegerField, DateField, Sum
from django.db.models.functions import Cast


from background_task.models import CompletedTask

from rest_framework.response import Response

from managr.api.emails import send_html_email
from managr.salesforce import constants as sf_consts
from managr.salesforce.background import (
    emit_gen_next_sync,
    emit_gen_next_object_field_sync,
    _process_stale_data_for_delete,
)
from managr.salesforce.models import SFObjectFieldsOperation, SFResourceSync, SalesforceAuthAccount
from managr.core.models import User

from managr.slack import constants as slack_const
from managr.slack.helpers import auth as slack_auth
from managr.slack.helpers import requests as slack_requests
from managr.slack.helpers import interactions as slack_interactions
from managr.slack.helpers import block_builders
from managr.slack.helpers.block_sets import get_block_set
from managr.slack.models import UserSlackIntegration
from managr.api.decorators import log_all_exceptions, sf_api_exceptions
from managr.slack.helpers.exceptions import (
    UnHandeledBlocksException,
    InvalidBlocksFormatException,
    InvalidBlocksException,
    InvalidAccessToken,
)
from managr.salesforce.adapter.exceptions import (
    TokenExpired,
    FieldValidationError,
    RequiredFieldError,
    SFQueryOffsetError,
    SFNotFoundError,
    InvalidRefreshToken,
)

logger = logging.getLogger("managr")


class ArrayLength(Func):
    function = "CARDINALITY"


@kronos.register("*/10  * * * *")
def queue_users_sf_resource(force_all=False):
    """ 
        runs every 12 hours and initiates user sf syncs if their prev workflow is done 
        force_all will attempt all failed and not faild
    """
    sf_accounts = SalesforceAuthAccount.objects.filter(user__is_active=True)
    for account in sf_accounts:
        logger.info(f"syncing data for {account.user.email}")
        # get latest workflow
        if not force_all:
            flows = SFResourceSync.objects.filter(user=account.user)
            if not flows.count():
                init_sf_resource_sync(account.user.id)
            latest_flow = flows.latest("datetime_created") if flows else None
            if latest_flow and latest_flow.progress == 100:
                logger.info(
                    f"SF_LATEST_RESOURCE_SYNC --- Operation id {str(latest_flow.id)}, email {latest_flow.user.email}"
                )
                init_sf_resource_sync(latest_flow.user.id)
            elif latest_flow and latest_flow.progress != 100:
                # check to see if the tasks were completed but not recorded
                completed_tasks = set(latest_flow.completed_operations)
                all_tasks = set(latest_flow.operations)
                tasks_diff = list(all_tasks - completed_tasks)
                for task_hash in tasks_diff:
                    # check to see if there was a problem completing the flow but all tasks are ready
                    task = CompletedTask.objects.filter(task_hash=task_hash).count()
                    if task:
                        latest_flow.completed_operations.append(task_hash)

                latest_flow.save()
                if latest_flow.progress == 100:
                    init_sf_resource_sync(account.user.id)

        else:
            init_sf_resource_sync(account.user.id)

    return


@kronos.register("0 */12 * * *")
def queue_users_sf_fields(force_all=False):
    """ 
        runs every 12 hours and initiates user sf syncs if their prev workflow is done 
        force_all will attempt all failed and not faild
    """
    sf_accounts = SalesforceAuthAccount.objects.filter(user__is_active=True)
    for account in sf_accounts:
        # get latest workflow
        if not force_all:
            flows = SFObjectFieldsOperation.objects.filter(user=account.user)
            if not flows.count():
                init_sf_field_sync(account.user)
            latest_flow = flows.latest("datetime_created") if flows else None
            if latest_flow and latest_flow.progress == 100:
                logger.info(
                    f"SF_LATEST_RESOURCE_SYNC --- Operation id {str(latest_flow.id)}, email {latest_flow.user.email}"
                )
                init_sf_field_sync(latest_flow.user)
            elif latest_flow and latest_flow.progress != 100:
                # check to see if the tasks were completed but not recorded
                completed_tasks = set(latest_flow.completed_operations)
                all_tasks = set(latest_flow.operations)
                tasks_diff = list(all_tasks - completed_tasks)
                for task_hash in tasks_diff:
                    # check to see if there was a problem completing the flow but all tasks are ready
                    task = CompletedTask.objects.filter(task_hash=task_hash).count()
                    if task:
                        latest_flow.completed_operations.append(task_hash)

                latest_flow.save()
                if latest_flow.progress == 100:
                    init_sf_field_sync(account.user)

        else:
            init_sf_field_sync(account.user)
        # if latest workflow is at 100 emit sf resource sync
    return


@kronos.register("*/60 * * * *")
def report_sf_data_sync(sf_account=None):
    """ runs every 60 mins and initiates user sf syncs if their prev workflow is done """
    # latest_flow total_flows total_incomplete_flows total_day_flows total_incomplete_day_flows
    reports = []
    if not sf_account:
        # get all reports
        sf_accounts = SalesforceAuthAccount.objects.filter(user__is_active=True)
        for account in sf_accounts:
            report = get_report_data(account)
            reports.append(report)
    else:
        report = get_report_data(sf_account)
        reports.append(report)

    subject = render_to_string("salesforce/sync_report-subject.txt")
    recipient = [settings.STAFF_EMAIL]
    send_html_email(
        subject,
        "salesforce/sync_report.html",
        settings.SERVER_EMAIL,
        recipient,
        context={"data": reports},
    )

    # if latest workflow is at 100 emit sf resource sync
    return


@kronos.register("0 */24 * * *")
def queue_stale_sf_data_for_delete(cutoff=1440):
    """ 
        This should queue stale data for delete, it should only do this for users who are active and who have an sf account 
        In the future we will be having a flag for users who's salesforce token is soft revoked aka, they would like to pause the sync 
        or for whom we are having issues and they would like to refresh their token, for these users we should not be deleting data
    """
    resource_items = []
    limit = 0
    pages = 1
    # get users who are active and have a salesforce_account
    qs = User.objects.filter(is_active=True, salesforce_account__isnull=False).distinct()
    # count them to paginate the response
    user_count = qs.count()
    # set limit of 100 or less
    limit = max(100, user_count)
    # divide into pages
    pages = math.ceil(user_count / limit)
    # cutoff of 1 day
    cutoff = timezone.now() - timezone.timedelta(minutes=cutoff)

    for i in range(0, pages):
        users = qs[i * limit : i + 1 * limit].select_related("salesforce_account")
        for user in users:
            # only run this for users with a successful latest flow
            flows = SFResourceSync.objects.filter(user=user)
            latest_flow = not flows.latest("datetime_created").in_progress if flows else False
            field_flows = SFObjectFieldsOperation.objects.filter(user=user)
            latest_field_flow = (
                not field_flows.latest("datetime_created").in_progress if field_flows else False
            )

            if not latest_flow and not latest_field_flow:
                logger.info(
                    f"skipping clear data for user {user.email} with id {str(user.id)} because the latest field and resource flow were not successful"
                )
                continue

            elif not latest_flow and latest_field_flow:

                logger.info(
                    f"skipping clear resource data (fields only) for user {user.email} with id {str(user.id)} because the latest resource flow was not successful"
                )
                resource_items = [
                    "sobjectfield",
                    "sobjectvalidation",
                    "sobjectpicklist",
                ]
            elif latest_flow and not latest_field_flow:
                logger.info(
                    f"skipping clear field data (resources only) for user {user.email} with id {str(user.id)} because the latest resource flow was not successful"
                )
                resource_items.extend(
                    ["opportunity", "account", "contact", "lead",]
                )
            else:
                resource_items.extend(
                    [
                        "sobjectfield",
                        "sobjectvalidation",
                        "sobjectpicklist",
                        "opportunity",
                        "account",
                        "contact",
                        "lead",
                    ]
                )

            for r in resource_items:

                try:
                    qs = getattr(user, f"imported_{r}").filter(last_edited__lt=cutoff)
                    resource_count = qs.count()

                    if resource_count and resource_count <= 500:
                        # emit current batch to delete queue and start new
                        # TODO - Eventually remove the .now to make async
                        _process_stale_data_for_delete.now(
                            [
                                {
                                    "user_id": str(user.id),
                                    "resource": {r: qs.values_list("id", flat=True)},
                                }
                            ],
                        )
                    elif resource_count and resource_count > 500:
                        # create make into batches of 500 and send
                        resource_pages = 1
                        resource_pages = math.ceil(resource_count / 500)
                        for i in range(0, resource_pages):
                            items = qs[i * 500 : i + 1 * 500].values_list("id", flat=True)
                            # TODO - Eventually remove the .now to make async
                            _process_stale_data_for_delete.now(
                                [
                                    {
                                        "user_id": str(user.id),
                                        "resource": {r: items.values_list("id", flat=True)},
                                    }
                                ],
                            )

                except AttributeError as e:
                    logger.info(f"{user.email} does not have {r} to delete {e}")
                    continue


def init_sf_resource_sync(user_id):
    operations = [
        sf_consts.RESOURCE_SYNC_ACCOUNT,
        sf_consts.RESOURCE_SYNC_CONTACT,
        sf_consts.RESOURCE_SYNC_OPPORTUNITY,
        sf_consts.RESOURCE_SYNC_LEAD,
    ]
    scheduled_time = timezone.now()
    formatted_time = scheduled_time.strftime("%Y-%m-%dT%H:%M%Z")
    return emit_gen_next_sync(str(user_id), operations, formatted_time)


def init_sf_field_sync(user):
    logger.info(f"Initiating Object Field Sync for User {str(user.id)} with email {user.email}")
    operations = [
        f"{sf_consts.SALESFORCE_OBJECT_FIELDS}.{sf_consts.RESOURCE_SYNC_ACCOUNT}",
        f"{sf_consts.SALESFORCE_OBJECT_FIELDS}.{sf_consts.RESOURCE_SYNC_CONTACT}",
        f"{sf_consts.SALESFORCE_OBJECT_FIELDS}.{sf_consts.RESOURCE_SYNC_LEAD}",
        f"{sf_consts.SALESFORCE_OBJECT_FIELDS}.{sf_consts.RESOURCE_SYNC_OPPORTUNITY}",
        f"{sf_consts.SALESFORCE_PICKLIST_VALUES}.{sf_consts.RESOURCE_SYNC_LEAD}",
        f"{sf_consts.SALESFORCE_PICKLIST_VALUES}.{sf_consts.RESOURCE_SYNC_ACCOUNT}",
        f"{sf_consts.SALESFORCE_PICKLIST_VALUES}.{sf_consts.RESOURCE_SYNC_CONTACT}",
        f"{sf_consts.SALESFORCE_PICKLIST_VALUES}.{sf_consts.RESOURCE_SYNC_OPPORTUNITY}",
    ]
    if user.is_admin:
        # we only need validations to show the user who is creating the forms

        operations.extend(
            [
                f"{sf_consts.SALESFORCE_VALIDATIONS}.{sf_consts.RESOURCE_SYNC_ACCOUNT}",
                f"{sf_consts.SALESFORCE_VALIDATIONS}.{sf_consts.RESOURCE_SYNC_CONTACT}",
                f"{sf_consts.SALESFORCE_VALIDATIONS}.{sf_consts.RESOURCE_SYNC_OPPORTUNITY}",
                f"{sf_consts.SALESFORCE_VALIDATIONS}.{sf_consts.RESOURCE_SYNC_LEAD}",
            ]
        )

    scheduled_time = timezone.now()
    formatted_time = scheduled_time.strftime("%Y-%m-%dT%H:%M%Z")
    emit_gen_next_object_field_sync(str(user.id), operations, formatted_time)
    return


def get_report_data(account):
    workflows = SFResourceSync.objects.filter(user=account.user)
    total_workflows = workflows.count()
    total_incomplete_flows = (
        workflows.annotate(
            progress_l=Sum(
                ArrayLength("completed_operations")
                + ArrayLength("failed_operations")
                - ArrayLength("operations"),
                output_field=IntegerField(),
            )
        )
        .filter(progress_l__lt=0)
        .count()
    )
    todays_flows = (
        workflows.annotate(creation_date=Cast("datetime_created", DateField()))
        .filter(creation_date=datetime.now().date())
        .order_by("-creation_date")
    ).count()
    todays_failed_flows = (
        workflows.annotate(
            progress_l=Sum(
                ArrayLength("completed_operations")
                + ArrayLength("failed_operations")
                - ArrayLength("operations"),
                output_field=IntegerField(),
            )
        )
        .annotate(creation_date=Cast("datetime_created", DateField()))
        .filter(creation_date=datetime.now().date(), progress_l__lt=0)
        .values_list("creation_date", flat=True)
        .order_by("-creation_date")
    ).count()
    latest_flow = SFResourceSync.objects.filter(user=account.user)
    if latest_flow:
        latest_flow = latest_flow.latest("datetime_created")
        latest_flow_data = {}
        if latest_flow:
            latest_flow_data = {
                "date_time": latest_flow.datetime_created.strftime("%m/%d/%Y, %H:%M"),
                "progress": latest_flow.progress,
                "status": latest_flow.status,
            }

    return {
        "user": f"{account.user.email}-{account.user.id}",
        "total_workflows": total_workflows,
        "total_incomplete_workflows": total_incomplete_flows,
        "todays_workflows": todays_flows,
        "todays_failed_flows": todays_failed_flows,
        "latest_flow": latest_flow_data if latest_flow else None,
    }

