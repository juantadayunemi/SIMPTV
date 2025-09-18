from django.apps import AppConfig


class EntitiesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "entities"
    verbose_name = "Shared Models Library"
    verbose_name_plural = "Shared Models Library"

    def ready(self):
        """Initialize the models library when Django starts"""
        # This app functions as a DLL/library for shared models
        # Models are auto-generated from TypeScript entities
        pass
