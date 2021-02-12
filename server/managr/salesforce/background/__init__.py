import logging
import json
from datetime import datetime
from background_task import background

from django.utils import timezone

from managr.api.decorators import log_all_exceptions

from managr.core.models import User
from managr.organization.models import Account, Stage
from managr.organization.serializers import AccountSerializer, StageSerializer
from managr.opportunity.models import Opportunity
from managr.opportunity.serializers import OpportunitySerializer
from managr.slack import constants as slack_consts
from managr.slack.models import OrgCustomSlackForm

from ..routes import routes
from ..models import SFSyncOperation
from ..adapter.models import AccountAdapter, OpportunityAdapter, ActivityAdapter
from ..adapter.exceptions import TokenExpired

from .. import constants as sf_consts

logger = logging.getLogger("managr")


def emit_sf_sync(user_id, sync_id, resource, offset):
    user_id = str(user_id)
    sync_id = str(sync_id)
    return _process_resource_sync(user_id, sync_id, resource, offset)


def emit_gen_next_sync(user_id, ops_list, schedule_time=timezone.now()):
    schedule = datetime.strptime(schedule_time, "%Y-%m-%dT%H:%M%Z")
    return _process_gen_next_sync(user_id, ops_list, schedule=schedule)


def emit_sf_add_call_to_sf(user_id, data):
    return _process_add_call_to_sf(user_id, data)


def emit_sf_update_opportunity(user_id, meeting_review_id):
    return _process_update_opportunity(user_id, meeting_review_id)


def emit_add_c_role_to_opp(user_id, opp_id, sf_contact_id):
    return _process_add_c_role_to_opp(user_id, opp_id, sf_contact_id)


def emit_generate_forms(user_id):
    return _generate_forms(user_id)


@background(schedule=0)
@log_all_exceptions
def _process_add_call_to_sf(user_id, data, attempts=1):
    user = User.objects.filter(id=user_id).first()
    if not user:
        return logger.exception(f"User not found unable to log call {user_id}")
    if not hasattr(user, "salesforce_account"):
        return logger.exception("User does not have a salesforce account cannot push to sf")

    sf = user.salesforce_account
    try:
        return ActivityAdapter.save_zoom_meeting_to_salesforce(
            data, sf.access_token, sf.instance_url
        )
    except TokenExpired:
        if attempts >= 5:
            return logger.exception(
                f"Failed to refresh user token for Salesforce operation add contact as contact role to opportunity"
            )
        else:
            sf.regenerate_token()
            attempts += 1
            return _process_add_call_to_sf(user_id, data, attempts=attempts)


@background(schedule=0)
@log_all_exceptions
def _process_add_c_role_to_opp(user_id, opp_id, sf_contact_id, attempts=1):
    user = User.objects.filter(id=user_id).first()
    if not user:
        return logger.exception(
            f"User not found add contact role not initiated {user_id}, {str(opp_id)}, {sf_contact_id}"
        )
    opp = user.owned_opportunities.filter(id=opp_id).first()
    if not opp:
        return logger.exception(
            f"Opportunity not found add contact role not initiated {user_id}, {str(opp_id)}, {sf_contact_id}"
        )
    sf = user.salesforce_account
    try:
        opp.add_contact_role(sf.access_token, sf.instance_url, sf_contact_id)
    except TokenExpired:
        if attempts >= 5:
            return logger.exception(
                f"Failed to refresh user token for Salesforce operation add contact as contact role to opportunity"
            )
        else:
            sf.regenerate_token()
            attempts += 1
            return _process_add_c_role_to_opp(user_id, opp_id, sf_contact_id, attempts=attempts)


@background(schedule=0)
@log_all_exceptions
def _process_gen_next_sync(user_id, operations_list):
    user = User.objects.filter(id=user_id).first()
    if not user:
        return logger.exception(f"User not found sync operation not created {user_id}")

    return SFSyncOperation.objects.create(user=user, operations_list=operations_list).begin_tasks()


@background()
@log_all_exceptions
def _generate_forms(user_id):
    ## TODO: Work on updating forms automatically with new fields
    user = User.objects.get(id=user_id)
    org = user.organization
    for form in slack_consts.INITIAL_FORMS:
        resource, form_type = form.split(".")
        slack_form = org.custom_slack_forms.filter(resource=resource, form_type=form_type).first()
        new_form_config = routes[resource]["model"].generate_slack_form_config(user, form_type)
        if slack_form:
            current_config = slack_form.config
            # replace all current fields that exist in the new fields
            # remove any fields that no longer exist
            current_fields = current_config.get("fields", [])
            new_form_fields = new_form_config.get("fields", [])
            combined_fields = []
            if len(new_form_fields) >= len(current_fields):
                for field in new_form_fields:
                    combined_fields.append(field)
                    for i, f in enumerate(current_fields):
                        if field["key"] == f["key"]:
                            del current_fields[i]
            else:
                for i, field in enumerate(current_fields):
                    for f in new_form_fields:
                        combined_fields.append(f)
                        if field["key"] == f["key"]:
                            del current_fields[i]

            new_form_config["fields"] = combined_fields
            slack_form.config = new_form_config
            slack_form.save()
        else:
            OrgCustomSlackForm.objects.create(
                organization=org, resource=resource, form_type=form_type, config=new_form_config,
            )


@background(schedule=0, queue=sf_consts.SALESFORCE_RESOURCE_SYNC_QUEUE)
@log_all_exceptions
def _process_resource_sync(user_id, sync_id, resource, offset, attempts=1):
    user = User.objects.filter(id=user_id).select_related("salesforce_account").first()
    if not hasattr(user, "salesforce_account"):
        return
    sf = user.salesforce_account

    # if route doesnt exist catch all will catch the value error here
    route = routes[resource]
    model_class = route["model"]
    serializer_class = route["serializer"]

    while True:
        try:
            res = sf.list_resource_data(resource, offset)
            break
        except TokenExpired:
            if attempts >= 5:
                return logger.exception(
                    f"Failed to sync {resource} data for user {user_id} after {attempts} tries"
                )
            else:
                sf.regenerate_token()
                attempts += 1

    for item in res:
        existing = model_class.objects.filter(integration_id=item.integration_id).first()
        if existing:
            serializer = serializer_class(data=item.as_dict, instance=existing)
        else:
            serializer = serializer_class(data=item.as_dict)
        # check if already exists and update

        try:
            serializer.is_valid(raise_exception=True)
            serializer.save()
        except Exception as e:
            print(e)
            logger.exception(
                f"failed to import {resource} with integration id of {item.integration_id} from {item.integration_source} for user {str(user.id)} {e}"
            )
            pass
    return


@background(schedule=0)
def _process_update_opportunity(user_id, meeting_review_id, attempts=1):
    user = (
        User.objects.filter(id=user_id)
        .select_related("zoom_account")
        .select_related("salesforce_account")
        .first()
    )
    if user and user.has_zoom_integration and user.has_slack_integration:
        meeting = user.zoom_account.meetings.filter(meeting_review__id=meeting_review_id).first()
        meeting_review = meeting.meeting_review
        if meeting_review:
            formatted_data = meeting_review.as_sf_update
            sf = user.salesforce_account
            try:
                return meeting.opportunity.update_in_salesforce(formatted_data)
            except TokenExpired:
                if attempts >= 5:
                    return logger.exception(
                        f"Failed to sync STAGE data for user {user_id} after {attempts} tries"
                    )
                else:
                    sf.regenerate_token()
                    attempts += 1
                    return _process_update_opportunity(user_id, meeting_review_id, attempts)

            # push to sf
    return

