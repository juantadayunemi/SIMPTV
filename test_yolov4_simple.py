#!/usr/bin/env python3
"""
Test simple: YOLOv4-Tiny sin Django
Carga directamente el modelo y prueba detección
"""

import cv2
import numpy as np
from pathlib import Path

def test_yolov4():
    """Test YOLOv4-Tiny sin dependencias Django"""
    
    print("=" * 70)
    print("🧪 TEST YOLOv4-Tiny (Sin Django)")
    print("=" * 70)
    
    # Rutas de modelos
    models_dir = Path(__file__).parent / 'backend' / 'models'
    cfg_path = models_dir / 'yolov4-tiny.cfg'
    weights_path = models_dir / 'yolov4-tiny.weights'
    names_path = models_dir / 'coco.names'
    
    print("\n1️⃣  Verificando modelos...")
    if not cfg_path.exists():
        print(f"   ❌ No encontrado: {cfg_path}")
        return False
    if not weights_path.exists():
        print(f"   ❌ No encontrado: {weights_path}")
        return False
    if not names_path.exists():
        print(f"   ❌ No encontrado: {names_path}")
        return False
    
    print(f"   ✅ {cfg_path.name} ({cfg_path.stat().st_size / 1024:.1f} KB)")
    print(f"   ✅ {weights_path.name} ({weights_path.stat().st_size / 1024 / 1024:.1f} MB)")
    print(f"   ✅ {names_path.name} ({names_path.stat().st_size / 1024:.1f} KB)")
    
    # Cargar clases COCO
    print("\n2️⃣  Cargando clases COCO...")
    with open(names_path, 'r') as f:
        classes = [line.strip() for line in f.readlines()]
    
    vehicle_classes = {1: "bicycle", 2: "car", 3: "motorcycle", 5: "bus", 7: "truck"}
    vehicle_ids = list(vehicle_classes.keys())
    
    print(f"   ✅ {len(classes)} clases totales")
    print(f"   🚗 Vehículos: {', '.join(vehicle_classes.values())}")
    
    # Cargar red YOLOv4-Tiny
    print("\n3️⃣  Cargando YOLOv4-Tiny...")
    net = cv2.dnn.readNetFromDarknet(str(cfg_path), str(weights_path))
    
    # Intentar usar GPU
    try:
        net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
        net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)
        print("   ✅ Red cargada (Backend: CUDA GPU)")
    except:
        net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
        net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)
        print("   ✅ Red cargada (Backend: OpenCV CPU)")
    
    # Obtener capas de salida
    layer_names = net.getLayerNames()
    output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]
    print(f"   📋 Capas de salida: {output_layers}")
    
    # Crear frame de prueba
    print("\n4️⃣  Generando frame de prueba...")
    test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    cv2.rectangle(test_frame, (200, 150), (440, 330), (255, 255, 255), -1)
    print("   ✅ Frame 640x480 generado")
    
    # Crear blob para YOLO
    print("\n5️⃣  Ejecutando inferencia YOLOv4-Tiny...")
    blob = cv2.dnn.blobFromImage(test_frame, 1/255.0, (416, 416), swapRB=True, crop=False)
    net.setInput(blob)
    
    import time
    start = time.time()
    detections = net.forward(output_layers)
    inference_time = (time.time() - start) * 1000
    
    print(f"   ✅ Inferencia completada ({inference_time:.1f} ms)")
    print(f"   📊 Outputs: {len(detections)} capas")
    
    # Procesar detecciones
    print("\n6️⃣  Procesando detecciones...")
    boxes = []
    confidences = []
    class_ids = []
    
    h, w = test_frame.shape[:2]
    
    for output in detections:
        for detection in output:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            
            if confidence > 0.3 and class_id in vehicle_ids:
                center_x = int(detection[0] * w)
                center_y = int(detection[1] * h)
                width = int(detection[2] * w)
                height = int(detection[3] * h)
                
                x1 = int(center_x - width / 2)
                y1 = int(center_y - height / 2)
                
                boxes.append([x1, y1, width, height])
                confidences.append(float(confidence))
                class_ids.append(class_id)
    
    print(f"   ✅ {len(boxes)} detecciones antes de NMS")
    
    # Aplicar NMS
    if len(boxes) > 0:
        indices = cv2.dnn.NMSBoxes(boxes, confidences, 0.3, 0.4)
        if len(indices) > 0:
            indices = indices.flatten() if len(indices.shape) > 1 else indices
            print(f"   ✅ {len(indices)} detecciones después de NMS")
            
            for i in indices:
                print(f"      - {vehicle_classes[class_ids[i]].upper()} ({confidences[i]:.2%})")
        else:
            print("   ⚠️  No sobrevivieron detecciones después de NMS")
    else:
        print("   ⚠️  No se detectaron vehículos (frame sintético)")
    
    # Probar con video real si existe
    print("\n7️⃣  Buscando videos de prueba...")
    media_dir = Path(__file__).parent / 'backend' / 'media' / 'videos'
    
    if media_dir.exists():
        videos = list(media_dir.glob('*.mp4')) + list(media_dir.glob('*.avi'))
        
        if videos:
            test_video = videos[0]
            print(f"   📹 Video encontrado: {test_video.name}")
            
            cap = cv2.VideoCapture(str(test_video))
            ret, frame = cap.read()
            cap.release()
            
            if ret:
                print(f"   ✅ Frame extraído ({frame.shape[1]}x{frame.shape[0]})")
                
                # Detectar en frame real
                blob_real = cv2.dnn.blobFromImage(frame, 1/255.0, (416, 416), swapRB=True, crop=False)
                net.setInput(blob_real)
                
                start = time.time()
                detections_real = net.forward(output_layers)
                inference_time_real = (time.time() - start) * 1000
                
                print(f"   ⚡ Inferencia: {inference_time_real:.1f} ms ({1000/inference_time_real:.1f} FPS)")
                
                # Procesar detecciones reales
                boxes_real = []
                confidences_real = []
                class_ids_real = []
                
                h, w = frame.shape[:2]
                
                for output in detections_real:
                    for detection in output:
                        scores = detection[5:]
                        class_id = np.argmax(scores)
                        confidence = scores[class_id]
                        
                        if confidence > 0.3 and class_id in vehicle_ids:
                            center_x = int(detection[0] * w)
                            center_y = int(detection[1] * h)
                            width = int(detection[2] * w)
                            height = int(detection[3] * h)
                            
                            x1 = int(center_x - width / 2)
                            y1 = int(center_y - height / 2)
                            
                            boxes_real.append([x1, y1, width, height])
                            confidences_real.append(float(confidence))
                            class_ids_real.append(class_id)
                
                if len(boxes_real) > 0:
                    indices_real = cv2.dnn.NMSBoxes(boxes_real, confidences_real, 0.3, 0.4)
                    if len(indices_real) > 0:
                        indices_real = indices_real.flatten() if len(indices_real.shape) > 1 else indices_real
                        
                        print(f"\n   🚗 {len(indices_real)} vehículos detectados:")
                        for i in indices_real:
                            print(f"      - {vehicle_classes[class_ids_real[i]].upper()} ({confidences_real[i]:.2%})")
                        
                        # Guardar resultado anotado
                        annotated = frame.copy()
                        for i in indices_real:
                            x1, y1, w_box, h_box = boxes_real[i]
                            x2, y2 = x1 + w_box, y1 + h_box
                            
                            cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 255, 0), 2)
                            label = f"{vehicle_classes[class_ids_real[i]]} {confidences_real[i]:.2%}"
                            cv2.putText(annotated, label, (x1, y1-10), 
                                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                        
                        output_path = Path(__file__).parent / 'test_yolov4_result.jpg'
                        cv2.imwrite(str(output_path), annotated)
                        print(f"\n   💾 Resultado guardado: {output_path.name}")
                    else:
                        print("   ⚠️  No se detectaron vehículos en el video")
                else:
                    print("   ⚠️  No se detectaron vehículos en el video")
        else:
            print("   ⚠️  No hay videos en media/videos/")
    else:
        print("   ⚠️  Directorio media/videos/ no existe")
    
    print("\n" + "=" * 70)
    print("✅ TEST COMPLETADO - YOLOv4-Tiny funcionando")
    print("=" * 70)
    
    return True


if __name__ == '__main__':
    import sys
    success = test_yolov4()
    sys.exit(0 if success else 1)
