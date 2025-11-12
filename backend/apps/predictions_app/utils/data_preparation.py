import json
import os
import joblib
import pandas as pd
from apps.predictions_app.models import PredictionSource
from apps.predictions_app.utils.prophet_forecasting import train_prophet_models
from config.settings import FORECAST_MODELS_PATH
from django.core.cache import cache


def get_cached_json(key):
    """Devuelve un objeto Python desde el caché (ya decodificado), o None si no existe."""
    cached_data = cache.get(key)
    if cached_data:
        try:
            result = json.loads(cached_data)
            return result
        except json.JSONDecodeError:
            return None
    return None


def set_cached_json(key, data, timeout=3600):
    """Guarda un objeto Python en caché codificado como JSON."""
    cache.set(key, json.dumps(data, default=str), timeout=timeout)


def get_filter_params(
    location_id,
    camera_id,
    key=None,
    values: tuple = ("startedAt", "totalVehicleCount", "avgSpeed"),
):
    """
    Filtra los parámetros de la consulta para obtener las predicciones.
    """
    historical_cache = get_cached_json(key)


    if historical_cache is not None:
        return historical_cache

    historical = (
        PredictionSource.objects.filter(
            locationId=location_id,
            cameraId=camera_id,
            isActive=True,
        )
        .values("startedAt", "totalVehicleCount", "avgSpeed")
        .order_by("startedAt")
    )

    if not historical.exists():
        return None

    set_cached_json(key, list(historical), timeout=3600)

    return historical.values(*values)


def create_dataframe(predictions) -> pd.DataFrame:
    df = pd.DataFrame(predictions)
    if "startedAt" in df.columns:
        df["startedAt"] = pd.to_datetime(df["startedAt"], errors="coerce")
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


def convert_forescast_to_str(forecast_df: pd.DataFrame) -> list:
    """Convierte el DataFrame de forecast a una lista de diccionarios con fechas en formato string."""
    forecast = forecast_df[["ds", "yhat"]].tail(144)
    forecast["ds"] = forecast["ds"].astype(str)

    return forecast.to_dict(orient="records")
