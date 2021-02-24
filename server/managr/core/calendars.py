"""
Helpers for interacting with Google and Microsoft calendars via Nylas.
"""
import logging
from nylas import APIClient

from django.conf import settings
from django.utils import timezone

from .models import NylasAuthAccount

logger = logging.getLogger("managr")


def calendar_participants_from_zoom_meeting(zoom_meeting, user):
    """Given a `ZoomMeeting` instance, look for matching calendar event and get participants.

    Args:
        zoom_meeting (ZoomMtg): ZoomMtg helper instance that corresponds to a Zoom meeting
                                            that ended, which we were notified about through
                                            a webhook.
        user (User): Required because we are working with a ZoomMtg helper instance, 
                     not a full model.
    """
    logger.info("Retrieving participants for Zoom meeting from Nylas Calendar...")

    # Do nothing if the user hasn't connected Nylas
    try:
        nylas = user.nylas
    except NylasAuthAccount.DoesNotExist:
        logger.warning(
            "Attempted to look up calendar participants for a Zoom Meeting that ended "
            "but the user does not have an active Nylas integration."
        )
        return

    # Otherwise, init the Nylas Client
    nylas = APIClient(settings.NYLAS_CLIENT_ID, settings.NYLAS_CLIENT_SECRET, nylas.access_token)

    """
    Zoom and Calendar meeting datetimes might not exactly match up, so
    we use some heuristics for finding the matching calendar event.

    Things we can match on:
     - Start and End time - This should match from Zoom to calendar. Searchable in the Nylas API.
     - "Topic": The title of the meeting. Searchable in the Nylas API.
     - "Owner": NOT searchable in the Nylas API, but we can check the resulting event objects.
    """
    zoom_start = zoom_meeting.start_time_timestamp
    zoom_end = zoom_meeting.end_time_timestamp
    filters = {
        "limit": 50,
        # Get all events starting/ending within two hours of the start/end times
        "starts_after": zoom_start - (60 * 60 * 2),
        "ends_before": zoom_end + (60 * 60 * 2),
    }

    # NOTE: The time range should really narrow things down, but there is a chance
    #       we could get back a lot of events from multiple calendars, hence the limit here.
    nylas_response = nylas.events.where(**filters)

    # Force-invoke the API call
    events = list(nylas_response)

    logger.info(f"    Found {len(events)} event/s")

    # Narrow down results
    # Get user-owned events
    user_events = [e for e in events if user.email in e.owner]

    logger.info(f"    Found {len(user_events)} user event/s")

    # Compute the overlap percentage of the zoom meeting vs each calendar meeting
    overlaps = []
    for e in user_events:
        calendar_end = e.when["end_time"]
        calendar_start = e.when["start_time"]
        if zoom_end > calendar_start:
            zoom_diff = zoom_end - calendar_start
            calendar_duration = calendar_end - calendar_start
        elif zoom_start < calendar_end:
            zoom_diff = calendar_end - zoom_start
            calendar_duration = calendar_end - calendar_start
        else:
            # No overlap, omit from list
            continue

        # Compute percentage overlap with calendar event, 1-100
        overlap = int((zoom_diff / calendar_duration) * 100)

        # Bundle overlaps with event objects
        overlaps.append(
            {"overlap": overlap, "event": e,}
        )

    # Get events with overlap greater than 70%
    best_events = [o["event"] for o in overlaps if o["overlap"] > 70]

    logger.info(f"    Found {len(best_events)} events with overlap over 70%")

    # Collect participants from ALL of the meeting/s we retrieved and return that list
    participants = []
    for event in best_events:
        logger.info(f"     Getting participants from event: {event}")
        participants = [*participants, *event.participants]

    logger.info(f"    Got calendar participants: {participants}")

    # HACK: Here we translate this dictionary to match dict structure of Zoom participants
    return [{"user_email": p.get("email"), "name": p.get("name"),} for p in participants]
