from django.apps import AppConfig


class HubspotConfig(AppConfig):
    name = "hubspot"

    def ready(self):
        import managr.hubspot.signals
