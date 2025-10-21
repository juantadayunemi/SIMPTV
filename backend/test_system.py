"""
Script de diagnóstico del sistema
Verifica que todas las importaciones y configuraciones funcionen
"""

import sys
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

print("=" * 80)
print("🔍 DIAGNÓSTICO DEL SISTEMA")
print("=" * 80)

# 1. Verificar importación de VideoProcessor
print("\n1️⃣ Verificando VideoProcessor...")
try:
    from apps.traffic_app.services import VideoProcessor
    print(f"   ✅ VideoProcessor importado correctamente")
    print(f"   📦 Clase: {VideoProcessor.__name__}")
    print(f"   📍 Módulo: {VideoProcessor.__module__}")
except Exception as e:
    print(f"   ❌ Error importando VideoProcessor: {e}")
    sys.exit(1)

# 2. Verificar modelos existen
print("\n2️⃣ Verificando modelos MobileNetSSD...")
try:
    from pathlib import Path
    from django.conf import settings
    
    models_dir = Path(settings.BASE_DIR) / 'models'
    prototxt = models_dir / 'MobileNetSSD_deploy.prototxt'
    caffemodel = models_dir / 'MobileNetSSD_deploy.caffemodel'
    haarcascade = models_dir / 'haarcascade_russian_plate_number.xml'
    
    if prototxt.exists():
        print(f"   ✅ MobileNetSSD_deploy.prototxt ({prototxt.stat().st_size / 1024:.1f} KB)")
    else:
        print(f"   ❌ MobileNetSSD_deploy.prototxt NO ENCONTRADO")
    
    if caffemodel.exists():
        print(f"   ✅ MobileNetSSD_deploy.caffemodel ({caffemodel.stat().st_size / (1024*1024):.1f} MB)")
    else:
        print(f"   ❌ MobileNetSSD_deploy.caffemodel NO ENCONTRADO")
    
    if haarcascade.exists():
        print(f"   ✅ haarcascade_russian_plate_number.xml ({haarcascade.stat().st_size / 1024:.1f} KB)")
    else:
        print(f"   ❌ haarcascade_russian_plate_number.xml NO ENCONTRADO")
        
except Exception as e:
    print(f"   ❌ Error verificando modelos: {e}")

# 3. Verificar que los modelos cargan
print("\n3️⃣ Probando inicialización de VideoProcessor...")
try:
    processor = VideoProcessor(
        model_path=str(models_dir),
        confidence_threshold=0.5,
        iou_threshold=0.3
    )
    print("   ✅ VideoProcessor inicializado correctamente")
    print(f"   📊 Confidence threshold: {processor.confidence_threshold}")
    print(f"   📊 IOU threshold: {processor.iou_threshold}")
except Exception as e:
    print(f"   ❌ Error inicializando VideoProcessor: {e}")
    import traceback
    traceback.print_exc()

# 4. Verificar database
print("\n4️⃣ Verificando base de datos...")
try:
    from apps.traffic_app.models import Camera, Location
    
    locations_count = Location.objects.count()
    cameras_count = Camera.objects.count()
    
    print(f"   ✅ Conexión a base de datos OK")
    print(f"   📍 Ubicaciones: {locations_count}")
    print(f"   📷 Cámaras: {cameras_count}")
    
    if cameras_count == 0:
        print("\n   ⚠️  NO HAY CÁMARAS EN LA BASE DE DATOS")
        print("   💡 Crea cámaras desde el frontend o con el admin de Django")
        
except Exception as e:
    print(f"   ❌ Error con base de datos: {e}")

# 5. Verificar URLs
print("\n5️⃣ Verificando configuración de URLs...")
try:
    from django.urls import reverse
    
    # Intentar resolver algunas URLs importantes
    urls_to_check = [
        ('camera-list', 'Listado de cámaras'),
        ('location-list', 'Listado de ubicaciones'),
    ]
    
    for url_name, description in urls_to_check:
        try:
            url = reverse(url_name)
            print(f"   ✅ {description}: {url}")
        except Exception as e:
            print(f"   ⚠️  {description}: No se pudo resolver")
            
except Exception as e:
    print(f"   ❌ Error verificando URLs: {e}")

print("\n" + "=" * 80)
print("🎯 DIAGNÓSTICO COMPLETADO")
print("=" * 80)
print("\nSi todo está ✅, el backend debería funcionar correctamente.")
print("Si hay ❌, revisa los errores arriba.\n")
