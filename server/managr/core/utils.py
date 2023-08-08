import calendar
import json


from django.conf import settings
from django.utils import timezone
from managr.utils.client import Variable_Client
from datetime import datetime
from django.db.models import Q
from managr.core.models import User
from managr.alerts.models import AlertConfig
from managr.slack.models import OrgCustomSlackFormInstance
from managr.organization.models import Organization
from managr.core import constants as core_const


def count_character_tokens(text):
    count = 0
    in_token = False

    for char in text:
        if char.isspace() or char == "\n":
            if in_token:
                count += 1
                in_token = False
        else:
            count += 1
            in_token = True

    if in_token:
        count += 1

    return count


def max_token_calculator(text):
    token_count = count_character_tokens(text)
    use_tokens = 4000 - token_count
    tokens = int(use_tokens) if int(use_tokens) > 0 else 0
    return tokens


def qsort(inlist, obj):
    if inlist == []:
        return []
    else:
        pivot = inlist[0]
        lesser = qsort([x for x in inlist[1:] if obj[x] < obj[pivot]], obj)
        greater = qsort([x for x in inlist[1:] if obj[x] >= obj[pivot]], obj)
        return lesser + [pivot] + greater


def get_month_start_and_end(year, current_month, return_current_month_only=False):
    # create dictionary of normal month lengths
    months = {
        "01": "31",
        "02": "28",
        "03": "31",
        "04": "30",
        "05": "31",
        "06": "30",
        "07": "31",
        "08": "31",
        "09": "30",
        "10": "31",
        "11": "30",
        "12": "31",
    }
    if calendar.isleap(year):
        months["02"] = "29"
    if return_current_month_only:
        month = f"0{current_month}" if current_month < 10 else f"{current_month}"
        date_arr = [(f"{year}-{month}-01", f"{year}-{month}-{months[month]}")]
        return date_arr
    date_arr = [(f"{year}-{key}-01", f"{year}-{key}-{value}") for key, value in months.items()]
    return date_arr[:current_month]


def get_instance_averages(model_queryset, month_end):
    obj = {}
    for record in model_queryset:
        if record.datetime_created.date() in obj.keys():
            obj[record.datetime_created.date()] += 1
        else:
            obj[record.datetime_created.date()] = 1
    days_list = obj.values()
    average = (sum(days_list) / len(days_list)) if len(days_list) else 0
    return {
        "session average": average,
        "total sessions": len(days_list),
    }


def get_org_averages(user_obj):
    total_active = 0
    update_total = 0
    session_total = 0
    for user in user_obj.keys():
        if int(user_obj[user]["session average"]) > 0:
            total_active += 1
            update_total += user_obj[user]["session average"]
            session_total += user_obj[user]["total sessions"]
    if total_active > 0:
        session_average = update_total / total_active
        session_total_average = session_total / total_active
    else:
        session_average = 0
        session_total_average = 0
    return {"session average": session_average, "average total sessions": session_total_average}


def get_org_fields(org, first, last):
    forms = OrgCustomSlackFormInstance.objects.filter(
        user__organization=org, datetime_created__range=(first, last)
    ).exclude(template__isnull=True)
    if len(forms):
        list(forms.first().__dict__.get("saved_data").keys())
        obj = {}
        for form in forms:
            old_data = form.previous_data
            new_data = form.saved_data
            for key, new_value in new_data.items():
                if key in old_data:
                    if str(old_data.get(key)) != str(new_value):
                        if form.user.email in obj.keys():
                            if key in obj[form.user.email].keys():
                                obj[form.user.email][key] += 1
                            else:
                                obj[form.user.email][key] = 1
                        else:
                            obj[form.user.email] = {}
                            obj[form.user.email][key] = 1
                else:
                    if form.user.email in obj.keys():
                        if key in obj[form.user.email].keys():
                            obj[form.user.email][key] += 1
                        else:
                            obj[form.user.email][key] = 1
                    else:
                        obj[form.user.email] = {}
                        obj[form.user.email][key] = 1
        return obj


def get_user_fields(user_id, first, last):
    user = User.objects.get(id=user_id)
    forms = OrgCustomSlackFormInstance.objects.filter(
        user=user, datetime_created__range=(first, last)
    ).exclude(template__isnull=True)
    obj = {}
    if len(forms):
        list(forms.first().__dict__.get("saved_data").keys())
        for form in forms:
            old_data = form.previous_data
            new_data = form.saved_data
            for key, new_value in new_data.items():
                if key in old_data:
                    if str(old_data.get(key)) != str(new_value):
                        if key in obj.keys():
                            obj[key] += 1
                        else:
                            obj[key] = 1
                else:
                    if key in obj.keys():
                        obj[key] += 1
                    else:
                        obj[key] = 1
    return obj


def get_totals_for_year(month_only=False):
    # Base queries
    totals = {}
    current_date = datetime.now(tz=timezone.utc)
    date_list = get_month_start_and_end(current_date.year, current_date.month, month_only)

    for date in date_list:
        curr_month = {}
        start = timezone.make_aware(datetime.strptime(f"{date[0]} 00:01", "%Y-%m-%d %H:%M"))
        end = timezone.make_aware(datetime.strptime(f"{date[1]} 23:59", "%Y-%m-%d %H:%M"))
        if settings.IN_STAGING or settings.IN_DEV:
            slack_form_instances = (
                OrgCustomSlackFormInstance.objects.filter(datetime_created__range=(start, end))
                .filter(is_submitted=True)
                .exclude(template__isnull=True)
            )
        else:
            slack_form_instances = (
                OrgCustomSlackFormInstance.objects.filter(datetime_created__range=(start, end))
                .filter(is_submitted=True)
                .exclude(Q(user__organization__name="Managr") | Q(template__isnull=True))
            )
        curr_month["users"] = (
            User.objects.filter(datetime_created__range=(start, end))
            .exclude(organization__name="Managr")
            .count()
        )
        curr_month["workflows"] = (
            AlertConfig.objects.filter(datetime_created__range=(start, end))
            .exclude(template__user__organization__name="Managr")
            .count()
        )
        updates = {}
        update_forms = slack_form_instances.filter(
            template__form_type__in=["UPDATE", "STAGE_GATING"]
        )
        updates["total"] = update_forms.count()
        updates["alert"] = update_forms.filter(update_source="alert").count()
        updates["command"] = update_forms.filter(update_source="command").count()
        updates["meeting"] = update_forms.filter(update_source="meeting").count()
        updates["pipeline"] = update_forms.filter(update_source="pipeline").count()
        curr_month["updates"] = updates
        creates = {}
        create_forms = slack_form_instances.filter(template__form_type="CREATE")
        creates["total"] = create_forms.count()
        creates["contacts"] = create_forms.filter(template__resource="Contact").count()
        creates["accounts"] = create_forms.filter(template__resource="Account").count()
        creates["opportunities"] = create_forms.filter(template__resource="Opportunity").count()
        creates["products"] = create_forms.filter(template__resource="OpportunityLineItem").count()
        curr_month["creates"] = creates
        total_active = 0
        for user in slack_form_instances.order_by().values_list("user", flat=True).distinct("user"):
            if len(slack_form_instances.filter(user__id=user)) >= 10:
                total_active += 1
        curr_month["total active users"] = total_active
        totals[date[1]] = curr_month
    return totals


def get_organization_totals(month_only=False):
    totals = {}
    current_date = datetime.now(tz=timezone.utc)
    date_list = get_month_start_and_end(current_date.year, current_date.month, month_only)
    orgs = Organization.objects.all().order_by("name")
    users = User.objects.all()
    for date in date_list:
        start = timezone.make_aware(datetime.strptime(f"{date[0]} 00:01", "%Y-%m-%d %H:%M"))
        end = timezone.make_aware(datetime.strptime(f"{date[1]} 23:59", "%Y-%m-%d %H:%M"))
        if settings.IN_STAGING or settings.IN_DEV:
            slack_form_instances = (
                OrgCustomSlackFormInstance.objects.filter(datetime_created__range=(start, end))
                .filter(is_submitted=True)
                .exclude(template__isnull=True)
            )
        else:
            slack_form_instances = (
                OrgCustomSlackFormInstance.objects.filter(datetime_created__range=(start, end))
                .filter(is_submitted=True)
                .exclude(Q(user__organization__name="Managr") | Q(template__isnull=True))
            )
        org_totals = {}
        for org in orgs:
            org_obj = {}
            org_totals_instances = slack_form_instances.filter(user__organization=org)
            org_users = users.filter(organization=org)
            users_obj = {}
            for user in org_users:
                user_obj = {}
                user_instances = org_totals_instances.filter(user=user)
                per_day = get_instance_averages(user_instances, date[1])
                user_obj = {**per_day}
                user_obj["updates"] = user_instances.filter(
                    template__form_type__in=["UPDATE", "STAGE_GATING"]
                ).count()
                user_obj["creates"] = user_instances.filter(template__form_type="CREATE").count()
                users_obj[user.email] = user_obj
            org_obj["users"] = users_obj
            org_obj["updates"] = org_totals_instances.filter(
                template__form_type__in=["UPDATE", "STAGE_GATING"]
            ).count()
            org_obj["creates"] = org_totals_instances.filter(template__form_type="CREATE").count()
            org_averages = get_org_averages(users_obj)
            org_obj.update(org_averages)
            org_obj["fields"] = get_org_fields(org, start, end)
            org_totals[org.name] = org_obj

        totals[date[1]] = org_totals

    return totals


def get_user_totals(user_id, month_only=False):
    totals = {}
    current_date = datetime.now(tz=timezone.utc)
    date_list = get_month_start_and_end(current_date.year, current_date.month, month_only)
    user = User.objects.get(id=user_id)
    for date in date_list:
        start = timezone.make_aware(datetime.strptime(f"{date[0]} 00:01", "%Y-%m-%d %H:%M"))
        end = timezone.make_aware(datetime.strptime(f"{date[1]} 23:59", "%Y-%m-%d %H:%M"))
        slack_form_instances = (
            OrgCustomSlackFormInstance.objects.filter(datetime_created__range=(start, end))
            .filter(is_submitted=True, user=user)
            .exclude(template__isnull=True)
        )
        user_obj = {}
        user_instances = slack_form_instances.filter(user=user)
        per_day = get_instance_averages(user_instances, date[1])
        user_obj = {**per_day}
        user_obj["updates"] = user_instances.filter(
            template__form_type__in=["UPDATE", "STAGE_GATING"]
        ).count()
        user_obj["meetings"] = user_instances.filter(workflow__isnull=False).count()
        user_obj["contacts"] = user_instances.filter(
            template__form_type="CREATE", template__resource="Contact"
        ).count()
        field_obj = get_user_fields(user_id, start, end)
        sorted_fields = qsort(list(field_obj.keys()), field_obj)
        user_obj["fields"] = field_obj
        user_obj["field_order"] = sorted_fields
        user_fields = user.object_fields.filter(api_name__in=sorted_fields)
        label_obj = {}
        for field in sorted_fields:
            field_ref = user_fields.filter(api_name=field).first()
            if field_ref is not None:
                label_obj[field_ref.api_name] = field_ref.label
        user_obj["field_labels"] = label_obj
        totals[date[1][6:7]] = user_obj
    return totals


def pull_usage_data(month_only=False):
    totals = get_totals_for_year(month_only)
    orgs = get_organization_totals(month_only)
    return {"totals": totals, "org": orgs}


def get_summary_completion(user, data):
    summary_prompt = core_const.OPEN_AI_SUMMARY_PROMPT(data)
    tokens = max_token_calculator(summary_prompt)
    body = core_const.OPEN_AI_COMPLETIONS_BODY(user.email, summary_prompt, tokens)
    url = core_const.OPEN_AI_COMPLETIONS_URI
    with Variable_Client() as client:
        r = client.post(url, data=json.dumps(body), headers=core_const.OPEN_AI_HEADERS,)
        r = r.json()
    return r


def clean_apostrophes(string):
    letters = ["s", "r", "t", "m", "a", "d", "l", "v"]
    for letter in letters:
        string = string.replace(f"'{letter}", f"@{letter}").replace(f" @{letter}", f" '{letter}")
    return string


def clean_at_sign(string):
    letters = ["s", "r", "t", "m", "a", "d", "l", "v"]
    for letter in letters:
        string = string.replace(f"@{letter}", f"'{letter}")
    return string


def clean_prompt_string(prompt_string):
    random_bracket_insert_check = prompt_string[:5].find("}")
    if random_bracket_insert_check == 0:
        prompt_string = prompt_string[1:]
    prompt_string = prompt_string[prompt_string.index("{") : prompt_string.index("}") + 1]
    prompt_string = clean_apostrophes(prompt_string)
    cleaned_string = prompt_string.replace("\n", "").replace('"', "'")
    while "  " in cleaned_string:
        cleaned_string = cleaned_string.replace("  ", "")
    if "'}" not in cleaned_string and '"}' not in cleaned_string:
        cleaned_string = cleaned_string.replace("}", "'}")
    try:
        res_obj = eval(cleaned_string)
        for key in res_obj.keys():
            if isinstance(res_obj[key], str):
                res_obj[key] = clean_at_sign(res_obj[key])
        return res_obj
    except Exception as e:
        raise Exception(e)


def remove_underscores(object):
    fixed_key_object = {}
    for key in object.keys():
        new_key = key.replace("_", " ")
        fixed_key_object[new_key] = object[key]
    return fixed_key_object


def swap_submitted_data_labels(data, fields):
    data = remove_underscores(data)
    api_key_data = {}
    for label in data.keys():
        api_name_check = fields.filter(api_name=label).first()
        if api_name_check:
            api_key_data[api_name_check.api_name] = data[label]
        else:
            try:
                field_list = fields.filter(label__icontains=label)
                field = None
                for field_value in field_list:
                    if len(field_value.label) == len(label):
                        field = field_value
                        break
                api_key_data[field.api_name] = data[label]
            except Exception as e:
                continue
    return api_key_data


WORD_TO_NUMBER = {
    "a": 1,
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
}

TIME_TO_NUMBER = {"week": 7, "weeks": 7, "month": 30, "months": 30, "year": 365, "tomorrow": 1}
DAYS_TO_NUMBER = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6,
}


def convert_date_string(date_string, value):
    from dateutil.parser import parse

    if value is None:
        value = datetime.now()
    else:
        value = value.split("T")[0]
    split_date_string = date_string.lower().split(" ")
    time_key = None
    number_key = 1
    if any("push" in s for s in split_date_string) or any("move" in s for s in split_date_string):
        for key in split_date_string:
            if key in TIME_TO_NUMBER.keys():
                time_key = TIME_TO_NUMBER[key]
            if key in WORD_TO_NUMBER:
                number_key = WORD_TO_NUMBER[key]
    elif any(key in split_date_string for key in DAYS_TO_NUMBER.keys()):
        for key in split_date_string:
            if key in DAYS_TO_NUMBER.keys():
                current = datetime.now()
                start = current - timezone.timedelta(days=current.weekday())
                day_value = start + timezone.timedelta(days=DAYS_TO_NUMBER[key])
                if any("next" in s for s in split_date_string):
                    day_value = day_value + timezone.timedelta(days=7)
                return day_value
    elif any("end" in s for s in split_date_string):
        if any("week" in s for s in split_date_string):
            current = datetime.strptime(value, "%Y-%m-%d")
            start = current - timezone.timedelta(days=current.weekday())
            return start + timezone.timedelta(days=4)
        elif any("month" in s for s in split_date_string):
            current = datetime.strptime(value, "%Y-%m-%d")
            last_of_month = calendar.monthrange(current.year, current.month)[1]
            return current.replace(day=last_of_month)
    elif any("week" in s for s in split_date_string):
        current = datetime.strptime(value, "%Y-%m-%d")
        return current + timezone.timedelta(days=7)
    if "back" in date_string:
        new_value = datetime.strptime(value, "%Y-%m-%d") - timezone.timedelta(
            days=(time_key * number_key)
        )
    else:
        if time_key:
            new_value = datetime.strptime(value, "%Y-%m-%d") + timezone.timedelta(
                days=(time_key * number_key)
            )
        else:
            try:
                date_parsed = parse(date_string)
                new_value = date_parsed
            except Exception as e:
                print(e)
                new_value = value
    return new_value


def ask_managr_data_collector(user_id, resource_type, resource_id):
    from managr.core.models import User
    from managr.salesforce.models import MeetingWorkflow
    from managr.slack.models import OrgCustomSlackFormInstance, OrgCustomSlackForm
    from managr.salesforce.routes import routes as sf_routes
    from managr.hubspot.routes import routes as hs_routes

    CRM_SWITCHER = {"SALESFORCE": sf_routes, "HUBSPOT": hs_routes}
    user = User.objects.get(id=user_id)
    resource = CRM_SWITCHER[user.crm][resource_type]["model"].objects.get(id=resource_id)
    workflow_check = MeetingWorkflow.objects.filter(user=user, resource_id=resource_id).first()
    form_check = OrgCustomSlackFormInstance.objects.filter(
        user=user_id, resource_id=resource_id
    ).first()
    if form_check and form_check.saved_data:
        data_from_resource = form_check.saved_data
    else:
        template = (
            OrgCustomSlackForm.objects.for_user(user)
            .filter(resource=resource_type, form_type="UPDATE")
            .first()
        )
        api_names = template.list_field_api_names()
        data_from_resource = {}
        for name in api_names:
            data_from_resource[name] = resource.secondary_data[name]

    if workflow_check:
        if workflow_check.transcript_summary:
            data_from_resource["summary"] = workflow_check.transcript_summary
        if workflow_check.transcript_analysis:
            data_from_resource["analysis"] = workflow_check.transcript_analysis
    return data_from_resource
