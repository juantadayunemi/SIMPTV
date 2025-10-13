from rest_framework import status
from rest_framework.response import Response
from prophet import Prophet
import pandas as pd
from datetime import datetime
from rest_framework.views import APIView
from apps.traffic_app.models import TrafficAnalysis


# Create your views here.
class PredictionView(APIView):
    """ "
    ViewSet para manejar las predicciones de tráfico vehicular.
    /api/predictions/traffic-predictions/?locationId=<id>&cameraId=<id>&date=<date>&hour=<hour>,
    &minute=<minute>
    """
    def get(self, request):

        print("HOLA DESDE PREDICTIONS VIEW")
        # from traffic_app.models import TrafficAnalysis

        """
        Obtener los registros de la base de datos de análisis de tráfico
        y devolverlos como predicciones.
        """
        try:

            location_id = request.query_params.get("locationId")
            camera_id = request.query_params.get("cameraId")
            date = request.query_params.get("date")
            hour = int(request.query_params.get("hour"))
            minute = int(request.query_params.get("minute", "00"))

            print(
                f"Params: locationId={location_id}, cameraId={camera_id}, date={date}, hour={hour}, minute={minute}"
            )

            predictions = TrafficAnalysis.objects.filter(
                locationId=location_id,
                cameraId=camera_id,
                status="COMPLETED",
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
            df["ds"] = df["ds"].dt.tz_convert("America/Guayaquil").dt.tz_localize(None)

            holidays = pd.DataFrame(
                {
                    "holiday": "national_holiday",
                    "ds": pd.to_datetime(
                        [
                            "2025-01-01",
                            "2023-03-03",
                            "2025-03-04",
                            "2025-04-18",
                            "2025-04-02",
                            "2025-05-23",
                            "2025-08-11",
                            "2025-10-10",
                            "2025-11-03",
                            "2025-11-04",
                            "2025-12-25",
                            "2025-12-31",
                        ]
                    ),
                    "lower_window": 0,
                    "upper_window": 1,
                }
            )

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

            return Response(forecast)

        except Exception as e:
            print(f"Error obteniendo predicciones: {e}")

            return Response(
                {
                    "error": "Ocurrió un error al obtener las predicciones.",
                    "details": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
