from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from managr.core.utils import get_totals_for_year, get_organization_totals
from managr.api.emails import send_html_email


class Command(BaseCommand):
    """
    Usage:
        ./manage.py pull_usage_data

    Description: pulls high-level usage statistics from the database.
    Currently limited to the number of users, the number of meetings,
    and the number of SalesForce fields.

    By default, this pulls the usage statistics for the month 
    or range if args passed in 
    """

    help = "Pull usage statistics for the application"

    def add_arguments(self, parser):
        parser.add_argument("-m", "--month", action="store_true")

    def handle(self, *args, **options):
        # email_subject = "Managr Usage Data"
        # recipients = ["zach@mymanagr.com"]
        if options["month"]:
            totals = get_totals_for_year(True)
            orgs = get_organization_totals(True)
        else:
            totals = get_totals_for_year()
            orgs = get_organization_totals()
        # send_html_email(
        #     email_subject,
        #     "core/email-templates/usage-data.html",
        #     settings.SERVER_EMAIL,
        #     recipients,
        #     context=totals,
        # )
        for date in orgs.keys():
            print(f"{date}")
            print(
                f" New Users: {totals[date]['users']} | Total Active Users: {totals[date]['total active users']}"
            )
            print(f" Workflows Created: {totals[date]['workflows']}")
            updates = totals[date]["updates"]
            creates = totals[date]["creates"]
            print(
                f" Updates: Total {updates['total']} | Alert: {updates['alert']} | Command: {updates['command']} | Meeting: {updates['meeting']} | Pipeline: {updates['pipeline']}"
            )
            print(
                f" Creates: Total {creates['total']} | Contacts: {creates['contacts']} | Accounts: {creates['accounts']} | Opportunities: {creates['opportunities']} | Products: {creates['products']}"
            )
            print("\n Per Organization:")
            print(" ---------------------------------------------------------------")

            for org in orgs[date].keys():
                print(f" {org}")
                o = orgs[date][org]
                if o:
                    print(
                        f" Org: Session Avg: {o['session average']} | Avg Total Sessions: {o['average total sessions']} | Updates: {o['updates']} | Creates: {o['creates']}"
                    )
                    print(f" Users:")
                    for user in o["users"].keys():
                        u = o["users"][user]
                        print(
                            f"  {user} - Session Avg: {u['session average']} | Total Sessions: {u['total sessions']} | Updates: {u['updates']} | Creates: {u['creates']}"
                        )
                    print(f" Fields:")
                    print(f" {o['fields']}")
                else:
                    print(
                        f" Org: Session Avg: N/A | Avg Total Sessions: N/A | Updates: N/A | Creates: N/A"
                    )
                    print(" Users: N/A")
                    print(" Fields: N/A")

                print(" ---------------------------------------------------------------")
            print("---------------------------------------------------------------")

