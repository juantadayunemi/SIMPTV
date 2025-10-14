"""
Verifica que Django esté configurado para usar ASGI (Daphne)
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.conf import settings

print("\n" + "="*60)
print("🔍 VERIFICACIÓN DE CONFIGURACIÓN ASGI")
print("="*60 + "\n")

# 1. Verificar que daphne esté instalado
try:
    import daphne
    print("✅ Daphne instalado:", daphne.__version__)
except ImportError:
    print("❌ Daphne NO instalado - ejecuta: pip install daphne")
    sys.exit(1)

# 2. Verificar que daphne esté en INSTALLED_APPS
if 'daphne' in settings.INSTALLED_APPS:
    daphne_index = settings.INSTALLED_APPS.index('daphne')
    print(f"✅ Daphne en INSTALLED_APPS (posición: {daphne_index})")
    
    # Debe estar ANTES de django.contrib.staticfiles
    if 'django.contrib.staticfiles' in settings.INSTALLED_APPS:
        staticfiles_index = settings.INSTALLED_APPS.index('django.contrib.staticfiles')
        if daphne_index < staticfiles_index:
            print("✅ Daphne está ANTES de django apps (correcto)")
        else:
            print("⚠️  Daphne está DESPUÉS de django apps (podría no funcionar)")
else:
    print("❌ Daphne NO está en INSTALLED_APPS")
    sys.exit(1)

# 3. Verificar ASGI_APPLICATION
if hasattr(settings, 'ASGI_APPLICATION'):
    print(f"✅ ASGI_APPLICATION configurado: {settings.ASGI_APPLICATION}")
else:
    print("❌ ASGI_APPLICATION no está configurado")
    sys.exit(1)

# 4. Verificar CHANNEL_LAYERS
if hasattr(settings, 'CHANNEL_LAYERS'):
    channel_backend = settings.CHANNEL_LAYERS['default']['BACKEND']
    print(f"✅ CHANNEL_LAYERS configurado: {channel_backend}")
    
    if 'InMemory' in channel_backend:
        print("   ℹ️  Usando InMemoryChannelLayer (sin Redis)")
    elif 'Redis' in channel_backend:
        print("   ℹ️  Usando RedisChannelLayer")
else:
    print("❌ CHANNEL_LAYERS no está configurado")

# 5. Verificar channels
try:
    import channels
    print(f"✅ Django Channels instalado: {channels.__version__}")
except ImportError:
    print("❌ Django Channels NO instalado")
    sys.exit(1)

print("\n" + "="*60)
print("📋 RESUMEN")
print("="*60 + "\n")

print("✅ Configuración correcta para WebSocket")
print("\n🚀 Para iniciar Django con soporte ASGI:")
print("   cd backend")
print("   python manage.py runserver 8001")
print("\n💡 Al iniciar, deberías ver:")
print('   "Daphne running..."')
print('   "Listening on TCP address 0.0.0.0:8001"')
print("\n✅ Si ves ese mensaje, los WebSockets funcionarán correctamente")
print()
