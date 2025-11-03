"""
Script para probar Firebase Admin directamente con el proyecto trafismart
"""

import os
import sys
import django
from dotenv import load_dotenv

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
load_dotenv()

django.setup()

from firebase_admin import messaging
import firebase_admin

print("\n" + "=" * 60)
print("🔥 Verificando Firebase Admin SDK")
print("=" * 60)

# Verificar que Firebase esté inicializado
try:
    app = firebase_admin.get_app()
    print(f"✅ Firebase Admin inicializado")
    print(f"   Project ID: {app.project_id}")
except ValueError:
    print("❌ Firebase Admin NO está inicializado")
    sys.exit(1)

# Verificar token desde la BD
from apps.notifications_app.models import FCMDevice
from django.contrib.auth import get_user_model

User = get_user_model()

devices = FCMDevice.objects.filter(is_active=True)
print(f"\n📱 Dispositivos registrados: {devices.count()}")

if devices.exists():
    device = devices.first()
    print(f"\n🔍 Probando con dispositivo:")
    print(f"   Usuario: {device.user.email}")
    print(f"   Token: {device.token[:30]}...")
    print(f"   Tipo: {device.device_type}")

    # Intentar enviar mensaje de prueba
    print(f"\n📤 Enviando mensaje de prueba...")

    try:
        message = messaging.Message(
            notification=messaging.Notification(
                title="🧪 Prueba Directa", body="Mensaje de prueba desde script Python"
            ),
            token=device.token,
        )

        response = messaging.send(message)
        print(f"✅ Mensaje enviado exitosamente!")
        print(f"   Message ID: {response}")

    except Exception as e:
        print(f"❌ Error al enviar mensaje:")
        print(f"   Tipo: {type(e).__name__}")
        print(f"   Mensaje: {str(e)}")

        # Detalles adicionales del error
        if hasattr(e, "code"):
            print(f"   Código: {e.code}")
        if hasattr(e, "http_response"):
            print(f"   HTTP Response: {e.http_response}")

        # Sugerencias según el error
        if "NOT_FOUND" in str(e) or "Requested entity was not found" in str(e):
            print(f"\n💡 Posibles causas:")
            print(f"   1. El token FCM es antiguo o fue generado para otro proyecto")
            print(f"   2. El navegador generó el token con credenciales diferentes")
            print(f"   3. Cloud Messaging no está habilitado en el proyecto")
            print(f"\n🔧 Solución:")
            print(f"   1. En el navegador, ejecuta: localStorage.clear()")
            print(f"   2. Recarga la página y vuelve a iniciar sesión")
            print(f"   3. Verifica que se registre un nuevo token")
else:
    print("⚠️ No hay dispositivos registrados")

print("\n" + "=" * 60)
