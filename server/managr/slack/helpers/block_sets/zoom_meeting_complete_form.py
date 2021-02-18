from managr.opportunity.models import Opportunity
from managr.opportunity import constants as opp_consts
from managr.salesforce import constants as sf_consts
from managr.slack import constants as slack_const
from managr.slack.helpers.utils import action_with_params, block_set, map_fields_to_type
from managr.slack.helpers import block_builders


@block_set(required_context=["opp", "m"])
def zoom_meeting_complete_form(context):
    opportunity = Opportunity.objects.get(pk=context.get("opp"))
    sf_account = opportunity.imported_by.salesforce_account
    organization = sf_account.user.organization

    # get user slack form

    slack_form = organization.custom_slack_forms.filter(
        form_type=slack_const.FORM_TYPE_MEETING_REVIEW, resource="Opportunity"
    ).first()

    fields = slack_form.config.get("fields", [])
    values = opportunity.secondary_data
    for k, value in values.items():
        for i, field in enumerate(fields):
            if field["key"] == k:
                field["value"] = value
                fields[i] = field

    blocks = map_fields_to_type(fields)

    # make params here

    return blocks
