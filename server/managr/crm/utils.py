from managr.salesforce.routes import routes as sf_routes
from managr.hubspot.routes import routes as hs_routes
from managr.slack.models import OrgCustomSlackForm, OrgCustomSlackFormInstance
from django.db.models import Q

CRM_SWITCHER = {"SALESFORCE": sf_routes, "HUBSPOT": hs_routes}


def process_text_field_format(user_id, resource, saved_data):
    from managr.core.models import User
    from managr.crm.models import ObjectField

    user = User.objects.get(id=user_id)
    public_fields = ObjectField.objects.filter(
        Q(is_public=True) & Q(data_type="String", length__gt=250)
    ).values_list("api_name", flat=True)
    fields = list(
        ObjectField.objects.for_user(user)
        .filter(
            Q(crm_object=resource, data_type="TextArea") | Q(data_type="String", length__gt=250)
        )
        .values_list("api_name", flat=True)
    )
    fields.extend(public_fields)
    to_check_fields = [field for field in saved_data if field in fields]
    if len(to_check_fields):
        for field in to_check_fields:
            if saved_data[field]:
                split_field = saved_data[field].split("\n")
                if len(split_field) > 1:
                    salesforce_formatted = "\r\n".join(split_field)
                    saved_data[field] = salesforce_formatted
        return saved_data
    return False


def create_form_instance(
    user, resource_type, form_type, resource_id, stage_name, update_source="pipeline"
):
    form_ids = []
    template_list = OrgCustomSlackForm.objects.for_user(user).filter(resource=resource_type)
    template = template_list.filter(form_type=form_type).first()
    slack_form = (
        OrgCustomSlackFormInstance.objects.create(
            template=template, user=user, resource_id=resource_id, update_source=update_source
        )
        if form_type == "UPDATE"
        else OrgCustomSlackFormInstance.objects.create(
            template=template, user=user, update_source=update_source
        )
    )
    if slack_form:
        if stage_name:
            stage_template = template_list.filter(stage=stage_name).first()
            stage_form = OrgCustomSlackFormInstance.objects.create(
                template=stage_template, user=user, update_source=update_source
            )
            if stage_form:
                form_ids.append(str(stage_form.id))
        form_ids.append(str(slack_form.id))
    return form_ids
