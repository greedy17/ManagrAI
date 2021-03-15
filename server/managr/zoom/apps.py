from django.apps import AppConfig


class ZoomConfig(AppConfig):
    name = "managr.zoom"

    def ready(self):
        import managr.zoom.signals
