from django.apps import AppConfig


class CommsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'comms'

    _startup_reset_performed = False

    def ready(self):
        super().ready()

        if CommsConfig._startup_reset_performed:
            return

        from .cache_utils import reset_connection_counts

        reset_connection_counts()
        CommsConfig._startup_reset_performed = True
