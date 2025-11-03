#!/usr/bin/env python
"""
Script para limpiar las tablas de django.contrib.auth que no se necesitan
"""
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.db import connection

# Lista de tablas de Django a eliminar
TABLES_TO_DROP = [
    "auth_user",
    "auth_group",
    "auth_permission",
    "auth_user_groups",
    "auth_user_user_permissions",
    "auth_group_permissions",
    "django_admin_log",  # Depende de auth_user
]

print("=" * 70)
print("SCRIPT DE LIMPIEZA: Eliminar tablas de django.contrib.auth")
print("=" * 70)

with connection.cursor() as cursor:
    # Obtener tablas que existen
    cursor.execute("SELECT name FROM sys.tables WHERE type='U' ORDER BY name")
    existing_tables = [row[0] for row in cursor.fetchall()]

    for table in TABLES_TO_DROP:
        if table in existing_tables:
            print(f"\n⚠️  Eliminando tabla: {table}")
            try:
                # Eliminar foreign keys primero
                cursor.execute(
                    f"""
                    SELECT CONSTRAINT_NAME 
                    FROM INFORMATION_SCHEMA.REFERENTIAL_CONSTRAINTS 
                    WHERE CONSTRAINT_TABLE_NAME = '{table}'
                """
                )
                fks = cursor.fetchall()
                for fk in fks:
                    print(f"  - Eliminando FK: {fk[0]}")
                    cursor.execute(f"ALTER TABLE {table} DROP CONSTRAINT {fk[0]}")

                # Eliminar la tabla
                cursor.execute(f"DROP TABLE {table}")
                print(f"  ✓ Tabla {table} eliminada exitosamente")
            except Exception as e:
                print(f"  ✗ Error eliminando {table}: {str(e)}")
        else:
            print(f"\n✓ La tabla {table} no existe (no necesita limpieza)")

print("\n" + "=" * 70)
print("LIMPIEZA COMPLETADA")
print("=" * 70)
