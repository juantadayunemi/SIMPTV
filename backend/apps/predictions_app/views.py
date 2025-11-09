from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.predictions_app.services.prediction_service import (
    get_all_predictions,
    get_bottleneck_traffic,
    get_level_prediction,
    get_speed_prediction,
    get_traffic_prediction,
)
from apps.traffic_app.models import Vehicle
from apps.predictions_app.history_filter import HistoryTrafficFilter


class TrafficPredictionView(APIView):
    """
    Endpoint: /api/predictions/traffic-predictions/?locationId=<id>&cameraId=<id>&date=<date>&hour=<hour>&minute=<minute>
    &periodsType=<periodsType>
    """

    def get(self, request):
        try:
            result = get_all_predictions(request.query_params)

            return Response(result, status=status.HTTP_200_OK)

        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            print(f"Error en PredictionView: {e}")
            return Response(
                {
                    "error": "Ocurrió un error al obtener las predicciones.",
                    "details": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class SpeedPredictionView(APIView):
    """
    Endpoint: /api/predictions/speed-predictions/?locationId=<id>&cameraId=<id>&date=<date>&hour=<hour>&minute=<minute>
    """

    def get(self, request):
        try:
            result = get_speed_prediction(request.query_params)

            return Response(result, status=status.HTTP_200_OK)

        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            print(f"Error en SpeedPredictionView: {e}")
            return Response(
                {
                    "error": "Ocurrió un error al obtener las predicciones de velocidad.",
                    "details": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class HistoryTrafficAPIView(APIView):
    """
    Endpoint: api/predictions/history-traffic/?<congestion|velocity|volume>=<true|false>&locationId=<id>&dateFrom=<dateFrom>&dateTo=<dateTo>
    """

    def get(self, request, *args, **kwargs):
        filterset = HistoryTrafficFilter(
            data=request.GET, queryset=Vehicle.objects.all(), request=request
        )
        _ = filterset.qs
        if hasattr(filterset, "congestion_result"):
            return Response(filterset.congestion_result)
        elif hasattr(filterset, "velocity_result"):
            return Response(filterset.velocity_result)
        elif hasattr(filterset, "volume_result"):
            return Response(filterset.volume_result)

        return Response({"detail": "No filters applied."})


class BottleneckTrafficAPIView(APIView):
    """
    Endpoint: api/predictions/bottleneck-traffic/?locationId=<id>&cameraId=<id>&date=<date>&hour=<hour>&minute=<minute>&periodsType=<periodsType>
    """

    def get(self, request):
        try:
            result = get_bottleneck_traffic(request.query_params)

            return Response(result, status=status.HTTP_200_OK)

        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            print(f"Error en BottleneckTrafficAPIView: {e}")
            return Response(
                {
                    "error": "Ocurrió un error al obtener las predicciones de embotellamiento.",
                    "details": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

class LevelPredictionView(APIView):
    """
    Endpoint: /api/predictions/level-predictions/?locationId=<id>&cameraId=<id>&yhat_count=<yhat_count>&yhat_speed=<yhat_speed>
    """
    def get(self, request):
        try:
            result = get_level_prediction(request.query_params)

            return Response(result, status=status.HTTP_200_OK)

        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            print(f"Error en LevelPredictionView: {e}")
            return Response(
                {
                    "error": "Ocurrió un error al obtener las predicciones de nivel de tráfico.",
                    "details": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )