import calendar
from django.conf import settings
from datetime import datetime
from xml.parsers.expat import model
from managr.core.models import User
from managr.alerts.models import AlertConfig
from managr.slack.models import OrgCustomSlackFormInstance
from managr.organization.models import Organization


def get_month_start_and_end(year, current_month):
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
    total_average = (
        (sum(days_list) / int(month_end[len(month_end) - 2 :])) if sum(days_list) > 0 else 0
    )
    return {
        "month average": total_average,
        "session average": average,
        "total sessions": len(days_list),
    }


def get_totals_for_year():
    # Base queries
    totals = {}
    current_date = datetime.now()
    date_list = get_month_start_and_end(current_date.year, current_date.month)
    for date in date_list:
        curr_month = {}
        start = datetime.strptime(f"{date[0]} 00:01", "%Y-%m-%d %H:%M")
        end = datetime.strptime(f"{date[1]} 23:59", "%Y-%m-%d %H:%M")
        if settings.IN_STAGING or settings.IN_DEV:
            slack_form_instances = OrgCustomSlackFormInstance.objects.filter(
                datetime_created__range=(start, end)
            ).filter(is_submitted=True)
        else:
            slack_form_instances = (
                OrgCustomSlackFormInstance.objects.filter(datetime_created__range=(start, end))
                .filter(is_submitted=True)
                .exclude(user__organization__name="Managr")
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
        update_forms = slack_form_instances.filter(template__form_type="UPDATE")
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


def get_organization_totals():
    totals = {}
    current_date = datetime.now()
    date_list = get_month_start_and_end(current_date.year, current_date.month)
    orgs = Organization.objects.all()
    users = User.objects.all()
    for date in date_list:
        start = datetime.strptime(f"{date[0]} 00:01", "%Y-%m-%d %H:%M")
        end = datetime.strptime(f"{date[1]} 23:59", "%Y-%m-%d %H:%M")
        if settings.IN_STAGING or settings.IN_DEV:
            slack_form_instances = OrgCustomSlackFormInstance.objects.filter(
                datetime_created__range=(start, end)
            ).filter(is_submitted=True)
        else:
            slack_form_instances = (
                OrgCustomSlackFormInstance.objects.filter(datetime_created__range=(start, end))
                .filter(is_submitted=True)
                .exclude(user__organization__name="Managr")
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
                user_obj["updates"] = user_instances.filter(template__form_type="UPDATE").count()
                user_obj["creates"] = user_instances.filter(template__form_type="CREATE").count()
                users_obj[user.email] = user_obj
            org_obj["users"] = users_obj
            org_obj["updates"] = org_totals_instances.filter(template__form_type="UPDATE").count()
            org_obj["creates"] = org_totals_instances.filter(template__form_type="CREATE").count()
            org_averages = get_instance_averages(org_totals_instances, date[1])
            org_obj.update(org_averages)
            org_totals[org.name] = org_obj

        totals[date[1]] = org_totals
    return totals

