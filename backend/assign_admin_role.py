"""
Script para asignar rol de ADMIN a usuarios existentes
Uso: python assign_admin_role.py
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.contrib.auth import get_user_model
from apps.auth_app.models import UserRole

User = get_user_model()


def main():
    print("\n" + "=" * 60)
    print("🔧 ASIGNAR ROL DE ADMINISTRADOR")
    print("=" * 60 + "\n")

    # 1️⃣ Listar usuarios disponibles
    users = User.objects.filter(isActive=True).order_by("id")

    if not users.exists():
        print("❌ No hay usuarios activos en el sistema.")
        return

    print(f"📋 Usuarios disponibles ({users.count()}):\n")
    for user in users:
        # Verificar si ya tiene rol ADMIN
        has_admin = UserRole.objects.filter(user=user, role="ADMIN").exists()
        status = "✅ YA ES ADMIN" if has_admin else ""

        full_name = f"{user.firstName or ''} {user.lastName or ''}".strip()
        display_name = full_name if full_name else user.email

        print(f"   [{user.id}] {display_name}")
        print(f"       Email: {user.email}")
        if status:
            print(f"       {status}")
        print()

    # 2️⃣ Solicitar ID del usuario
    print("=" * 60)
    try:
        user_input = input(
            "\n👤 Ingrese el ID del usuario para hacer ADMIN (o 'q' para salir): "
        ).strip()

        if user_input.lower() == "q":
            print("\n👋 Operación cancelada.\n")
            return

        user_id = int(user_input)
        selected_user = User.objects.get(id=user_id, isActive=True)

    except ValueError:
        print("\n❌ Error: Debe ingresar un número válido.\n")
        return
    except User.DoesNotExist:
        print(f"\n❌ Error: Usuario con ID {user_id} no encontrado o no está activo.\n")
        return

    # 3️⃣ Verificar si ya es admin
    existing_role = UserRole.objects.filter(user=selected_user, role="ADMIN").first()

    if existing_role:
        print(f"\n⚠️  El usuario ya tiene rol de ADMIN asignado.")
        print(f"    Usuario: {selected_user.email}")
        print(f"    Rol creado: {existing_role.created_at}")
        print()
        return

    # 4️⃣ Confirmar asignación
    full_name = (
        f"{selected_user.firstName or ''} {selected_user.lastName or ''}".strip()
    )
    display_name = full_name if full_name else selected_user.email

    print("\n" + "=" * 60)
    print("📝 CONFIRMAR ASIGNACIÓN:")
    print(f"   Usuario: {display_name}")
    print(f"   Email: {selected_user.email}")
    print(f"   Rol: ADMIN")
    print("=" * 60)

    confirm = input("\n¿Confirmar asignación? (s/n): ").strip().lower()

    if confirm != "s":
        print("\n👋 Operación cancelada.\n")
        return

    # 5️⃣ Crear rol de ADMIN
    try:
        user_role = UserRole.objects.create(user=selected_user, role="ADMIN")

        print("\n" + "=" * 60)
        print("✅ ROL DE ADMINISTRADOR ASIGNADO EXITOSAMENTE")
        print("=" * 60)
        print(f"   Usuario: {display_name}")
        print(f"   Email: {selected_user.email}")
        print(f"   Rol: {user_role.role}")
        print(f"   Fecha: {user_role.created_at}")
        print("=" * 60 + "\n")

        # 6️⃣ Mostrar resumen de admins
        total_admins = UserRole.objects.filter(role="ADMIN").count()
        print(f"📊 Total de administradores en el sistema: {total_admins}\n")

    except Exception as e:
        print(f"\n❌ Error al crear rol: {e}\n")
        return


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Operación cancelada por el usuario.\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}\n")
        sys.exit(1)
