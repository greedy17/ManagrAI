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
from managr.salesforce.background import emit_gen_next_sync, emit_gen_next_object_field_sync
from managr.salesforce.models import SFObjectFieldsOperation, SFResourceSync, SalesforceAuthAccount
from managr.core.models import User

from managr.slack import constants as slack_const
from managr.slack.helpers import auth as slack_auth
from managr.slack.helpers import requests as slack_requests
from managr.slack.helpers import interactions as slack_interactions
from managr.slack.helpers import block_builders
from managr.slack.helpers.block_sets import get_block_set
from managr.slack.models import UserSlackIntegration

from managr.slack.helpers.exceptions import (
    UnHandeledBlocksException,
    InvalidBlocksFormatException,
    InvalidBlocksException,
)
from managr.salesforce.adapter.exceptions import (
    TokenExpired,
    FieldValidationError,
    RequiredFieldError,
    SFQueryOffsetError,
    SFNotFoundError,
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
def queue_stale_sf_data_for_delete():
    """ 
        This should queue stale data for delete, it should only do this for users who are active and who have an sf account 
        In the future we will be having a flag for users who's salesforce token is soft revoked aka, they would like to pause the sync 
        or for whom we are having issues and they would like to refresh their token, for these users we should not be deleting data
    """
    resource_items = {
        "sobjectfield",
        "sobjectvalidation",
        "sobjectpicklist",
        "opportunity",
        "account",
        "contact",
        "lead",
    }
    limit = 0
    pages = 1
    # get users who are active and have a salesforce_account
    qs = User.objects.filter(is_active=True, salesforce_account__isnull=False).distinct()
    # count them to paginate the response
    user_count = qs.count()
    # set limit of 100 or less
    limit = max(100, user_count)
    # divide into pages
    pages = math.floor(user_count / limit)
    # cutoff of 1 day
    cutoff = timezone.now() - timezone.timedelta(days=1)

    for i in range(0, pages):
        users = qs[i * limit : i + 1 * limit].select_related("salesforce_account")
        batch = []
        batch_resource_count = 0
        for user in users:
            current_user_batch_resource = []
            for r in resource_items:
                try:
                    resource_count = getattr(user, f"imported_{r}").filter(last_edited__lt=cutoff)
                    future_count = batch_resource_count + resource_count
                    if future_count > 500:
                        # emit current batch to delete queue and start new
                        print(batch)
                    else:
                        current_user_batch_resource.append(r)
                        print(batch)

                    batch_resource_count = future_count
                except AttributeError as e:
                    logger.info(f"{user.email} does not have {r} to delete {e}")


def to_date_string(date):
    if not date:
        return "n/a"
    d = datetime.strptime(date, "%Y-%m-%d")
    return d.strftime("%a, %B %d, %Y")


@kronos.register("0 7 * * *")
def send_daily_tasks():
    """ 
        runs every day at 7am 
    """
    accounts = SalesforceAuthAccount.objects.filter(user__is_active=True).select_related("user")
    for account in accounts:
        user = account.user
        # Pulls tasks from Salesforce
        attempts = 0
        while True:
            ## TODO this is repetitive we need to get the new sf info after update maybe move this to the bottom within the except
            sf = user.salesforce_account
            try:
                tasks = sf.adapter_class.list_tasks()
                break

            except TokenExpired:
                if attempts >= 5:
                    logger.exception(f"Failed to gather tasks after 5 tries")
                    continue
                else:
                    sf.regenerate_token()
                    attempts += 1
        try:
            blocks = []
            channel = user.slack_integration.channel
            access_token = user.organization.slack_integration.access_token

            if not len(tasks):
                message = "Congratulations. You have no future tasks at this time."
                # this wont work need to update to send request
                Response(
                    data={"response_type": "ephemeral", "text": message,}
                )
            blocks.extend(
                [
                    block_builders.header_block("View Tasks"),
                    block_builders.simple_section(
                        f"You have *{len(tasks)}* upcoming tasks", "mrkdwn"
                    ),
                    block_builders.divider_block(),
                ]
            )
            for t in tasks:
                resource = "_salesforce object n/a_"
                # get the resource if it is what_id is for account/opp
                # get the resource if it is who_id is for lead
                if t.what_id:
                    # first check for opp
                    obj = user.imported_opportunity.filter(integration_id=t.what_id).first()
                    if not obj:
                        obj = user.imported_account.filter(integration_id=t.what_id).first()
                    if obj:
                        resource = f"*{obj.name}*"

                elif t.who_id:
                    obj = user.imported_lead.filter(integration_id=t.who_id).first()
                    if obj:
                        resource = f"*{obj.name}*"

                blocks.extend(
                    [
                        block_builders.simple_section(
                            f"{resource}, due _*{to_date_string(t.activity_date)}*_, {t.subject} `{t.status}`",
                            "mrkdwn",
                        ),
                        block_builders.divider_block(),
                        block_builders.section_with_button_block(
                            "View Task",
                            "view_task",
                            "_*View task in salesforce*_",
                            url=f"{user.salesforce_account.instance_url}/lightning/r/Task/{t.id}/view",
                        ),
                    ]
                )

            slack_requests.send_ephemeral_message(
                channel,
                access_token,
                user.slack_integration.slack_id,
                text="Tasks",
                block_set=blocks,
            )
        except InvalidBlocksException as e:
            logger.exception(f"Failed to list tasks for user {user.name} email {user.email} {e}")

        except InvalidBlocksFormatException as e:
            logger.exception(f"Failed to list tasks for user {user.name} email {user.email} {e}")

        except UnHandeledBlocksException as e:
            logger.exception(f"Failed to list tasks for user {user.name} email {user.email} {e}")

    return


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
        .filter(creation_date=datetime.datetime.now().date())
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
        .filter(creation_date=datetime.datetime.now().date(), progress_l__lt=0)
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

