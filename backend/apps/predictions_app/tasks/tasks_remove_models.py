import os
from datetime import datetime, timedelta
from celery import shared_task
from config.settings import FORECAST_MODELS_PATH

EXPIRATION_TIME = 30  # minutos


@shared_task
def remove_old_forecast_models():
    """
    Elimina modelos Prophet (.joblib) que superen el tiempo de vida permitido.
    Se ejecutará periódicamente con Celery Beat.
    """
    now = datetime.now()
    deleted_files = []

    if not os.path.exists(FORECAST_MODELS_PATH):
        print(f"Carpeta no encontrada: {FORECAST_MODELS_PATH}")
        return []

    for file in os.listdir(FORECAST_MODELS_PATH):
        if file.endswith(".joblib"):
            path = os.path.join(FORECAST_MODELS_PATH, file)
            modified_time = datetime.fromtimestamp(os.path.getmtime(path))
            if now - modified_time > timedelta(minutes=EXPIRATION_TIME):
                os.remove(path)
                deleted_files.append(file)

    return deleted_files
