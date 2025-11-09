from apps.predictions_app.utils.data_preparation import (
    get_filter_params,
    create_dataframe,
    get_model_prediction,
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


def get_model_path(location_id, camera_id, variable):
    return f"{FORECAST_MODELS_PATH}/prophet_{variable}_location_{location_id}_camera_{camera_id}.joblib"


def get_all_predictions(params):
    traffic = get_traffic_prediction(params)
    speed = get_speed_prediction(params)

    print("Traffic Prediction: ", traffic)
    print("Speed Prediction: ", speed)
    level = get_level_prediction(
        {
            "locationId": params.get("locationId"),
            "cameraId": params.get("cameraId"),
            "yhat_count": traffic["yhat"],
            "yhat_speed": speed["yhat_speed"],
        }
    )
    print("Level Prediction: ", level)
    return {
        "traffic": traffic,
        "speed": speed,
        "level": level,
    }


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

    model_path = get_model_path(location_id, camera_id, "speed")
    model = get_model_prediction(model_path, holidays, df_speed)

    # calcular el periodo a predecir en el futuro
    periods, current_datetime = calculate_periods(df_speed, date, hour, minute)

    # se obtienen las predicciones de la variable velocidad
    forecast_speed = get_forecast(model, periods, freq="10T")
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

    return results


def get_level_prediction(params):
    print("Params in level prediction: ", params)
    print(params.get("locationId"))
    print("Ultima prueba")
    print(params.get("cameraId"))
    print("Pasa la prueba")
    location_id = int(params.get("locationId"))
    camera_id = int(params.get("cameraId"))
    print("Pasa la prueba de location y camera")
    yhat_count = float(params.get("yhat_count"))
    yhat_speed = float(params.get("yhat_speed"))

    historical = get_filter_params(location_id, camera_id)
    if not historical:
        raise ValueError("No existen datos históricos para esta cámara o ubicación.")

    df_hist = create_dataframe(historical, ("avgSpeed", "totalVehicleCount"))
    level, IC = traffic_level_classification(df_hist, yhat_count, yhat_speed)
    return {
        "IC": IC,
        "level": level,
    }
