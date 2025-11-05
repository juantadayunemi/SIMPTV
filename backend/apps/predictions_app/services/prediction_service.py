import pandas as pd
import numpy as np
from prophet import Prophet
from datetime import datetime
from apps.predictions_app.models import PredictionSource
from apps.predictions_app.utils.predictions import (
    get_forecast_by_date,
    get_previous_forecast,
    get_total_seasonality,
    traffic_level_classification,
    get_forecast,
)
from apps.predictions_app.utils.holidays import (
    create_dataframe_holiday,
    create_holidays_object,
    get_name_holiday,
)
from apps.predictions_app.utils.calculations import (
    add_to_date,
    convert_datetime,
    get_percentage,
    previous_periods,
)


import pandas as pd
from prophet import Prophet
from datetime import datetime
from apps.predictions_app.models import PredictionSource
from apps.predictions_app.utils.predictions import (
    get_forecast_by_date,
    get_previous_forecast,
    get_total_seasonality,
    traffic_level_classification,
)
from apps.predictions_app.utils.holidays import (
    create_dataframe_holiday,
    create_holidays_object,
    get_name_holiday,
)
from apps.predictions_app.utils.calculations import (
    add_to_date,
    convert_datetime,
    get_percentage,
    previous_periods,
)


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


def calculate_periods(df, date, hour, minute):
    # calcular el periodo a predecir en el futuro
    last_datetime = df["ds"].max()
    current_datetime = convert_datetime(date, hour, minute)
    target_datetime = current_datetime.replace(hour=23, minute=50)
    delta = target_datetime - last_datetime
    periods = int(delta.total_seconds() // 600)

    return periods, current_datetime


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

    predictions = get_filter_params(location_id, camera_id)

    if predictions is None:
        raise ValueError(
            "No existe ningún análisis para los parámetros proporcionados."
        )

    df = create_dataframe(
        predictions,
        (
            "startedAt",
            "totalVehicleCount",
        ),
    )
    df = df.rename(columns={"startedAt": "ds", "totalVehicleCount": "y"})
    df["ds"] = df["ds"].dt.tz_convert("America/Guayaquil").dt.tz_localize(None)

    local_holidays = create_holidays_object()
    holidays = create_dataframe_holiday(local_holidays)

    # calcular el periodo a predecir en el futuro
    periods, current_datetime = calculate_periods(df, date, hour, minute)
    # predicciones de la variable totalVehicleCount
    forecast = get_forecast(df, periods, holidays)

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

    return {
        "yhat": yhat,
        "trend": get_percentage(trend, yhat),
        "seasonality": get_percentage(seasonality, yhat),
        "holidays": get_percentage(row["holidays"], yhat),
        "holidays_name": holiday_name,
        "confidenceLevel": 0.80 * 100,
        "variation_forecast_metrics": variation_forecast_metrics,
        "forecast": forecast[["ds", "yhat"]].tail(144).to_dict(orient="records"),
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
    print(location_id, camera_id, date, hour, minute)

    predictions = get_filter_params(location_id, camera_id)

    if predictions is None:
        raise ValueError(
            "No existe ningún análisis para los parámetros proporcionados."
        )

    df = create_dataframe(
        predictions,
        (
            "startedAt",
            "avgSpeed",
        ),
    )

    df_speed = df.rename(columns={"startedAt": "ds", "avgSpeed": "y"})
    df_speed["ds"] = (
        df_speed["ds"].dt.tz_convert("America/Guayaquil").dt.tz_localize(None)
    )

    local_holidays = create_holidays_object()
    holidays = create_dataframe_holiday(local_holidays)

    # calcular el periodo a predecir en el futuro
    periods, current_datetime = calculate_periods(df_speed, date, hour, minute)

    # se obtienen las predicciones de la variable velocidad
    forecast_speed = get_forecast(df_speed, periods, holidays)
    row_speed = get_forecast_by_date(forecast_speed, current_datetime)

    print(
        "Comprobacion de row_speed:", row_speed["yhat"] < 0 or row_speed["yhat"] > 1000
    )

    return {
        "yhat_speed": row_speed["yhat"],
        "forecast_speed": forecast_speed[["ds", "yhat"]]
        .tail(144)
        .to_dict(orient="records"),
        "is_reliable": not (row_speed["yhat"] < 0 or row_speed["yhat"] > 1000),
    }


def get_bottleneck_traffic(params):
    """
    Calcula el Índice de Congestión (IC) y nivel de tráfico
    usando percentiles históricos.
    """
    print("SI EJECUTA MUY BIEN")
    traffic_pred = get_traffic_prediction(params)
    speed_pred = get_speed_prediction(params)

    location_id = int(params.get("locationId"))
    camera_id = int(params.get("cameraId"))

    historical = get_filter_params(location_id, camera_id)
    if not historical:
        raise ValueError("No existen datos históricos para esta cámara o ubicación.")

    df_hist = create_dataframe(historical, ("avgSpeed", "totalVehicleCount"))

    results = []

    for traffic, speed in zip(traffic_pred["forecast"], speed_pred["forecast_speed"]):
        yhat_count = float(traffic["yhat"])
        yhat_speed = float(speed["yhat"])

        level, IC = traffic_level_classification(df_hist, yhat_count, yhat_speed)

        hour_minute = traffic["ds"].strftime("%H:%M")

        results.append(
            {
                "ds": hour_minute,
                "yhat_count": yhat_count,
                "yhat_speed": yhat_speed,
                "IC": IC,
                "level": level,
            }
        )

    print("RESULTADOS CORRECTOS")

    return results


def get_level_prediction(params):
    yhat_count = float(params.get("yhat_count"))
    yhat_speed = float(params.get("yhat_speed"))
    location_id = int(params.get("locationId"))
    camera_id = int(params.get("cameraId"))

    historical = get_filter_params(location_id, camera_id)
    if not historical:
        raise ValueError("No existen datos históricos para esta cámara o ubicación.")

    df_hist = create_dataframe(historical, ("avgSpeed", "totalVehicleCount"))
    level, IC = traffic_level_classification(df_hist, yhat_count, yhat_speed)
    return {
        "IC": IC,
        "level": level,
    }
