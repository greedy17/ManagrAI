# -*- coding: utf-8 -*-
from django.apps import AppConfig


class ManagrCoreConfig(AppConfig):
    name = "managr.core"

    def ready(self):
        import managr.core.signals
