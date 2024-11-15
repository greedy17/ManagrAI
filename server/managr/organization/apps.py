from django.apps import AppConfig


class OrganizationConfig(AppConfig):
    name = "managr.organization"

    def ready(self):
        import managr.organization.signals

        return
