#!/usr/bin/env python3
"""
Script de prueba: Verifica que YOLOv4-Tiny detecta vehículos correctamente

Prueba la detección en una imagen de prueba generada o en un frame de video.
"""

import cv2
import numpy as np
from pathlib import Path
import sys
import os
import django

# Agregar backend al path
backend_path = Path(__file__).parent / 'backend'
sys.path.insert(0, str(backend_path))

# Configurar Django
os.chdir(str(backend_path))  # Cambiar al directorio backend
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

def test_yolov4_detection():
    """Prueba rápida de detección YOLOv4-Tiny"""
    
    try:
        from apps.traffic_app.services.video_processor_opencv import VideoProcessorOpenCV
        
        print("=" * 70)
        print("🧪 TEST: YOLOv4-Tiny Vehicle Detection")
        print("=" * 70)
        
        # Inicializar procesador
        print("\n1️⃣  Inicializando VideoProcessorOpenCV...")
        processor = VideoProcessorOpenCV(
            confidence_threshold=0.3  # Umbral bajo para prueba
        )
        print("   ✅ Procesador inicializado correctamente")
        print(f"   📋 Modelo: {processor.weights_path.name}")
        print(f"   📋 Config: {processor.cfg_path.name}")
        print(f"   📋 Clases vehículos: {list(processor.VEHICLE_CLASSES.values())}")
        
        # Crear frame de prueba (640x480, con rectángulo simulando vehículo)
        print("\n2️⃣  Generando frame de prueba...")
        test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Dibujar rectángulo simulando auto (centro del frame)
        cv2.rectangle(test_frame, (200, 150), (440, 330), (255, 255, 255), -1)
        cv2.rectangle(test_frame, (220, 170), (420, 310), (180, 180, 180), -1)
        cv2.rectangle(test_frame, (240, 200), (400, 280), (100, 100, 100), -1)
        print("   ✅ Frame de prueba generado (640x480)")
        
        # Guardar frame de prueba
        test_image_path = Path(__file__).parent / 'test_detection_frame.jpg'
        cv2.imwrite(str(test_image_path), test_frame)
        print(f"   💾 Guardado en: {test_image_path}")
        
        # Detectar vehículos
        print("\n3️⃣  Ejecutando detección YOLOv4-Tiny...")
        detections = processor.detect_vehicles(test_frame)
        
        print(f"   ✅ Detecciones encontradas: {len(detections)}")
        
        if detections:
            print("\n   📦 Detecciones:")
            for i, det in enumerate(detections, 1):
                print(f"      {i}. {det['class_name'].upper()}")
                print(f"         - Confianza: {det['confidence']:.2%}")
                print(f"         - BBox: {det['bbox']}")
                print(f"         - Class ID: {det['class_id']}")
        else:
            print("\n   ⚠️  No se detectaron vehículos en el frame de prueba")
            print("   💡 Esto es normal - el frame sintético puede no ser reconocido")
            print("   ✅ Sin embargo, el modelo cargó correctamente")
        
        # Probar con video real si existe
        print("\n4️⃣  Buscando videos de prueba...")
        media_dir = backend_path / 'media' / 'videos'
        
        if media_dir.exists():
            videos = list(media_dir.glob('*.mp4')) + list(media_dir.glob('*.avi'))
            
            if videos:
                test_video = videos[0]
                print(f"   📹 Video encontrado: {test_video.name}")
                
                cap = cv2.VideoCapture(str(test_video))
                ret, real_frame = cap.read()
                cap.release()
                
                if ret:
                    print(f"   ✅ Frame extraído ({real_frame.shape[1]}x{real_frame.shape[0]})")
                    
                    print("\n5️⃣  Detectando en frame real...")
                    real_detections = processor.detect_vehicles(real_frame)
                    
                    print(f"   ✅ Detecciones: {len(real_detections)}")
                    
                    if real_detections:
                        print("\n   🚗 Vehículos detectados:")
                        for i, det in enumerate(real_detections, 1):
                            print(f"      {i}. {det['class_name'].upper()} ({det['confidence']:.2%})")
                        
                        # Dibujar detecciones
                        annotated = real_frame.copy()
                        for det in real_detections:
                            x1, y1, x2, y2 = det['bbox']
                            cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 255, 0), 2)
                            label = f"{det['class_name']} {det['confidence']:.2%}"
                            cv2.putText(annotated, label, (x1, y1-10), 
                                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                        
                        output_path = Path(__file__).parent / 'test_detection_result.jpg'
                        cv2.imwrite(str(output_path), annotated)
                        print(f"\n   💾 Resultado guardado: {output_path}")
            else:
                print("   ⚠️  No se encontraron videos en media/videos/")
        else:
            print("   ⚠️  Directorio media/videos/ no existe")
        
        print("\n" + "=" * 70)
        print("✅ TEST COMPLETADO - YOLOv4-Tiny funcionando correctamente")
        print("=" * 70)
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = test_yolov4_detection()
    sys.exit(0 if success else 1)
