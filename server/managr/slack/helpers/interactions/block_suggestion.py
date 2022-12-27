import logging
import json

from django.db.models import Q
from managr.slack import constants as slack_const
from managr.salesforce import constants as sf_consts
from managr.hubspot import constants as hs_consts
from managr.gong.models import GongCall
from managr.core.models import User
from managr.opportunity.models import Opportunity, Lead
from managr.hubspot.models import Deal, Company, HubspotContact
from managr.organization.models import (
    Organization,
    Account,
    Contact,
    Pricebook2,
    PricebookEntry,
)
from managr.outreach.models import Sequence
from managr.slack.helpers import block_builders
from managr.slack.helpers.utils import process_action_id, NO_OP, processor
from managr.crm.exceptions import TokenExpired, InvalidFieldError
from managr.salesloft.models import Cadence, People
from managr.crm.models import BaseOpportunity, BaseAccount, BaseContact

logger = logging.getLogger("managr")


class UnformattedSlackOptions:
    def __init__(self, kwargs):
        self.label = kwargs.get("label", None)
        self.value = kwargs.get("value", None)

    @staticmethod
    def type_check(opt):
        return isinstance(opt, UnformattedSlackOptions)

    @property
    def as_dict(self):
        return vars(self)

    @property
    def as_slack_option(self):
        from managr.slack.helpers.block_builders import option

        return option(self.label, self.value)


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
            l.as_slack_option
            for l in Opportunity.objects.for_user(user).filter(title__icontains=value)
        ],
    }


@processor(required_context=["u"])
def process_get_user_contacts(payload, context):
    user = User.objects.get(id=context["u"])
    value = payload["value"]
    return {
        "options": [
            l.as_slack_option
            for l in Contact.objects.for_user(user).filter(email__icontains=value)[:50]
        ],
    }


@processor(required_context=["u"])
def process_get_user_accounts(payload, context):
    user = User.objects.get(id=context["u"])
    value = payload["value"]
    return {
        "options": [
            l.as_slack_option
            for l in Account.objects.for_user(user).filter(name__icontains=value)[:50]
        ],
    }


@processor(required_context=["u", "resource_type"])
def process_get_local_resource_options(payload, context):
    """
    Retrieves data saved in our db for resources, note this is not used when fields are from the slack forms built with fields
    additional options can be passed in the context
    """
    user = User.objects.get(pk=context["u"])
    value = payload["value"]
    resource = context.get("resource_type")
    additional_opts = json.loads(context.get("add_opts", json.dumps([])))
    field_id = context.get("field_id")
    # conver type to make sure it follows {label:str|num, values:str|num}
    additional_opts = [UnformattedSlackOptions(opt).as_slack_option for opt in additional_opts]
    if resource in [sf_consts.RESOURCE_SYNC_ACCOUNT, hs_consts.RESOURCE_SYNC_COMPANY]:
        return {
            "options": [
                *additional_opts,
                *[
                    l.as_slack_option
                    for l in BaseAccount.objects.for_user(user).filter(name__icontains=value)[:50]
                ],
            ],
        }

    elif resource == sf_consts.RESOURCE_SYNC_LEAD:
        return {
            "options": [
                *additional_opts,
                *[
                    l.as_slack_option
                    for l in Lead.objects.for_user(user).filter(name__icontains=value)[:50]
                ],
            ],
        }
    elif resource in [sf_consts.RESOURCE_SYNC_CONTACT, hs_consts.RESOURCE_SYNC_CONTACT]:
        return {
            "options": [
                *additional_opts,
                *[
                    l.as_slack_option
                    for l in BaseContact.objects.for_user(user).filter(Q(email__icontains=value))[
                        :50
                    ]
                ],
            ],
        }
    elif resource in [sf_consts.RESOURCE_SYNC_OPPORTUNITY, hs_consts.RESOURCE_SYNC_DEAL]:
        return {
            "options": [
                *additional_opts,
                *[
                    l.as_slack_option
                    for l in BaseOpportunity.objects.for_user(user).filter(name__icontains=value)[
                        :50
                    ]
                ],
            ],
        }
    elif resource == slack_const.SLACK_ACTION_RESOURCE_ACTION_CHOICE:
        return {
            "options": [
                *additional_opts,
                *[
                    l.as_slack_option
                    for l in user.organization.action_choices.filter(title__icontains=value)[:50]
                ],
            ],
        }
    elif resource == slack_const.SLACK_ACTION_RESOURCE_PRICEBOOKENTRY:
        pricebook = context.get("pricebook", None)
        if pricebook != "None":
            pricebookentries = PricebookEntry.objects.filter(pricebook__integration_id=pricebook)
        else:
            pricebookentries = PricebookEntry.objects.filter(
                pricebook__organization=user.organization
            )

        return {
            "options": [
                *additional_opts,
                *[l.as_slack_option for l in pricebookentries.filter(name__icontains=value)[:50]],
            ],
        }
    elif resource == slack_const.SLACK_ACTION_RESOURCE_USER:
        query = Q()
        if field_id == "e286d1d5-5447-47e6-ad55-5f54fdd2b00d":
            query = Q(user_level="MANAGER")
        elif field_id == "fae88a10-53cc-470e-86ec-32376c041893":
            query = Q(user_level="REP")

        query &= Q(first_name__icontains=value) | Q(last_name__icontains=value)

        return {
            "options": [
                *additional_opts,
                *[u.as_slack_option for u in user.organization.users.filter(query)[:50]],
            ],
        }


@processor(required_context=["u", "field"])  # takes in additional_options list as an optional param
def process_get_picklist_options(payload, context):
    """
    Gets picklist options for options saved in our db, for all options except stages we use an external picklist block
    Using the external picklist means we can avoid the slack 50 block limit since each option counts as a limit
    Only stages use the static select block because we require the ordering to retrieve the linked stage forms in order
    """
    additional_opts = json.loads(context.get("add_opts", json.dumps([])))

    # conver type to make sure it follows {label:str|num, values:str|num}

    additional_opts = [UnformattedSlackOptions(opt).as_slack_option for opt in additional_opts]

    user = User.objects.get(pk=context["u"])
    value = payload["value"]

    field = user.object_fields.filter(id=context.get("field")).first()
    options = field.get_slack_options
    if not len(options):
        logger.exception(f"No values found for picklist {field.api_name}")
        return {"options": []}
    if value and len(value):
        options = list(filter(lambda opt: value in opt["value"].lower(), options))

    if len(options) and len(options) > 30:
        return {"options": [*additional_opts, *options[: (30 - len(additional_opts))]]}
    else:
        return {"options": [*additional_opts, *options]}


@processor(required_context=["u", "resource", "field"])
def process_get_external_picklist_options(payload, context):
    """This retrieves external picklist options for picklists we do not currently store in our DB eg Tasks"""
    # TODO pass in values as query
    # pass in limit for query
    user = User.objects.get(pk=context["u"])
    value = payload["value"]
    data = user.crm_account.get_individual_picklist_values(
        context.get("resource"), field=context.get("field")
    )
    options = data.values if user.crm == "SALESFORCE" else data.values()
    if not len(options):
        logger.exception(
            f"No values found for picklist {context.get('resource')} with field {context.get('field')}"
        )
        return {"options": []}
    # if value and len(value):
    #    options = list(filter(lambda opt: value in opt["value"].lower(), options))

    if len(options) > 30:
        return {"options": options[:30]}
    else:
        return {
            "options": [
                block_builders.option(opt.get("label"), opt.get("value")) for opt in options
            ]
        }


@processor(required_context=["u", "resource_id"])
def process_get_deal_stage_options(payload, context):
    deal = Deal.objects.get(id=context.get("resource_id"))
    user = User.objects.get(id=context.get("u"))
    stages = deal.get_deal_stage_options(user.hubspot_account.access_token)

    return {
        "options": [block_builders.option(opt.get("label"), opt.get("value")) for opt in stages]
    }


@processor(required_context=["u", "relationship", "fields"])
def process_get_external_relationship_options(payload, context):
    user = User.objects.get(pk=context["u"])
    relationship = context.get("relationship")
    fields = context.get("fields").split(",") if len(context.get("fields")) else []
    value = payload["value"]
    resource = context.get("resource")
    add_fields = context.get("add", None)
    if relationship == "Group":
        relationship = "User"
        fields = ["FirstName", "LastName", "Name"]
    attempts = 1
    while True:
        crm_account = user.crm_account
        crm_adapter = crm_account.adapter_class
        try:
            res = crm_adapter.list_relationship_data(
                relationship, fields, value, resource, add_fields=add_fields
            )
            break
        except TokenExpired:
            if attempts >= 5:
                return logger.exception(
                    f"Failed to retrieve reference data for {relationship} data for user {str(user.id)} after {attempts} tries"
                )
            else:
                crm_account.regenerate_token()
                attempts += 1
        except InvalidFieldError as e:
            if attempts >= 5:
                return logger.exception(
                    f"Failed to retrieve reference data for {relationship} data for user {str(user.id)} after {attempts} tries"
                )
            elif resource == "OpportunityLineItem":
                fields.remove("CurrencyIsoCode")
                attempts += 1
            else:
                attempts += 1
    if "CurrencyIsoCode" in fields:
        return {
            "options": list(
                map(
                    lambda val: block_builders.option(
                        f"{val.get('Name')} - {val.get('CurrencyIsoCode')}", val.get("Id")
                    ),
                    res,
                )
            ),
        }
    return {
        "options": list(
            map(lambda val: block_builders.option(val.get("Name"), val.get("Id")), res)
        ),
    }


@processor(required_context=["u"])
def process_get_cadences(payload, context):
    user = User.objects.get(id=context["u"])
    cadences = Cadence.objects.filter(
        Q(is_team_cadence=True, is_shared=True) | Q(owner=user.salesloft_account)
    )
    value = payload["value"]
    return {
        "options": [l.as_slack_option for l in cadences.filter(name__icontains=value)[:50]],
    }


@processor(required_context=["u"])
def process_get_sequences(payload, context):
    user = User.objects.get(id=context["u"])
    sequences = Sequence.objects.filter(owner=user.outreach_account)
    value = payload["value"]
    return {
        "options": [l.as_slack_option for l in sequences.filter(name__icontains=value)[:50]],
    }


@processor(required_context=["resource_id", "resource_type"])
def process_get_people(payload, context):
    type = context.get("resource_type")
    resource_id = context.get("resource_id")
    value = payload["value"]
    if type == "Opportunity":
        opportunity = Opportunity.objects.get(id=resource_id)
        account = Account.objects.filter(opportunities__in=[resource_id]).first()
        contacts = account.contacts.all() if hasattr(account, "contacts") else opportunity.contacts
    else:
        account = Account.objects.get(id=resource_id)
        contacts = account.contacts.all()
    return {
        "options": [l.as_slack_option for l in contacts.filter(email__icontains=value)[:50]],
    }


def process_get_calls(payload, context):
    opp_id = context.get("opp_id")
    calls = GongCall.objects.filter(crm_id=opp_id)
    return {"options": [l.slack_option for l in calls]}


def process_get_sobject_list(payload, context):
    user = User.objects.get(id=context["u"])
    add_opt = context.get("add_option", None)
    value = payload["value"]
    sobject = context.get("resource_type")
    if sobject == "Opportunity":
        sobject_value = user.owned_opportunities
    elif sobject == "Account":
        sobject_value = user.accounts
    elif sobject == "Lead":
        sobject_value = user.owned_leads
    elif sobject == "Contact":
        sobject_value = user.contacts
    options = (
        [l.as_slack_option for l in sobject_value.filter(email__icontains=value)[:50]]
        if sobject == "Contact"
        else [l.as_slack_option for l in sobject_value.filter(name__icontains=value)[:50]]
    )
    if add_opt:
        options.insert(0, add_opt)
    return {
        "options": options,
    }


def process_get_pricebook_entry_options(payload, context):
    value = payload["value"]
    pricebooks = Pricebook2.objects.filter(organization=context.get("org"))
    return {
        "options": [l.as_slack_option for l in pricebooks.filter(name__icontains=value)[:50]],
    }


def CRM_FILTERS(crm, crm_id):
    filters = {
        "HUBSPOT": [{"propertyName": "hubspot_owner_id", "operator": "EQ", "value": crm_id,},],
        "SALESFORCE": [],
    }
    return filters[crm]


def CRM_RESOURCE_FILTER(crm, resource, value):
    if resource == slack_const.FORM_RESOURCE_DEAL:
        property_name = "dealname"
    elif resource == slack_const.FORM_RESOURCE_COMPANY:
        property_name = "name"
    elif resource == slack_const.FORM_RESOURCE_CONTACT:
        property_name = "email" if crm == "HUBSPOT" else "Email"
    return {
        "propertyName": property_name,
        "value": f"*{value}*",
        "operator": "CONTAINS_TOKEN",
    }


def RESOURCE_OPTIONS(resource, options):
    if resource in [slack_const.FORM_RESOURCE_COMPANY, slack_const.FORM_RESOURCE_DEAL]:
        return {
            "options": [
                block_builders.option(option.name, option.integration_id) for option in options
            ]
        }
    return


@processor(required_context=["u", "resource_type"])
def process_get_crm_resource_options(payload, context):
    user = User.objects.get(pk=context["u"])
    value = payload["value"]
    resource = context.get("resource_type")
    attempts = 1
    while True:
        crm_account = user.crm_account
        crm_adapter = crm_account.adapter_class
        try:
            filters = CRM_FILTERS(user.crm, user.crm_account.crm_id)
            if value:
                filters.append(CRM_RESOURCE_FILTER(user.crm, resource, value))
            res = crm_adapter.list_resource_data(resource, filters=filters)
            break
        except TokenExpired:
            if attempts >= 5:
                return logger.exception(
                    f"Failed to retrieve resource options for user {str(user.id)} after {attempts} tries"
                )
            else:
                crm_account.regenerate_token()
                attempts += 1
        except InvalidFieldError as e:
            if attempts >= 5:
                return logger.exception(
                    f"Failed to retrieve resource options for user {str(user.id)} beacuse of {e}"
                )
            else:
                attempts += 1
        except Exception as e:
            return logger.exception(
                f"Failed to retrieve resource options for user {str(user.id)} after {attempts} tries"
            )
    options = RESOURCE_OPTIONS(resource, res)
    return options


def handle_block_suggestion(payload):
    """
    This takes place when a select_field requires data from Managr
    to populate its options.
    """
    switcher = {
        slack_const.GET_ORGANIZATION_ACTION_CHOICES: process_get_organization_action_choices,
        slack_const.GET_USER_OPPORTUNITIES: process_get_user_opportunities,
        slack_const.GET_USER_CONTACTS: process_get_user_contacts,
        slack_const.GET_USER_ACCOUNTS: process_get_user_accounts,
        slack_const.GET_LOCAL_RESOURCE_OPTIONS: process_get_local_resource_options,
        slack_const.GET_EXTERNAL_RELATIONSHIP_OPTIONS: process_get_external_relationship_options,
        slack_const.COMMAND_FORMS__GET_LOCAL_RESOURCE_OPTIONS: process_get_local_resource_options,
        slack_const.GONG_CALL_RECORDING: process_get_local_resource_options,
        slack_const.GET_NOTES: process_get_local_resource_options,
        slack_const.COMMAND_SUMMARY__GET_LOCAL_RESOURCE_OPTIONS: process_get_local_resource_options,
        slack_const.GET_PICKLIST_OPTIONS: process_get_picklist_options,
        slack_const.COMMAND_FORMS__PIPELINE_SELECTED: process_get_picklist_options,
        slack_const.GET_EXTERNAL_PICKLIST_OPTIONS: process_get_external_picklist_options,
        slack_const.GET_CADENCE_OPTIONS: process_get_cadences,
        slack_const.GET_SEQUENCE_OPTIONS: process_get_sequences,
        slack_const.GET_CONTACT_OPTIONS: process_get_people,
        slack_const.GET_CALLS: process_get_calls,
        slack_const.GET_SOBJECT_LIST: process_get_sobject_list,
        slack_const.COMMAND_FORMS__CONVERT_LEAD: process_get_sobject_list,
        slack_const.PROCESS_SHOW_ENGAGEMENT_MODEL: process_get_local_resource_options,
        slack_const.GET_PRICEBOOK_ENTRY_OPTIONS: process_get_pricebook_entry_options,
        slack_const.GET_DEAL_STAGE_OPTIONS: process_get_deal_stage_options,
        slack_const.GET_CRM_RESOURCE_OPTIONS: process_get_crm_resource_options,
    }
    action_query_string = payload["action_id"]
    processed_string = process_action_id(action_query_string)
    action_id = processed_string.get("true_id")
    action_params = processed_string.get("params")
    return switcher.get(action_id, NO_OP)(payload, action_params)
