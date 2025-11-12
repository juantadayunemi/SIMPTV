"""
Script para corregir el formato de vehicleType en la base de datos
Convierte todos los valores a mayúsculas según VEHICLE_TYPES_CHOICES
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.db import connection


def fix_vehicle_types():
    """Corregir vehicleType en todas las tablas relevantes"""

    tables_to_fix = [
        "traffic_vehicles",
        "traffic_vehicletracks",
        "traffic_predictions",
        "plates_vehiclecomplaintdetections",
    ]

    # Mapeo de valores incorrectos a correctos
    type_mapping = {
        "car": "CAR",
        "truck": "TRUCK",
        "motorcycle": "MOTORCYCLE",
        "bus": "BUS",
        "bicycle": "BICYCLE",
        "other": "OTHER",
    }

    print("=" * 60)
    print("🔧 CORRECCIÓN DE TIPOS DE VEHÍCULOS")
    print("=" * 60)

    with connection.cursor() as cursor:
        for table in tables_to_fix:
            print(f"\n📋 Procesando tabla: {table}")

            # Verificar si la tabla existe
            cursor.execute(
                f"""
                SELECT COUNT(*) 
                FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_NAME = '{table}'
            """
            )

            if cursor.fetchone()[0] == 0:
                print(f"   ⚠️  Tabla {table} no existe, saltando...")
                continue

            # Contar registros antes
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            total_before = cursor.fetchone()[0]
            print(f"   📊 Total de registros: {total_before}")

            if total_before == 0:
                print(f"   ℹ️  Tabla vacía, saltando...")
                continue

            # Actualizar cada tipo
            updated_total = 0
            for old_value, new_value in type_mapping.items():
                cursor.execute(
                    f"""
                    SELECT COUNT(*) 
                    FROM {table} 
                    WHERE vehicleType = '{old_value}'
                """
                )
                count = cursor.fetchone()[0]

                if count > 0:
                    cursor.execute(
                        f"""
                        UPDATE {table} 
                        SET vehicleType = '{new_value}' 
                        WHERE vehicleType = '{old_value}'
                    """
                    )
                    updated_total += count
                    print(
                        f"   ✅ {old_value:12} → {new_value:12} ({count:4} registros)"
                    )

            # Verificar valores finales
            cursor.execute(
                f"""
                SELECT vehicleType, COUNT(*) as count
                FROM {table}
                GROUP BY vehicleType
                ORDER BY vehicleType
            """
            )

            print(f"\n   📊 Distribución final en {table}:")
            for row in cursor.fetchall():
                vehicle_type, count = row
                print(f"      - {vehicle_type}: {count} registros")

            print(f"   ✨ Total actualizado: {updated_total} registros")

    print("\n" + "=" * 60)
    print("✅ CORRECCIÓN COMPLETADA")
    print("=" * 60)


if __name__ == "__main__":
    try:
        fix_vehicle_types()
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback

        traceback.print_exc()
