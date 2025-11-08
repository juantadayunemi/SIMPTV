"""
Script para actualizar el status y velocidad promedio de los análisis de tráfico
- Convierte status antiguos a nuevos valores con choices (COMPLETED, etc.)
- Recalcula avgSpeed desde la tabla de vehículos cuando sea NULL o 0
- Actualiza densityLevel con valores correctos (LOW, MEDIUM, HIGH, HEAVY)
"""

import os
import sys
import django
from decimal import Decimal

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.db.models import Avg, Q
from apps.traffic_app.models import TrafficAnalysis, Vehicle
from apps.entities.constants import ANALYSIS_STATUS, DENSITY_LEVELS


def update_analysis_status():
    """Actualizar status de análisis a valores estandarizados"""
    print("🔄 Actualizando status de análisis...")

    # Mapeo de valores antiguos a nuevos
    status_mapping = {
        "Completado": ANALYSIS_STATUS.COMPLETED,
        "completado": ANALYSIS_STATUS.COMPLETED,
        "completed": ANALYSIS_STATUS.COMPLETED,
        "COMPLETE": ANALYSIS_STATUS.COMPLETED,
        "Procesando": ANALYSIS_STATUS.PROCESSING,
        "procesando": ANALYSIS_STATUS.PROCESSING,
        "processing": ANALYSIS_STATUS.PROCESSING,
        "Pendiente": ANALYSIS_STATUS.PENDING,
        "pendiente": ANALYSIS_STATUS.PENDING,
        "pending": ANALYSIS_STATUS.PENDING,
        "Fallido": ANALYSIS_STATUS.FAILED,
        "fallido": ANALYSIS_STATUS.FAILED,
        "failed": ANALYSIS_STATUS.FAILED,
        "error": ANALYSIS_STATUS.FAILED,
    }

    updated_count = 0
    for old_status, new_status in status_mapping.items():
        count = TrafficAnalysis.objects.filter(status=old_status).update(
            status=new_status
        )
        if count > 0:
            print(
                f"  ✅ Convertidos {count} análisis de '{old_status}' a '{new_status}'"
            )
            updated_count += count

    # Asegurar que todos los análisis finalizados estén como COMPLETED
    without_ended = TrafficAnalysis.objects.filter(
        endedAt__isnull=False, status__in=["PROCESSING", "PENDING"]
    ).update(status=ANALYSIS_STATUS.COMPLETED)

    if without_ended > 0:
        print(f"  ✅ Marcados {without_ended} análisis finalizados como COMPLETED")
        updated_count += without_ended

    print(f"✅ Total de análisis actualizados: {updated_count}\n")
    return updated_count


def update_density_levels():
    """Actualizar densityLevel a valores estandarizados"""
    print("🔄 Actualizando niveles de densidad...")

    # Mapeo de valores antiguos a nuevos
    density_mapping = {
        "Baja": DENSITY_LEVELS.LOW,
        "baja": DENSITY_LEVELS.LOW,
        "low": DENSITY_LEVELS.LOW,
        "Media": DENSITY_LEVELS.MEDIUM,
        "media": DENSITY_LEVELS.MEDIUM,
        "moderate": DENSITY_LEVELS.MEDIUM,
        "MODERATE": DENSITY_LEVELS.MEDIUM,
        "Alta": DENSITY_LEVELS.HIGH,
        "alta": DENSITY_LEVELS.HIGH,
        "high": DENSITY_LEVELS.HIGH,
        "Crítica": DENSITY_LEVELS.HEAVY,
        "critica": DENSITY_LEVELS.HEAVY,
        "crítica": DENSITY_LEVELS.HEAVY,
        "critical": DENSITY_LEVELS.HEAVY,
        "CRITICAL": DENSITY_LEVELS.HEAVY,
        "heavy": DENSITY_LEVELS.HEAVY,
    }

    updated_count = 0
    for old_density, new_density in density_mapping.items():
        count = TrafficAnalysis.objects.filter(densityLevel=old_density).update(
            densityLevel=new_density
        )
        if count > 0:
            print(
                f"  ✅ Convertidos {count} análisis de '{old_density}' a '{new_density}'"
            )
            updated_count += count

    print(f"✅ Total de densidades actualizadas: {updated_count}\n")
    return updated_count


def recalculate_avg_speed():
    """Recalcular velocidad promedio desde la tabla de vehículos"""
    print("🔄 Recalculando velocidades promedio...")

    # Obtener análisis con velocidad 0 o NULL
    analyses_to_fix = TrafficAnalysis.objects.filter(
        Q(avgSpeed__isnull=True) | Q(avgSpeed=0)
    )

    total_count = analyses_to_fix.count()
    updated_count = 0
    skipped_count = 0

    print(f"  📊 Encontrados {total_count} análisis con velocidad 0 o NULL")

    for analysis in analyses_to_fix:
        # Calcular velocidad promedio desde los vehículos de este análisis
        vehicles_avg = Vehicle.objects.filter(
            trafficAnalysisId=analysis, avgSpeed__isnull=False, avgSpeed__gt=0
        ).aggregate(avg_speed=Avg("avgSpeed"))

        if vehicles_avg["avg_speed"]:
            # Actualizar con la velocidad calculada
            analysis.avgSpeed = Decimal(str(round(vehicles_avg["avg_speed"], 2)))
            analysis.save(update_fields=["avgSpeed"])
            updated_count += 1
            print(
                f"  ✅ Análisis #{analysis.id}: velocidad actualizada a {analysis.avgSpeed} km/h"
            )
        else:
            # No hay vehículos con velocidad, dejar en NULL
            skipped_count += 1
            if skipped_count <= 5:  # Mostrar solo los primeros 5
                print(
                    f"  ⚠️  Análisis #{analysis.id}: sin vehículos con velocidad registrada"
                )

    if skipped_count > 5:
        print(
            f"  ⚠️  ... y {skipped_count - 5} análisis más sin vehículos con velocidad"
        )

    print(f"✅ Velocidades recalculadas: {updated_count}")
    print(f"⚠️  Sin datos de vehículos: {skipped_count}\n")
    return updated_count


def recalculate_all_avg_speed():
    """Recalcular TODAS las velocidades promedio, incluso las que tienen valor"""
    print("🔄 Recalculando TODAS las velocidades promedio...")

    all_analyses = TrafficAnalysis.objects.all()
    total_count = all_analyses.count()
    updated_count = 0

    print(f"  📊 Procesando {total_count} análisis")

    for analysis in all_analyses:
        # Calcular velocidad promedio desde los vehículos
        vehicles_avg = Vehicle.objects.filter(
            trafficAnalysisId=analysis, avgSpeed__isnull=False, avgSpeed__gt=0
        ).aggregate(avg_speed=Avg("avgSpeed"))

        if vehicles_avg["avg_speed"]:
            new_speed = Decimal(str(round(vehicles_avg["avg_speed"], 2)))

            # Solo actualizar si cambió
            if analysis.avgSpeed != new_speed:
                old_speed = analysis.avgSpeed
                analysis.avgSpeed = new_speed
                analysis.save(update_fields=["avgSpeed"])
                updated_count += 1
                print(f"  ✅ Análisis #{analysis.id}: {old_speed} → {new_speed} km/h")

    print(f"✅ Total de velocidades actualizadas: {updated_count}\n")
    return updated_count


def show_statistics():
    """Mostrar estadísticas finales"""
    print("📊 Estadísticas Finales:")
    print("=" * 60)

    # Status
    print("\n🔹 Status de Análisis:")
    for status_value in [
        ANALYSIS_STATUS.COMPLETED,
        ANALYSIS_STATUS.PROCESSING,
        ANALYSIS_STATUS.PENDING,
        ANALYSIS_STATUS.FAILED,
    ]:
        count = TrafficAnalysis.objects.filter(status=status_value).count()
        print(f"  {status_value}: {count}")

    # Density Levels
    print("\n🔹 Niveles de Densidad:")
    for density_value in [
        DENSITY_LEVELS.LOW,
        DENSITY_LEVELS.MEDIUM,
        DENSITY_LEVELS.HIGH,
        DENSITY_LEVELS.HEAVY,
    ]:
        count = TrafficAnalysis.objects.filter(densityLevel=density_value).count()
        print(f"  {density_value}: {count}")

    # Velocidades
    print("\n🔹 Velocidades:")
    with_speed = TrafficAnalysis.objects.filter(
        avgSpeed__isnull=False, avgSpeed__gt=0
    ).count()
    without_speed = TrafficAnalysis.objects.filter(
        Q(avgSpeed__isnull=True) | Q(avgSpeed=0)
    ).count()
    total = TrafficAnalysis.objects.count()

    print(f"  Con velocidad: {with_speed}")
    print(f"  Sin velocidad: {without_speed}")
    print(f"  Total: {total}")

    if with_speed > 0:
        avg_speed_all = TrafficAnalysis.objects.filter(
            avgSpeed__isnull=False, avgSpeed__gt=0
        ).aggregate(avg=Avg("avgSpeed"))
        print(
            f"  Velocidad promedio global: {round(avg_speed_all['avg'] or 0, 2)} km/h"
        )

    print("\n" + "=" * 60)


if __name__ == "__main__":
    print("=" * 60)
    print("🚀 INICIANDO ACTUALIZACIÓN DE ANÁLISIS DE TRÁFICO")
    print("=" * 60)
    print()

    try:
        # 1. Actualizar status
        update_analysis_status()

        # 2. Actualizar density levels
        update_density_levels()

        # 3. Recalcular velocidades (solo las que están en 0 o NULL)
        recalculate_avg_speed()

        # Opción para recalcular TODAS (comentado por defecto)
        # recalculate_all_avg_speed()

        # 4. Mostrar estadísticas
        show_statistics()

        print("\n✅ ¡Actualización completada exitosamente!")

    except Exception as e:
        print(f"\n❌ Error durante la actualización: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
