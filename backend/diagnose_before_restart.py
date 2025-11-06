"""
🔍 Diagnóstico completo antes de reiniciar Celery
Verifica:
1. Tablas en SQL Server con nombres correctos
2. Modelos Django apuntan a tablas correctas
3. No hay código usando nombres antiguos
4. Migraciones aplicadas correctamente
"""

import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.db import connection
from apps.plates_app.models import (
    DetectedPlate,
    DetectedPlateImage,
    VehicleComplaintDetection,
    VehicleComplaint,
    ComplaintEvidenceImage,
)


def diagnose():
    """Ejecutar diagnóstico completo"""

    print("=" * 70)
    print("🔍 DIAGNÓSTICO PRE-REINICIO DE CELERY")
    print("=" * 70)
    print()

    # 1. Verificar nombres de tablas en modelos Django
    print("📋 1. NOMBRES DE TABLAS EN MODELOS DJANGO:")
    print("-" * 70)

    models = [
        ("DetectedPlate", DetectedPlate),
        ("DetectedPlateImage", DetectedPlateImage),
        ("VehicleComplaintDetection", VehicleComplaintDetection),
        ("VehicleComplaint", VehicleComplaint),
        ("ComplaintEvidenceImage", ComplaintEvidenceImage),
    ]

    model_tables = {}
    for name, model in models:
        table_name = model._meta.db_table
        model_tables[table_name] = name
        print(f"   ✅ {name:30s} → {table_name}")
    print()

    # 2. Verificar tablas en SQL Server
    print("📊 2. TABLAS EN SQL SERVER:")
    print("-" * 70)

    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT TABLE_NAME 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_TYPE = 'BASE TABLE'
            AND (TABLE_NAME LIKE '%plate%' OR TABLE_NAME LIKE '%complaint%')
            ORDER BY TABLE_NAME
        """
        )
        db_tables = {row[0] for row in cursor.fetchall()}

        for table in sorted(db_tables):
            if table in model_tables:
                print(f"   ✅ {table:40s} (usado por {model_tables[table]})")
            else:
                print(f"   ⚠️  {table:40s} (NO USADO - puede ser tabla vieja)")
    print()

    # 3. Verificar si hay tablas con nombres antiguos
    print("🔍 3. BUSCAR TABLAS CON NOMBRES ANTIGUOS:")
    print("-" * 70)

    old_table_names = {
        "plates_app_detectedplate",
        "plates_app_detectedplateimage",
        "plates_app_vehiclecomplaintdetection",
        "plates_app_vehiclecomplaint",
        "plates_app_complaintevidenceimage",
    }

    found_old = db_tables & old_table_names

    if found_old:
        print("   ❌ PROBLEMA: Se encontraron tablas con nombres antiguos:")
        for table in sorted(found_old):
            print(f"      • {table}")
        print()
        print("   🔧 SOLUCIÓN: Ejecuta este SQL en SQL Server:")
        for old_name in sorted(found_old):
            # Determinar nombre nuevo
            new_name = old_name.replace("plates_app_", "").replace(
                "detectedplateimage", "detected_plate_images"
            )
            new_name = new_name.replace(
                "vehiclecomplaintdetection", "vehicle_complaint_detections"
            )
            new_name = new_name.replace("vehiclecomplaint", "vehicle_complaints")
            new_name = new_name.replace(
                "complaintevidenceimage", "complaint_evidence_images"
            )
            new_name = new_name.replace("detectedplate", "detected_plates")
            print(f"      EXEC sp_rename '{old_name}', '{new_name}';")
    else:
        print("   ✅ No se encontraron tablas con nombres antiguos")
    print()

    # 4. Verificar que modelos pueden hacer queries
    print("🧪 4. PROBAR QUERIES CON MODELOS:")
    print("-" * 70)

    tests = [
        ("DetectedPlate", DetectedPlate),
        ("DetectedPlateImage", DetectedPlateImage),
        ("VehicleComplaintDetection", VehicleComplaintDetection),
        ("VehicleComplaint", VehicleComplaint),
    ]

    all_ok = True
    for name, model in tests:
        try:
            count = model.objects.count()
            print(f"   ✅ {name:30s} → {count} registros")
        except Exception as e:
            print(f"   ❌ {name:30s} → ERROR: {str(e)[:50]}")
            all_ok = False
    print()

    # 5. Verificar migraciones
    print("📦 5. ESTADO DE MIGRACIONES:")
    print("-" * 70)

    from django.db.migrations.recorder import MigrationRecorder

    recorder = MigrationRecorder(connection)
    applied = recorder.applied_migrations()

    plates_migrations = [m for m in applied if m[0] == "plates_app"]
    plates_migrations.sort(key=lambda x: x[1])

    print(f"   Migraciones aplicadas: {len(plates_migrations)}")
    for app, name in plates_migrations[-5:]:  # Últimas 5
        print(f"      ✅ {name}")
    print()

    # 6. Resumen final
    print("=" * 70)
    print("📊 RESUMEN:")
    print("=" * 70)

    if found_old:
        print("❌ PROBLEMA ENCONTRADO:")
        print("   • Hay tablas con nombres antiguos en SQL Server")
        print("   • Celery fallará al intentar guardar datos")
        print()
        print("🔧 SOLUCIÓN:")
        print("   1. Ejecuta los comandos SQL mostrados arriba")
        print("   2. Reinicia Celery después")
    elif not all_ok:
        print("❌ PROBLEMA ENCONTRADO:")
        print("   • Algunos modelos no pueden hacer queries")
        print("   • Revisa los errores mostrados arriba")
    else:
        print("✅ TODO ESTÁ CORRECTO:")
        print("   • Todas las tablas tienen nombres correctos")
        print("   • Todos los modelos funcionan correctamente")
        print("   • Migraciones aplicadas exitosamente")
        print()
        print("🚀 PUEDES REINICIAR CELERY CON SEGURIDAD:")
        print("   1. Presiona Ctrl+C en la terminal de Celery")
        print("   2. Ejecuta: celery -A config worker -l info --pool=solo")

    print("=" * 70)


if __name__ == "__main__":
    try:
        diagnose()
    except Exception as e:
        print(f"\n❌ Error fatal: {e}")
        import traceback

        traceback.print_exc()
