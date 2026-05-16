from django.apps import AppConfig

class EamsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'eams'

    def ready(self):
        import eams.signals
