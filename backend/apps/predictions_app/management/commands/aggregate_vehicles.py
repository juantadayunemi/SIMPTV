from django.core.management.base import BaseCommand
from backend.apps.predictions_app.tasks.tasks_aggregate_vehicles import aggregate_prediction_data

"""
Comando para ejecutar la tarea de agregación manualmente:
python manage.py aggregate_vehicles
"""


class Command(BaseCommand):
    help = "Agrupa vehículos en bloques de 10 minutos"

    def handle(self, *args, **options):
        result = aggregate_prediction_data()
        # self.stdout.write(
        #     self.style.SUCCESS(f"Procesados {result['blocks_processed']} bloques, ")
        # )
