from django.http import HttpResponse
from django.views.decorators.http import require_GET
from background_task.models import CompletedTask
from django.http import HttpResponseServerError
import uuid
import time

def check_task_status(verbose_name):
    if verbose_name:
        try:
            task = CompletedTask.objects.get(verbose_name=verbose_name)
            if task:
                return True
        except CompletedTask.DoesNotExist:
            return False
        except Exception as e:
            return False


def sse_stream(request):
    from managr.zoom.background import _process_frontend_transcript

    response = HttpResponse(content_type="text/event-stream")
    response["Cache-Control"] = "no-cache"
    response["Connection"] = "keep-alive"

    request_data = {
        'user_id': request.data["user_id"],
        'meeting_id': request.data["meeting_id"],
        'resource_type': request.data["resource_type"],
        'integration_id': request.data["integration_id"],
        'resource_id': request.data["resource_id"],
    }

    user = request.user
    task = _process_frontend_transcript(
        request_data, verbose_name=f"transcript-{user.email}-{uuid.uuid4()}"
    )

    verbose_name = task.verbose_name

    while True:
        task_status = check_task_status(verbose_name)
        if task_status:
            response.write("data: {\"status\": \"completed\"}\n\n")
            response.flush()
            break
        else:
            response.write("data: {\"status\": \"in_progress\"}\n\n")
            response.flush()

        # Adjust the interval duration (in seconds) based on your needs
        time.sleep(30)

    return response
