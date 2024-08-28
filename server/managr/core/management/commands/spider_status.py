import datetime
from django.core.management.base import BaseCommand
from managr.core.models import CrawlerReport
from managr.comms.models import NewsSource
from managr.comms.tasks import _run_spider_batch
from background_task.models import Task
from django.conf import settings
from managr.api.emails import send_html_email
from managr.slack.helpers.utils import send_to_error_channel


class Command(BaseCommand):
    help = "Batch Spiders to run"

    def handle(self, *args, **options):
        batch_size = 10
        tasks = Task.objects.all()
        locked_tasks = tasks.filter(locked_at__isnull=False, task_name__contains="spider")
        if len(locked_tasks):
            dt = datetime.datetime.now().replace(tzinfo=datetime.timezone.utc)
            for task in locked_tasks:
                task_locked = task.locked_at.replace(tzinfo=datetime.timezone.utc)
                seconds_since_locked = dt - task_locked
                if seconds_since_locked.seconds >= 1500:
                    params = task.params()[0]
                    print(f"TASK RESTARTED: {params}")
                    task.delete()
                    url_list = ",".join(params)
                    _run_spider_batch(url_list)

        if len(tasks) == 0:
            sources = NewsSource.domain_list(True)
            if len(sources):
                print(f"SOURCE NOT RAN: {sources}")
            else:
                report = CrawlerReport.objects.all().order_by("-datetime_created").first()
                if not report.end_ts:
                    data = report.create_report_data()
                    send_to_error_channel(
                        f"Crawler finished at: {datetime.datetime.now()}, Completed in: {data['time']}",
                        None,
                        "crawler",
                        f"Crawler Update {settings.ENVIRONMENT}",
                        str(report.id),
                    )
                    report.end_ts = datetime.datetime.now()
                    report.save()
                    problem_urls = NewsSource.problem_urls()
                    problem_urls = ", ".join(problem_urls)
                    data["problem_urls"] = problem_urls
                    try:
                        send_html_email(
                            f"Managr Crawler Report",
                            "core/email-templates/crawler-email.html",
                            settings.DEFAULT_FROM_EMAIL,
                            ["zach@mymanagr.com"],
                            context=data,
                        )
                    except Exception as e:
                        print(str(e))
