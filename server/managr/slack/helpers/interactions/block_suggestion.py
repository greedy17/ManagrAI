import pdb
from django.db.models import Q

from managr.core.models import User
from managr.organization.models import Organization, Stage
from managr.lead import constants as lead_const

from managr.slack import constants as slack_const
from managr.slack.helpers.utils import process_action_id, NO_OP, processor
from managr.slack.helpers import block_builders


@processor(required_context=["o"])
def process_get_organization_stages(payload, context):
    organization = Organization.objects.get(pk=context["o"])
    return {
        "options": [
            s.as_slack_option
            for s in Stage.objects.filter(
                Q(type="PUBLIC") | Q(organization=organization)
            )
        ],
    }


@processor(required_context=["o"])
def process_get_organization_action_choices(payload, context):
    organization = Organization.objects.get(pk=context["o"])
    return {
        "options": [ac.as_slack_option for ac in organization.action_choices.all()],
    }


@processor()
def process_get_lead_forecasts(payload, context):
    return {
        "options": [
            block_builders.option(f[1], f[0]) for f in lead_const.FORECAST_CHOICES
        ],
    }


@processor(required_context=["u"])
def process_get_user_leads(payload, context):
    user = User.objects.get(pk=context["u"])
    value = payload["value"]
    return {
        "options": [
            l.as_slack_option for l in user.claimed_leads.filter(title__icontains=value)
        ],
    }


def handle_block_suggestion(payload):
    """
    This takes place when a select_field requires data from Managr
    to populate its options.
    """
    switcher = {
        slack_const.GET_ORGANIZATION_STAGES: process_get_organization_stages,
        slack_const.GET_ORGANIZATION_ACTION_CHOICES: process_get_organization_action_choices,
        slack_const.GET_LEAD_FORECASTS: process_get_lead_forecasts,
        slack_const.GET_USER_OPPORTUNITIES: process_get_user_leads,
    }
    action_query_string = payload["action_id"]
    processed_string = process_action_id(action_query_string)
    action_id = processed_string.get("true_id")
    action_params = processed_string.get("params")
    print(f"ID: {action_query_string}")
    return switcher.get(action_id, NO_OP)(payload, action_params)
