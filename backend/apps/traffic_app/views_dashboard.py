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
from apps.entities.constants import CAMERA_STATUS, ANALYSIS_STATUS, DENSITY_LEVELS

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

        # 2. Velocidad promedio - ÚLTIMOS 50 ANÁLISIS
        recent_analyses = TrafficAnalysis.objects.filter(
            status=ANALYSIS_STATUS.COMPLETED,
            avgSpeed__isnull=False,
            avgSpeed__gt=0,  # Excluir velocidades 0
        ).order_by("-endedAt")[
            :50
        ]  # Últimos 50 análisis completados

        if recent_analyses.exists():
            # Calcular promedio simple de los últimos 50 análisis
            avg_speed_data = recent_analyses.aggregate(avg_speed=Avg("avgSpeed"))
            avg_speed = round(float(avg_speed_data["avg_speed"] or 45), 1)
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

        # 4. Eficiencia de la red - BASADO EN FPS DE PROCESAMIENTO
        # La eficiencia mide la capacidad del sistema de procesar video en tiempo real

        # Factores que afectan la eficiencia del sistema:
        # 1. Cámaras activas vs total (40% - disponibilidad del sistema)
        camera_efficiency = (
            (active_cameras / max(total_cameras, 1)) * 100 if total_cameras > 0 else 0
        )

        # 2. Capacidad de procesamiento - FPS (60% - calidad del sistema)
        # Obtener los últimos 10 análisis completados para calcular FPS promedio
        recent_completed = TrafficAnalysis.objects.filter(
            status=ANALYSIS_STATUS.COMPLETED,
            startedAt__isnull=False,  # Necesitamos fecha de inicio
            endedAt__isnull=False,  # Necesitamos fecha de fin
            totalFrames__gt=0,  # Excluir análisis sin frames
        ).order_by("-endedAt")[:10]

        avg_fps = 0
        if recent_completed.exists():
            # Calcular FPS de procesamiento para cada análisis
            fps_list = []
            for analysis in recent_completed:
                # Calcular duración real del análisis (endedAt - startedAt)
                duration_seconds = (
                    analysis.endedAt - analysis.startedAt
                ).total_seconds()

                if duration_seconds > 0:
                    # FPS = totalFrames / duración en segundos
                    fps = analysis.totalFrames / duration_seconds
                    fps_list.append(fps)

            if fps_list:
                # Promedio de FPS
                avg_fps = sum(fps_list) / len(fps_list)

                # Escalar FPS a porcentaje
                # Consideramos:
                # - 30+ FPS = 100% (excelente)
                # - 15-30 FPS = 50-100% (bueno)
                # - <15 FPS = 0-50% (necesita mejora)
                if avg_fps >= 30:
                    processing_efficiency = 100
                elif avg_fps >= 15:
                    processing_efficiency = 50 + ((avg_fps - 15) / 15) * 50
                else:
                    processing_efficiency = (avg_fps / 15) * 50
            else:
                # Si no hay análisis válidos, asumir eficiencia media
                processing_efficiency = 50
        else:
            # Si no hay análisis, asumir eficiencia media
            processing_efficiency = 50

        # Fórmula final: 40% disponibilidad cámaras + 60% capacidad procesamiento
        network_efficiency = int(
            (float(camera_efficiency) * 0.4) + (float(processing_efficiency) * 0.6)
        )
        network_efficiency = max(0, min(100, network_efficiency))  # Entre 0-100

        # 5. Datos de tráfico actual por cámara - USANDO PROCEDIMIENTO ALMACENADO
        current_traffic_data = []

        # Ejecutar procedimiento almacenado
        from django.db import connection

        with connection.cursor() as cursor:
            try:
                cursor.execute("EXEC sp_get_latest_analysis_per_camera")
                columns = [col[0] for col in cursor.description]
                results = [dict(zip(columns, row)) for row in cursor.fetchall()]

                # Mapeo de densityLevel a congestion info
                congestion_map = {
                    DENSITY_LEVELS.LOW: ("low", 20),
                    DENSITY_LEVELS.MEDIUM: ("moderate", 50),
                    DENSITY_LEVELS.HIGH: ("high", 80),
                    DENSITY_LEVELS.HEAVY: ("critical", 95),
                }

                for row in results:
                    density_level = row.get("densityLevel", DENSITY_LEVELS.LOW)
                    congestion_level, congestion_index = congestion_map.get(
                        density_level, ("low", 10)
                    )

                    # Manejar el timestamp correctamente
                    ended_at = row.get("endedAt")
                    timestamp_iso = ended_at.isoformat() if ended_at else None

                    current_traffic_data.append(
                        {
                            "cameraId": row.get("cameraId"),
                            "cameraName": row.get("cameraName", "Desconocida"),
                            "location": f"{row.get('city', 'Ciudad')}, {row.get('locationDescription', '')}",
                            "congestionLevel": congestion_level,
                            "averageSpeed": round(float(row.get("avgSpeed") or 0), 1),
                            "vehicleCount": row.get("totalVehicles", 0),
                            "congestionIndex": congestion_index,
                            "timestamp": timestamp_iso,
                        }
                    )

            except Exception as sp_error:
                logger.warning(
                    f"⚠️ Error ejecutando procedimiento almacenado: {sp_error}"
                )
                # Fallback: usar método anterior si falla el SP
                cameras = Camera.objects.filter(status=CAMERA_STATUS.ACTIVE)
                six_hours_ago = timezone.now() - timedelta(hours=6)

                for camera in cameras:
                    latest_analysis = (
                        TrafficAnalysis.objects.filter(
                            cameraId=camera,
                            startedAt__gte=six_hours_ago,
                            status__in=[
                                ANALYSIS_STATUS.COMPLETED,
                                ANALYSIS_STATUS.PROCESSING,
                            ],
                        )
                        .order_by("-startedAt")
                        .first()
                    )

                    if latest_analysis:
                        congestion_map = {
                            DENSITY_LEVELS.LOW: ("low", 20),
                            DENSITY_LEVELS.MEDIUM: ("moderate", 50),
                            DENSITY_LEVELS.HIGH: ("high", 80),
                            DENSITY_LEVELS.HEAVY: ("critical", 95),
                        }

                        congestion_level, congestion_index = congestion_map.get(
                            latest_analysis.densityLevel, ("low", 10)
                        )

                        avg_speed_camera = latest_analysis.avgSpeed or 50
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
                                "averageSpeed": round(float(avg_speed_camera), 1),
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
                    status__in=[ANALYSIS_STATUS.COMPLETED, ANALYSIS_STATUS.PROCESSING],
                )
                .order_by("-startedAt")
                .first()
            )

            if latest_analysis:
                congestion_map = {
                    DENSITY_LEVELS.LOW: ("low", 20),
                    DENSITY_LEVELS.MEDIUM: ("moderate", 50),
                    DENSITY_LEVELS.HIGH: ("high", 80),
                    DENSITY_LEVELS.HEAVY: ("critical", 95),
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
            startedAt__gte=one_hour_ago,
            densityLevel__in=[DENSITY_LEVELS.HIGH, DENSITY_LEVELS.HEAVY],
        ).select_related("cameraId")

        alerts = []
        for analysis in critical_analyses:
            severity = (
                "critical" if analysis.densityLevel == DENSITY_LEVELS.HEAVY else "high"
            )

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
            startedAt__gte=start_date,
            startedAt__lte=end_date,
            status=ANALYSIS_STATUS.COMPLETED,
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
        for level in [
            DENSITY_LEVELS.LOW,
            DENSITY_LEVELS.MEDIUM,
            DENSITY_LEVELS.HIGH,
            DENSITY_LEVELS.HEAVY,
        ]:
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
