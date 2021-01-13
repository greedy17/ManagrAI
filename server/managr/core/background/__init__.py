import logging

import datetime

from background_task import background

from django.db.models import F, Q, Count
from django.utils import timezone


from managr.core.models import EmailAuthAccount, User
from managr.opportunity.background import emit_event as log_event
from managr.opportunity import constants as lead_constants
from managr.core import constants as core_consts
from managr.opportunity.models import Notification,LeadActivityLog

from managr.report.story_report_generation import generate_story_report_data
from managr.report.performance_report_generation import generate_performance_report_data

from managr.report import constants as report_const



logger = logging.getLogger("managr")


def emit_generate_story_report_on_close(report, share_to_channel):
    return _generate_story_report_data(str(report.id), share_to_channel)


def emit_report_event(report_id, report_type):
    if report_type is report_const.STORY_REPORT:
        _generate_story_report_data(report_id)
    else:
        _generate_performance_report_data(report_id)


@background(schedule=0)
def _generate_story_report_data(report_id, share_to_channel=False):
    return generate_story_report_data(report_id, share_to_channel)


@background(schedule=0)
def _generate_performance_report_data(report_id):
    return generate_performance_report_data(report_id)



