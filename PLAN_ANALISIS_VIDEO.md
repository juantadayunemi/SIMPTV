# 🎥 Plan de Implementación - Análisis de Video en Tiempo Real

## 📋 Resumen

Este documento describe el plan completo para implementar el sistema de análisis de tráfico con visualización en tiempo real de detecciones de vehículos.

---

## ✅ Componentes Ya Implementados

### Frontend

#### 1. **VideoPlayerWithOverlay Component** ✅
**Ubicación:** `frontend/src/components/traffic/VideoPlayerWithOverlay.tsx`

**Características:**
- ✅ Video HTML5 con controles nativos
- ✅ Canvas overlay para dibujar bounding boxes
- ✅ Sincronización timestamp video ↔ detecciones (±300ms tolerancia)
- ✅ Colores por tipo de vehículo:
  - 🚗 Autos: Verde (`#00FF00`)
  - 🚚 Camiones: Rojo (`#FF0000`)
  - 🚌 Autobuses: Azul (`#0000FF`)
  - 🏍️ Motos: Amarillo (`#FFFF00`)
- ✅ Panel de estadísticas en tiempo real
- ✅ Log de eventos con scroll
- ✅ WebSocket para recibir detecciones

**Propiedades:**
```typescript
interface VideoPlayerProps {
  videoFile: File;        // Archivo de video local
  analysisId: string;     // ID del análisis
  wsUrl: string;          // URL del WebSocket (localhost:8001)
}
```

#### 2. **RealTimeAnalysisPage** ✅
**Ubicación:** `frontend/src/pages/traffic/RealTimeAnalysisPage.tsx`

**Características:**
- ✅ Formulario de carga de video
- ✅ Selección de cámara (opcional)
- ✅ Selección de ubicación (opcional)
- ✅ Indicador de progreso durante subida
- ✅ Integración con `VideoPlayerWithOverlay`

**Ruta:** `/traffic/realtime`

#### 3. **Card UI Components** ✅
**Ubicación:** `frontend/src/components/ui/card.tsx`

Componentes básicos:
- `Card` - Contenedor principal
- `CardHeader` - Encabezado
- `CardTitle` - Título
- `CardContent` - Contenido

---

## 🔧 Componentes Pendientes de Implementación

### Backend

#### 1. **Modificar `tasks.py` para enviar detecciones frame-by-frame** ⚙️

**Ubicación:** `backend/apps/traffic_app/tasks.py`

**Cambios necesarios:**

```python
# ACTUAL (envía todo al final):
@shared_task
def process_video_analysis(analysis_id):
    # ... procesa todo el video ...
    # Envía resultado final
    
# PROPUESTO (envía frame por frame):
@shared_task
def process_video_analysis(analysis_id):
    analysis = TrafficAnalysis.objects.get(id=analysis_id)
    channel_layer = get_channel_layer()
    
    # Configurar YOLO + Deep SORT
    model = YOLO('yolov8n.pt')
    tracker = DeepSort(...)
    
    cap = cv2.VideoCapture(analysis.videoPath)
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_number = 0
    
    vehicle_tracks = {}  # track_id -> VehicleEntity
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
            
        frame_number += 1
        timestamp = frame_number / fps
        
        # Detección YOLO
        results = model(frame)
        
        # Tracking Deep SORT
        tracks = tracker.update(results)
        
        # Para cada vehículo detectado
        for track in tracks:
            track_id = track['id']
            vehicle_type = track['class']
            bbox = track['bbox']
            confidence = track['confidence']
            
            # Crear VehicleEntity si es primera aparición
            if track_id not in vehicle_tracks:
                vehicle = VehicleEntity.objects.create(
                    analysisId=analysis,
                    trackId=track_id,
                    vehicleType=vehicle_type,
                    firstDetectedAt=timestamp,
                    totalFrames=0
                )
                vehicle_tracks[track_id] = vehicle
                first_appearance = True
            else:
                vehicle = vehicle_tracks[track_id]
                first_appearance = False
            
            # Actualizar VehicleEntity
            vehicle.lastDetectedAt = timestamp
            vehicle.totalFrames += 1
            vehicle.save()
            
            # Guardar VehicleFrameEntity
            VehicleFrameEntity.objects.create(
                vehicleId=vehicle,
                frameNumber=frame_number,
                timestamp=timestamp,
                boundingBoxX=bbox[0],
                boundingBoxY=bbox[1],
                boundingBoxWidth=bbox[2],
                boundingBoxHeight=bbox[3],
                confidence=confidence
            )
            
            # 🚀 ENVIAR DETECCIÓN POR WEBSOCKET (NUEVO)
            async_to_sync(channel_layer.group_send)(
                f"traffic_analysis_{analysis_id}",
                {
                    "type": "vehicle_detected",
                    "data": {
                        "timestamp": timestamp,
                        "track_id": str(track_id),
                        "vehicle_type": vehicle_type,
                        "confidence": float(confidence),
                        "bbox": {
                            "x": int(bbox[0]),
                            "y": int(bbox[1]),
                            "width": int(bbox[2]),
                            "height": int(bbox[3])
                        },
                        "first_appearance": first_appearance
                    }
                }
            )
        
        # Enviar progreso cada 30 frames
        if frame_number % 30 == 0:
            progress = (frame_number / total_frames) * 100
            async_to_sync(channel_layer.group_send)(
                f"traffic_analysis_{analysis_id}",
                {
                    "type": "progress_update",
                    "progress": progress,
                    "current_frame": frame_number,
                    "total_frames": total_frames
                }
            )
    
    # Enviar completado
    async_to_sync(channel_layer.group_send)(
        f"traffic_analysis_{analysis_id}",
        {
            "type": "processing_complete",
            "total_vehicles": len(vehicle_tracks),
            "total_frames": frame_number
        }
    )
```

#### 2. **Actualizar Consumer WebSocket** ⚙️

**Ubicación:** `backend/apps/traffic_app/consumers.py`

**Verificar que tenga:**

```python
class TrafficAnalysisConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.analysis_id = self.scope['url_route']['kwargs']['analysis_id']
        self.group_name = f'traffic_analysis_{self.analysis_id}'
        
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()
    
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )
    
    # Manejar diferentes tipos de mensajes
    async def vehicle_detected(self, event):
        await self.send(text_data=json.dumps({
            'type': 'vehicle_detected',
            **event['data']
        }))
    
    async def progress_update(self, event):
        await self.send(text_data=json.dumps({
            'type': 'progress_update',
            'progress': event['progress'],
            'current_frame': event['current_frame'],
            'total_frames': event['total_frames']
        }))
    
    async def processing_complete(self, event):
        await self.send(text_data=json.dumps({
            'type': 'processing_complete',
            'total_vehicles': event['total_vehicles'],
            'total_frames': event['total_frames']
        }))
    
    async def processing_error(self, event):
        await self.send(text_data=json.dumps({
            'type': 'processing_error',
            'error': event['error']
        }))
```

---

## 🧪 Pruebas Necesarias

### 1. **Prueba Local Básica**
```bash
# Terminal 1 - Backend Django
cd backend
python manage.py runserver

# Terminal 2 - Daphne WebSocket
cd backend
daphne -b 0.0.0.0 -p 8001 config.asgi:application

# Terminal 3 - Celery Worker
cd backend
python -m celery -A config worker --loglevel=info --pool=solo

# Terminal 4 - Redis
redis-server

# Terminal 5 - Frontend
cd frontend
npm run dev
```

### 2. **Flujo de Prueba**
1. ✅ Abrir navegador en `http://localhost:5173/traffic/realtime`
2. ✅ Seleccionar video de tráfico (30-60 segundos)
3. ✅ Seleccionar cámara o ubicación
4. ✅ Click en "Iniciar Análisis"
5. ✅ Esperar subida de video
6. ✅ Ver video reproduciéndose con bounding boxes en tiempo real
7. ✅ Verificar que estadísticas se actualicen
8. ✅ Verificar logs en panel derecho

### 3. **Validaciones**
- [ ] Bounding boxes siguen correctamente a los vehículos
- [ ] Colores diferentes por tipo de vehículo
- [ ] IDs persistentes durante todo el recorrido
- [ ] Sincronización timestamp correcta (±300ms)
- [ ] Estadísticas actualizadas en tiempo real
- [ ] Logs muestran eventos correctamente
- [ ] Video se reproduce a 60 FPS
- [ ] Bajo ancho de banda (1-2 KB/s de detecciones)

---

## 📊 Arquitectura de Datos

### Flujo de Datos:

```
Video Frame → YOLO → Deep SORT → Celery Task
                                      ↓
                                 VehicleEntity
                                      ↓
                             VehicleFrameEntity
                                      ↓
                                 WebSocket
                                      ↓
                                 Frontend
                                      ↓
                          Canvas Overlay (Dibujo)
```

### Tipos de Mensajes WebSocket:

```typescript
// 1. Detección de vehículo
{
  type: 'vehicle_detected',
  timestamp: 5.2,
  track_id: 'VEH_001',
  vehicle_type: 'car',
  confidence: 0.95,
  bbox: { x: 320, y: 180, width: 120, height: 80 },
  first_appearance: true
}

// 2. Actualización de progreso
{
  type: 'progress_update',
  progress: 45.5,
  current_frame: 1350,
  total_frames: 3000
}

// 3. Procesamiento completado
{
  type: 'processing_complete',
  total_vehicles: 47,
  total_frames: 3000
}

// 4. Error
{
  type: 'processing_error',
  error: 'Failed to load video'
}
```

---

## 🎯 Próximos Pasos (Prioridad)

### Inmediato (Hoy):
1. ⚙️ **Modificar `tasks.py`** - Enviar detecciones frame-by-frame via WebSocket
2. ⚙️ **Verificar Consumer** - Asegurar que maneja todos los tipos de mensajes
3. 🧪 **Prueba end-to-end** - Subir video y verificar visualización

### Corto Plazo (Esta Semana):
4. 📊 **Optimizaciones**:
   - Reducir frecuencia de envío (cada 2-3 frames)
   - Comprimir coordenadas (enviar solo cambios)
   - Cachear resultados

5. 🎨 **Mejoras UI**:
   - Botón para pausar detecciones
   - Filtro por tipo de vehículo
   - Timeline con thumbnails
   - Exportar resultados a PDF

### Medio Plazo (Antes del Demo):
6. 📹 **Chunked Upload**:
   - Subir video en chunks de 5MB
   - Procesar chunks en paralelo
   - Mostrar detecciones antes de terminar subida

7. 📦 **Videos Pre-procesados**:
   - Generar 3 videos de demo
   - Guardar JSON con todas las detecciones
   - Carga instantánea para presentación

---

## 📝 Notas Importantes

### Rendimiento:
- **Video local**: 60 FPS nativo (fluido)
- **WebSocket**: 1-2 KB/s (bajo ancho de banda)
- **Sincronización**: ±300ms tolerancia (imperceptible)

### Limitaciones:
- Solo funciona con video completo subido
- No soporta streaming RTSP en vivo (por ahora)
- Requiere Celery + Redis funcionando

### Demo Universitario:
- Sistema diseñado para 1-3 videos simultáneos
- Laptop puede manejar procesamiento en tiempo real
- Presentación profesional con bounding boxes fluidos

---

## 🔗 Referencias

- **YOLO v8**: https://docs.ultralytics.com/
- **Deep SORT**: https://github.com/nwojke/deep_sort
- **Django Channels**: https://channels.readthedocs.io/
- **Canvas API**: https://developer.mozilla.org/en-US/docs/Web/API/Canvas_API

---

**Última actualización:** 11 de octubre de 2025  
**Estado:** Frontend completo ✅ | Backend en progreso ⚙️ | Pruebas pendientes 🧪
