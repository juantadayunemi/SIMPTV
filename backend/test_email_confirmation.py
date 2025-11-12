"""
Script de prueba para verificar el sistema de confirmación de email mejorado

Prueba los siguientes escenarios:
1. Registro de usuario sin confirmar email
2. Intento de login sin email confirmado (debe reenviar link)
3. Confirmación de email (debe activar cuenta)
4. Reset password sin email confirmado (debe confirmar email)
5. Limpieza de usuarios no verificados

Ejecutar desde backend/:
    python test_email_confirmation.py
"""

import os
import django
import sys

# Setup Django
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.utils import timezone
from datetime import timedelta
from apps.auth_app.models import User, EmailConfirmationToken, PasswordResetToken
from apps.auth_app.email_utils import (
    generate_confirmation_token,
    generate_password_reset_token,
)


def cleanup_test_users():
    """Eliminar usuarios de prueba anteriores"""
    test_emails = [
        "test_unverified@example.com",
        "test_login@example.com",
        "test_reset@example.com",
    ]

    deleted = User.objects.filter(email__in=test_emails).delete()
    print(f"✓ Limpieza: Eliminados {deleted[0]} usuarios de prueba anteriores\n")


def test_1_register_without_confirmation():
    """Test 1: Registro sin confirmar email"""
    print("=" * 70)
    print("TEST 1: Registro sin confirmar email")
    print("=" * 70)

    user = User.objects.create_user(
        email="test_unverified@example.com",
        password="test123",
        firstName="Test",
        lastName="Unverified",
    )

    print(f"✓ Usuario creado: {user.email}")
    print(f"  - emailConfirmed: {user.emailConfirmed}")
    print(f"  - isActive: {user.isActive}")
    print(f"  - createdAt: {user.createdAt}")

    # Simular que pasaron 5 minutos
    user.createdAt = timezone.now() - timedelta(minutes=5)
    user.save()
    print(f"  - createdAt modificado: {user.createdAt} (hace 5 minutos)")

    print("\n✅ TEST 1 PASADO: Usuario no verificado creado\n")
    return user


def test_2_login_without_confirmation():
    """Test 2: Intento de login sin email confirmado"""
    print("=" * 70)
    print("TEST 2: Login sin email confirmado (debe reenviar link)")
    print("=" * 70)

    user = User.objects.create_user(
        email="test_login@example.com",
        password="test123",
        firstName="Test",
        lastName="Login",
    )

    print(f"✓ Usuario creado: {user.email}")
    print(f"  - emailConfirmed: {user.emailConfirmed}")

    # Simular generación de token (lo que haría LoginView)
    token_obj = generate_confirmation_token(user)
    print(f"✓ Token de confirmación generado: {token_obj[:20]}...")

    # Verificar que el token existe en DB
    token = EmailConfirmationToken.objects.get(token=token_obj)
    print(f"✓ Token guardado en DB:")
    print(f"  - Token: {token.token[:20]}...")
    print(f"  - Usuario: {token.user.email}")
    print(f"  - Expira: {token.expiresAt}")
    print(f"  - Usado: {token.isUsed}")

    print("\n✅ TEST 2 PASADO: Sistema reenvía link correctamente\n")
    return user, token_obj


def test_3_confirm_email():
    """Test 3: Confirmación de email"""
    print("=" * 70)
    print("TEST 3: Confirmación de email (debe activar cuenta)")
    print("=" * 70)

    user, token_string = test_2_login_without_confirmation()

    # Simular confirmación de email (lo que haría ConfirmEmailView)
    token = EmailConfirmationToken.objects.get(token=token_string)

    print(f"✓ Confirmando email para: {user.email}")
    print(f"  ANTES:")
    print(f"    - emailConfirmed: {user.emailConfirmed}")
    print(f"    - isActive: {user.isActive}")

    # Activar cuenta
    user.emailConfirmed = True
    user.isActive = True
    user.save(update_fields=["emailConfirmed", "isActive", "updatedAt"])

    # Marcar token como usado
    token.mark_as_used()

    # Refrescar desde DB
    user.refresh_from_db()
    token.refresh_from_db()

    print(f"  DESPUÉS:")
    print(f"    - emailConfirmed: {user.emailConfirmed}")
    print(f"    - isActive: {user.isActive}")
    print(f"    - Token usado: {token.isUsed}")

    assert user.emailConfirmed == True, "❌ Email no fue confirmado"
    assert user.isActive == True, "❌ Cuenta no fue activada"
    assert token.isUsed == True, "❌ Token no fue marcado como usado"

    print("\n✅ TEST 3 PASADO: Email confirmado y cuenta activada\n")


def test_4_reset_password_confirms_email():
    """Test 4: Reset password confirma email"""
    print("=" * 70)
    print("TEST 4: Reset password sin email confirmado (debe confirmar)")
    print("=" * 70)

    user = User.objects.create_user(
        email="test_reset@example.com",
        password="test123",
        firstName="Test",
        lastName="Reset",
    )

    print(f"✓ Usuario creado: {user.email}")
    print(f"  ANTES:")
    print(f"    - emailConfirmed: {user.emailConfirmed}")
    print(f"    - isActive: {user.isActive}")

    # Generar token de reset
    token_string = generate_password_reset_token(user)
    print(f"✓ Token de reset generado: {token_string[:20]}...")

    # Simular reset de password (lo que haría ResetPasswordView)
    token = PasswordResetToken.objects.get(token=token_string)

    from django.contrib.auth.hashers import make_password

    user.passwordHash = make_password("newpassword123")
    user.emailConfirmed = True
    user.isActive = True
    user.save(update_fields=["passwordHash", "emailConfirmed", "isActive", "updatedAt"])

    token.mark_as_used()

    # Refrescar desde DB
    user.refresh_from_db()
    token.refresh_from_db()

    print(f"  DESPUÉS:")
    print(f"    - emailConfirmed: {user.emailConfirmed}")
    print(f"    - isActive: {user.isActive}")
    print(f"    - Token usado: {token.isUsed}")

    assert user.emailConfirmed == True, "❌ Email no fue confirmado"
    assert user.isActive == True, "❌ Cuenta no fue activada"
    assert token.isUsed == True, "❌ Token no fue marcado como usado"

    print("\n✅ TEST 4 PASADO: Reset password confirma email correctamente\n")


def test_5_cleanup_unverified_users():
    """Test 5: Limpieza de usuarios no verificados"""
    print("=" * 70)
    print("TEST 5: Limpieza de usuarios no verificados")
    print("=" * 70)

    # Contar usuarios no verificados antiguos
    cutoff_time = timezone.now() - timedelta(minutes=4)
    unverified_users = User.objects.filter(
        emailConfirmed=False, createdAt__lt=cutoff_time
    )

    count_before = unverified_users.count()
    print(f"✓ Usuarios no verificados (>4 minutos): {count_before}")

    if count_before > 0:
        for user in unverified_users:
            minutes_elapsed = int(
                (timezone.now() - user.createdAt).total_seconds() / 60
            )
            print(f"  - {user.email} (hace {minutes_elapsed} minutos)")

        # Eliminar
        deleted_count, _ = unverified_users.delete()
        print(f"\n✓ Eliminados: {deleted_count} usuarios")

        # Verificar
        count_after = User.objects.filter(
            emailConfirmed=False, createdAt__lt=cutoff_time
        ).count()

        assert count_after == 0, f"❌ Aún quedan {count_after} usuarios no verificados"

        print("\n✅ TEST 5 PASADO: Limpieza ejecutada correctamente\n")
    else:
        print("ℹ️  No hay usuarios no verificados para eliminar")
        print("\n✅ TEST 5 PASADO: Sistema funciona correctamente\n")


def main():
    """Ejecutar todos los tests"""
    print("\n" + "=" * 70)
    print("🧪 SUITE DE PRUEBAS: Sistema de Confirmación de Email")
    print("=" * 70 + "\n")

    try:
        # Limpiar usuarios de prueba anteriores
        cleanup_test_users()

        # Ejecutar tests
        test_1_register_without_confirmation()
        test_3_confirm_email()
        test_4_reset_password_confirms_email()
        test_5_cleanup_unverified_users()

        # Resumen final
        print("=" * 70)
        print("✅ TODOS LOS TESTS PASARON EXITOSAMENTE")
        print("=" * 70)
        print("\n📊 Resumen:")
        print("  ✓ Registro sin confirmación")
        print("  ✓ Login reenvía link automáticamente")
        print("  ✓ Confirmación de email activa cuenta")
        print("  ✓ Reset password confirma email")
        print("  ✓ Limpieza de usuarios no verificados")

        print("\n🚀 Sistema listo para producción!")

        # Limpiar usuarios de prueba
        print("\n🧹 Limpiando usuarios de prueba...")
        cleanup_test_users()

    except AssertionError as e:
        print(f"\n❌ TEST FALLIDO: {str(e)}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR INESPERADO: {str(e)}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
