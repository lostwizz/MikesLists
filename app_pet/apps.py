from django.apps import AppConfig


class AppPetConfig(AppConfig):
    name = 'app_pet'
    verbose_name = 'Digital Pet'

    def ready(self):
        import app_pet.signals  # noqa: F401 - registers signal handlers
