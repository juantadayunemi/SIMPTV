"""
Script para verificar que las tablas de plates_app existen en SQL Server
con los nombres correctos definidos en models.py
"""

import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.db import connection


def verify_tables():
    """Verifica tablas en SQL Server."""

    expected_tables = {
        "detected_plates",
        "detected_plate_images",
        "vehicle_complaint_detections",
        "vehicle_complaints",
        "complaint_evidence_images",
    }

    with connection.cursor() as cursor:
        print("🔍 Verificando tablas en SQL Server...\n")

        # Obtener todas las tablas
        cursor.execute(
            """
            SELECT TABLE_NAME 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_TYPE = 'BASE TABLE'
            AND TABLE_NAME LIKE '%plate%' OR TABLE_NAME LIKE '%complaint%'
            ORDER BY TABLE_NAME
        """
        )
        existing_tables = {row[0] for row in cursor.fetchall()}

        print("📋 Tablas encontradas:")
        for table in sorted(existing_tables):
            status = "✅" if table in expected_tables else "⚠️"
            print(f"   {status} {table}")

        print(f"\n{'='*60}")

        # Verificar cada tabla esperada
        missing = expected_tables - existing_tables
        found = expected_tables & existing_tables

        print(f"\n✅ Encontradas ({len(found)}/{len(expected_tables)}):")
        for table in sorted(found):
            # Contar registros
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"   • {table}: {count} registros")

        if missing:
            print(f"\n❌ Faltantes ({len(missing)}):")
            for table in sorted(missing):
                print(f"   • {table}")

        # Verificar específicamente detected_plate_images (la que falla)
        print(f"\n{'='*60}")
        print("🔍 Detalles de 'detected_plate_images':\n")

        if "detected_plate_images" in existing_tables:
            # Columnas
            cursor.execute(
                """
                SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_NAME = 'detected_plate_images'
                ORDER BY ORDINAL_POSITION
            """
            )
            columns = cursor.fetchall()
            print(f"📊 Columnas ({len(columns)}):")
            for col_name, data_type, nullable in columns:
                print(
                    f"   • {col_name}: {data_type} ({'NULL' if nullable == 'YES' else 'NOT NULL'})"
                )

            # Registros
            cursor.execute("SELECT COUNT(*) FROM detected_plate_images")
            count = cursor.fetchone()[0]
            print(f"\n📈 Total registros: {count}")

            if count > 0:
                cursor.execute(
                    """
                    SELECT TOP 3 id, detectedPlateId_id, imageType, capturedAt 
                    FROM detected_plate_images 
                    ORDER BY capturedAt DESC
                """
                )
                recent = cursor.fetchall()
                print("\n🕒 Últimos 3 registros:")
                for row in recent:
                    print(
                        f"   • ID={row[0]}, PlateID={row[1]}, Type={row[2]}, Date={row[3]}"
                    )
        else:
            print("❌ Tabla 'detected_plate_images' NO EXISTE")

        print(f"\n{'='*60}\n")

        if missing:
            print("⚠️  ACCIÓN REQUERIDA: Aplicar migraciones pendientes")
            print("   python manage.py migrate plates_app")
        else:
            print("✅ Todas las tablas están correctas!")


if __name__ == "__main__":
    try:
        verify_tables()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()
