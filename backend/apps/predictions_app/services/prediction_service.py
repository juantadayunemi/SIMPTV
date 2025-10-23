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


def get_traffic_prediction(params):
    """
    Servicio que procesa la predicción de tráfico vehicular.
    """
    # Obtener parámetros de consulta
    location_id = int(params.get("locationId"))
    date = params.get("date")
    hour = int(params.get("hour"))
    minute = int(params.get("minute", "00"))
    periods_type = params.get("periodsType", "monthly")

    print(">>> date", periods_type)

    if all([location_id, date, hour, periods_type is None]):
        raise ValueError("Faltan parámetros requeridos (locationId, date, hour).")

    predictions = PredictionSource.objects.filter(
        locationId=location_id,
        isActive=True,
    ).order_by("startedAt")

    if not predictions.exists():
        raise ValueError(
            "No existe ningún análisis para los parámetros proporcionados."
        )

    df = pd.DataFrame(
        list(
            predictions.values(
                "startedAt",
                "totalVehicleCount",
            )
        )
    )
    df = df.rename(columns={"startedAt": "ds", "totalVehicleCount": "y"})
    last_datetime = df["ds"].max()
    df["ds"] = df["ds"].dt.tz_convert("America/Guayaquil").dt.tz_localize(None)

    local_holidays = create_holidays_object()
    holidays = create_dataframe_holiday(local_holidays)
    model = Prophet(holidays=holidays)
    model.fit(df)

    # calcular el periodo a predecir en el futuro
    last_datetime = df["ds"].max()
    current_datetime = convert_datetime(date, hour, minute)
    target_datetime = current_datetime.replace(hour=23, minute=50)
    delta = target_datetime - last_datetime
    periods = int(delta.total_seconds() // 600)

    future = model.make_future_dataframe(periods=periods, freq="10T")
    forecast = model.predict(future)  # se obtienen las predicciones

    row = get_forecast_by_date(forecast, current_datetime)
    yhat = row["yhat"]
    holidays = row["holidays"]
    trend = row["trend"]
    seasonality = get_total_seasonality(row)

    print("yaht:", yhat)
    print("holidays", holidays)
    print("trend", trend)
    print("seasonality", seasonality)

    # obtener forecast del mes anterior
    holiday_name = get_name_holiday(local_holidays, date)
    previous_date = previous_periods(date, periods_type)
    print("?>>>>>previous date: ", previous_date)
    previous_date = convert_datetime(previous_date, hour, minute)
    variation_forecast_metrics = get_previous_forecast(
        forecast,
        previous_date,
        yhat,
        trend,
    )
    print("variation_forecast_metrics:", variation_forecast_metrics)
    return {
        "yhat": yhat,
        "trend": get_percentage(trend, yhat),
        "seasonality": get_percentage(seasonality, yhat),
        "holidays": get_percentage(holidays, yhat),
        "holidays_name": holiday_name,
        "levelTraffic": traffic_level_classification(df["y"], yhat),
        "confidenceLevel": 0.95,
        "variation_forecast_metrics": variation_forecast_metrics,
        "forecast": forecast[["ds", "yhat"]].tail(144).to_dict(orient="records"),
    }
    return {
        "yhat": yhat,
        "trend": trend,
        "seasonality": seasonality,
        "holidays": holidays,
        "holidays_name": holiday_name,
        "levelTraffic": traffic_level_classification(df["y"], yhat),
        "confidenceLevel": 0.95,
        "variation_forecast_metrics": variation_forecast_metrics,
        "forecast": forecast[["ds", "yhat"]].tail(144).to_dict(orient="records"),
    }
