from datetime import datetime, timedelta
from django.apps import AppConfig
import sys


class ValdataConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'valdata'

    def ready(self):
        if 'runserver' not in sys.argv:
            return True
        from .tasks import set_data
        set_data.delay()