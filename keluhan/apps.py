from django.apps import AppConfig

class KeluhanConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'keluhan'

    def ready(self):
        import keluhan.signals