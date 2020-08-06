from django.utils import timezone


def generate_story_report_data(story_report):
    """
    Given an instance of StoryReport, generate the report's
    data and update the instance with the generated data.
    Finally, trigger email regarding report generation to
    user that triggered this story_report to be generated.
    """
    pass
    # print story report mockups
    # meet with Marcy to iron out report data details

    # story_report.data = x
    # story_report.datetime_generated = timezone.now()
    # story_report.save()
    # trigger email
