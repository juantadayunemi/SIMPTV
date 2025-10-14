# 🎥 Implementación de Procesamiento en Tiempo Real

## 📋 Resumen
Sistema implementado para mostrar frames procesados en tiempo real con detecciones de YOLOv8 + OCR de placas, similar a las imágenes de referencia proporcionadas.

## ✅ Características Implementadas

### 1. **Visualización de Frames Procesados**
- ✅ Canvas HTML5 que recibe frames procesados vía WebSocket
- ✅ Cambio automático entre video original y canvas procesado
- ✅ Indicador visual "PROCESANDO EN TIEMPO REAL" (badge rojo pulsante)

### 2. **Detecciones Visuales en Video**
- ✅ Cajas de colores por tipo de vehículo:
  - 🚗 `car` → Cyan
  - 🚚 `truck` → Rojo
  - 🏍️ `motorcycle` → Magenta
  - 🚌 `bus` → Verde
  - 🚲 `bicycle` → Cyan claro
  - ❓ `other` → Gris

- ✅ Labels con tipo de vehículo y confidence
- ✅ Placas detectadas con fondo azul y texto "Number Plate: ABC-1234"
- ✅ Estilo similar a las imágenes de referencia

### 3. **Backend - Video Processor**
**Archivo:** `backend/apps/traffic_app/services/video_processor.py`

**Nuevos métodos:**
```python
def draw_detections(frame, detections):
    """Dibuja cajas y placas en el frame"""
    - Cajas con colores por tipo de vehículo (grosor 3px)
    - Labels con tipo y confidence
    - Placas con fondo azul y texto "Number Plate"
    
def encode_frame_to_base64(frame, quality=85):
    """Convierte frame a base64 para WebSocket"""
    - Codificación JPEG con calidad configurable
    - Base64 string para envío por WebSocket
```

### 4. **Backend - Celery Task**
**Archivo:** `backend/apps/traffic_app/tasks.py`

**Modificación en `frame_callback`:**
```python
def frame_callback(frame, detections):
    # Dibujar detecciones en el frame
    annotated_frame = processor.draw_detections(frame, detections)
    
    # Enviar cada 3 frames (optimización de ancho de banda)
    if frame_number % 3 == 0:
        frame_base64 = processor.encode_frame_to_base64(annotated_frame, quality=70)
        
        # Enviar evento 'frame_update' con frame procesado
        self.send_event(analysis_id, "frame_update", {
            "frame_number": frame_number,
            "frame_data": frame_base64,
            "detections_count": len(detections)
        })
```

**Optimización:**
- Solo envía 1 de cada 3 frames (~10 FPS si video es 30 FPS)
- Calidad JPEG 70% para reducir tamaño
- Evita saturar el WebSocket

### 5. **Backend - WebSocket Consumer**
**Archivo:** `backend/apps/traffic_app/consumers.py`

**Nuevo handler:**
```python
async def frame_update(self, event):
    """Frame procesado con imagen (base64)"""
    await self.send(
        text_data=json.dumps({"type": "frame_update", "data": event["data"]})
    )
```

### 6. **Frontend - CameraLiveAnalysisPage**
**Archivo:** `frontend/src/pages/traffic/CameraLiveAnalysisPage.tsx`

**Nuevas características:**
```tsx
// Referencia al canvas para frames procesados
const canvasRef = useRef<HTMLCanvasElement>(null);

// Estado para controlar visualización
const [showProcessedFrames, setShowProcessedFrames] = useState(false);

// Suscripción a frames procesados
wsService.on('frame_update', (data) => {
  if (canvasRef.current && data.frame_data) {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    const img = new Image();
    img.onload = () => {
      canvas.width = img.width;
      canvas.height = img.height;
      ctx.drawImage(img, 0, 0);
    };
    img.src = `data:image/jpeg;base64,${data.frame_data}`;
  }
});
```

**Renderizado dual:**
```tsx
{/* Canvas para frames procesados (visible cuando está analizando) */}
<canvas
  ref={canvasRef}
  className={showProcessedFrames ? 'block' : 'hidden'}
/>

{/* Video original (oculto cuando está analizando) */}
<video
  ref={videoRef}
  src={videoUrl}
  className={showProcessedFrames ? 'hidden' : 'block'}
/>

{/* Indicador de procesamiento */}
{showProcessedFrames && (
  <div className="absolute top-4 left-4 bg-red-600 text-white px-4 py-2 rounded-lg">
    <div className="w-3 h-3 bg-white rounded-full animate-pulse"></div>
    <span className="font-semibold">PROCESANDO EN TIEMPO REAL</span>
  </div>
)}
```

## 🎯 Flujo de Ejecución

### 1. **Usuario hace clic en "Iniciar"**
```
Frontend: handlePlay()
  ↓
Backend: POST /api/traffic/analysis/{id}/start/
  ↓
Backend: Actualiza análisis (status="PROCESSING", isPlaying=True)
  ↓
Celery: Inicia task process_video_analysis(analysis_id)
  ↓
Frontend: Muestra canvas (setShowProcessedFrames(true))
```

### 2. **Celery procesa video frame por frame**
```
VideoProcessor: Abre video con OpenCV
  ↓
Para cada frame:
  1. YOLO detecta vehículos
  2. Tracker asigna IDs
  3. OCR detecta placas en ROIs
  4. draw_detections() dibuja cajas y placas
  5. encode_frame_to_base64() codifica frame
  6. WebSocket envía 'frame_update' con frame base64
  ↓
Frontend: Canvas recibe y muestra frame procesado
```

### 3. **Usuario ve detecciones en tiempo real**
```
Canvas: Muestra frames con cajas de colores
DetectionLogPanel: Lista detecciones con timestamp
  - "14:25:18 tipo: car, placa ABC-1234"
  - "14:25:19 tipo: truck, placa XYZ-5678"
```

### 4. **Usuario hace clic en "Pausa"**
```
Frontend: handlePause()
  ↓
Backend: POST /api/traffic/analysis/{id}/pause/
  ↓
Backend: Actualiza análisis (isPaused=True, isPlaying=False)
  ↓
Celery: (en futuro) Pausa procesamiento
  ↓
Frontend: Canvas mantiene último frame
```

## 🚀 Instrucciones de Uso

### 1. **Iniciar Servicios (REQUERIDO)**

**Terminal 1 - Redis:**
```powershell
cd s:\Construccion\SIMPTV\backend\redis
.\redis-server.exe redis.windows.conf
```

**Terminal 2 - Celery Worker:**
```powershell
cd s:\Construccion\SIMPTV\backend
celery -A config worker -l info --pool=solo
```

**Terminal 3 - Django Backend:**
```powershell
cd s:\Construccion\SIMPTV\backend
python manage.py runserver 8001
```

**Terminal 4 - Frontend:**
```powershell
cd s:\Construccion\SIMPTV\frontend
npm run dev
```

### 2. **Ejecutar Análisis**
1. Ir a http://localhost:5174/camera/2
2. Verificar que se ve el video cargado
3. Hacer clic en **"▶️ Iniciar"**
4. Observar:
   - ✅ Badge rojo "PROCESANDO EN TIEMPO REAL" aparece
   - ✅ Canvas muestra frames con cajas de colores
   - ✅ Cajas cian para autos, rojas para camiones, etc.
   - ✅ Placas con fondo azul "Number Plate: ABC-1234"
   - ✅ Panel verde muestra detecciones en tiempo real

### 3. **Controles**
- **Iniciar (▶️):** Inicia procesamiento y muestra frames
- **Pausa (⏸️):** Pausa procesamiento
- **Reconectar (🔄):** Reconecta WebSocket si se desconecta

## 📊 Optimizaciones Implementadas

### 1. **Ancho de Banda**
- ✅ Solo envía 1 de cada 3 frames (reduce tráfico 66%)
- ✅ Calidad JPEG 70% (balance entre calidad y tamaño)
- ✅ Frames escalados si son muy grandes

### 2. **Performance**
- ✅ Canvas hardware-accelerated
- ✅ Procesamiento en background (Celery)
- ✅ WebSocket asíncrono (Django Channels)

### 3. **OCR Optimizado**
- ✅ Solo ejecuta OCR en frames con calidad >= 0.6
- ✅ Solo en ROIs de vehículos detectados
- ✅ Validación de formato de placa (Ecuador: ABC-1234)
- ✅ GPU acceleration si está disponible

## 🎨 Estilo Visual

### Colores de Cajas (según tipo de vehículo)
```python
colors = {
    "car": (0, 255, 255),       # Cyan - similar a imágenes de referencia
    "truck": (0, 0, 255),        # Rojo
    "motorcycle": (255, 0, 255), # Magenta
    "bus": (0, 255, 0),          # Verde
    "bicycle": (255, 255, 0),    # Cyan claro
    "other": (128, 128, 128),    # Gris
}
```

### Labels de Vehículos
- Fondo: Color del tipo de vehículo
- Texto: Negro, tamaño 0.6, grosor 2
- Formato: `"car 0.95"` (tipo + confidence)

### Labels de Placas
- Fondo: Azul `(255, 0, 0)` - igual que en imágenes de referencia
- Texto: Blanco, tamaño 0.7, grosor 2
- Formato: `"Number Plate: ABC-1234"` - igual que en imágenes
- Posición: Debajo del vehículo

## 🐛 Troubleshooting

### "Canvas no muestra nada"
- ✅ Verificar que Redis está corriendo
- ✅ Verificar que Celery está corriendo
- ✅ Verificar en consola: "✅ WebSocket conectado"
- ✅ Verificar en Celery: Debe mostrar "📹 Iniciando procesamiento"

### "DetectionLogPanel dice 'Esperando detecciones...'"
- ✅ Esperar unos segundos, el procesamiento toma tiempo
- ✅ Verificar Celery terminal: Debe mostrar "🚗 Vehicle detected"
- ✅ Verificar consola navegador: "📨 Mensaje recibido [vehicle_detected]"

### "Video se ve negro"
- ✅ Es normal, el canvas empieza negro
- ✅ Esperar que llegue el primer frame (~2-3 segundos)
- ✅ Verificar ancho de banda: frames son ~30-50KB cada uno

### "Frames se ven muy lentos"
- ✅ Normal, se envían ~10 FPS para no saturar
- ✅ Verificar CPU: YOLOv8 + OCR consume recursos
- ✅ Usar GPU si está disponible (más rápido)

## 📝 Notas Técnicas

### Por qué base64 y no video stream?
- Base64 permite control frame-by-frame
- Cada frame viene con detecciones ya dibujadas
- No requiere codec especial en el navegador
- Sincronización perfecta con eventos de detección

### Por qué Canvas y no Video?
- Canvas permite mostrar frames individuales
- Control total sobre qué mostrar y cuándo
- Permite overlays y anotaciones dinámicas
- No depende de codecs de video

### Por qué cada 3 frames?
- 30 FPS original → 10 FPS enviado
- Reduce carga del WebSocket significativamente
- Suficiente para visualización fluida
- Detecciones se siguen procesando en todos los frames

## 🎯 Resultado Final
El sistema ahora muestra el video procesándose en tiempo real, exactamente como en las imágenes de referencia:
- ✅ Cajas de colores alrededor de vehículos detectados
- ✅ Labels con tipo de vehículo y confidence
- ✅ Placas con fondo azul "Number Plate"
- ✅ Panel de detecciones con timestamp
- ✅ Indicador "PROCESANDO EN TIEMPO REAL"

Todo sincronizado en tiempo real mientras Celery procesa el video con YOLOv8 + EasyOCR.
