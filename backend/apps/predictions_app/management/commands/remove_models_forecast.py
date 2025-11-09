from backend.apps.predictions_app.tasks.tasks_remove_models import remove_old_forecast_models
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "Agrupa vehículos en bloques de 10 minutos"

    def handle(self, *args, **options):
        
        result = remove_old_forecast_models()
        if result:
            self.stdout.write(
                self.style.SUCCESS(f"Procesados {len(result)} bloques: {result.join(', ')}")
            )
           
        else:
            self.stdout.write(self.style.WARNING("No hay modelos expirados para eliminar."))
            
