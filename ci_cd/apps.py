from django.apps import AppConfig


class CiCdConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ci_cd'

    def ready(self):
        import ci_cd.signals


