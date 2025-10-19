from rest_framework import status
from rest_framework.response import Response
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
)
from prophet import Prophet
import pandas as pd
from datetime import datetime
from rest_framework.views import APIView
import holidays as pyholidays


# Create your views here.
class PredictionView(APIView):
    """
    ViewSet para manejar las predicciones de tráfico vehicular.
    Endpoint: /api/predictions/traffic-predictions/?locationId=<id>&date=<date>&hour=<hour>,
    &minute=<minute>
    """

    def get(self, request):
        """
        Obtener los registros de la base de datos de análisis de tráfico
        y devolverlos como predicciones.
        """
        try:
            # Obtener parámetros de consulta
            location_id = request.query_params.get("locationId")
            date = request.query_params.get("date")
            hour = int(request.query_params.get("hour"))
            minute = int(request.query_params.get("minute", "00"))

            print(
                f"Params: locationId={location_id}, date={date}, hour={hour}, minute={minute}"
            )

            predictions = PredictionSource.objects.filter(
                locationId=location_id,
                isActive=True,
            ).order_by("startedAt")

            if not predictions.exists():
                return Response(
                    {
                        "error": "No existe ningún análisis para los parámetros proporcionados."
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )

            # Convertir a DataFrame para manipulación
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
            print(f"Last datetime in data: {last_datetime}")
            target_datetime = datetime.strptime(
                f"{date} {hour}:{minute}:00", "%Y-%m-%d %H:%M:%S"
            )

            delta = target_datetime - last_datetime

            print(f"Delta: {delta}, total seconds: {delta.total_seconds()}")

            periods = int(delta.total_seconds() // 600) + 1

            print(f"Periods to predict: {periods}")

            future = model.make_future_dataframe(periods=periods, freq="10T")
            forecast = model.predict(future)  # se obtienen las predicciones

            row = get_forecast_by_date(forecast, target_datetime)
            yhat = row["yhat"]
            holidays = row["holidays"]
            trend = row["trend"]
            seasonality = get_total_seasonality(row)

            print(f"yhat: {yhat}")
            print(f"holidays: {holidays}")
            print(f"Trend: {trend}")
            print(f"Seasonality: {seasonality}")

            print(f"holidays: {get_percentage(holidays,yhat)}%")
            print(f"Trend: {get_percentage(trend,yhat)}%")
            print(f"Seasonality: {get_percentage(seasonality,yhat)}%")

            holiday_name = get_name_holiday(local_holidays, date)

            # obtener forecast del mes anterior
            previous_date = add_to_date(date, 0, -1)
            variation_forecast_metrics = get_previous_forecast(
                forecast,
                convert_datetime(previous_date, hour, minute),
                yhat,
                trend,
            )

            # return Response(forecast)

            return Response(
                {
                    "yhat": yhat,
                    "trend": get_percentage(trend, yhat),
                    "seasonality": get_percentage(seasonality, yhat),
                    "holidays": get_percentage(holidays, yhat),
                    "levelTraffic": traffic_level_classification(df["y"], yhat),
                    "confidenceLevel": 0.95,
                    "variation_forecast_metrics": variation_forecast_metrics,
                    "forecast": forecast,
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            print(f"Error obteniendo predicciones: {e}")

            return Response(
                {
                    "error": "Ocurrió un error al obtener las predicciones.",
                    "details": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
