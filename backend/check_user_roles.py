"""
Script para verificar roles de usuario y tokens
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.auth_app.models import User, UserRole


def check_user_roles(email):
    """Verificar roles de un usuario"""
    try:
        user = User.objects.get(email=email)
        print(f"\n✅ Usuario encontrado: {user.email}")
        print(f"   ID: {user.id}")
        print(f"   Nombre: {user.firstName} {user.lastName}")
        print(f"   Activo: {user.isActive}")

        # Obtener roles
        user_roles = user.userRoles.all()
        print(f"\n📋 Roles del usuario ({user_roles.count()}):")
        for role in user_roles:
            print(f"   - {role.role} (activo: {role.isActive})")

        # Verificar si es ADMIN
        is_admin = user.userRoles.filter(role="ADMIN", isActive=True).exists()
        print(f"\n🔐 ¿Es ADMIN?: {is_admin}")

        return True
    except User.DoesNotExist:
        print(f"❌ Usuario con email '{email}' no encontrado")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


if __name__ == "__main__":
    # Usar el email del test script
    email = "juantadaymalan3@gmail.com"

    print("=" * 60)
    print("🔍 VERIFICACIÓN DE ROLES DE USUARIO")
    print("=" * 60)

    check_user_roles(email)

    # Mostrar todos los usuarios ADMIN
    print("\n" + "=" * 60)
    print("👥 TODOS LOS USUARIOS ADMIN:")
    print("=" * 60)
    admin_users = User.objects.filter(
        userRoles__role="ADMIN", userRoles__isActive=True
    ).distinct()
    for user in admin_users:
        print(f"   - {user.email} ({user.firstName} {user.lastName})")
