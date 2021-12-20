"""
Helpers for interacting with Google and Microsoft calendars via Nylas.
"""
import logging
import math
from nylas import APIClient

from django.conf import settings

from .models import NylasAuthAccount

logger = logging.getLogger("managr")

# Calendar events will be accepted as a match for the Zoom Meeting if
# their (start, end) "distance" from the actual (start, end) distance
# falls within this threshold. This is measured as seconds since
# the epoch.
#
# NOTE: This may be less accurate for longer or shorter meetings, so
#       it might be a good idea to scale the threshold based on meeting
#       duration.
#
DISTANCE_THRESHOLD = 2500


def _euclidean_distance(x, y):
    """Get the Euclidean distance between two vectors.

    Args:
        x (tuple)
        y (tuple)
    """
    return math.sqrt(sum([(a - b) ** 2 for a, b in zip(x, y)]))


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
        return []

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
        # Get all events starting within two hours of the start/end times
        # NOTE: We use start time only because the filters are combined using an AND,
        #       so we don't want to miss longer events that might end just outside
        #       of the window of time we're looking at.
        "starts_after": zoom_start - (60 * 60 * 2),
        "starts_before": zoom_end + (60 * 60 * 2),
    }

    # NOTE: The time range should really narrow things down, but there is a chance
    #       we could get back a lot of events from multiple calendars, hence the limit here.

    # Force-invoke the API call
    try:
        nylas_response = nylas.events.where(**filters)
        events = list(nylas_response)
    except:
        logger.error("Error calling the Nylas API")
        events = list()
    # Force-invoke the API call

    # events = list()

    logger.info(f"    Found {len(events)} event/s")

    # Narrow down results
    # Get user-owned events
    user_events = [e for e in events if user.email in e.owner]

    logger.info(f"    Found {len(user_events)} user event/s")

    # Compute the distance between the zoom meeting and each calendar meeting
    distances = []
    for e in user_events:
        # Get the distance between Calendar (start, end) and Zoom (start, end)
        distance = _euclidean_distance(
            (e.when["start_time"], e.when["end_time"]), (zoom_start, zoom_end)
        )
        # Bundle distances with event objects
        distances.append(
            {"distance": distance, "event": e,}
        )

    # Get events with distances less than the defined threshold
    best_events = [d["event"] for d in distances if d["distance"] < DISTANCE_THRESHOLD]

    distances_str = ", ".join([str(d["distance"]) for d in distances])
    logger.info(f"    Meeting distances: {distances_str}")
    logger.info(f"    Found {len(best_events)} event/s within the threshold distance.")

    # Collect participants from ALL of the meeting/s we retrieved and return that list
    participants = []
    for event in best_events:
        logger.info(f"     Getting participants from event: {event}")
        participants = [*participants, *event.participants]

    logger.info(f"    Got calendar participants: {participants}")

    # HACK: Here we translate this dictionary to match dict structure of Zoom participants
    return [{"user_email": p.get("email"), "name": p.get("name"),} for p in participants]
