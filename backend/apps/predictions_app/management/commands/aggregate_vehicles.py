from django.core.management.base import BaseCommand
from apps.predictions_app.tasks import aggregate_prediction_data
class Command(BaseCommand):
    help = 'Agrupa vehículos en bloques de 10 minutos'

    def handle(self, *args, **options):
        result = aggregate_prediction_data()
        self.stdout.write(
            self.style.SUCCESS(
                f"Procesados {result['blocks_processed']} bloques, "
                f"creados {result['groups_created']} grupos"
            )
        )