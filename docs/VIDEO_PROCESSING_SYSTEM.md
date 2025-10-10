# 🎥 Sistema de Análisis de Tráfico - Documentación Técnica

## ✅ Componentes Implementados

### 1. **Video Processor** (`video_processor.py`)
Núcleo del sistema de procesamiento de video.

**Características:**
- **Detección con YOLO8**: Detecta 5 tipos de vehículos (car, truck, motorcycle, bus, bicycle)
- **Evaluación de Calidad**: Analiza nitidez, brillo y tamaño para seleccionar mejores frames
- **Extracción Inteligente**: Guarda los mejores 8 frames por vehículo
- **GPU/CPU Auto**: Detecta automáticamente si hay GPU disponible
- **Visualización**: Dibuja bounding boxes con colores por tipo de vehículo

**Ejemplo de uso:**
```python
from apps.traffic_app.services import VideoProcessor

processor = VideoProcessor()

def progress_callback(frame_num, total_frames, stats):
    print(f"Progreso: {frame_num}/{total_frames}")
    print(f"Vehículos detectados: {stats['unique_vehicles']}")

stats = processor.process_video(
    video_source="/path/to/video.mp4",
    progress_callback=progress_callback
)
```

---

### 2. **Vehicle Tracker** (`vehicle_tracker.py`)
Sistema avanzado de tracking con re-identificación.

**Características:**
- **Tracking por IoU**: Mantiene IDs únicos usando Intersection over Union
- **Re-identificación Visual**: Detecta vehículos que regresan después de 1 minuto
- **Feature Extraction**: Extrae histogramas de color para comparación
- **Gestión de Estado**: Diferencia entre tracks activos y perdidos
- **Limpieza Automática**: Elimina tracks antiguos para optimizar memoria

**Flujo de Tracking:**
```
Frame N:
  ├─ Detectar vehículos (YOLO)
  ├─ Matching por IoU con tracks activos
  ├─ Intentar re-identificar con tracks perdidos (>1 min)
  ├─ Crear nuevos tracks para detecciones no matched
  └─ Mover tracks inactivos a "perdidos"
```

**Ventana de Re-identificación:**
- **0-60 segundos**: Vehículo perdido pero no re-identificable
- **60-120 segundos**: Ventana de re-identificación activa
- **>120 segundos**: Track eliminado definitivamente

---

### 3. **WebSocket Consumer** (`consumers.py`)
Comunicación en tiempo real con el frontend.

**Eventos Soportados:**

| Evento | Descripción | Data |
|--------|-------------|------|
| `connection_established` | Cliente conectado | `{analysis_id, message}` |
| `analysis_started` | Análisis iniciado | `{analysis_id, video_info}` |
| `progress_update` | Actualización de progreso | `{frame, total, percentage}` |
| `vehicle_detected` | Nuevo vehículo detectado | `{track_id, type, bbox, is_new}` |
| `frame_processed` | Frame procesado | `{frame_num, detections[]}` |
| `stats_update` | Estadísticas actualizadas | `{counts, unique_vehicles}` |
| `log_message` | Mensaje de log | `{level, message, timestamp}` |
| `analysis_completed` | Análisis terminado | `{stats, duration}` |
| `analysis_error` | Error en análisis | `{error, traceback}` |

**Conexión desde Frontend:**
```typescript
const ws = new WebSocket('ws://localhost:8000/ws/traffic/analysis/123/');

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  
  switch(message.type) {
    case 'vehicle_detected':
      console.log('Nuevo vehículo:', message.data);
      break;
    case 'progress_update':
      updateProgressBar(message.data.percentage);
      break;
    // ...
  }
};
```

---

## 🔄 Flujo Completo del Sistema

```
┌─────────────────────────────────────────────────────────────┐
│ USUARIO                                                      │
│ ├─ Sube video o proporciona URL de stream                   │
│ └─ Abre VideoAnalysisModal                                  │
└────────────────────┬────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────────┐
│ FRONTEND (React)                                             │
│ ├─ Conecta WebSocket: ws://.../ /analysis/{id}/             │
│ ├─ POST /api/traffic/analyses/ {cameraId, video}            │
│ └─ POST /api/traffic/analyses/{id}/start/                   │
└────────────────────┬────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────────┐
│ DJANGO API                                                   │
│ ├─ Crea TrafficAnalysis (status=PENDING)                    │
│ ├─ Guarda video en MEDIA_ROOT                               │
│ └─ Lanza Celery Task: process_video_analysis.delay(id)      │
└────────────────────┬────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────────┐
│ CELERY TASK (Background)                                     │
│ ├─ Carga VideoProcessor                                     │
│ ├─ Procesa video frame por frame:                           │
│ │  ├─ YOLO: Detecta vehículos                              │
│ │  ├─ Tracker: Asigna IDs únicos                           │
│ │  ├─ Evalúa calidad de frames                             │
│ │  ├─ Guarda mejores 8 frames por vehículo                 │
│ │  └─ Cada 1 seg → WebSocket update                        │
│ └─ Al finalizar → Guarda Vehicle + VehicleFrame en BD       │
└────────────────────┬────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────────┐
│ WEBSOCKET (Channels)                                         │
│ ├─ Envía eventos a frontend en tiempo real:                 │
│ │  ├─ progress_update (cada segundo)                        │
│ │  ├─ vehicle_detected (vehículo nuevo)                     │
│ │  ├─ stats_update (contadores actualizados)                │
│ │  └─ log_message (eventos para log UI)                     │
│ └─ analysis_completed (fin exitoso)                         │
└────────────────────┬────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────────┐
│ FRONTEND (React)                                             │
│ ├─ Recibe eventos WebSocket                                 │
│ ├─ Actualiza UI en tiempo real:                             │
│ │  ├─ Barra de progreso                                     │
│ │  ├─ Contador de vehículos                                 │
│ │  ├─ Log de actividad (scroll automático)                  │
│ │  └─ Video con bounding boxes (canvas overlay)             │
│ └─ Al completar → Muestra resultados finales                │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 Estructura de Datos

### TrafficAnalysis (Base de Datos)
```python
{
    'id': 1,
    'cameraId': 1,
    'locationId': 1,
    'videoPath': 'traffic_videos/2025-10-09_143022_video.mp4',
    'status': 'PROCESSING',  # PENDING → PROCESSING → COMPLETED/FAILED
    'startedAt': '2025-10-09T14:30:22Z',
    'totalVehicleCount': 45,
    'carCount': 28,
    'truckCount': 8,
    'motorcycleCount': 7,
    'busCount': 2,
    'bicycleCount': 0,
    'densityLevel': 'MEDIUM'
}
```

### Vehicle (Vehículo Detectado)
```python
{
    'id': 'V00001',  # ID único generado por tracker
    'trafficAnalysisId': 1,
    'vehicleType': 'car',
    'confidence': 0.92,
    'firstDetectedAt': '2025-10-09T14:30:25Z',
    'lastDetectedAt': '2025-10-09T14:30:38Z',
    'trackingStatus': 'COMPLETED',
    'totalFrames': 390,  # Total de frames donde apareció
    'storedFrames': 8,   # Mejores 8 frames guardados
    'avgSpeed': 45.5,
    'direction': 'NORTH',
    'lane': 2
}
```

### VehicleFrame (Frame Guardado)
```python
{
    'id': 123,
    'vehicleId': 'V00001',
    'frameNumber': 150,
    'timestamp': '2025-10-09T14:30:27Z',
    'boundingBoxX': 450,
    'boundingBoxY': 200,
    'boundingBoxWidth': 180,
    'boundingBoxHeight': 120,
    'confidence': 0.95,
    'frameQuality': 0.87,  # Score de calidad (0-1)
    'imagePath': 'frames/V00001_frame_150.jpg'
}
```

---

## 🎯 Próximos Pasos

### Inmediato (Esta Sesión):
1. ✅ Video Processor Service
2. ✅ Vehicle Tracker
3. ✅ WebSocket Consumer
4. 📝 **Celery Tasks** ← SIGUIENTE
5. 📝 ViewSet Updates

### Siguiente Sesión:
6. Frontend: VideoAnalysisModal
7. Frontend: WebSocket Service
8. OCR de Placas (EasyOCR)

---

## 🚀 Cómo Probar (Cuando esté completo)

```bash
# Terminal 1: Iniciar Redis
redis-server

# Terminal 2: Iniciar Celery Worker
cd backend
celery -A config worker --loglevel=info --pool=solo

# Terminal 3: Iniciar Django
python manage.py runserver

# Terminal 4: Frontend
cd frontend
npm run dev
```

**Luego:**
1. Ir a http://localhost:5173/traffic
2. Click en cámara → Click en video negro
3. Subir video o pegar URL de stream
4. Click "Iniciar Análisis"
5. Ver procesamiento en tiempo real! 🎉

---

**Estado Actual**: ✅ Backend Core Completado (75%)  
**Siguiente**: 📝 Celery Tasks + ViewSet Updates
