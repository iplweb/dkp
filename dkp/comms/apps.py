import sys
from django.apps import AppConfig


class CommsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'comms'

    _startup_reset_performed = False

    def ready(self):
        super().ready()

        if CommsConfig._startup_reset_performed:
            return

        # Skip Redis operations during build-time commands only
        skip_commands = {'collectstatic', 'migrate', 'makemigrations', 'check'}
        if len(sys.argv) > 1 and sys.argv[1] in skip_commands:
            return

        from .cache_utils import reset_connection_counts

        # Redis MUST be available at runtime - fail loudly if not
        reset_connection_counts()
        CommsConfig._startup_reset_performed = True
