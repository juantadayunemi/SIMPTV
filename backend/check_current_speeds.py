"""
Ver velocidades actuales del análisis 243
"""
import os
import sys
import django

sys.path.insert(0, 'D:/TrafiSmart/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.traffic_app.models import Vehicle

# Solo los vehículos más recientes
vehicles = Vehicle.objects.filter(
    trafficAnalysisId_id=243,
    createdAt__gte='2025-10-29 02:54:59'
).order_by('-avgSpeed')[:10]

print("🚗 TOP 10 VELOCIDADES MÁS ALTAS:\n")
print(f"{'ID':<15} {'Tipo':<12} {'Frames':<8} {'Velocidad':<12} {'px/s Estimado'}")
print("=" * 70)

for v in vehicles:
    # Calcular px/s basándonos en la velocidad guardada
    px_per_sec = v.avgSpeed / 0.3 if v.avgSpeed else 0
    print(f"{v.id[:12]:<15} {v.vehicleType:<12} {v.totalFrames:<8} {v.avgSpeed:.1f} km/h    {px_per_sec:.1f}")

print("\n💡 Si estas velocidades están bien (30-60 km/h), el factor 0.3 está correcto")
print("   Si están muy bajas, necesitamos aumentar el factor a 1.0 o 1.5")