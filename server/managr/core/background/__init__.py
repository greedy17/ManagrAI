import logging
import pytz
from datetime import datetime


from background_task import background

from django.db.models import F, Q, Count
from django.utils import timezone

from managr.salesforce.models import MeetingWorkflow

from ..models import User

logger = logging.getLogger("managr")


def emit_create_calendar_event(user, title, start_time, participants, meeting_link, description):
    return _process_create_calendar_event(
        user, title, start_time, participants, meeting_link, description
    )


def _process_create_calendar_event(
    user, title, start_time, participants, meeting_link, description
):
    converted_time = datetime.strptime(start_time, "%Y-%m-%dT%H:%M:%S%z")
    unix_start_time = int(converted_time.timestamp())
    unix_end_time = unix_start_time + 1800
    try:
        res = user.nylas.schedule_meeting(
            title, unix_start_time, unix_end_time, participants, meeting_link, description
        )
        return res
    except Exception as e:
        logger.info(f"Nylas warning {e}")


def check_for_time(tz, hour, minute):
    user_timezone = pytz.timezone(tz)
    currenttime = datetime.today().time()
    current = pytz.utc.localize(datetime.combine(datetime.today(), currenttime)).astimezone(
        user_timezone
    )
    return current >= current.replace(hour=hour) and current <= current.replace(
        hour=hour, minute=minute
    )


def check_for_uncompleted_meetings(user_id):
    user = User.objects.get(id=user_id)
    total_meetings = MeetingWorkflow.objects.filter(user=user.id).filter(
        datetime_created__contains=datetime.today().date()
    )
    not_completed = [meeting for meeting in total_meetings if meeting.progress == 0]
    if len(not_completed):
        return {"status": True, "total": len(total_meetings), "not_completed": len(not_completed)}
    return {"status": False}


def _process_send_meeting_reminder(user_id, total, not_completed):
    user = User.objects.get(id=user_id)

    return
