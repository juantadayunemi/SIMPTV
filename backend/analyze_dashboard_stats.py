"""
Script para analizar las estadísticas del dashboard
Muestra de dónde salen los valores calculados
"""

import os
import sys
import django
from decimal import Decimal

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.db.models import Avg, Count, Sum
from django.utils import timezone
from datetime import timedelta
from apps.traffic_app.models import Camera, TrafficAnalysis
from apps.plates_app.models import VehicleComplaint
from apps.entities.constants import CAMERA_STATUS, ANALYSIS_STATUS


print("=" * 80)
print("📊 ANÁLISIS DE ESTADÍSTICAS DEL DASHBOARD")
print("=" * 80)
print()

# ============================================
# 1. CÁMARAS ACTIVAS
# ============================================
print("🎥 CÁMARAS ACTIVAS")
print("-" * 80)
active_cameras = Camera.objects.filter(status=CAMERA_STATUS.ACTIVE).count()
total_cameras = Camera.objects.count()
print(f"Cámaras activas: {active_cameras}")
print(f"Cámaras totales: {total_cameras}")
print()

# Mostrar todas las cámaras
print("Lista de cámaras:")
for camera in Camera.objects.all():
    print(f"  - ID: {camera.id}, Nombre: {camera.name}, Status: {camera.status}")
print()

# ============================================
# 2. VELOCIDAD PROMEDIO
# ============================================
print("🚗 VELOCIDAD PROMEDIO")
print("-" * 80)
yesterday = timezone.now() - timedelta(hours=24)

recent_analyses = TrafficAnalysis.objects.filter(
    startedAt__gte=yesterday,
    status=ANALYSIS_STATUS.COMPLETED,
    avgSpeed__isnull=False,
    avgSpeed__gt=0,
)

print(f"Análisis completados (últimas 24 horas): {recent_analyses.count()}")

if recent_analyses.exists():
    speed_stats = recent_analyses.aggregate(
        total_speed=Sum("avgSpeed"),
        count=Count("id"),
        avg_speed=Avg("avgSpeed"),
    )

    print(f"Total speed sum: {speed_stats['total_speed']}")
    print(f"Count: {speed_stats['count']}")
    print(f"Average speed: {round(float(speed_stats['avg_speed'] or 0), 2)} km/h")
    print()
    print("Detalle de análisis recientes:")
    for analysis in recent_analyses[:10]:
        print(
            f"  - ID: {analysis.id}, Velocidad: {analysis.avgSpeed} km/h, "
            f"Vehículos: {analysis.totalVehicles}, Fecha: {analysis.startedAt}"
        )
else:
    print("⚠️ No hay análisis recientes, buscando en todos los análisis...")
    all_analyses = TrafficAnalysis.objects.filter(
        status=ANALYSIS_STATUS.COMPLETED, avgSpeed__isnull=False, avgSpeed__gt=0
    ).order_by("-startedAt")[:10]

    if all_analyses.exists():
        avg_speed_data = all_analyses.aggregate(avg_speed=Avg("avgSpeed"))
        print(
            f"Velocidad promedio (últimos 10): {round(float(avg_speed_data['avg_speed'] or 0), 2)} km/h"
        )
        for analysis in all_analyses:
            print(f"  - ID: {analysis.id}, Velocidad: {analysis.avgSpeed} km/h")
    else:
        print("⚠️ No hay análisis completados con velocidad")

print()

# ============================================
# 3. ALERTAS CRÍTICAS
# ============================================
print("⚠️  ALERTAS CRÍTICAS (DENUNCIAS)")
print("-" * 80)
one_week_ago = timezone.now() - timedelta(days=7)

# Total de denuncias
total_complaints = VehicleComplaint.objects.count()
print(f"Total de denuncias en el sistema: {total_complaints}")

# Denuncias últimos 7 días
recent_complaints = VehicleComplaint.objects.filter(createdAt__gte=one_week_ago)
print(f"Denuncias últimos 7 días: {recent_complaints.count()}")

# Denuncias únicas por detección
unique_detections = (
    VehicleComplaint.objects.filter(createdAt__gte=one_week_ago)
    .values("detectionId")
    .distinct()
    .count()
)
print(f"Detecciones únicas con denuncias (últimos 7 días): {unique_detections}")
print()

if recent_complaints.exists():
    print("Lista de denuncias recientes:")
    for complaint in recent_complaints[:10]:
        print(
            f"  - ID: {complaint.id}, DetectionID: {complaint.detectionId}, "
            f"Fecha: {complaint.createdAt}, Tipo: {complaint.complaintType}"
        )
    if recent_complaints.count() > 10:
        print(f"  ... y {recent_complaints.count() - 10} denuncias más")
else:
    print("⚠️ No hay denuncias en los últimos 7 días")

print()

# ============================================
# 4. EFICIENCIA DE RED
# ============================================
print("📈 EFICIENCIA DE RED")
print("-" * 80)

# Calcular igual que en el código
camera_efficiency = (
    (active_cameras / max(total_cameras, 1)) * 100 if total_cameras > 0 else 0
)

# Obtener velocidad promedio calculada
recent_analyses_for_speed = TrafficAnalysis.objects.filter(
    startedAt__gte=yesterday,
    status=ANALYSIS_STATUS.COMPLETED,
    avgSpeed__isnull=False,
    avgSpeed__gt=0,
)

if recent_analyses_for_speed.exists():
    speed_stats = recent_analyses_for_speed.aggregate(
        total_speed=Sum("avgSpeed"),
        count=Count("id"),
    )
    avg_speed = speed_stats["total_speed"] / speed_stats["count"]
else:
    avg_speed = 45.0

speed_efficiency = min(100, max(0, (float(avg_speed) / 60) * 100))
alert_penalty = min(20, (unique_detections / 10) * 5)

network_efficiency = int(
    (float(camera_efficiency) * 0.5)
    + (float(speed_efficiency) * 0.4)
    - float(alert_penalty)
)
network_efficiency = max(0, min(100, network_efficiency))

print(f"Eficiencia de cámaras: {camera_efficiency:.2f}%")
print(f"  → {active_cameras}/{total_cameras} cámaras activas")
print()
print(f"Eficiencia de velocidad: {speed_efficiency:.2f}%")
print(f"  → Velocidad promedio: {avg_speed:.2f} km/h")
print(f"  → Base: 60 km/h = 100%")
print()
print(f"Penalización por alertas: {alert_penalty:.2f}%")
print(f"  → {unique_detections} detecciones con denuncias")
print(f"  → Cada 10 alertas = -5%")
print()
print(f"FÓRMULA:")
print(f"  Network Efficiency = (camera_eff * 0.5) + (speed_eff * 0.4) - alert_penalty")
print(
    f"  Network Efficiency = ({camera_efficiency:.2f} * 0.5) + ({speed_efficiency:.2f} * 0.4) - {alert_penalty:.2f}"
)
print(
    f"  Network Efficiency = {camera_efficiency * 0.5:.2f} + {speed_efficiency * 0.4:.2f} - {alert_penalty:.2f}"
)
print(f"  Network Efficiency = {network_efficiency}%")

print()
print("=" * 80)
print("✅ ANÁLISIS COMPLETADO")
print("=" * 80)
