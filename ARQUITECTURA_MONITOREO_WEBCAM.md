# Arquitectura de Monitoreo en Vivo con Webcam

## 📋 Estado Actual (5 Nov 2025 - 21:11)

### ✅ Implementado

#### Frontend - LiveMonitoring.tsx
**Ubicación**: `frontend/src/pages/monitoring/LiveMonitoring.tsx`

**Funcionalidad**:
- ✅ Detección de cámaras físicas del dispositivo usando `navigator.mediaDevices`
- ✅ Selección de cámara del dropdown
- ✅ Captura de video en tiempo real desde webcam
- ✅ Visualización del stream de video en elemento `<video>`
- ✅ Controles: Iniciar / Detener / Guardar
- ✅ Indicador visual "TRANSMITIENDO"
- ✅ Integración con sistema de cámaras existente (muestra ubicación si viene de `/traffic`)

**Flujo de Ejecución**:
```
1. Usuario abre /monitoring/live
   ↓
2. loadPhysicalCameras() 
   → Solicita permisos de cámara
   → Enumera dispositivos disponibles
   → Muestra en dropdown
   ↓
3. Usuario selecciona cámara y presiona "Iniciar"
   ↓
4. handleStartStream()
   → getUserMedia() con deviceId específico
   → Guarda stream en streamRef.current
   → setIsStreaming(true)
   ↓
5. React renderiza elemento <video>
   ↓
6. useEffect detecta isStreaming=true
   → Adjunta streamRef.current al videoRef.current.srcObject
   → Reproduce video automáticamente
   ↓
7. Video se muestra en pantalla ✅
```

**Estado de los Refs**:
- `videoRef`: Referencia al elemento `<video>` HTML
- `streamRef`: MediaStream actual de la cámara
- `canvasRef`: Canvas para futuras detecciones YOLO (preparado pero no usado aún)

---

### ⚠️ Pendiente de Implementación

#### 1. Procesamiento YOLO en Backend
**Problema Actual**: No hay endpoint para procesar frames de webcam

**Necesario**:
```python
# backend/apps/streaming/views.py
@api_view(['POST'])
def process_frame(request):
    """
    Recibe un frame en base64 desde el frontend
    Procesa con YOLO
    Devuelve detecciones
    """
    frame_base64 = request.data.get('frame')
    frame = decode_base64_to_image(frame_base64)
    
    # Procesar con YOLO
    detections = yolo_processor.detect(frame)
    
    return Response({
        'detections': detections,
        'timestamp': time.time()
    })
```

#### 2. Captura y Envío de Frames
**Frontend necesita**:
```typescript
// Capturar frame del canvas cada 100ms
const captureFrame = () => {
  const canvas = canvasRef.current;
  const video = videoRef.current;
  
  if (!canvas || !video) return;
  
  const ctx = canvas.getContext('2d');
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  ctx.drawImage(video, 0, 0);
  
  // Convertir a base64
  const frameData = canvas.toDataURL('image/jpeg', 0.8);
  
  // Enviar al backend
  sendFrameToBackend(frameData);
};

setInterval(captureFrame, 100); // 10 FPS
```

#### 3. Dibujar Detecciones YOLO
**Frontend necesita**:
```typescript
const drawDetections = (detections) => {
  const canvas = canvasRef.current;
  const ctx = canvas.getContext('2d');
  
  detections.forEach(det => {
    const [x, y, w, h] = det.bbox;
    
    // Dibujar bounding box
    ctx.strokeStyle = '#00FF00';
    ctx.lineWidth = 3;
    ctx.strokeRect(x, y, w, h);
    
    // Dibujar label
    ctx.fillStyle = '#00FF00';
    ctx.font = '16px Arial';
    ctx.fillText(`${det.class} ${(det.confidence * 100).toFixed(1)}%`, x, y - 5);
  });
};
```

#### 4. Guardado a AWS S3
**Backend necesita**:
```python
@api_view(['POST'])
def save_recording(request):
    """
    Recibe chunks de video del frontend
    Guarda en S3
    """
    camera_id = request.data.get('camera_id')
    video_blob = request.data.get('video_blob')
    
    # Subir a S3
    s3_key = f"recordings/{camera_id}/{timestamp}.webm"
    s3_service.upload(video_blob, s3_key)
    
    return Response({'success': True, 's3_key': s3_key})
```

---

## 🏗️ Arquitectura Completa (Objetivo Final)

```
┌─────────────────────────────────────────────────────────────┐
│                      FRONTEND (React)                        │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  /monitoring/live                                            │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  1. Webcam → navigator.mediaDevices                 │   │
│  │     getUserMedia() → MediaStream                    │   │
│  │                                                       │   │
│  │  2. Video Element                                    │   │
│  │     <video ref={videoRef} srcObject={stream} />     │   │
│  │                                                       │   │
│  │  3. Canvas Capture (cada 100ms)                     │   │
│  │     ctx.drawImage(video, 0, 0)                      │   │
│  │     frame = canvas.toDataURL('image/jpeg')          │   │
│  │                                                       │   │
│  │  4. HTTP POST a /api/streaming/process-frame        │   │
│  │     { frame: base64_data }                          │   │
│  │                  ↓                                    │   │
│  └──────────────────┼────────────────────────────────────┘   │
│                     │                                         │
└─────────────────────┼─────────────────────────────────────────┘
                      │
                      │ HTTP POST
                      │
┌─────────────────────▼─────────────────────────────────────────┐
│                   BACKEND (Django)                            │
├───────────────────────────────────────────────────────────────┤
│                                                               │
│  /api/streaming/process-frame                                │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  1. Recibir frame base64                            │    │
│  │     frame_data = request.data['frame']              │    │
│  │                                                       │    │
│  │  2. Decodificar imagen                              │    │
│  │     img = base64_to_cv2(frame_data)                 │    │
│  │                                                       │    │
│  │  3. Procesar con YOLO                               │    │
│  │     results = yolo_model(img)                       │    │
│  │                                                       │    │
│  │  4. Extraer detecciones                             │    │
│  │     detections = [                                   │    │
│  │       {                                              │    │
│  │         'class': 'car',                             │    │
│  │         'confidence': 0.95,                         │    │
│  │         'bbox': [x, y, w, h]                        │    │
│  │       }                                              │    │
│  │     ]                                                │    │
│  │                                                       │    │
│  │  5. Responder con detecciones                       │    │
│  │     return {'detections': detections}               │    │
│  │                  ↓                                    │    │
│  └──────────────────┼────────────────────────────────────┘    │
│                     │                                         │
└─────────────────────┼─────────────────────────────────────────┘
                      │
                      │ JSON Response
                      │
┌─────────────────────▼─────────────────────────────────────────┐
│                      FRONTEND                                 │
├───────────────────────────────────────────────────────────────┤
│                                                               │
│  6. Recibir detecciones                                      │
│  7. Dibujar en canvas sobre video                            │
│     ctx.strokeRect(x, y, w, h)                               │
│     ctx.fillText(label, x, y)                                │
│                                                               │
│  8. Actualizar estadísticas                                  │
│     - Frames procesados                                      │
│     - Detecciones totales                                    │
│     - Tiempo transcurrido                                    │
│                                                               │
└───────────────────────────────────────────────────────────────┘
```

---

## 🔧 Endpoints Necesarios

### Backend - apps/streaming/urls.py
```python
urlpatterns = [
    # ✅ EXISTENTE (pero no usado actualmente)
    path('stream/start/', views.start_stream, name='start_stream'),
    path('stream/stop/', views.stop_stream, name='stop_stream'),
    path('recordings/', views.list_recordings, name='list_recordings'),
    
    # ❌ FALTA IMPLEMENTAR
    path('process-frame/', views.process_frame, name='process_frame'),
    path('save-recording/', views.save_recording, name='save_recording'),
]
```

---

## 📊 Estado de Componentes

| Componente | Estado | Notas |
|------------|--------|-------|
| Detección de cámaras | ✅ | navigator.mediaDevices.enumerateDevices() |
| Captura de video | ✅ | getUserMedia() funcionando |
| Visualización de video | ✅ | Elemento `<video>` muestra stream |
| Controles UI | ✅ | Iniciar/Detener/Guardar |
| Procesamiento YOLO | ❌ | Endpoint no existe |
| Dibujo de detecciones | ⚠️ | Canvas preparado pero no usado |
| Guardado en S3 | ❌ | No implementado |
| Estadísticas en tiempo real | ⚠️ | UI lista pero sin datos reales |

---

## 🚀 Próximos Pasos

### Prioridad Alta
1. **Crear endpoint `/api/streaming/process-frame/`**
   - Recibir frame base64
   - Procesar con YOLO
   - Devolver detecciones

2. **Implementar captura de frames en frontend**
   - Usar requestAnimationFrame o setInterval
   - Convertir canvas a base64
   - Enviar vía HTTP POST

3. **Implementar dibujo de detecciones**
   - Recibir respuesta del backend
   - Dibujar bounding boxes en canvas
   - Mostrar labels y confianza

### Prioridad Media
4. **Sistema de grabación**
   - MediaRecorder API en frontend
   - Guardar video localmente primero
   - Subir a S3 cuando termine

### Prioridad Baja
5. **Optimizaciones**
   - WebSocket en lugar de HTTP polling
   - Compresión de frames
   - Rate limiting (10-15 FPS máximo)

---

## 🐛 Problema Resuelto Hoy

**Issue**: Video element mostraba pantalla negra aunque el stream se obtenía correctamente.

**Causa**: React no había renderizado el elemento `<video>` cuando intentábamos asignar `srcObject` en `handleStartStream`.

**Solución**: 
- Guardar stream en `streamRef.current`
- Cambiar estado a `isStreaming = true`
- Dejar que React renderice
- Usar `useEffect` para adjuntar stream después del render

**Código clave**:
```typescript
// useEffect se ejecuta DESPUÉS de que React renderiza el <video>
useEffect(() => {
  if (isStreaming && streamRef.current && videoRef.current) {
    videoRef.current.srcObject = streamRef.current;
    await videoRef.current.play();
  }
}, [isStreaming]);
```

---

## 📁 Archivos Modificados Hoy

1. `frontend/src/pages/monitoring/LiveMonitoring.tsx`
   - Implementación completa de captura de webcam
   - Refs para video, canvas y stream
   - Controles de inicio/detención
   - Integración con sistema de cámaras existente

2. `frontend/src/components/layout/Sidebar.tsx`
   - Removido "Monitoreo en Vivo" del menú (se accede desde `/traffic`)

3. `frontend/src/pages/traffic/CamerasPage.tsx`
   - Botón "Conectar (Cámara)" ahora redirige a `/monitoring/live?cameraId=X`

---

## 💡 Notas Importantes

- **NO hay backend de streaming de webcam todavía** - Todo es frontend puro
- **YOLO no está procesando** - Solo captura de video funciona
- **S3 no está conectado** - El botón "Guardar" solo detiene el stream
- **Canvas está listo** - Solo falta recibir detecciones y dibujarlas

