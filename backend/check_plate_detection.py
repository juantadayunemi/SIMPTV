# Script para verificar configuración de detección de placas
# Ejecutar con: python check_plate_detection.py

import os
import sys
from pathlib import Path

# Agregar el directorio backend al path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# Configurar Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django

django.setup()

from django.conf import settings
from apps.traffic_app.models import TrafficAnalysis


def check_plate_detection_config():
    """Verifica la configuración de detección de placas"""

    print("=" * 80)
    print("🔍 VERIFICACIÓN DE CONFIGURACIÓN - DETECCIÓN DE PLACAS")
    print("=" * 80)
    print()

    # 1. Variables de entorno
    print("📋 1. VARIABLES DE ENTORNO:")
    print(f"   ENABLE_PLATE_DETECTION = {settings.ENABLE_PLATE_DETECTION}")

    if settings.ENABLE_PLATE_DETECTION:
        print("   ✅ Detección de placas HABILITADA")
    else:
        print("   ❌ Detección de placas DESHABILITADA")
        print("   💡 Edita backend/.env y agrega: ENABLE_PLATE_DETECTION=True")

    print()
    print(
        f"   ROBOFLOW_API_KEY = {'Configurado ✅' if settings.ROBOFLOW_API_KEY else 'No configurado ⚠️'}"
    )

    if settings.ROBOFLOW_API_KEY:
        print("   ✅ Roboflow API configurado (Detección mejorada con IA)")
    else:
        print("   ⚠️ Roboflow API no configurado (usando métodos tradicionales)")
        print("   💡 Opcional: Obtén API key en https://roboflow.com/")

    print()

    # 2. Carpetas de salida
    print("📁 2. CARPETAS DE SALIDA:")

    media_root = Path(settings.MEDIA_ROOT)
    directories = [
        ("ROI YOLO", media_root / "ROI YOLO"),
        ("Placas", media_root / "Placas"),
        ("Datos", media_root / "datos"),
    ]

    for name, path in directories:
        if path.exists():
            files_count = len(list(path.rglob("*.*")))
            print(f"   ✅ {name}: {path} ({files_count} archivos)")
        else:
            print(f"   ⚠️ {name}: {path} (No existe - se creará automáticamente)")

    print()

    # 3. Modelos requeridos
    print("🤖 3. MODELOS REQUERIDOS:")

    # Verificar Haarcascade
    cascade_path = BASE_DIR / "models" / "haarcascade_russian_plate_number.xml"
    if cascade_path.exists():
        print(f"   ✅ Haarcascade: {cascade_path}")
    else:
        print(f"   ❌ Haarcascade NO encontrado: {cascade_path}")
        print(
            "   💡 Descarga desde: https://github.com/opencv/opencv/tree/master/data/haarcascades"
        )

    # Verificar EasyOCR
    try:
        import easyocr

        print(f"   ✅ EasyOCR instalado (versión {easyocr.__version__})")
    except ImportError:
        print("   ❌ EasyOCR NO instalado")
        print("   💡 Instalar con: pip install easyocr")

    print()

    # 4. Estadísticas de análisis
    print("📊 4. ESTADÍSTICAS DE ANÁLISIS:")

    try:
        total_analyses = TrafficAnalysis.objects.count()
        completed = TrafficAnalysis.objects.filter(status="COMPLETED").count()

        print(f"   Total de análisis: {total_analyses}")
        print(f"   Completados: {completed}")

        if completed > 0:
            latest = (
                TrafficAnalysis.objects.filter(status="COMPLETED")
                .order_by("-endedAt")
                .first()
            )
            print()
            print(f"   Último análisis completado:")
            print(f"   - ID: {latest.id}")
            print(f"   - Vehículos detectados: {latest.totalVehicles}")
            print(f"   - Placas detectadas: {latest.platesDetected}")
            print(f"   - Placas capturadas: {latest.platesCaptured}")
            print(f"   - Fecha: {latest.endedAt.strftime('%Y-%m-%d %H:%M:%S')}")

            # Verificar si se guardaron imágenes
            video_name = Path(latest.videoPath).stem if latest.videoPath else "unknown"
            analysis_id = latest.id

            roi_dir = media_root / "ROI YOLO" / f"{video_name}_analysis_{analysis_id}"
            placas_dir = media_root / "Placas" / f"{video_name}_analysis_{analysis_id}"

            if roi_dir.exists() or placas_dir.exists():
                roi_count = len(list(roi_dir.glob("*.jpg"))) if roi_dir.exists() else 0
                placas_count = (
                    len(list(placas_dir.glob("*.jpg"))) if placas_dir.exists() else 0
                )

                print(f"   - Imágenes ROI guardadas: {roi_count}")
                print(f"   - Imágenes placas guardadas: {placas_count}")
            else:
                print(f"   ⚠️ No se encontraron carpetas de imágenes para este análisis")
        else:
            print("   ⚠️ No hay análisis completados aún")

    except Exception as e:
        print(f"   ❌ Error obteniendo estadísticas: {e}")

    print()
    print("=" * 80)
    print("🚀 PRÓXIMOS PASOS:")
    print("=" * 80)
    print()

    if not settings.ENABLE_PLATE_DETECTION:
        print("1. ✏️ Edita backend/.env y agrega:")
        print("   ENABLE_PLATE_DETECTION=True")
        print()
        print("2. 🔄 Reinicia los servicios de Celery:")
        print("   - Detén Celery Worker y Beat (Ctrl+C)")
        print("   - Inicia nuevamente con:")
        print("     celery -A config worker -l INFO")
        print("     celery -A config beat -l INFO")
        print()
        print("3. 📹 Procesa un video de prueba desde el frontend")
        print()
    else:
        print("✅ Configuración correcta. Puedes procesar videos ahora.")
        print()
        print("💡 Para mejorar la precisión:")
        print("   - Configura Roboflow API (opcional)")
        print("   - Instala EasyOCR si no está instalado")
        print()

    print("📖 Ver documentación completa en: PLATE_DETECTION_STATUS.md")
    print()


if __name__ == "__main__":
    check_plate_detection_config()
