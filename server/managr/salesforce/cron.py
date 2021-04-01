import logging
import kronos
import datetime
import logging

from django.conf import settings
from django.template.loader import render_to_string
from django.utils import timezone
from django.db.models import Q, F, Func, IntegerField, DateField, Sum
from django.db.models.functions import Cast
from managr.api.emails import send_html_email
from managr.salesforce import constants as sf_consts
from managr.salesforce.background import emit_gen_next_sync, emit_gen_next_object_field_sync
from managr.salesforce.models import SFObjectFieldsOperation, SFResourceSync, SalesforceAuthAccount

logger = logging.getLogger("managr")


class ArrayLength(Func):
    function = "CARDINALITY"


@kronos.register("*/10  * * * *")
def queue_users_sf_resource():
    """ runs every 10 mins and initiates user sf syncs if their prev workflow is done """
    sf_accounts = SalesforceAuthAccount.objects.filter(user__is_active=True)
    for account in sf_accounts:
        # get latest workflow
        flows = SFResourceSync.objects.filter(user=account.user)

        latest_flow = flows.latest("datetime_created") if flows else None
        if latest_flow and latest_flow.progress == 100:
            logger.info(
                f"SF_LATEST_RESOURCE_SYNC --- Operation id {str(latest_flow.id)}, email {latest_flow.user.email}"
            )
            init_sf_resource_sync(latest_flow.user.id)
            continue
        if not flows.count():
            init_sf_resource_sync(account.user.id)
        # if latest workflow is at 100 emit sf resource sync
    return


@kronos.register("*/10  * * * *")
def report_sf_data_sync(sf_account=None):
    """ runs every 10 mins and initiates user sf syncs if their prev workflow is done """
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


@kronos.register("0 */12 * * *")
def queue_users_sf_fields():
    """ runs every 12 hours and initiates user sf syncs if their prev workflow is done """
    sf_accounts = SalesforceAuthAccount.objects.filter(user__is_active=True)
    for account in sf_accounts:
        # get latest workflow
        flows = SFObjectFieldsOperation.objects.filter(user=account.user)
        latest_flow = flows.latest("datetime_created") if flows else None
        if latest_flow and latest_flow.progress == 100:
            logger.info(
                f"SF_LATEST_RESOURCE_SYNC --- Operation id {str(latest_flow.id)}, email {latest_flow.user.email}"
            )
            init_sf_field_sync(latest_flow.user)
            continue
        if not flows.count():
            init_sf_field_sync(account.user)
        # if latest workflow is at 100 emit sf resource sync
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
    operations = [
        f"{sf_consts.SALESFORCE_OBJECT_FIELDS}.{sf_consts.RESOURCE_SYNC_ACCOUNT}",
        f"{sf_consts.SALESFORCE_PICKLIST_VALUES}.{sf_consts.RESOURCE_SYNC_ACCOUNT}",
        f"{sf_consts.SALESFORCE_OBJECT_FIELDS}.{sf_consts.RESOURCE_SYNC_CONTACT}",
        f"{sf_consts.SALESFORCE_PICKLIST_VALUES}.{sf_consts.RESOURCE_SYNC_CONTACT}",
        f"{sf_consts.SALESFORCE_OBJECT_FIELDS}.{sf_consts.RESOURCE_SYNC_LEAD}",
        f"{sf_consts.SALESFORCE_PICKLIST_VALUES}.{sf_consts.RESOURCE_SYNC_LEAD}",
        f"{sf_consts.SALESFORCE_OBJECT_FIELDS}.{sf_consts.RESOURCE_SYNC_OPPORTUNITY}",
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

