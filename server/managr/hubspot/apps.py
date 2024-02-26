from django.apps import AppConfig


class HubspotConfig(AppConfig):
    name = "managr.hubspot"

    def ready(self):
        import managr.hubspot.signals
