from celery import shared_task
from apps.predictions_app.utils.data_preparation import (
    convert_forescast_to_str,
    get_cached_json,
    get_filter_params,
    create_dataframe,
    get_model_prediction,
    set_cached_json,
)
from apps.predictions_app.utils.prophet_forecasting import (
    get_forecast,
    get_forecast_by_date,
)
from apps.predictions_app.utils.holidays import (
    create_holidays_object,
    create_dataframe_holiday,
    get_name_holiday,
)
from apps.predictions_app.utils.calculations import (
    calculate_periods,
    previous_periods,
    convert_datetime,
)
from apps.predictions_app.utils.calculations import get_percentage
from apps.predictions_app.utils.forecast_analysis import (
    get_total_seasonality,
    get_previous_forecast,
    traffic_level_classification,
)

from config.settings import FORECAST_MODELS_PATH
from django.core.cache import cache
import json
import pandas as pd


def get_model_path(location_id, camera_id, variable):
    return f"{FORECAST_MODELS_PATH}/prophet_{variable}_location_{location_id}_camera_{camera_id}.joblib"


def get_value_param(params, key, default=None):
    return params.get(key, default)


def get_all_predictions(params):
    location_id = int(params.get("locationId"))
    camera_id = int(params.get("cameraId"))
    date = params.get("date")
    hour = int(params.get("hour"))
    minute = int(params.get("minute", "00"))
    # cache.delete(cache_key_historical)
    key = f"traffic_pred_{location_id}_{camera_id}_{date}_{hour}_{minute}"

    # cache.delete(f"historical_{location_id}_{camera_id}")
    result_cache = get_cached_json(key)

    if result_cache is not None:
        del result_cache["traffic"]["full_forecast"]
        return result_cache

    traffic = get_traffic_prediction(params)

    speed = get_speed_prediction(params)

    level = get_level_prediction(
        {
            "locationId": params.get("locationId"),
            "cameraId": params.get("cameraId"),
            "yhat_count": traffic["yhat"],
            "yhat_speed": speed["yhat_speed"],
        },
    )

    result = {
        "traffic": traffic,
        "speed": speed,
        "level": level,
    }

    set_cached_json(key, result, timeout=3600)
    result_return = result.copy()
    del result_return["traffic"]["full_forecast"]

    return result_return


def get_traffic_prediction(params):
    """
    Servicio que procesa la predicción de tráfico vehicular.
    """
    # Obtener parámetros de consulta
    location_id = int(params.get("locationId"))
    camera_id = int(params.get("cameraId"))
    date = params.get("date")
    hour = int(params.get("hour"))
    minute = int(params.get("minute", "00"))
    periods_type = params.get("periodsType", "monthly")

    if all([location_id, camera_id, date, hour, minute, periods_type is None]):
        raise ValueError(
            "Faltan parámetros requeridos (locationId, cameraId, date, hour, minute, periodsType)."
        )

    predictions = get_filter_params(
        location_id,
        camera_id,
        key=f"historical_{location_id}_{camera_id}",
        values=("startedAt", "totalVehicleCount"),
    )

    if not predictions:
        raise ValueError(
            "No existe ningún análisis para los parámetros proporcionados."
        )

    df = create_dataframe(predictions)

    df = df.rename(columns={"startedAt": "ds", "totalVehicleCount": "y"})
    df["ds"] = df["ds"].dt.tz_convert("America/Guayaquil").dt.tz_localize(None)

    local_holidays = create_holidays_object()
    holidays = create_dataframe_holiday(local_holidays)
    model_path = get_model_path(location_id, camera_id, "traffic")
    df_model = get_model_prediction(model_path, holidays, df)

    # calcular el periodo a predecir en el futuro
    periods, current_datetime = calculate_periods(df, date, hour, minute)
    # predicciones de la variable totalVehicleCount
    forecast = get_forecast(df_model, periods, freq="10T")

    row = get_forecast_by_date(forecast, current_datetime)
    yhat = row["yhat"]
    trend = row["trend"]
    seasonality = get_total_seasonality(row)

    # obtener forecast del mes anterior
    holiday_name = get_name_holiday(local_holidays, date)
    previous_date = previous_periods(date, periods_type)
    previous_date = convert_datetime(previous_date, hour, minute)
    variation_forecast_metrics = get_previous_forecast(
        forecast,
        previous_date,
        yhat,
        trend,
    )
    full_forecast = forecast.copy()

    return {
        "yhat": yhat,
        "trend": get_percentage(trend, yhat),
        "seasonality": get_percentage(seasonality, yhat),
        "holidays": get_percentage(row["holidays"], yhat),
        "holidays_name": holiday_name,
        "confidenceLevel": 0.80 * 100,
        "variation_forecast_metrics": variation_forecast_metrics,
        "forecast": convert_forescast_to_str(forecast),
        "full_forecast": full_forecast.to_dict(orient="records"),
        "is_reliable": not (row["yhat"] < 0 or row["yhat"] > 1000),
    }


def get_speed_prediction(params):
    """
    Servicio que procesa la predicción de velocidad vehicular.
    """
    # Obtener parámetros de consulta
    location_id = int(params.get("locationId"))
    camera_id = int(params.get("cameraId"))
    date = params.get("date")
    hour = int(params.get("hour"))
    minute = int(params.get("minute", "00"))

    predictions = get_filter_params(
        location_id,
        camera_id,
        key=f"historical_{location_id}_{camera_id}",
        values=(
            "startedAt",
            "avgSpeed",
        ),
    )

    if predictions is None:
        raise ValueError(
            "No existe ningún análisis para los parámetros proporcionados."
        )

    df = create_dataframe(predictions)

    df_speed = df.rename(columns={"startedAt": "ds", "avgSpeed": "y"})
    df_speed["ds"] = (
        df_speed["ds"].dt.tz_convert("America/Guayaquil").dt.tz_localize(None)
    )

    local_holidays = create_holidays_object()
    holidays = create_dataframe_holiday(local_holidays)

    model_path = get_model_path(location_id, camera_id, "speed")
    model = get_model_prediction(model_path, holidays, df_speed)

    # calcular el periodo a predecir en el futuro
    periods, current_datetime = calculate_periods(df_speed, date, hour, minute)

    # se obtienen las predicciones de la variable velocidad
    forecast_speed = get_forecast(model, periods, freq="10T")
    row_speed = get_forecast_by_date(forecast_speed, current_datetime)

    return {
        "yhat_speed": row_speed["yhat"],
        "forecast_speed": convert_forescast_to_str(forecast_speed),
        "is_reliable": not (row_speed["yhat"] < 0 or row_speed["yhat"] > 1000),
    }


@shared_task
def get_bottleneck_traffic(params):
    """
    Calcula el Índice de Congestión (IC) y nivel de tráfico
    usando percentiles históricos.

    """
    location_id = int(params.get("locationId"))
    camera_id = int(params.get("cameraId"))
    date = params.get("date")
    hour = int(params.get("hour", "00"))
    minute = int(params.get("minute", "00"))

    cached_data = get_cached_json(
        f"traffic_pred_{location_id}_{camera_id}_{date}_{hour}_{minute}"
    )

    if cached_data:
        traffic_pred = cached_data["traffic"]
        speed_pred = cached_data["speed"]
    else:
        traffic_pred = get_traffic_prediction(params)
        speed_pred = get_speed_prediction(params)

    traffic_pred = list(traffic_pred["forecast"])
    speed_pred = list(speed_pred["forecast_speed"])

    historical = get_filter_params(
        location_id,
        camera_id,
        key=f"historical_{location_id}_{camera_id}",
        values=("avgSpeed", "totalVehicleCount"),
    )

    if not historical:
        raise ValueError("No existen datos históricos para esta cámara o ubicación.")

    df_hist = create_dataframe(historical)

    results = []

    for traffic, speed in zip(traffic_pred, speed_pred):
        yhat_count = float(traffic["yhat"])
        yhat_speed = float(speed["yhat"])

        level, IC = traffic_level_classification(df_hist, yhat_count, yhat_speed)

        traffic["ds"] = pd.to_datetime(traffic["ds"])
        hour_minute = traffic["ds"].strftime("%H:%M")

        results.append(
            {
                "ds": traffic["ds"].strftime("%Y-%m-%d %H:%M:%S"),
                "yhat_count": yhat_count,
                "yhat_speed": yhat_speed,
                "IC": IC,
                "level": level,
            }
        )

        datos = [
            {
                "ds": "2025-11-11 22:50:00",
                "yhat_count": 18.555146343120015,
                "yhat_speed": 73.52243285129268,
                "IC": 0.19,
                "level": "Embotellamiento",
            },
            {
                "ds": "2025-11-11 23:10:00",
                "yhat_count": 22.531889345204668,
                "yhat_speed": 72.3796040614809,
                "IC": 0.26,
                "level": "Embotellamiento",
            },
        ]
    return datos


def get_level_prediction(params):

    location_id = int(params.get("locationId"))
    camera_id = int(params.get("cameraId"))
    yhat_count = float(params.get("yhat_count"))
    yhat_speed = float(params.get("yhat_speed"))

    historical = get_filter_params(
        location_id,
        camera_id,
        key=f"historical_{location_id}_{camera_id}",
        values=("avgSpeed", "totalVehicleCount"),
    )

    if not historical:
        raise ValueError("No existen datos históricos para esta cámara o ubicación.")

    df_hist = create_dataframe(historical)
    level, IC = traffic_level_classification(df_hist, yhat_count, yhat_speed)
    return {
        "IC": IC,
        "level": level,
    }


def get_forecast_change_percent(params):
    location_id = int(params.get("locationId"))
    camera_id = int(params.get("cameraId"))
    date = params.get("date")
    hour = int(params.get("hour"))
    minute = int(params.get("minute", "00"))
    periods_type = params.get("periodsType", "monthly")

    cache_key = f"traffic_pred_{location_id}_{camera_id}_{date}_{hour}_{minute}"

    cached_data = get_cached_json(cache_key)
    if cached_data:
        traffic_pred = cached_data["traffic"]
        forecast_df = traffic_pred["full_forecast"] = pd.DataFrame(
            traffic_pred["full_forecast"]
        )
        forecast_df["ds"] = pd.to_datetime(forecast_df["ds"])
    else:
        traffic_pred = get_traffic_prediction(params)

    previous_date = previous_periods(date, periods_type)
    previous_date = convert_datetime(previous_date, hour, minute)

    variation_forecast_metrics = get_previous_forecast(
        forecast_df,
        previous_date,
        traffic_pred["yhat"],
        traffic_pred["trend"],
    )

    return variation_forecast_metrics
