"""
Script para configurar usuarios ADMIN en el sistema
"""

import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.auth_app.models import UserRole
from django.contrib.auth import get_user_model

User = get_user_model()

print("=" * 80)
print("🔧 CONFIGURACIÓN DE USUARIOS ADMINISTRADORES")
print("=" * 80)

# 1. Listar todos los usuarios existentes
print("\n1️⃣ Usuarios existentes en el sistema:")
all_users = User.objects.all()

if not all_users.exists():
    print("   ❌ No hay usuarios en el sistema")
    print("\n   💡 Necesitas crear un superusuario primero:")
    print("      python manage.py createsuperuser")
    exit(1)

for user in all_users:
    full_name = f"{user.firstName or ''} {user.lastName or ''}".strip() or "Sin nombre"
    print(f"   • ID: {user.id} | Email: {user.email} | Nombre: {full_name}")

    # Verificar si tiene rol
    user_roles = UserRole.objects.filter(user=user)
    if user_roles.exists():
        roles = ", ".join([ur.role for ur in user_roles])
        print(f"      → Roles: {roles}")
    else:
        print(f"      → Sin roles asignados")

# 2. Verificar roles ADMIN existentes
print("\n2️⃣ Usuarios con rol ADMIN:")
admin_roles = UserRole.objects.filter(role="ADMIN")

if admin_roles.exists():
    for admin_role in admin_roles:
        full_name = (
            f"{admin_role.user.firstName or ''} {admin_role.user.lastName or ''}".strip()
            or admin_role.user.email
        )
        print(f"   • {full_name} (ID: {admin_role.user.id})")
else:
    print("   ❌ No hay usuarios con rol ADMIN")

# 3. Ofrecer asignar rol ADMIN a usuarios
print("\n3️⃣ Configuración de roles ADMIN:")

if all_users.count() == 1:
    # Si solo hay un usuario, asignarlo automáticamente
    user = all_users.first()
    full_name = f"{user.firstName or ''} {user.lastName or ''}".strip() or user.email
    print(f"\n   Solo hay un usuario: {full_name}")
    print(f"   ¿Asignar rol ADMIN? (s/n): ", end="")

    response = input().strip().lower()

    if response == "s":
        # Verificar si ya tiene el rol
        existing_role = UserRole.objects.filter(user=user, role="ADMIN").first()

        if existing_role:
            print(f"   ℹ️ El usuario {full_name} ya tiene rol ADMIN")
        else:
            UserRole.objects.create(user=user, role="ADMIN")
            print(f"   ✅ Rol ADMIN asignado a {full_name}")
    else:
        print("   ⏭️ Operación cancelada")
else:
    # Múltiples usuarios - permitir elegir
    print("\n   Usuarios disponibles:")
    for idx, user in enumerate(all_users, 1):
        has_admin = UserRole.objects.filter(user=user, role="ADMIN").exists()
        admin_marker = " [YA ES ADMIN]" if has_admin else ""
        full_name = (
            f"{user.firstName or ''} {user.lastName or ''}".strip() or user.email
        )
        print(f"      {idx}. {full_name} (ID: {user.id}){admin_marker}")

    print(
        f"\n   Ingrese el número del usuario para asignar rol ADMIN (0 para cancelar): ",
        end="",
    )

    try:
        choice = int(input().strip())

        if choice == 0:
            print("   ⏭️ Operación cancelada")
        elif 1 <= choice <= all_users.count():
            selected_user = list(all_users)[choice - 1]

            # Verificar si ya tiene el rol
            existing_role = UserRole.objects.filter(
                user=selected_user, role="ADMIN"
            ).first()

            if existing_role:
                print(f"   ℹ️ El usuario {selected_user.username} ya tiene rol ADMIN")
            else:
                UserRole.objects.create(user=selected_user, role="ADMIN")
                print(f"   ✅ Rol ADMIN asignado a {selected_user.username}")
        else:
            print("   ❌ Opción inválida")
    except ValueError:
        print("   ❌ Entrada inválida")

# 4. Resumen final
print("\n4️⃣ Resumen final:")
admin_roles_final = UserRole.objects.filter(role="ADMIN")
admin_users_final = User.objects.filter(
    id__in=admin_roles_final.values_list("user_id", flat=True)
)

print(f"   Total usuarios ADMIN: {admin_users_final.count()}")

if admin_users_final.exists():
    print("\n   Usuarios ADMIN configurados:")
    for admin in admin_users_final:
        full_name = (
            f"{admin.firstName or ''} {admin.lastName or ''}".strip() or admin.email
        )
        print(f"      • {full_name} (ID: {admin.id}, Email: {admin.email})")

        # Verificar dispositivos FCM
        from apps.notifications_app.models import FCMDevice

        devices = FCMDevice.objects.filter(user=admin, is_active=True)
        print(f"         → Dispositivos FCM: {devices.count()}")

    print("\n   ✅ Sistema configurado correctamente")
    print("\n   📱 Próximos pasos:")
    print("      1. Registra dispositivos FCM para estos usuarios desde la app móvil")
    print("      2. Procesa un nuevo video con placas que tengan denuncias")
    print("      3. Las notificaciones FCM llegarán automáticamente")
else:
    print("\n   ⚠️ Aún no hay usuarios ADMIN configurados")
    print("   Ejecuta este script nuevamente para asignar roles")

print("\n" + "=" * 80)
print("✅ CONFIGURACIÓN COMPLETADA")
print("=" * 80)
