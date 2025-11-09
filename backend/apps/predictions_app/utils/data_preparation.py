import os
import joblib
import pandas as pd
from apps.predictions_app.models import PredictionSource
from apps.predictions_app.utils.prophet_forecasting import train_prophet_models
from config.settings import FORECAST_MODELS_PATH


def get_filter_params(location_id, camera_id):
    """
    Filtra los parámetros de la consulta para obtener las predicciones.
    """
    predictions = PredictionSource.objects.filter(
        locationId=location_id,
        cameraId=camera_id,
        isActive=True,
    ).order_by("startedAt")

    if not predictions.exists():
        return None

    return predictions


def create_dataframe(predictions, values: tuple) -> pd.DataFrame:
    df = pd.DataFrame(
        list(
            predictions.values(
                *values,
            )
        )
    )
    return df


def get_model_prediction(model_path: str, holidays: pd.DataFrame, df: pd.DataFrame):
    if os.path.exists(model_path):
        model = joblib.load(model_path)
    else:
        model = train_prophet_models(holidays, df)
        if not os.path.exists(FORECAST_MODELS_PATH):
            os.makedirs(FORECAST_MODELS_PATH)
        joblib.dump(model, model_path)
    return model
