import logging

import datetime

from background_task import background

from django.db.models import F, Q, Count
from django.utils import timezone


logger = logging.getLogger("managr")

