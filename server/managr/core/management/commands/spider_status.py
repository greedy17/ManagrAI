import datetime
from django.core.management.base import BaseCommand
from managr.core.models import CrawlerReport
from managr.comms.models import NewsSource
from managr.comms.tasks import _run_spider_batch
from background_task.models import Task
from django.conf import settings
from managr.api.emails import send_html_email


class Command(BaseCommand):
    help = "Batch Spiders to run"

    def handle(self, *args, **options):
        batch_size = 10
        tasks = Task.objects.filter(task_name="managr.comms.tasks._run_spider_batch")
        locked_tasks = tasks.filter(locked_at__isnull=False)
        if len(locked_tasks):
            dt = datetime.datetime.now().replace(tzinfo=datetime.timezone.utc)
            for task in locked_tasks:
                task_locked = task.locked_at.replace(tzinfo=datetime.timezone.utc)
                seconds_since_locked = dt - task_locked
                if seconds_since_locked.seconds >= 1500:
                    # params = task.params()[0]
                    task.delete()
                    # url_list = ",".join(params)
                    # _run_spider_batch(url_list)

        if len(tasks) == 0:
            sources = NewsSource.domain_list(True)
            if len(sources):
                for i in range(0, len(sources), int(batch_size)):
                    batch = sources[i : i + int(batch_size)]
                    batch_url_list = ",".join(batch)
                    _run_spider_batch(batch_url_list)
            else:
                report = CrawlerReport.objects.all().order_by("-datetime_created").first()
                data = report.create_report_data()
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
