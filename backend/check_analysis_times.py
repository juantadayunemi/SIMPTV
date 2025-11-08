"""
Script para verificar los datos de tiempo de procesamiento
"""

import os
import sys
import django
from datetime import datetime

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.traffic_app.models import TrafficAnalysis
from apps.entities.constants import ANALYSIS_STATUS


print("=" * 80)
print("🔍 VERIFICACIÓN DE DATOS DE PROCESAMIENTO")
print("=" * 80)
print()

# Obtener últimos 10 análisis completados
analyses = TrafficAnalysis.objects.filter(status=ANALYSIS_STATUS.COMPLETED).order_by(
    "-endedAt"
)[:10]

print(f"📊 Análisis completados: {analyses.count()}")
print()

for i, analysis in enumerate(analyses, 1):
    print(f"{i}. ID: {analysis.id}")
    print(f"   totalFrames: {analysis.totalFrames}")
    print(f"   processingDuration: {analysis.processingDuration} segundos")
    print(f"   startedAt: {analysis.startedAt}")
    print(f"   endedAt: {analysis.endedAt}")

    # Calcular duración real si tenemos las fechas
    if analysis.startedAt and analysis.endedAt:
        duration = (analysis.endedAt - analysis.startedAt).total_seconds()
        print(f"   Duración calculada (endedAt - startedAt): {duration} segundos")

        if analysis.totalFrames and duration > 0:
            fps_real = analysis.totalFrames / duration
            print(f"   FPS REAL: {fps_real:.2f} frames/segundo")

    if (
        analysis.totalFrames
        and analysis.processingDuration
        and analysis.processingDuration > 0
    ):
        fps_stored = analysis.totalFrames / analysis.processingDuration
        print(
            f"   FPS ALMACENADO (usando processingDuration): {fps_stored:.2f} frames/segundo"
        )

    print()

print("=" * 80)
print("💡 PREGUNTA:")
print("   ¿Debemos usar processingDuration o calcular (endedAt - startedAt)?")
print("=" * 80)
