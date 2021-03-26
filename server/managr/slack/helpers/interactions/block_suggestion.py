import pdb
import logging

from django.db.models import Q
from managr.opportunity import constants as opp_consts
from managr.organization import constants as org_consts
from managr.slack import constants as slack_const
from managr.salesforce import constants as sf_consts

from managr.core.models import User
from managr.opportunity.models import Opportunity, Lead
from managr.organization.models import Organization, Account, ActionChoice
from managr.salesforce.models import SObjectPicklist

from managr.slack.helpers import block_builders
from managr.slack.helpers.utils import process_action_id, NO_OP, processor
from managr.salesforce.adapter.exceptions import TokenExpired

logger = logging.getLogger("managr")


@processor(required_context=["o"])
def process_get_organization_action_choices(payload, context):
    organization = Organization.objects.get(pk=context["o"])
    return {
        "options": [ac.as_slack_option for ac in organization.action_choices.all()],
    }


@processor(required_context=["u"])
def process_get_user_opportunities(payload, context):
    user = User.objects.get(pk=context["u"])
    value = payload["value"]
    return {
        "options": [
            l.as_slack_option for l in user.owned_opportunities.filter(title__icontains=value)
        ],
    }


@processor(required_context=["u", "resource"])
def process_get_local_resource_options(payload, context):
    user = User.objects.get(pk=context["u"])
    value = payload["value"]
    resource = context.get("resource")
    if resource == sf_consts.RESOURCE_SYNC_ACCOUNT:
        return {
            "options": [l.as_slack_option for l in user.accounts.filter(name__icontains=value)],
        }

    elif resource == sf_consts.RESOURCE_SYNC_LEAD:
        return {
            "options": [l.as_slack_option for l in user.owned_leads.filter(name__icontains=value)],
        }
    elif resource == sf_consts.RESOURCE_SYNC_OPPORTUNITY:
        return {
            "options": [
                l.as_slack_option for l in user.owned_opportunities.filter(name__icontains=value)
            ],
        }

    elif resource == slack_const.SLACK_ACTION_RESOURCE_ACTION_CHOICE:
        return {
            "options": [
                l.as_slack_option
                for l in user.organization.action_choices.filter(title__icontains=value)
            ],
        }


@processor(required_context=["u", "field"])
def process_get_picklist_options(payload, context):
    user = User.objects.get(pk=context["u"])
    value = payload["value"]
    field = user.salesforce_account.object_fields.filter(id=context.get("field")).first()
    options = field.get_slack_options
    if not len(options):
        logger.exception(f"No values found for picklist {field.api_name}")
        return {"options": []}
    if value and len(value):
        options = list(filter(lambda opt: value in opt["value"].lower(), options))

    if len(options) and len(options) > 30:
        return {"options": options[:30]}
    else:
        return {"options": options}


@processor(required_context=["u", "relationship", "fields"])
def process_get_external_relationship_options(payload, context):
    user = User.objects.get(pk=context["u"])
    relationship = context.get("relationship")
    fields = context.get("fields").split(",") if len(context.get("fields")) else []
    value = payload["value"]
    attempts = 1
    while True:
        sf_account = user.salesforce_account
        sf_adapter = sf_account.adapter_class
        try:
            res = sf_adapter.list_relationship_data(relationship, fields, value)
            break
        except TokenExpired:
            if attempts >= 5:
                return logger.exception(
                    f"Failed to retrieve reference data for {relationship} data for user {str(user.id)} after {attempts} tries"
                )
            else:
                sf_account.regenerate_token()
                attempts += 1

    return {
        "options": list(
            map(lambda val: block_builders.option(val.get("Name"), val.get("Id")), res)
        ),
    }


def handle_block_suggestion(payload):
    """
    This takes place when a select_field requires data from Managr
    to populate its options.
    """
    switcher = {
        slack_const.GET_ORGANIZATION_ACTION_CHOICES: process_get_organization_action_choices,
        slack_const.GET_USER_OPPORTUNITIES: process_get_user_opportunities,
        slack_const.GET_LOCAL_RESOURCE_OPTIONS: process_get_local_resource_options,
        slack_const.GET_EXTERNAL_RELATIONSHIP_OPTIONS: process_get_external_relationship_options,
        slack_const.COMMAND_FORMS__GET_LOCAL_RESOURCE_OPTIONS: process_get_local_resource_options,
        slack_const.COMMAND_SUMMARY__GET_LOCAL_RESOURCE_OPTIONS: process_get_local_resource_options,
        slack_const.GET_PICKLIST_OPTIONS: process_get_picklist_options,
    }
    action_query_string = payload["action_id"]
    processed_string = process_action_id(action_query_string)
    action_id = processed_string.get("true_id")
    action_params = processed_string.get("params")
    print(f"ID: {action_query_string}")
    return switcher.get(action_id, NO_OP)(payload, action_params)
