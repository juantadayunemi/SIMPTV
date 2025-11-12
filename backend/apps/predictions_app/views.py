from datetime import date
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from apps.predictions_app.services.prediction_service import (
    get_all_predictions,
    get_bottleneck_traffic,
    get_forecast_change_percent,
    get_level_prediction,
    get_speed_prediction,
    get_traffic_prediction,
)
from apps.traffic_app.models import Camera, Location, Vehicle
from apps.predictions_app.history_filter import HistoryTrafficFilter
from apps.predictions_app.serializers import NotificationBottleNeckSerializer
from apps.notifications_app.models import NotificationBottleNeck, NotificationTask
from rest_framework.decorators import action

from apps.auth_app.models import User
from .tasks import (
    schedule_bottleneck_notifications,
)
from django.db import transaction
from config.celery import app


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
        if "velocity" in request.GET:
            fields = ["id", "firstDetectedAt", "avgSpeed", "trafficAnalysisId"]
        elif "congestion" in request.GET:
            fields = ["id", "firstDetectedAt", "avgSpeed", "trafficAnalysisId"]
        elif "volume" in request.GET:
            fields = ["id", "firstDetectedAt", "trafficAnalysisId"]
        else:
            # Si no se especifica filtro, devolver vacío o todos si prefieres
            fields = ["id", "firstDetectedAt", "avgSpeed", "trafficAnalysisId"]

        queryset = Vehicle.objects.only(*fields).select_related("trafficAnalysisId")

        filterset = HistoryTrafficFilter(
            data=request.GET, queryset=queryset, request=request
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


class ForecastChangePercentView(APIView):
    """
    Endpoint: /api/predictions/forecast-change-percent/?locationId=<id>&cameraId=<id>&date=<date>&hour=<hour>&minute=<minute>&periodsType=<periodsType>
    """

    def get(self, request):
        try:
            params = request.query_params
            result = get_forecast_change_percent(params)

            return Response(
                result,
                status=status.HTTP_200_OK,
            )

        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            print(f"Error en ForecastChangePercent: {e}")
            return Response(
                {
                    "error": "Ocurrió un error al calcular el porcentaje de cambio del pronóstico.",
                    "details": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class NotificationBlottleneckViewSet(viewsets.ModelViewSet):
    """
    api/predictions/togle-notifications-bottleneck/
    """

    queryset = NotificationBottleNeck.objects.all()
    serializer_class = NotificationBottleNeckSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user_email = self.request.user
        user = User.objects.get(email=user_email)
        location_id = self.request.query_params.get("locationId")
        camera_id = self.request.query_params.get("cameraId")
        queryset = NotificationBottleNeck.objects.filter(
            userId=user,
            locationId=location_id,
            cameraId=camera_id,
        )
        print("Queryset de notificaciones:", queryset)
        return queryset

    @action(detail=False, methods=["post"], url_path="toggle")
    def toggle_notification(self, request, *args, **kwargs):
        user_email = request.user
        location_id = request.data.get("locationId")
        camera_id = request.data.get("cameraId")

        user = User.objects.get(email=user_email)
        location = get_object_or_404(Location, pk=location_id)
        camera = get_object_or_404(Camera, pk=camera_id)

        if not user or not user.is_authenticated:
            return Response(
                {"detail": "Usuario no autenticado."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        try:
            with transaction.atomic():
                notification, created = NotificationBottleNeck.objects.get_or_create(
                    userId=user,
                    locationId=location,
                    cameraId=camera,
                    defaults={"isActive": True},
                )

                if not created:
                    notification.isActive = not notification.isActive
                    notification.save()

                if not notification.isActive:
                    print("Entra a desactivar notificaciones")
                    scheduled_tasks = NotificationTask.objects.filter(
                        notificationBottleNeckId=notification
                    )
                    for task in scheduled_tasks:
                        app.control.revoke(task.taskId, terminate=True)
                        scheduled_tasks.update(isActive=False)

                if notification.isActive:
                    schedule_bottleneck_notifications(
                        user.id, location_id, camera_id, date.today()
                    )

            

            serializer = self.get_serializer(notification)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except IntegrityError as e:
            return Response(
                {"detail": f"Error de integridad: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        except Exception as e:

            return Response(
                {"detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
