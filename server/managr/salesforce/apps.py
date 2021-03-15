from django.apps import AppConfig


class SalesforceConfig(AppConfig):
    name = "managr.salesforce"

    def ready(self):
        import managr.salesforce.signals
