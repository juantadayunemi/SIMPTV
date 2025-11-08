"""
Script para eliminar análisis de tráfico con datos inválidos
Elimina análisis con menos de 10 vehículos (datos de prueba no realistas)
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.db import transaction
from apps.traffic_app.models import TrafficAnalysis, Vehicle, VehicleFrame, Camera


def delete_invalid_analyses(min_vehicles=10):
    """
    Eliminar análisis con menos de X vehículos

    Args:
        min_vehicles: Número mínimo de vehículos para considerar válido el análisis
    """
    print("=" * 60)
    print(f"🗑️  ELIMINANDO ANÁLISIS CON MENOS DE {min_vehicles} VEHÍCULOS")
    print("=" * 60)
    print()

    # Obtener análisis a eliminar
    invalid_analyses = TrafficAnalysis.objects.filter(totalVehicles__lt=min_vehicles)
    total_to_delete = invalid_analyses.count()

    if total_to_delete == 0:
        print("✅ No hay análisis inválidos para eliminar")
        return

    print(f"📊 Análisis a eliminar: {total_to_delete}")

    # Mostrar detalles
    for analysis in invalid_analyses[:10]:  # Mostrar primeros 10
        print(
            f"  - ID: {analysis.id}, Vehículos: {analysis.totalVehicles}, "
            f"Cámara: {analysis.cameraId.name if analysis.cameraId else 'N/A'}, "
            f"Fecha: {analysis.endedAt or 'N/A'}"
        )

    if total_to_delete > 10:
        print(f"  ... y {total_to_delete - 10} análisis más")

    print()

    # Confirmar con el usuario
    confirm = input(
        f"⚠️  ¿Estás seguro de eliminar {total_to_delete} análisis? (sí/no): "
    )

    if confirm.lower() not in ["sí", "si", "s", "yes", "y"]:
        print("❌ Operación cancelada")
        return

    print()
    print("🔄 Iniciando eliminación...")

    try:
        with transaction.atomic():
            # 1. Actualizar cámaras que referencien estos análisis
            cameras_updated = Camera.objects.filter(
                currentAnalysisId__in=invalid_analyses
            ).update(currentAnalysisId=None)

            if cameras_updated > 0:
                print(
                    f"  ✅ Actualizadas {cameras_updated} cámaras (currentAnalysisId=NULL)"
                )

            # 2. Eliminar frames de vehículos
            vehicles_to_delete = Vehicle.objects.filter(
                trafficAnalysisId__in=invalid_analyses
            )
            frames_count = VehicleFrame.objects.filter(
                vehicleId__in=vehicles_to_delete
            ).count()

            if frames_count > 0:
                VehicleFrame.objects.filter(vehicleId__in=vehicles_to_delete).delete()
                print(f"  ✅ Eliminados {frames_count} frames de vehículos")

            # 3. Eliminar vehículos
            vehicles_count = vehicles_to_delete.count()
            if vehicles_count > 0:
                vehicles_to_delete.delete()
                print(f"  ✅ Eliminados {vehicles_count} vehículos")

            # 4. Eliminar análisis
            deleted_count, _ = invalid_analyses.delete()
            print(f"  ✅ Eliminados {deleted_count} análisis")

        print()
        print("✅ ¡Eliminación completada exitosamente!")

    except Exception as e:
        print(f"\n❌ Error durante la eliminación: {e}")
        import traceback

        traceback.print_exc()
        return

    # Mostrar estadísticas finales
    print()
    print("📊 Estadísticas Finales:")
    print("=" * 60)

    remaining = TrafficAnalysis.objects.count()
    print(f"Total de análisis restantes: {remaining}")

    if remaining > 0:
        stats = TrafficAnalysis.objects.aggregate(
            min_vehicles=models.Min("totalVehicles"),
            max_vehicles=models.Max("totalVehicles"),
            avg_vehicles=models.Avg("totalVehicles"),
        )
        print(f"Vehículos mínimos: {stats['min_vehicles']}")
        print(f"Vehículos máximos: {stats['max_vehicles']}")
        print(f"Vehículos promedio: {round(stats['avg_vehicles'] or 0, 2)}")

    print()
    print("🔍 Últimos 5 análisis:")
    for analysis in TrafficAnalysis.objects.order_by("-endedAt")[:5]:
        print(
            f"  - ID: {analysis.id}, Vehículos: {analysis.totalVehicles}, "
            f"Densidad: {analysis.densityLevel}, "
            f"Fecha: {analysis.endedAt or 'N/A'}"
        )

    print("=" * 60)


if __name__ == "__main__":
    from django.db import models

    try:
        # Eliminar análisis con menos de 10 vehículos
        delete_invalid_analyses(min_vehicles=10)

    except KeyboardInterrupt:
        print("\n\n⚠️  Operación cancelada por el usuario")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
