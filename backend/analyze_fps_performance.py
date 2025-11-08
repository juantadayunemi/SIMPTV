"""
Script para analizar el FPS de procesamiento del sistema
Muestra la capacidad real del sistema para procesar video
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.traffic_app.models import Camera, TrafficAnalysis
from apps.entities.constants import CAMERA_STATUS, ANALYSIS_STATUS


print("=" * 80)
print("🎥 ANÁLISIS DE CAPACIDAD DE PROCESAMIENTO (FPS)")
print("=" * 80)
print()

# Obtener últimos 10 análisis completados
recent_completed = TrafficAnalysis.objects.filter(
    status=ANALYSIS_STATUS.COMPLETED,
    startedAt__isnull=False,
    endedAt__isnull=False,
    totalFrames__gt=0,
).order_by("-endedAt")[:10]

print(f"📊 Análisis completados recientes: {recent_completed.count()}")
print()

if recent_completed.exists():
    fps_list = []

    print("Detalle de análisis:")
    print("-" * 80)
    for i, analysis in enumerate(recent_completed, 1):
        # Calcular duración REAL usando las fechas
        duration_seconds = (analysis.endedAt - analysis.startedAt).total_seconds()

        # Calcular FPS
        fps = analysis.totalFrames / duration_seconds if duration_seconds > 0 else 0
        fps_list.append(fps)

        print(f"{i}. ID: {analysis.id}")
        print(f"   Frames totales: {analysis.totalFrames}")
        print(f"   Iniciado: {analysis.startedAt}")
        print(f"   Finalizado: {analysis.endedAt}")
        print(f"   Duración REAL: {duration_seconds:.2f} segundos")
        print(f"   FPS: {fps:.2f} frames/segundo")
        print()  # Calcular promedio
    avg_fps = sum(fps_list) / len(fps_list)

    print("-" * 80)
    print(f"🎯 FPS PROMEDIO: {avg_fps:.2f} frames/segundo")
    print()

    # Clasificación
    if avg_fps >= 30:
        classification = "🟢 EXCELENTE (30+ FPS)"
        efficiency = 100
    elif avg_fps >= 15:
        classification = "🟡 BUENO (15-30 FPS)"
        efficiency = 50 + ((avg_fps - 15) / 15) * 50
    else:
        classification = "🔴 NECESITA MEJORA (<15 FPS)"
        efficiency = (avg_fps / 15) * 50

    print(f"Clasificación: {classification}")
    print(f"Eficiencia de procesamiento: {efficiency:.1f}%")
    print()

    # Eficiencia total
    active_cameras = Camera.objects.filter(status=CAMERA_STATUS.ACTIVE).count()
    total_cameras = Camera.objects.count()
    camera_efficiency = (
        (active_cameras / max(total_cameras, 1)) * 100 if total_cameras > 0 else 0
    )

    network_efficiency = int(
        (float(camera_efficiency) * 0.4) + (float(efficiency) * 0.6)
    )

    print("=" * 80)
    print("📈 EFICIENCIA TOTAL DEL SISTEMA")
    print("=" * 80)
    print(f"Disponibilidad de cámaras: {camera_efficiency:.1f}% (peso: 40%)")
    print(f"  → {active_cameras}/{total_cameras} cámaras activas")
    print()
    print(f"Capacidad de procesamiento: {efficiency:.1f}% (peso: 60%)")
    print(f"  → FPS promedio: {avg_fps:.2f}")
    print()
    print(f"FÓRMULA:")
    print(f"  Eficiencia = (cámaras * 0.4) + (FPS * 0.6)")
    print(
        f"  Eficiencia = ({camera_efficiency:.1f}% * 0.4) + ({efficiency:.1f}% * 0.6)"
    )
    print(f"  Eficiencia = {camera_efficiency * 0.4:.1f}% + {efficiency * 0.6:.1f}%")
    print(f"  Eficiencia = {network_efficiency}%")
    print()

    if network_efficiency >= 80:
        status_msg = "🟢 EXCELENTE - Sistema funcionando óptimamente"
    elif network_efficiency >= 60:
        status_msg = "🟡 BUENO - Sistema funcionando correctamente"
    elif network_efficiency >= 40:
        status_msg = "🟠 REGULAR - Considerar optimizaciones"
    else:
        status_msg = "🔴 BAJO - Requiere atención inmediata"

    print(f"Estado: {status_msg}")

else:
    print("⚠️ No hay análisis completados con datos de procesamiento")
    print("   Ejecuta algunos análisis de video para obtener métricas")

print()
print("=" * 80)
