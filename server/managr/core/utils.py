import calendar
from datetime import datetime
from managr.core.models import User
from managr.alerts.models import AlertConfig
from managr.slack.models import OrgCustomSlackFormInstance


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


def get_totals_for_year():
    # Base queries
    totals = {}
    current_date = datetime.now()
    date_list = get_month_start_and_end(current_date.year, current_date.month)
    for date in date_list:
        curr_month = {}
        start = datetime.strptime(f"{date[0]} 00:01", "%Y-%m-%d %H:%M")
        end = datetime.strptime(f"{date[1]} 23:59", "%Y-%m-%d %H:%M")
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
        totals[date[1]] = curr_month
    return {"data": totals}
