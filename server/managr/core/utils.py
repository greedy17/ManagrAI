import calendar
from django.conf import settings
from django.utils import timezone
from datetime import datetime
from django.db.models import Q
from managr.core.models import User
from managr.alerts.models import AlertConfig
from managr.slack.models import OrgCustomSlackFormInstance
from managr.organization.models import Organization
from managr.salesforce.models import MeetingWorkflow


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
        curr_month["total active users"] = len(
            slack_form_instances.order_by().values("user").distinct("user")
        )
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
        user_obj["meetings"] = user_instances.values_list("workflow").distinct().count()
        user_obj["contacts"] = user_instances.filter(
            template__form_type="CREATE", template__resource="Contact"
        ).count()
        user_obj["fields"] = get_user_fields(user_id, start, end)
        totals = user_obj
        # totals[date[1]] = user_obj
    return totals


def pull_usage_data(month_only=True):
    totals = get_totals_for_year(month_only)
    orgs = get_organization_totals(month_only)
    return {"totals": totals, "org": orgs}
