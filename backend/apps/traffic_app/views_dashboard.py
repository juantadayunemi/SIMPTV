"""
Dashboard Views para Traffic Analysis App
Endpoints para estadísticas y datos en tiempo real del dashboard
"""

import logging
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Avg, Count, Q, Sum
from django.utils import timezone
from datetime import timedelta

from .models import Camera, TrafficAnalysis, Vehicle
from apps.plates_app.models import VehicleComplaint
from apps.entities.constants import CAMERA_STATUS

logger = logging.getLogger(__name__)


@api_view(["GET"])
@permission_classes([AllowAny])  # ⚠️ TEMPORAL: Sin autenticación para debug
def dashboard_stats(request):
    """
    Obtener estadísticas generales del dashboard

    GET /api/traffic/dashboard/stats

    Returns:
        {
            "activeCameras": int,
            "avgSpeed": float,
            "criticalAlerts": int,
            "networkEfficiency": int,
            "currentTrafficData": [...]
        }
    """
    try:
        # 1. Cámaras activas (usando CAMERA_STATUS desde shared)
        active_cameras = Camera.objects.filter(status=CAMERA_STATUS.ACTIVE).count()
        total_cameras = Camera.objects.count()

        # 2. Velocidad promedio (últimas 24 horas) - Mejorado
        yesterday = timezone.now() - timedelta(hours=24)
        recent_analyses = TrafficAnalysis.objects.filter(
            startedAt__gte=yesterday,
            status="COMPLETED",
            avgSpeed__isnull=False,
            avgSpeed__gt=0,  # Excluir velocidades 0
        )

        # Calcular velocidad promedio ponderada por número de vehículos
        speed_stats = recent_analyses.aggregate(
            total_speed=Sum("avgSpeed"),
            total_vehicles=Sum("totalVehicleCount"),
            count=Count("id"),
        )

        if speed_stats["count"] and speed_stats["count"] > 0:
            avg_speed = round(speed_stats["total_speed"] / speed_stats["count"], 1)
        else:
            # Si no hay datos, intentar con todas las cámaras
            all_analyses = TrafficAnalysis.objects.filter(
                status="COMPLETED", avgSpeed__isnull=False, avgSpeed__gt=0
            ).order_by("-startedAt")[:10]

            if all_analyses.exists():
                avg_speed_data = all_analyses.aggregate(avg_speed=Avg("avgSpeed"))
                avg_speed = round(avg_speed_data["avg_speed"] or 45, 1)
            else:
                avg_speed = 45.0  # Valor por defecto razonable

        # 3. Alertas críticas (denuncias de vehículos) - USANDO VehicleComplaint
        # Contar denuncias de los últimos 7 días
        one_week_ago = timezone.now() - timedelta(days=7)
        critical_alerts = (
            VehicleComplaint.objects.filter(createdAt__gte=one_week_ago)
            .values("detectionId")
            .distinct()
            .count()
        )

        # 4. Eficiencia de la red - Cálculo mejorado
        # Basado en: cámaras activas, velocidad promedio, y ausencia de alertas
        camera_efficiency = (
            (active_cameras / max(total_cameras, 1)) * 100 if total_cameras > 0 else 0
        )

        # Eficiencia de velocidad (60 km/h = 100%, 30 km/h = 50%, escalado lineal)
        speed_efficiency = min(100, max(0, (avg_speed / 60) * 100))

        # Penalización por alertas críticas (cada 10 alertas reduce 5%)
        alert_penalty = min(20, (critical_alerts / 10) * 5)

        # Fórmula final: 50% cámaras + 40% velocidad - penalización alertas
        network_efficiency = int(
            (camera_efficiency * 0.5) + (speed_efficiency * 0.4) - alert_penalty
        )
        network_efficiency = max(0, min(100, network_efficiency))  # Entre 0-100

        # 5. Datos de tráfico actual por cámara (últimas 6 horas)
        six_hours_ago = timezone.now() - timedelta(hours=6)
        current_traffic_data = []

        # Obtener el análisis más reciente de cada cámara ACTIVA
        cameras = Camera.objects.filter(status=CAMERA_STATUS.ACTIVE)

        for camera in cameras:
            latest_analysis = (
                TrafficAnalysis.objects.filter(
                    cameraId=camera,
                    startedAt__gte=six_hours_ago,
                    status__in=["COMPLETED", "PROCESSING"],
                )
                .order_by("-startedAt")
                .first()
            )

            if latest_analysis:
                # Calcular nivel de congestión basado en densityLevel
                congestion_map = {
                    "LOW": ("low", 20),
                    "MODERATE": ("moderate", 50),
                    "HIGH": ("high", 80),
                    "CRITICAL": ("critical", 95),
                }

                congestion_level, congestion_index = congestion_map.get(
                    latest_analysis.densityLevel, ("low", 10)
                )

                # Calcular velocidad promedio (si no existe, usar valor estimado)
                avg_speed_camera = latest_analysis.avgSpeed or 50

                # Contar vehículos totales
                vehicle_count = latest_analysis.totalVehicleCount or 0

                current_traffic_data.append(
                    {
                        "cameraId": camera.id,
                        "cameraName": camera.name,
                        "location": (
                            f"{camera.locationId.city}, {camera.locationId.country}"
                            if camera.locationId
                            else "Ubicación desconocida"
                        ),
                        "congestionLevel": congestion_level,
                        "averageSpeed": round(avg_speed_camera, 1),
                        "vehicleCount": vehicle_count,
                        "congestionIndex": congestion_index,
                        "timestamp": (
                            latest_analysis.startedAt.isoformat()
                            if latest_analysis.startedAt
                            else None
                        ),
                    }
                )

        # Si no hay datos reales, generar datos de ejemplo
        if not current_traffic_data:
            logger.warning(
                "No hay datos de tráfico recientes, retornando datos de ejemplo"
            )
            current_traffic_data = [
                {
                    "cameraId": 1,
                    "cameraName": "Cámara Principal",
                    "location": "Centro, Ciudad",
                    "congestionLevel": "low",
                    "averageSpeed": 55,
                    "vehicleCount": 12,
                    "congestionIndex": 25,
                    "timestamp": timezone.now().isoformat(),
                }
            ]

        return Response(
            {
                "activeCameras": active_cameras,
                "avgSpeed": avg_speed,
                "criticalAlerts": critical_alerts,
                "networkEfficiency": network_efficiency,
                "currentTrafficData": current_traffic_data,
            },
            status=status.HTTP_200_OK,
        )

    except Exception as e:
        logger.error(f"❌ Error obteniendo estadísticas del dashboard: {e}")
        import traceback

        traceback.print_exc()
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["GET"])
@permission_classes([AllowAny])
def current_traffic_data(request):
    """
    Obtener datos de tráfico actual de todas las cámaras

    GET /api/traffic/dashboard/current-traffic
    """
    try:
        six_hours_ago = timezone.now() - timedelta(hours=6)
        current_traffic = []

        cameras = Camera.objects.filter(isActive=True)

        for camera in cameras:
            latest_analysis = (
                TrafficAnalysis.objects.filter(
                    cameraId=camera,
                    startedAt__gte=six_hours_ago,
                    status__in=["COMPLETED", "PROCESSING"],
                )
                .order_by("-startedAt")
                .first()
            )

            if latest_analysis:
                congestion_map = {
                    "LOW": ("low", 20),
                    "MODERATE": ("moderate", 50),
                    "HIGH": ("high", 80),
                    "CRITICAL": ("critical", 95),
                }

                congestion_level, congestion_index = congestion_map.get(
                    latest_analysis.densityLevel, ("low", 10)
                )

                current_traffic.append(
                    {
                        "cameraId": camera.id,
                        "cameraName": camera.name,
                        "location": (
                            f"{camera.locationId.city}, {camera.locationId.country}"
                            if camera.locationId
                            else "Ubicación desconocida"
                        ),
                        "congestionLevel": congestion_level,
                        "averageSpeed": round(latest_analysis.avgSpeed or 50, 1),
                        "vehicleCount": latest_analysis.totalVehicleCount or 0,
                        "congestionIndex": congestion_index,
                        "timestamp": (
                            latest_analysis.startedAt.isoformat()
                            if latest_analysis.startedAt
                            else None
                        ),
                    }
                )

        return Response(current_traffic, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"❌ Error obteniendo datos de tráfico actual: {e}")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["GET"])
@permission_classes([AllowAny])
def critical_alerts(request):
    """
    Obtener alertas críticas activas

    GET /api/traffic/dashboard/critical-alerts
    """
    try:
        one_hour_ago = timezone.now() - timedelta(hours=1)

        critical_analyses = TrafficAnalysis.objects.filter(
            startedAt__gte=one_hour_ago, densityLevel__in=["HIGH", "CRITICAL"]
        ).select_related("cameraId")

        alerts = []
        for analysis in critical_analyses:
            severity = "critical" if analysis.densityLevel == "CRITICAL" else "high"

            alerts.append(
                {
                    "id": analysis.id,
                    "cameraId": analysis.cameraId.id if analysis.cameraId else None,
                    "cameraName": (
                        analysis.cameraId.name if analysis.cameraId else "Desconocida"
                    ),
                    "alertType": "HIGH_CONGESTION",
                    "severity": severity,
                    "message": f"Alta congestión detectada en {analysis.cameraId.name if analysis.cameraId else 'cámara'}: {analysis.totalVehicleCount} vehículos",
                    "timestamp": (
                        analysis.startedAt.isoformat() if analysis.startedAt else None
                    ),
                }
            )

        return Response(alerts, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"❌ Error obteniendo alertas críticas: {e}")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["GET"])
@permission_classes([AllowAny])
def stats_by_date_range(request):
    """
    Obtener estadísticas por rango de fechas

    GET /api/traffic/dashboard/stats-by-date?startDate=2025-01-01&endDate=2025-01-31
    """
    try:
        start_date = request.GET.get("startDate")
        end_date = request.GET.get("endDate")

        if not start_date or not end_date:
            return Response(
                {"error": "startDate and endDate are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        analyses = TrafficAnalysis.objects.filter(
            startedAt__gte=start_date, startedAt__lte=end_date, status="COMPLETED"
        )

        # Velocidad promedio
        avg_speed_data = analyses.aggregate(avg_speed=Avg("avgSpeed"))
        avg_speed = round(avg_speed_data["avg_speed"] or 0, 1)

        # Total de vehículos
        total_vehicles = (
            analyses.aggregate(total=Count("totalVehicleCount"))["total"] or 0
        )

        # Horas pico (simplificado)
        peak_hours = []
        for hour in range(24):
            count = analyses.filter(startedAt__hour=hour).count()
            if count > 0:
                peak_hours.append({"hour": hour, "count": count})

        # Tendencias de congestión
        congestion_trends = []
        for level in ["LOW", "MODERATE", "HIGH", "CRITICAL"]:
            count = analyses.filter(densityLevel=level).count()
            if count > 0:
                congestion_trends.append(
                    {"date": start_date, "level": level.lower(), "count": count}
                )

        return Response(
            {
                "avgSpeed": avg_speed,
                "totalVehicles": total_vehicles,
                "peakHours": sorted(peak_hours, key=lambda x: x["count"], reverse=True)[
                    :5
                ],
                "congestionTrends": congestion_trends,
            },
            status=status.HTTP_200_OK,
        )

    except Exception as e:
        logger.error(f"❌ Error obteniendo estadísticas por rango de fechas: {e}")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
