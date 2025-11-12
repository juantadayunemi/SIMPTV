"""
Script para forzar la eliminación de usuarios no verificados
Ejecutar: python force_cleanup.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.auth_app.models import User
from django.utils import timezone
from datetime import timedelta

# Configuración
MINUTES_THRESHOLD = 4

# Calculate cutoff time
cutoff_time = timezone.now() - timedelta(minutes=MINUTES_THRESHOLD)

# Find unverified users older than cutoff time
unverified_users = User.objects.filter(
    emailConfirmed=False,
    createdAt__lt=cutoff_time
)

count = unverified_users.count()

if count == 0:
    print("✓ No hay usuarios no verificados para eliminar.")
else:
    print(f"\n📋 Usuarios no verificados encontrados: {count}")
    print(f"   Cutoff time: {cutoff_time}")
    print(f"   (Usuarios creados antes de hace {MINUTES_THRESHOLD} minutos)\n")
    
    for user in unverified_users:
        minutes_elapsed = int((timezone.now() - user.createdAt).total_seconds() / 60)
        print(f"  - {user.email}")
        print(f"    Creado: {user.createdAt}")
        print(f"    Hace: {minutes_elapsed} minutos")
        print(f"    emailConfirmed: {user.emailConfirmed}")
        print()
    
    # Confirmar
    response = input(f"¿Eliminar estos {count} usuarios? (sí/no): ").strip().lower()
    
    if response in ['sí', 'si', 's', 'yes', 'y']:
        deleted_count, deleted_details = unverified_users.delete()
        print(f"\n✅ Eliminados {deleted_count} usuarios no verificados.")
        print(f"   Detalles: {deleted_details}")
    else:
        print("\n⚠️  Operación cancelada. No se eliminó ningún usuario.")
